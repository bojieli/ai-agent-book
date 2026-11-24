"""Inbound adapters. Each one: verify the source, build an envelope, append it
to the ingress log, and only then acknowledge the source.

| source  | verification            | dedupe_key            | thread              | ack            |
|---------|-------------------------|-----------------------|---------------------|----------------|
| Webhook | HMAC-SHA256 signature   | delivery id           | refund id           | HTTP 200       |
| SQS     | sender allowlist        | SQS MessageId         | MessageGroupId      | DeleteMessage  |
| Mailbox | DKIM result in headers  | Message-ID            | first References id | read position  |

An input that fails verification or is malformed is not logged as an event:
it is recorded as ``source_rejected`` in the audit trail and still acked, so
the source does not redeliver something that can never succeed.
"""

from __future__ import annotations

import hashlib
import hmac
import json
import re
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

from .envelope import Envelope, save_raw
from .fake_sqs import FakeSQS, ReceiptHandleInvalid
from .faults import fault_point
from .store import Store

# --------------------------------------------------------------------------
# Webhook: a payment service calls us when a refund changes state.
# --------------------------------------------------------------------------

WEBHOOK_PATH = "/webhooks/payments"


class Malformed(ValueError):
    pass


def parse(raw: bytes | str, required: tuple[str, ...], may_be_empty: tuple[str, ...] = ()) -> dict:
    """Parse a JSON object and check that the fields the runtime needs exist.

    Required fields must be non-blank strings unless listed in ``may_be_empty``:
    a blank id would make distinct inputs collide on one dedupe key.
    """
    try:
        payload = json.loads(raw)
    except ValueError as err:
        raise Malformed(f"not JSON: {err}") from None
    if not isinstance(payload, dict):
        raise Malformed("payload is not a JSON object")
    missing = [
        f
        for f in required
        if not isinstance(payload.get(f), str) or (f not in may_be_empty and not payload[f].strip())
    ]
    if missing:
        raise Malformed(f"missing, blank or non-string fields: {missing}")
    try:  # e.g. an escaped lone surrogate decodes but cannot be stored
        json.dumps(payload, ensure_ascii=False).encode("utf-8")
    except UnicodeEncodeError:
        raise Malformed("payload contains text that is not valid UTF-8") from None
    return payload


def sign(secret: str, delivery_id: str, body: bytes) -> str:
    """The signature covers the delivery id too, since it is the dedupe key."""
    message = delivery_id.encode() + b"." + body
    return "sha256=" + hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


WEBHOOK_FIELDS = ("type", "refund_id", "order_id", "occurred_at")
WEBHOOK_TYPES = {"refund.succeeded"}
MAX_BODY = 64 * 1024


def webhook_envelope(workdir: Path, delivery_id: str, body: bytes) -> Envelope:
    payload = parse(body, WEBHOOK_FIELDS)
    if payload["type"] not in WEBHOOK_TYPES:
        raise Malformed(f"unsupported event type {payload['type']!r}")
    return Envelope(
        source={"type": "webhook", "sender": "payments", "verified": True},
        dedupe_key=f"webhook:payments:delivery:{delivery_id}",
        thread=f"payments:refund:{payload['refund_id']}",
        kind="state",  # it reports the refund's current status
        correlation=[f"order:{payload['order_id']}"],
        content={"type": payload["type"], "data": payload},
        raw_ref=save_raw(workdir, "webhook", body),
        reply=None,  # a callback has no reply path
        occurred_at=payload["occurred_at"],
    )


