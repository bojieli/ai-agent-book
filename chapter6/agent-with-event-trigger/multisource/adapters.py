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


def parse(raw: bytes | str, required: tuple[str, ...]) -> dict:
    """Parse a JSON object and check that the fields the runtime needs exist."""
    try:
        payload = json.loads(raw)
    except ValueError as err:
        raise Malformed(f"not JSON: {err}") from None
    if not isinstance(payload, dict):
        raise Malformed("payload is not a JSON object")
    missing = [f for f in required if not isinstance(payload.get(f), str)]
    if missing:
        raise Malformed(f"missing or non-string fields: {missing}")
    return payload


def sign(secret: str, delivery_id: str, body: bytes) -> str:
    """The signature covers the delivery id too, since it is the dedupe key."""
    message = delivery_id.encode() + b"." + body
    return "sha256=" + hmac.new(secret.encode(), message, hashlib.sha256).hexdigest()


WEBHOOK_FIELDS = ("type", "refund_id", "order_id", "occurred_at")


def webhook_envelope(workdir: Path, delivery_id: str, body: bytes) -> Envelope:
    payload = parse(body, WEBHOOK_FIELDS)
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
            body = self.rfile.read(int(self.headers.get("Content-Length", 0)))
            delivery_id = self.headers.get("X-Delivery-Id", "")
            signature = self.headers.get("X-Signature-256", "")
            if self.path != WEBHOOK_PATH:
                return self._reply(404, {"error": "not found"})
            expected = sign(secret, delivery_id, body)
            if not delivery_id or not hmac.compare_digest(signature, expected):
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


def sqs_envelope(workdir: Path, msg: dict) -> Envelope:
    sender = msg["MessageAttributes"].get("SenderId", "")
    if sender not in SQS_ALLOWED_SENDERS:
        raise Malformed(f"sender {sender!r} is not on the allowlist")
    payload = parse(msg["Body"], SQS_FIELDS)
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


MAIL_FIELDS = ("message_id", "from", "subject", "body", "date")


def mail_envelope(workdir: Path, path: Path) -> Envelope:
    raw = path.read_bytes()
    mail = parse(raw, MAIL_FIELDS)
    if "dkim=pass" not in str(mail.get("authentication_results", "")):
        raise Malformed(f"no passing DKIM result for {mail['message_id']}")
    refs = mail.get("references") or [mail["message_id"]]
    root = refs[0] if isinstance(refs, list) and isinstance(refs[0], str) else mail["message_id"]
    return Envelope(
        source={"type": "mail", "sender": mail["from"], "verified": True},
        dedupe_key=f"mail:msgid:{mail['message_id']}",
        thread=f"mail:thread:{root}",
        kind="message",
        correlation=[f"order:{o}" for o in mail.get("orders", [])],
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
