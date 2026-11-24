"""The unified envelope every adapter produces.

Fields follow the book's example. The envelope records only facts known on
arrival; priority, deadlines and processing state live elsewhere.
"""

from __future__ import annotations

import hashlib
import json
import uuid
from dataclasses import asdict, dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="milliseconds")


def event_id_for(dedupe_key: str) -> str:
    """Derive the event id from the dedupe key, so a redelivery gets the same id."""
    return "evt_" + hashlib.sha256(dedupe_key.encode()).hexdigest()[:12]


@dataclass
class Envelope:
    source: dict[str, Any]  # {"type", "sender", "verified"}
    dedupe_key: str
    thread: str
    kind: str  # "message" or "state"
    content: dict[str, Any]
    raw_ref: str
    occurred_at: str
    reply: dict[str, Any] | None = None  # {"via", "target", ...}; None = no reply path
    correlation: list[str] = field(default_factory=list)
    expires_at: str | None = None
    id: str = ""

    def __post_init__(self) -> None:
        if not self.id:
            self.id = event_id_for(self.dedupe_key)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Envelope:
        return cls(**data)


def save_raw(workdir: Path, source: str, raw: bytes) -> str:
    """Keep the payload exactly as it arrived; the envelope points at it.

    The path is the payload's SHA-256, so a later delivery can never overwrite
    the bytes an earlier event refers to.
    """
    path = Path("raw") / source / f"{hashlib.sha256(raw).hexdigest()}.bin"
    target = workdir / path
    if not target.exists():
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(f"{target.name}.{uuid.uuid4().hex}.tmp")  # private per writer
        tmp.write_bytes(raw)
        tmp.replace(target)
    return path.as_posix()


def dumps(data: Any) -> str:
    return json.dumps(data, ensure_ascii=False, sort_keys=True)