def make_webhook_server(workdir: Path, store: Store, secret: str, port: int = 0) -> HTTPServer:
    class Handler(BaseHTTPRequestHandler):
        def do_POST(self) -> None:
            try:
                length = int(self.headers.get("Content-Length", ""))
            except ValueError:
                length = -1
            if not 0 <= length <= MAX_BODY:
                return self._reply(400, {"error": "missing or invalid Content-Length"})
            body = self.rfile.read(length)
            delivery_id = self.headers.get("X-Delivery-Id", "")
            signature = self.headers.get("X-Signature-256", "")
            if self.path != WEBHOOK_PATH:
                return self._reply(404, {"error": "not found"})
            expected = sign(secret, delivery_id, body)
            # compare_digest needs ASCII strings; anything else is simply wrong.
            ok = delivery_id and signature.isascii() and hmac.compare_digest(signature, expected)
            if not ok:
                store.audit(
                    "webhook-adapter",
                    "source_rejected",
                    f"delivery:{delivery_id}",
                    {"reason": "bad or missing HMAC signature"},
                )
                return self._reply(401, {"error": "invalid signature"})
            try:
                env = webhook_envelope(workdir, delivery_id, body)
            except Malformed as err:  # signed, but not a payload we understand
                store.audit(
                    "webhook-adapter",
                    "source_rejected",
                    f"delivery:{delivery_id}",
                    {"reason": f"malformed payload: {err}"},
                )
                return self._reply(400, {"error": "malformed payload"})
            appended, event_id = store.append(env, actor="webhook-adapter")
            # The 2xx below is the ack. It is sent only after the log write.
            self._reply(200, {"event_id": event_id, "deduplicated": not appended})

        timeout = 10  # seconds; a stalled client cannot hold the server forever

        def _reply(self, status: int, data: dict) -> None:
            out = json.dumps(data).encode()
            self.send_response(status)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(out)))
            self.end_headers()
            self.wfile.write(out)

        def log_message(self, *args) -> None:  # keep demo output readable
            pass

    return HTTPServer(("127.0.0.1", port), Handler)


# --------------------------------------------------------------------------
# SQS: the order service publishes order state changes to a FIFO queue.
# --------------------------------------------------------------------------

SQS_QUEUE = "orders.fifo"
SQS_ALLOWED_SENDERS = {"order-service"}


SQS_FIELDS = ("event", "order_id", "carrier", "occurred_at")
SQS_TYPES = {"order.shipped"}


def sqs_envelope(workdir: Path, msg: dict) -> Envelope:
    sender = msg["Attributes"]["SenderId"]  # queue-owned, not publisher-supplied
    if sender not in SQS_ALLOWED_SENDERS:
        raise Malformed(f"sender {sender!r} is not on the allowlist")
    payload = parse(msg["Body"], SQS_FIELDS)
    if payload["event"] not in SQS_TYPES:
        raise Malformed(f"unsupported event type {payload['event']!r}")
    return Envelope(
        source={"type": "sqs", "sender": sender, "verified": True},
        dedupe_key=f"sqs:{SQS_QUEUE}:msg:{msg['MessageId']}",
        thread=f"sqs:{SQS_QUEUE}:group:{msg['MessageGroupId']}",
        kind="state",
        correlation=[f"order:{payload['order_id']}"],
        content={"type": payload["event"], "data": payload},
        raw_ref=save_raw(workdir, "sqs", msg["Body"].encode()),
        reply=None,
        occurred_at=payload["occurred_at"],
    )


def sqs_poll_once(workdir: Path, store: Store, sqs: FakeSQS, visibility_timeout: float) -> bool:
    """Receive at most one message. Returns False when the queue had nothing visible."""
    msg = sqs.receive(visibility_timeout)
    if msg is None:
        return False
    source = f"sqs:{SQS_QUEUE}"
    store.set_source_progress(
        source, {"in_flight": msg["MessageId"], "receipt_handle": msg["ReceiptHandle"]}
    )
    ref = f"sqs:{SQS_QUEUE}:msg:{msg['MessageId']}"
    if msg["ApproximateReceiveCount"] > 1:
        store.audit(
            "sqs-adapter",
            "redelivered",
            ref,
            {"message_id": msg["MessageId"], "receive_count": msg["ApproximateReceiveCount"]},
        )
    try:
        store.append(sqs_envelope(workdir, msg), actor="sqs-adapter")
    except Malformed as err:
        store.audit("sqs-adapter", "source_rejected", ref, {"reason": str(err)})
    fault_point("sqs_after_log")  # crash here: logged, but not yet deleted
    try:
        sqs.delete(msg["ReceiptHandle"])  # the ack
    except ReceiptHandleInvalid:
        # Processing outlived the visibility timeout. The message will be read
        # again and deduplicated, so recording this is enough.
        store.audit("sqs-adapter", "ack_expired", ref, {"message_id": msg["MessageId"]})
        return True
    store.audit("sqs-adapter", "acked", ref, {"message_id": msg["MessageId"]})
    store.set_source_progress(source, {"last_deleted": msg["MessageId"]})
    return True


