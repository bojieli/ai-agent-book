"""One SQLite file holding the ingress log and the three kinds of progress.

| table             | book's term     | written by |
|-------------------|-----------------|------------|
| events            | ingress log     | adapters (append-only, unique dedupe_key) |
| audit             | fault evidence  | everyone (append-only) |
| source_progress   | 来源进度         | adapters   |
| dispatch          | 分派进度         | router     |
| task_state        | 任务状态         | runtime    |
| outbox            | 发件箱           | runtime    |

A production system would likely keep these in separate stores owned by
separate services; one file keeps the teaching code small. The tables stay
separate so that replaying the log touches only dispatch progress.
"""

from __future__ import annotations

import json
import sqlite3
from pathlib import Path
from typing import Any

from .envelope import Envelope, dumps, utc_now

SCHEMA = """
CREATE TABLE IF NOT EXISTS events (
    seq         INTEGER PRIMARY KEY AUTOINCREMENT,
    id          TEXT NOT NULL UNIQUE,
    dedupe_key  TEXT NOT NULL UNIQUE,
    thread      TEXT NOT NULL,
    thread_seq  INTEGER NOT NULL,
    envelope    TEXT NOT NULL,
    logged_at   TEXT NOT NULL,
    UNIQUE (thread, thread_seq)
);
CREATE TABLE IF NOT EXISTS audit (
    seq     INTEGER PRIMARY KEY AUTOINCREMENT,
    at      TEXT NOT NULL,
    actor   TEXT NOT NULL,
    action  TEXT NOT NULL,
    ref     TEXT NOT NULL,
    detail  TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS events_no_update BEFORE UPDATE ON events
    BEGIN SELECT RAISE(ABORT, 'ingress log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS events_no_delete BEFORE DELETE ON events
    BEGIN SELECT RAISE(ABORT, 'ingress log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_update BEFORE UPDATE ON audit
    BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;
CREATE TRIGGER IF NOT EXISTS audit_no_delete BEFORE DELETE ON audit
    BEGIN SELECT RAISE(ABORT, 'audit log is append-only'); END;

CREATE TABLE IF NOT EXISTS source_progress (
    source      TEXT PRIMARY KEY,
    position    TEXT NOT NULL,
    updated_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS dispatch (
    event_id       TEXT PRIMARY KEY REFERENCES events(id),
    task_id        TEXT NOT NULL,
    dispatched_at  TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS task_state (
    task_id     TEXT NOT NULL,
    event_id    TEXT NOT NULL REFERENCES events(id),
    step        TEXT NOT NULL,
    updated_at  TEXT NOT NULL,
    PRIMARY KEY (task_id, event_id)
);
CREATE TABLE IF NOT EXISTS outbox (
    idempotency_key  TEXT PRIMARY KEY,
    event_id         TEXT NOT NULL REFERENCES events(id),
    channel          TEXT NOT NULL,
    target           TEXT NOT NULL,
    body             TEXT NOT NULL,
    meta             TEXT NOT NULL,
    status           TEXT NOT NULL,
    receipt          TEXT,
    updated_at       TEXT NOT NULL
);
"""

TERMINAL_STEPS = {"done", "no_reply", "awaiting_human", "draft_failed"}


class Store:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        # Autocommit; writes that must be atomic use an explicit transaction.
        self.db = sqlite3.connect(path, timeout=30, isolation_level=None)
        self.db.row_factory = sqlite3.Row
        self.db.execute("PRAGMA journal_mode=WAL")
        self.db.executescript(SCHEMA)

    def close(self) -> None:
        self.db.close()

    # -- ingress log -------------------------------------------------------

    def append(self, env: Envelope, actor: str) -> tuple[bool, str]:
        """Append an envelope unless its dedupe_key is already logged.

        Returns (appended, event_id). A duplicate is recorded in the audit
        trail rather than silently dropped.
        """
        with self.transaction():
            row = self.db.execute(
                "SELECT id, seq FROM events WHERE dedupe_key = ?", (env.dedupe_key,)
            ).fetchone()
            if row:
                self._audit(
                    actor,
                    "deduplicated",
                    env.dedupe_key,
                    {"event_id": row["id"], "logged_at_seq": row["seq"]},
                )
                return False, row["id"]
            (thread_seq,) = self.db.execute(
                "SELECT COALESCE(MAX(thread_seq), 0) + 1 FROM events WHERE thread = ?",
                (env.thread,),
            ).fetchone()
            self.db.execute(
                "INSERT INTO events (id, dedupe_key, thread, thread_seq, envelope, logged_at)"
                " VALUES (?, ?, ?, ?, ?, ?)",
                (env.id, env.dedupe_key, env.thread, thread_seq, dumps(env.to_dict()), utc_now()),
            )
            self._audit(
                actor,
                "appended",
                env.dedupe_key,
                {"event_id": env.id, "thread": env.thread, "thread_seq": thread_seq},
            )
            return True, env.id

    def events(self) -> list[dict[str, Any]]:
        rows = self.db.execute("SELECT * FROM events ORDER BY seq").fetchall()
        return [{**dict(r), "envelope": json.loads(r["envelope"])} for r in rows]

    def count_events(self, dedupe_key: str | None = None) -> int:
        if dedupe_key is None:
            return self.db.execute("SELECT COUNT(*) FROM events").fetchone()[0]
        return self.db.execute(
            "SELECT COUNT(*) FROM events WHERE dedupe_key = ?", (dedupe_key,)
        ).fetchone()[0]

    # -- audit trail -------------------------------------------------------

    def audit(self, actor: str, action: str, ref: str, detail: dict[str, Any]) -> None:
        self._audit(actor, action, ref, detail)

    def _audit(self, actor: str, action: str, ref: str, detail: dict[str, Any]) -> None:
        self.db.execute(
            "INSERT INTO audit (at, actor, action, ref, detail) VALUES (?, ?, ?, ?, ?)",
            (utc_now(), actor, action, ref, dumps(detail)),
        )

    def audit_rows(self, action: str | None = None) -> list[dict[str, Any]]:
        sql, args = "SELECT * FROM audit", ()
        if action:
            sql, args = sql + " WHERE action = ?", (action,)
        rows = self.db.execute(sql + " ORDER BY seq", args).fetchall()
        return [{**dict(r), "detail": json.loads(r["detail"])} for r in rows]

    # -- source progress (adapters) ----------------------------------------

    def get_source_progress(self, source: str) -> dict[str, Any] | None:
        row = self.db.execute(
            "SELECT position FROM source_progress WHERE source = ?", (source,)
        ).fetchone()
        return json.loads(row["position"]) if row else None

    def set_source_progress(self, source: str, position: dict[str, Any]) -> None:
        self.db.execute(
            "INSERT INTO source_progress (source, position, updated_at) VALUES (?, ?, ?)"
            " ON CONFLICT(source) DO UPDATE SET position = excluded.position,"
            " updated_at = excluded.updated_at",
            (source, dumps(position), utc_now()),
        )

    # -- helpers -----------------------------------------------------------

    def transaction(self) -> _Transaction:
        return _Transaction(self.db)


class _Transaction:
    """BEGIN IMMEDIATE ... COMMIT, so concurrent adapters serialize on writes."""

    def __init__(self, db: sqlite3.Connection):
        self.db = db

    def __enter__(self) -> sqlite3.Connection:
        self.db.execute("BEGIN IMMEDIATE")
        return self.db

    def __exit__(self, exc_type, exc, tb) -> None:
        self.db.execute("ROLLBACK" if exc_type else "COMMIT")
