"""A local stand-in for an Amazon SQS FIFO queue.

It keeps the semantics the experiment depends on:

* ``receive`` hides a message for ``visibility_timeout`` seconds and hands out
  a fresh receipt handle; ``ApproximateReceiveCount`` goes up by one.
* ``delete`` needs the current receipt handle. An expired handle is refused,
  as it is for a FIFO queue.
* A message that is not deleted before its timeout becomes visible again.
* Within one ``MessageGroupId``, nothing is delivered while an earlier
  message of the group is in flight, so a group is consumed in order.

The queue lives in its own SQLite file, separate from the agent's store,
because it stands for an external service: killing the adapter process must
not lose or delete its messages.
"""

from __future__ import annotations

import json
import sqlite3
import time
import uuid
from pathlib import Path
from typing import Any

SCHEMA = """
CREATE TABLE IF NOT EXISTS messages (
    seq             INTEGER PRIMARY KEY AUTOINCREMENT,
    message_id      TEXT NOT NULL UNIQUE,
    group_id        TEXT NOT NULL,
    body            TEXT NOT NULL,
    sender_id       TEXT NOT NULL,
    attributes      TEXT NOT NULL,
    visible_at      REAL NOT NULL,
    receive_count   INTEGER NOT NULL DEFAULT 0,
    receipt_handle  TEXT
);
"""


class ReceiptHandleInvalid(Exception):
    pass


class FakeSQS:
    def __init__(self, path: Path, clock=time.time):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.db = sqlite3.connect(path, timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)
        self.clock = clock

    def close(self) -> None:
        self.db.close()

    def send(
        self,
        body: str,
        group_id: str,
        sender_id: str,
        attributes: dict[str, str] | None = None,
    ) -> str:
        """``sender_id`` stands for the authenticated principal. Real SQS sets the
        ``SenderId`` system attribute from the caller's IAM credentials; the
        publisher cannot choose it, unlike ``MessageAttributes``."""
        message_id = str(uuid.uuid4())
        self.db.execute(
            "INSERT INTO messages (message_id, group_id, body, sender_id, attributes, visible_at)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (message_id, group_id, body, sender_id, json.dumps(attributes or {}), self.clock()),
        )
        return message_id

    def receive(self, visibility_timeout: float) -> dict[str, Any] | None:
        now = self.clock()
        self.db.execute("BEGIN IMMEDIATE")
        try:
            # Head of each group only, and only if that head is visible.
            row = self.db.execute(
                """
                SELECT * FROM messages m
                WHERE visible_at <= ?
                  AND seq = (SELECT MIN(seq) FROM messages g WHERE g.group_id = m.group_id)
                ORDER BY seq LIMIT 1
                """,
                (now,),
            ).fetchone()
            if row is None:
                self.db.execute("COMMIT")
                return None
            handle = uuid.uuid4().hex
            self.db.execute(
                "UPDATE messages SET visible_at = ?, receive_count = receive_count + 1,"
                " receipt_handle = ? WHERE seq = ?",
                (now + visibility_timeout, handle, row["seq"]),
            )
            self.db.execute("COMMIT")
        except BaseException:
            self.db.execute("ROLLBACK")
            raise
        return {
            "MessageId": row["message_id"],
            "ReceiptHandle": handle,
            "Body": row["body"],
            "MessageGroupId": row["group_id"],
            "ApproximateReceiveCount": row["receive_count"] + 1,
            "Attributes": {"SenderId": row["sender_id"]},  # set by the queue
            "MessageAttributes": json.loads(row["attributes"]),  # set by the publisher
        }

    def delete(self, receipt_handle: str) -> None:
        cur = self.db.execute(
            "DELETE FROM messages WHERE receipt_handle = ? AND visible_at > ?",
            (receipt_handle, self.clock()),
        )
        if cur.rowcount != 1:
            raise ReceiptHandleInvalid(receipt_handle)

    def stats(self) -> dict[str, int]:
        """``visible`` counts what ``receive`` could return now: visible group heads."""
        now = self.clock()
        total, in_flight, visible = self.db.execute(
            """
            SELECT COUNT(*), COALESCE(SUM(visible_at > :now), 0),
                   COALESCE(SUM(visible_at <= :now AND seq =
                       (SELECT MIN(seq) FROM messages g WHERE g.group_id = m.group_id)), 0)
            FROM messages m
            """,
            {"now": now},
        ).fetchone()
        return {"messages": total, "in_flight": in_flight, "visible": visible}