# --------------------------------------------------------------------------
# Mailbox: a local test mailbox, one JSON file per message in INBOX/.
# --------------------------------------------------------------------------

MAILBOX_SOURCE = "mailbox:INBOX"
# Written by the (simulated) receiving mail server, e.g.
# "mx.agent.example; dkim=pass header.d=customer.example"
DKIM_PASS = re.compile(r"\s*dkim=pass\s+header\.d=([A-Za-z0-9.-]+)\s*")


def dkim_aligned(sender: str, results: object) -> bool:
    """A passing DKIM signature whose domain is the From address's domain."""
    if not isinstance(results, str) or "@" not in sender:
        return False
    domain = sender.rsplit("@", 1)[1].lower()
    for clause in results.split(";"):  # each result is checked on its own
        m = DKIM_PASS.fullmatch(clause)
        if m and m.group(1).lower() == domain:
            return True
    return False


def _str_list(value: object) -> bool:
    return isinstance(value, list) and all(isinstance(v, str) and v.strip() for v in value)


MAIL_FIELDS = ("message_id", "from", "subject", "body", "date")


def mail_envelope(workdir: Path, path: Path) -> Envelope:
    raw = path.read_bytes()
    mail = parse(raw, MAIL_FIELDS, may_be_empty=("subject", "body"))
    if not dkim_aligned(mail["from"], mail.get("authentication_results")):
        raise Malformed(f"no passing DKIM result for the sender of {mail['message_id']}")
    refs = mail.get("references", [])
    orders = mail.get("orders", [])
    if not _str_list(refs) or not _str_list(orders):
        raise Malformed("references and orders must be lists of non-blank strings")
    root = refs[0] if refs else mail["message_id"]
    return Envelope(
        source={"type": "mail", "sender": mail["from"], "verified": True},
        dedupe_key=f"mail:msgid:{mail['message_id']}",
        thread=f"mail:thread:{root}",
        kind="message",
        correlation=[f"order:{o}" for o in orders],
        content={"type": "email", "subject": mail["subject"], "text": mail["body"]},
        raw_ref=save_raw(workdir, "mail", raw),
        reply={
            "via": "mail",
            "target": mail["from"],
            "in_reply_to": mail["message_id"],
            "subject": "Re: " + mail["subject"],
        },
        occurred_at=mail["date"],
    )


def mailbox_poll(workdir: Path, store: Store, mailbox: Path) -> int:
    """Read INBOX messages after the stored read position. Returns how many."""
    last_uid = (store.get_source_progress(MAILBOX_SOURCE) or {}).get("last_uid", 0)
    read = 0
    inbox = [p for p in (mailbox / "INBOX").glob("*.json") if p.stem.isdigit()]
    for path in sorted(inbox, key=lambda p: int(p.stem)):  # numeric UID order
        uid = int(path.stem)
        if uid <= last_uid:
            continue
        try:
            store.append(mail_envelope(workdir, path), actor="mailbox-adapter")
        except Malformed as err:
            store.audit(
                "mailbox-adapter", "source_rejected", f"mail:uid:{uid}", {"reason": str(err)}
            )
        store.set_source_progress(MAILBOX_SOURCE, {"last_uid": uid})  # the ack
        read += 1
    return read
