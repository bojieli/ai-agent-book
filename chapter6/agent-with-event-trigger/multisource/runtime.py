"""The runtime: dispatch logged events to tasks, handle each thread in order,
and send replies through an outbox that survives a crash.

One pass of ``Runtime.run``:

1. reconcile the outbox -- replies whose send was intended but whose receipt
   was never recorded (the runtime died in between);
2. dispatch -- hand every logged event not yet dispatched to a task;
3. process -- for each thread, handle its pending events in ``thread_seq``
   order: draft a reply, record the intent, send, record the receipt.

Restarting is the same as starting: ``run`` replays from the log, and the
dispatch and task tables tell it what is already done.
"""

from __future__ import annotations

import json
from contextlib import contextmanager
from pathlib import Path
from typing import Any

from .envelope import Envelope, utc_now
from .faults import fault_point
from .store import TERMINAL_STEPS, Store

# Stands in for the business system that knows how to reach a customer
# about an order. Webhook and SQS events have no reply path of their own.
CUSTOMER_DIRECTORY = {
    "order:12345": {"via": "chat", "target": "app:conv:conv_88"},
    "order:67890": {"via": "sms", "target": "+86 138 0000 0000"},
}


def route_for(env: Envelope) -> dict[str, Any] | None:
    if env.reply:
        return env.reply
    for ref in env.correlation:
        if ref in CUSTOMER_DIRECTORY:
            return CUSTOMER_DIRECTORY[ref]
    return None


# --------------------------------------------------------------------------
# Responders: the model step. Offline runs use the scripted one.
# --------------------------------------------------------------------------


class ScriptedResponder:
    """Deterministic replies, so the fault scenarios run without an API key."""

    def draft(self, env: Envelope) -> str:
        data = env.content.get("data") or {}
        kind = env.content.get("type")
        if kind == "email":
            subject = env.content.get("subject", "")
            return f"您好，已收到您关于“{subject}”的来信，我们会在 24 小时内处理。"
        if kind == "refund.succeeded":
            return f"订单 {data.get('order_id')} 的退款已经到账（退款单 {data.get('refund_id')}）。"
        if kind == "order.shipped":
            return f"订单 {data.get('order_id')} 已发货，承运商 {data.get('carrier')}。"
        return f"已收到事件 {env.id}。"


class LiveResponder:
    """Drafts the reply with a real model through ``agentbook.providers``."""

    def __init__(self, provider: str, model: str | None = None):
        try:
            from openai import OpenAI

            from agentbook.providers import resolve_backend
        except ImportError as err:
            raise SystemExit(
                f"--live needs the repository package ({err}). From the repository root run "
                "`uv sync --locked --extra ch6 --extra ch4` or `pip install -e .`."
            ) from None

        backend = resolve_backend(provider, model=model)
        self.client = OpenAI(api_key=backend.api_key, base_url=backend.base_url)
        self.model = backend.model

    def draft(self, env: Envelope) -> str:
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {
                    "role": "system",
                    "content": "你是网店客服 Agent。根据事件内容，用一两句中文"
                    "写给顾客的通知或回复，只输出正文。",
                },
                {"role": "user", "content": json.dumps(env.content, ensure_ascii=False)},
            ],
        )
        text = (response.choices[0].message.content or "").strip()
        if not text:  # never send a blank reply; the runtime records draft_failed
            raise ValueError("model returned an empty reply")
        return text


# --------------------------------------------------------------------------
# The runtime
# --------------------------------------------------------------------------


class RuntimeAlreadyRunning(RuntimeError):
    pass


