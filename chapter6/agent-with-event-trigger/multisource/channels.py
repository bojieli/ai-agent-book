"""Outbound channels, one per kind of crash recovery.

| channel | capability        | after a crash before the receipt was recorded         |
|---------|-------------------|-------------------------------------------------------|
| mail    | ``sent_lookup``   | look for the reply in the Sent folder; resend if absent |
| chat    | ``idempotency_key`` | send again with the same key; the server keeps one copy |
| sms     | ``none``          | cannot tell; mark the reply for manual confirmation   |

Each channel keeps its state in files under the work directory, so it
survives the runtime being killed. ``deliveries()`` reads what the recipient
actually got; the runtime never calls it -- it exists so the demo and the
tests can show that nothing was delivered twice.
"""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any


def _append_jsonl(path: Path, record: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")
        f.flush()


def _read_jsonl(path: Path) -> list[dict[str, Any]]:
    if not path.exists():
        return []
    # Split on "\n" only: splitlines() would also split inside a record on
    # characters such as U+2028, which json.dumps(ensure_ascii=False) keeps.
    text = path.read_text(encoding="utf-8")
    return [json.loads(line) for line in text.split("\n") if line]


class MailChannel:
    """Sends into the test mailbox's Sent folder. The Message-ID is derived
    from the idempotency key, so the runtime can look a reply up later."""

    name, capability = "mail", "sent_lookup"

    def __init__(self, mailbox: Path):
        self.sent = mailbox / "Sent"

    @staticmethod
    def message_id(key: str) -> str:
        return f"<{key}@agent.example>"

    def send(self, target: str, body: str, key: str, meta: dict[str, Any]) -> dict[str, Any]:
        self.sent.mkdir(parents=True, exist_ok=True)
        message_id = self.message_id(key)
        mail = {
            "message_id": message_id,
            "to": target,
            "subject": meta.get("subject", ""),
            "in_reply_to": meta.get("in_reply_to"),
            "body": body,
        }
        # Write under a name the lookup ignores, then rename: a crash leaves
        # either a complete Sent record or none at all.
        name = uuid.uuid4().hex
        tmp = self.sent / f"{name}.partial"
        tmp.write_text(json.dumps(mail, ensure_ascii=False), encoding="utf-8")
        tmp.replace(self.sent / f"{name}.json")
        return {"message_id": message_id}

    def find_sent(self, key: str) -> dict[str, Any] | None:
        message_id = self.message_id(key)
        for mail in self.deliveries():
            if mail["message_id"] == message_id:
                return {"message_id": message_id}
        return None

    def deliveries(self) -> list[dict[str, Any]]:
        return [json.loads(p.read_text(encoding="utf-8")) for p in sorted(self.sent.glob("*.json"))]


class ChatChannel:
    """An app-chat API that honours an ``Idempotency-Key``: a repeated key
    returns the first message's receipt instead of posting again."""

    name, capability = "chat", "idempotency_key"

    def __init__(self, root: Path):
        self.server_log = root / "chat_server.jsonl"

    def send(self, target: str, body: str, key: str, meta: dict[str, Any]) -> dict[str, Any]:
        for msg in self.deliveries():  # server side: the idempotency check
            if msg["idempotency_key"] == key:
                return {"message_id": msg["message_id"], "replayed": True}
        msg = {
            "message_id": f"chat_{uuid.uuid4().hex[:8]}",
            "conversation": target,
            "idempotency_key": key,
            "text": body,
        }
        _append_jsonl(self.server_log, msg)
        return {"message_id": msg["message_id"], "replayed": False}

    def deliveries(self) -> list[dict[str, Any]]:
        return _read_jsonl(self.server_log)


class SmsChannel:
    """A fire-and-forget SMS gateway: no idempotency key, no sent-message API."""

    name, capability = "sms", "none"

    def __init__(self, root: Path):
        self.handset = root / "sms_handset.jsonl"  # what the phone received

    def send(self, target: str, body: str, key: str, meta: dict[str, Any]) -> dict[str, Any]:
        sms_id = f"sms_{uuid.uuid4().hex[:8]}"
        _append_jsonl(self.handset, {"sms_id": sms_id, "to": target, "text": body})
        return {"sms_id": sms_id}

    def deliveries(self) -> list[dict[str, Any]]:
        return _read_jsonl(self.handset)


def default_channels(workdir: Path) -> dict[str, Any]:
    return {
        "mail": MailChannel(workdir / "mailbox"),
        "chat": ChatChannel(workdir / "channels"),
        "sms": SmsChannel(workdir / "channels"),
    }