@contextmanager
def single_runtime(workdir: Path):
    """Allow one runtime per work directory.

    Reconciliation treats a pending send as a crashed one. That is only true if
    no other runtime is in the middle of sending it, so a second runtime must
    not start. The OS drops an ``flock`` when its holder dies, even by SIGKILL,
    so a crash never leaves a stale lock behind.
    """
    workdir.mkdir(parents=True, exist_ok=True)
    with open(workdir / "runtime.lock", "a+") as lock:
        try:
            try:
                import fcntl
            except ImportError:  # Windows: msvcrt locks are also dropped when the process dies
                import msvcrt

                lock.seek(0)
                msvcrt.locking(lock.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                fcntl.flock(lock, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError:
            raise RuntimeAlreadyRunning(f"another runtime holds {workdir}/runtime.lock") from None
        yield


class Runtime:
    actor = "runtime"

    def __init__(self, store: Store, channels: dict[str, Any], responder: Any):
        self.store, self.channels, self.responder = store, channels, responder
        self.db = store.db

    def run(self) -> None:
        self.store.audit(
            self.actor,
            "runtime_started",
            "-",
            {
                "events_in_log": self.store.count_events(),
                "already_dispatched": self.db.execute("SELECT COUNT(*) FROM dispatch").fetchone()[
                    0
                ],
            },
        )
        self.reconcile_outbox()
        self.dispatch()
        for events in self.pending_by_thread().values():
            for row in events:  # thread_seq order
                if not self.process(row):
                    break  # keep later events of this thread waiting

    # -- 1. outbox reconciliation -----------------------------------------

    def reconcile_outbox(self) -> None:
        pending = self.db.execute(
            "SELECT * FROM outbox WHERE status = 'pending' ORDER BY rowid"
        ).fetchall()
        for row in pending:
            key, channel = row["idempotency_key"], self.channels[row["channel"]]
            meta = json.loads(row["meta"])
            if channel.capability == "sent_lookup":
                receipt = channel.find_sent(key)
                if receipt:
                    self._record_receipt(
                        row,
                        receipt,
                        "reply_verified_not_resent",
                        {"checked": "Sent folder", "found": receipt},
                    )
                else:
                    receipt = channel.send(row["target"], row["body"], key, meta)
                    self._record_receipt(row, receipt, "reply_resent_after_lookup_miss", {})
            elif channel.capability == "idempotency_key":
                receipt = channel.send(row["target"], row["body"], key, meta)
                self._record_receipt(
                    row,
                    receipt,
                    "reply_confirmed_by_idempotency_key",
                    {"server_replayed_existing": receipt.get("replayed")},
                )
            else:
                with self.store.transaction():
                    self.db.execute(
                        "UPDATE outbox SET status = 'needs_manual_confirmation', updated_at = ?"
                        " WHERE idempotency_key = ?",
                        (utc_now(), key),
                    )
                    self._set_step(row["event_id"], "awaiting_human")
                    self.store.audit(
                        self.actor,
                        "reply_needs_manual_confirmation",
                        key,
                        {
                            "channel": row["channel"],
                            "target": row["target"],
                            "reason": "channel has no idempotency key and no sent-message lookup;"
                            " not resent",
                        },
                    )

    # -- 2. dispatch (router) -----------------------------------------------

    def dispatch(self) -> None:
        rows = self.db.execute(
            "SELECT e.id, e.envelope FROM events e LEFT JOIN dispatch d ON d.event_id = e.id"
            " WHERE d.event_id IS NULL ORDER BY e.seq"
        ).fetchall()
        for row in rows:
            env = Envelope.from_dict(json.loads(row["envelope"]))
            task_id = "task:" + (env.correlation[0] if env.correlation else env.thread)
            with self.store.transaction():
                self.db.execute(
                    "INSERT INTO dispatch VALUES (?, ?, ?)", (env.id, task_id, utc_now())
                )
                self.db.execute(
                    "INSERT INTO task_state VALUES (?, ?, 'received', ?)",
                    (task_id, env.id, utc_now()),
                )

    # -- 3. per-thread processing -----------------------------------------

    def pending_by_thread(self) -> dict[str, list[Any]]:
        rows = self.db.execute(
            "SELECT e.*, t.task_id, t.step FROM events e"
            " JOIN task_state t ON t.event_id = e.id"
            " ORDER BY (SELECT MIN(seq) FROM events f WHERE f.thread = e.thread), e.thread_seq"
        ).fetchall()
        threads: dict[str, list[Any]] = {}
        for row in rows:
            if row["step"] not in TERMINAL_STEPS:
                threads.setdefault(row["thread"], []).append(row)
        return threads

    def process(self, row: Any) -> bool:
        """Handle one event. Returns True once the event reached a terminal step."""
        if row["step"] != "received":
            return False  # e.g. a reply still pending; never skip ahead in a thread
        env = Envelope.from_dict(json.loads(row["envelope"]))
        position = {"thread": env.thread, "thread_seq": row["thread_seq"], "task": row["task_id"]}
        route = None if not env.source.get("verified") else route_for(env)
        if route is None:  # no reply path, or a sender we cannot vouch for
            self._set_step(env.id, "no_reply")
            self.store.audit(self.actor, "processed", env.id, {**position, "reply": None})
            return True

        try:
            body = self.responder.draft(env)
        except Exception as err:  # noqa: BLE001 - a model error must not block replay
            # Nothing was sent, so this event can be retried by hand later; it
            # must not stop every restart at the same place.
            self._set_step(env.id, "draft_failed")
            self.store.audit(self.actor, "draft_failed", env.id, {**position, "error": repr(err)})
            return True
        key = f"reply-{env.id}"
        meta = {k: v for k, v in route.items() if k not in ("via", "target")}
        with self.store.transaction():  # the send intent, before the send
            self.db.execute(
                "INSERT INTO outbox VALUES (?, ?, ?, ?, ?, ?, 'pending', NULL, ?)",
                (key, env.id, route["via"], route["target"], body, json.dumps(meta), utc_now()),
            )
            self._set_step(env.id, "reply_pending")
            self.store.audit(
                self.actor,
                "reply_intent",
                key,
                {**position, "channel": route["via"], "target": route["target"]},
            )

        receipt = self.channels[route["via"]].send(route["target"], body, key, meta)
        fault_point("runtime_after_send")  # crash here: sent, receipt not recorded
        outbox_row = self.db.execute(
            "SELECT * FROM outbox WHERE idempotency_key = ?", (key,)
        ).fetchone()
        self._record_receipt(outbox_row, receipt, "reply_sent", {})
        self.store.audit(self.actor, "processed", env.id, {**position, "reply": key})
        return True

    # -- helpers -------------------------------------------------------------

    def _record_receipt(self, row: Any, receipt: dict, action: str, detail: dict) -> None:
        with self.store.transaction():
            self.db.execute(
                "UPDATE outbox SET status = 'sent', receipt = ?, updated_at = ?"
                " WHERE idempotency_key = ?",
                (json.dumps(receipt), utc_now(), row["idempotency_key"]),
            )
            self._set_step(row["event_id"], "done")
            self.store.audit(
                self.actor,
                action,
                row["idempotency_key"],
                {"channel": row["channel"], "receipt": receipt, **detail},
            )

    def _set_step(self, event_id: str, step: str) -> None:
        self.db.execute(
            "UPDATE task_state SET step = ?, updated_at = ? WHERE event_id = ?",
            (step, utc_now(), event_id),
        )
