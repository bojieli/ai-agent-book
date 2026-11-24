"""Experiment 6-1 extension: multi-source ingress and fault injection.

The three fault tests run the same scenario as ``multisource_demo.py``: real
OS processes, a real local HTTP endpoint, and SIGKILL at named fault points.
No API key is needed; replies come from the scripted responder.
"""

from __future__ import annotations

import json
import sqlite3

import multisource_demo
import pytest
from multisource.channels import default_channels
from multisource.envelope import Envelope
from multisource.fake_sqs import FakeSQS, ReceiptHandleInvalid
from multisource.runtime import Runtime, ScriptedResponder
from multisource.store import Store

# ---------------------------------------------------------------------------
# The three faults, end to end
# ---------------------------------------------------------------------------


@pytest.fixture(scope="module")
def scenario(tmp_path_factory):
    workdir = tmp_path_factory.mktemp("multisource")
    return workdir, multisource_demo.run_all(workdir)


def assert_checks(result: dict) -> None:
    failed = [name for name, ok in result["checks"].items() if not ok]
    assert not failed, json.dumps(result, ensure_ascii=False, indent=1, default=str)


def test_fault_1_duplicate_webhook_delivery_logs_one_event(scenario):
    _, results = scenario
    assert_checks(results["fault_1"])
    actions = [a["action"] for a in results["fault_1"]["audit"]]
    assert actions == ["appended", "deduplicated", "source_rejected"]


def test_fault_2_crash_before_sqs_ack_rereads_without_duplicate(scenario):
    _, results = scenario
    assert_checks(results["fault_2"])
    actions = [a["action"] for a in results["fault_2"]["audit"]]
    assert actions == ["appended", "redelivered", "deduplicated", "acked"]


def test_fault_3_crash_before_receipt_never_sends_twice(scenario):
    workdir, results = scenario
    assert_checks(results["fault_3"])
    # Every reply reached its recipient exactly once.
    channels = default_channels(workdir)
    mail_ids = [m["message_id"] for m in channels["mail"].deliveries()]
    assert len(mail_ids) == len(set(mail_ids)) == 2
    assert len(channels["chat"].deliveries()) == 1
    assert len(channels["sms"].deliveries()) == 1


def test_every_logged_event_was_handled_once(scenario):
    workdir, _ = scenario
    store = Store(workdir / "agent.db")
    assert store.count_events() == 4  # 1 webhook + 1 SQS + 2 mail
    steps = dict(store.db.execute("SELECT event_id, step FROM task_state").fetchall())
    assert sorted(steps.values()) == ["awaiting_human", "done", "done", "done"]
    store.close()


# ---------------------------------------------------------------------------
# Building blocks
# ---------------------------------------------------------------------------


def envelope(thread: str, n: int, reply_to: str | None = "someone@example.com") -> Envelope:
    return Envelope(
        source={"type": "mail", "sender": "someone@example.com", "verified": True},
        dedupe_key=f"test:{thread}:{n}",
        thread=thread,
        kind="message",
        content={"type": "email", "subject": f"{thread} #{n}", "text": ""},
        raw_ref="-",
        occurred_at="2026-11-23T00:00:00+00:00",
        reply={"via": "mail", "target": reply_to} if reply_to else None,
    )


def test_ingress_log_is_append_only_and_unique_on_dedupe_key(tmp_path):
    store = Store(tmp_path / "agent.db")
    assert store.append(envelope("t", 1), "test") == (True, envelope("t", 1).id)
    assert store.append(envelope("t", 1), "test")[0] is False
    assert store.count_events() == 1
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        store.db.execute("UPDATE events SET thread = 'x'")
    with pytest.raises(sqlite3.DatabaseError, match="append-only"):
        store.db.execute("DELETE FROM audit")
    with pytest.raises(sqlite3.IntegrityError):  # the constraint backs up the check
        store.db.execute(
            "INSERT INTO events (id, dedupe_key, thread, thread_seq, envelope, logged_at)"
            " VALUES ('other', 'test:t:1', 't', 99, '{}', 'now')"
        )


def test_runtime_keeps_per_thread_order_across_interleaved_sources(tmp_path):
    store = Store(tmp_path / "agent.db")
    # Two threads interleaved in the log: A1 B1 A2 B2 A3.
    for thread, n in [("A", 1), ("B", 1), ("A", 2), ("B", 2), ("A", 3)]:
        store.append(envelope(thread, n), "test")

    seen = []

    class Recording(ScriptedResponder):
        def draft(self, env):
            seen.append(env.content["subject"])
            return super().draft(env)

    Runtime(store, default_channels(tmp_path), Recording()).run()
    assert [s for s in seen if s.startswith("A")] == ["A #1", "A #2", "A #3"]
    assert [s for s in seen if s.startswith("B")] == ["B #1", "B #2"]
    rows = store.audit_rows("processed")
    for thread in "AB":
        seqs = [r["detail"]["thread_seq"] for r in rows if r["detail"]["thread"] == thread]
        assert seqs == sorted(seqs)


def test_pending_reply_blocks_later_events_of_its_thread_only(tmp_path):
    store = Store(tmp_path / "agent.db")
    for thread, n in [("A", 1), ("A", 2), ("B", 1)]:
        store.append(envelope(thread, n), "test")
    runtime = Runtime(store, default_channels(tmp_path), ScriptedResponder())
    runtime.dispatch()
    # A1 is stuck mid-send (e.g. a step this runtime cannot finish yet).
    store.db.execute(
        "UPDATE task_state SET step = 'reply_pending' WHERE event_id = ?", (envelope("A", 1).id,)
    )
    for events in runtime.pending_by_thread().values():
        for row in events:
            if not runtime.process(row):
                break
    steps = dict(store.db.execute("SELECT event_id, step FROM task_state").fetchall())
    assert steps[envelope("A", 2).id] == "received"  # waits behind A1
    assert steps[envelope("B", 1).id] == "done"  # other threads go on


def test_sent_lookup_miss_resends_once(tmp_path):
    """Crash after recording the intent but before the send: the Sent folder
    has no copy, so reconciliation sends the reply now."""
    store = Store(tmp_path / "agent.db")
    store.append(envelope("A", 1), "test")
    runtime = Runtime(store, default_channels(tmp_path), ScriptedResponder())
    runtime.dispatch()
    key = f"reply-{envelope('A', 1).id}"
    store.db.execute(
        "INSERT INTO outbox VALUES (?, ?, 'mail', 'someone@example.com', 'hi', '{}',"
        " 'pending', NULL, 'now')",
        (key, envelope("A", 1).id),
    )
    store.db.execute("UPDATE task_state SET step = 'reply_pending'")
    runtime.run()
    assert [r["action"] for r in store.audit_rows() if r["ref"] == key] == [
        "reply_resent_after_lookup_miss"
    ]
    assert len(default_channels(tmp_path)["mail"].deliveries()) == 1
    runtime.run()  # a second pass finds nothing left to do
    assert len(default_channels(tmp_path)["mail"].deliveries()) == 1


def test_event_without_reply_path_is_logged_but_not_answered(tmp_path):
    store = Store(tmp_path / "agent.db")
    store.append(envelope("A", 1, reply_to=None), "test")
    Runtime(store, default_channels(tmp_path), ScriptedResponder()).run()
    assert store.db.execute("SELECT step FROM task_state").fetchone()[0] == "no_reply"
    assert store.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0] == 0


class Clock:
    def __init__(self):
        self.now = 1000.0

    def __call__(self):
        return self.now


def test_fake_sqs_visibility_timeout_and_receipt_handles(tmp_path):
    clock = Clock()
    sqs = FakeSQS(tmp_path / "sqs.db", clock=clock)
    sqs.send("m1", group_id="g", sender_id="order-service")
    first = sqs.receive(visibility_timeout=30)
    assert first["ApproximateReceiveCount"] == 1
    assert sqs.receive(visibility_timeout=30) is None  # hidden while in flight
    clock.now += 31
    second = sqs.receive(visibility_timeout=30)  # visible again
    assert second["MessageId"] == first["MessageId"]
    assert second["ApproximateReceiveCount"] == 2
    with pytest.raises(ReceiptHandleInvalid):
        sqs.delete(first["ReceiptHandle"])  # the old handle is stale
    sqs.delete(second["ReceiptHandle"])
    clock.now += 31
    assert sqs.receive(visibility_timeout=30) is None  # deleted for good


def test_fake_sqs_fifo_group_is_delivered_in_order(tmp_path):
    clock = Clock()
    sqs = FakeSQS(tmp_path / "sqs.db", clock=clock)
    sqs.send("g1-a", group_id="g1", sender_id="order-service")
    sqs.send("g1-b", group_id="g1", sender_id="order-service")
    sqs.send("g2-a", group_id="g2", sender_id="order-service")
    a = sqs.receive(visibility_timeout=30)
    assert a["Body"] == "g1-a"
    # g1-b must wait for g1-a; another group is not blocked.
    assert sqs.receive(visibility_timeout=30)["Body"] == "g2-a"
    assert sqs.receive(visibility_timeout=30) is None
    sqs.delete(a["ReceiptHandle"])
    assert sqs.receive(visibility_timeout=30)["Body"] == "g1-b"


def test_sqs_ack_after_visibility_timeout_is_recorded_and_redelivery_deduplicated(tmp_path):
    from multisource.adapters import sqs_poll_once

    clock = Clock()
    sqs = FakeSQS(tmp_path / "sqs.db", clock=clock)
    store = Store(tmp_path / "agent.db")
    body = {"event": "order.shipped", "order_id": "1", "carrier": "x", "occurred_at": "t"}
    sqs.send(json.dumps(body), group_id="g", sender_id="order-service")

    class SlowStore(Store):
        def append(self, env, actor):
            clock.now += 60  # processing outlives the 30 s visibility timeout
            return super().append(env, actor)

    slow = SlowStore(tmp_path / "agent.db")
    assert sqs_poll_once(tmp_path, slow, sqs, visibility_timeout=30)
    assert sqs_poll_once(tmp_path, store, sqs, visibility_timeout=30)  # read again
    actions = [r["action"] for r in store.audit_rows()]
    assert actions == ["appended", "ack_expired", "redelivered", "deduplicated", "acked"]
    assert store.count_events() == 1
    assert sqs.stats()["messages"] == 0


def post_once(tmp_path, store, body: bytes, delivery_id: str, signature: str) -> int:
    """Serve one request on this thread (the store belongs to it, as in the CLI)."""
    import threading
    import urllib.error
    import urllib.request

    from multisource.adapters import WEBHOOK_PATH, make_webhook_server

    server = make_webhook_server(tmp_path, store, "s3cret")
    req = urllib.request.Request(
        f"http://127.0.0.1:{server.server_port}{WEBHOOK_PATH}",
        data=body,
        method="POST",
        headers={"X-Delivery-Id": delivery_id, "X-Signature-256": signature},
    )
    codes = []

    def client():
        try:
            with urllib.request.urlopen(req, timeout=10) as resp:
                codes.append(resp.status)
        except urllib.error.HTTPError as e:
            codes.append(e.code)

    thread = threading.Thread(target=client, daemon=True)
    thread.start()
    server.handle_request()
    thread.join(timeout=10)
    server.server_close()
    return codes[0]


@pytest.mark.parametrize(
    "body",
    [b'{"type": "refund.succeeded"}', b"[1, 2]", b"null", b"not json"],
    ids=["missing-fields", "array", "null", "not-json"],
)
def test_webhook_rejects_malformed_signed_payload(tmp_path, body):
    from multisource.adapters import sign

    store = Store(tmp_path / "agent.db")
    assert post_once(tmp_path, store, body, "d1", sign("s3cret", "d1", body)) == 400
    assert store.count_events() == 0
    assert [r["action"] for r in store.audit_rows()] == ["source_rejected"]


def test_webhook_signature_binds_the_delivery_id(tmp_path):
    """Replaying a signed body under a new delivery id must not pass as new."""
    from multisource.adapters import sign

    store = Store(tmp_path / "agent.db")
    body = multisource_demo.webhook_body()
    signature = sign("s3cret", "d1", body)
    assert post_once(tmp_path, store, body, "d1", signature) == 200
    assert post_once(tmp_path, store, body, "d2", signature) == 401
    assert store.count_events() == 1


def test_unverified_sqs_sender_and_mail_are_rejected_and_never_answered(tmp_path):
    from multisource.adapters import mailbox_poll, sqs_poll_once

    store = Store(tmp_path / "agent.db")
    sqs = FakeSQS(tmp_path / "sqs.db")
    body = {"event": "order.shipped", "order_id": "67890", "carrier": "x", "occurred_at": "t"}
    # The publisher claims to be the order service in its own attributes.
    sqs.send(
        json.dumps(body),
        group_id="g",
        sender_id="intruder",
        attributes={"SenderId": "order-service"},
    )
    sqs.send(
        json.dumps({"event": "order.shipped"}),
        group_id="h",
        sender_id="order-service",
    )  # allowed sender, missing fields
    while sqs_poll_once(tmp_path, store, sqs, visibility_timeout=30):
        pass
    inbox = tmp_path / "mailbox" / "INBOX"
    inbox.mkdir(parents=True)
    mail = {
        "message_id": "<m1@x>",
        "from": "a@x",
        "subject": "s",
        "body": "b",
        "date": "t",
        "authentication_results": "dkim=fail",
    }
    (inbox / "1.json").write_text(json.dumps(mail))
    assert mailbox_poll(tmp_path, store, tmp_path / "mailbox") == 1
    Runtime(store, default_channels(tmp_path), ScriptedResponder()).run()

    assert store.count_events() == 0
    assert len(store.audit_rows("source_rejected")) == 3
    assert sqs.stats()["messages"] == 0  # rejected inputs are still acked
    assert store.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0] == 0


def test_runtime_skips_reply_for_unverified_envelope(tmp_path):
    store = Store(tmp_path / "agent.db")
    env = envelope("A", 1)
    env.source["verified"] = False
    store.append(env, "test")
    Runtime(store, default_channels(tmp_path), ScriptedResponder()).run()
    assert store.db.execute("SELECT step FROM task_state").fetchone()[0] == "no_reply"
    assert store.db.execute("SELECT COUNT(*) FROM outbox").fetchone()[0] == 0


def test_mailbox_cursor_follows_numeric_uid_order(tmp_path):
    from multisource.adapters import mailbox_poll

    store = Store(tmp_path / "agent.db")
    inbox = tmp_path / "mailbox" / "INBOX"
    inbox.mkdir(parents=True)
    for uid in (2, 10):
        mail = {
            "message_id": f"<m{uid}@x>",
            "from": "a@x",
            "subject": str(uid),
            "body": "",
            "date": "t",
            "authentication_results": "mx; dkim=pass header.d=x",
        }
        (inbox / f"{uid}.json").write_text(json.dumps(mail))
    mailbox_poll(tmp_path, store, tmp_path / "mailbox")
    assert [e["envelope"]["content"]["subject"] for e in store.events()] == ["2", "10"]
    assert store.get_source_progress("mailbox:INBOX") == {"last_uid": 10}


def test_raw_payload_is_content_addressed_and_never_overwritten(tmp_path):
    from multisource.envelope import save_raw

    first = save_raw(tmp_path, "webhook", b"one")
    second = save_raw(tmp_path, "webhook", b"two")
    assert first != second
    assert (tmp_path / first).read_bytes() == b"one"
    assert save_raw(tmp_path, "webhook", b"one") == first


def test_only_one_runtime_per_workdir(tmp_path):
    from multisource.runtime import RuntimeAlreadyRunning, single_runtime

    held = single_runtime(tmp_path)
    held.__enter__()
    with pytest.raises(RuntimeAlreadyRunning), single_runtime(tmp_path):
        pass
    held.__exit__(None, None, None)
    with single_runtime(tmp_path):  # released on exit
        pass


@pytest.mark.parametrize(
    "results, ok",
    [
        ("mx.agent.example; dkim=pass header.d=customer.example", True),
        ("mx.agent.example; dkim=pass header.d=CUSTOMER.example", True),
        ("mx.agent.example; dkim=pass header.d=evil.example", False),
        ("mx.agent.example; dkim=fail header.d=customer.example", False),
        ("x-note: dkim=pass header.d=customer.example.evil", False),
        (None, False),
    ],
)
def test_dkim_must_pass_for_the_senders_own_domain(results, ok):
    from multisource.adapters import dkim_aligned

    assert dkim_aligned("li.lei@customer.example", results) is ok


def test_mailbox_rejects_bad_orders_field_and_keeps_reading(tmp_path):
    from multisource.adapters import mailbox_poll

    store = Store(tmp_path / "agent.db")
    inbox = tmp_path / "mailbox" / "INBOX"
    inbox.mkdir(parents=True)
    for uid, orders in ((1, None), (2, ["55501"])):
        mail = {
            "message_id": f"<m{uid}@x>",
            "from": "a@x",
            "subject": "s",
            "body": "",
            "date": "t",
            "authentication_results": "mx; dkim=pass header.d=x",
            "orders": orders,
        }
        (inbox / f"{uid}.json").write_text(json.dumps(mail))
    assert mailbox_poll(tmp_path, store, tmp_path / "mailbox") == 2
    assert len(store.audit_rows("source_rejected")) == 1
    assert [e["envelope"]["correlation"] for e in store.events()] == [["order:55501"]]


def test_unsupported_event_type_is_rejected_at_ingress(tmp_path):
    from multisource.adapters import sign

    store = Store(tmp_path / "agent.db")
    body = json.dumps(
        {"type": "order.shipped", "refund_id": "R", "order_id": "12345", "occurred_at": "t"}
    ).encode()
    assert post_once(tmp_path, store, body, "d1", sign("s3cret", "d1", body)) == 400
    assert store.count_events() == 0


def test_failed_draft_does_not_block_replay(tmp_path):
    store = Store(tmp_path / "agent.db")
    for thread, n in [("A", 1), ("A", 2), ("B", 1)]:
        store.append(envelope(thread, n), "test")

    class Flaky(ScriptedResponder):
        def draft(self, env):
            if env.content["subject"] == "A #1":
                raise RuntimeError("model unavailable")
            return super().draft(env)

    Runtime(store, default_channels(tmp_path), Flaky()).run()
    steps = dict(store.db.execute("SELECT event_id, step FROM task_state").fetchall())
    assert steps[envelope("A", 1).id] == "draft_failed"
    assert steps[envelope("A", 2).id] == steps[envelope("B", 1).id] == "done"
    assert len(store.audit_rows("draft_failed")) == 1


def test_webhook_rejects_bad_content_length(tmp_path):
    import http.client

    from multisource.adapters import WEBHOOK_PATH, make_webhook_server

    store = Store(tmp_path / "agent.db")
    server = make_webhook_server(tmp_path, store, "s3cret")
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    conn.putrequest("POST", WEBHOOK_PATH)
    conn.putheader("Content-Length", "-5")
    conn.endheaders()
    server.handle_request()
    assert conn.getresponse().status == 400
    conn.close()
    server.server_close()


def test_sent_lookup_ignores_partial_writes(tmp_path):
    from multisource.channels import MailChannel

    mail = MailChannel(tmp_path / "mailbox")
    mail.sent.mkdir(parents=True)
    (mail.sent / "crashed.partial").write_text('{"message_id": "<rep')  # torn write
    assert mail.find_sent("reply-x") is None
    mail.send("a@x", "hi", "reply-x", {})
    assert mail.find_sent("reply-x") == {"message_id": "<reply-x@agent.example>"}


def test_fake_sqs_stats_match_receivable_fifo_heads(tmp_path):
    clock = Clock()
    sqs = FakeSQS(tmp_path / "sqs.db", clock=clock)
    sqs.send("a", group_id="g", sender_id="s")
    sqs.send("b", group_id="g", sender_id="s")
    sqs.receive(visibility_timeout=30)
    assert sqs.stats() == {"messages": 2, "in_flight": 1, "visible": 0}


def test_blank_message_ids_are_rejected_not_deduplicated(tmp_path):
    from multisource.adapters import mailbox_poll

    store = Store(tmp_path / "agent.db")
    inbox = tmp_path / "mailbox" / "INBOX"
    inbox.mkdir(parents=True)
    for uid in (1, 2):
        mail = {
            "message_id": "  ",
            "from": "a@x",
            "subject": "s",
            "body": "",
            "date": "t",
            "authentication_results": "mx; dkim=pass header.d=x",
        }
        (inbox / f"{uid}.json").write_text(json.dumps(mail))
    mailbox_poll(tmp_path, store, tmp_path / "mailbox")
    assert store.count_events() == 0
    assert len(store.audit_rows("source_rejected")) == 2
    assert not store.audit_rows("deduplicated")


def test_chat_log_survives_unicode_line_separator(tmp_path):
    from multisource.channels import ChatChannel

    chat = ChatChannel(tmp_path)
    first = chat.send("conv", "第一行 第二行", "k1", {})
    assert chat.send("conv", "第一行 第二行", "k1", {})["message_id"] == first["message_id"]
    assert len(chat.deliveries()) == 1


def test_non_ascii_signature_gets_401(tmp_path):
    import http.client

    from multisource.adapters import WEBHOOK_PATH, make_webhook_server

    store = Store(tmp_path / "agent.db")
    server = make_webhook_server(tmp_path, store, "s3cret")
    conn = http.client.HTTPConnection("127.0.0.1", server.server_port, timeout=10)
    conn.putrequest("POST", WEBHOOK_PATH)
    conn.putheader("Content-Length", "2")
    conn.putheader("X-Delivery-Id", "d1")
    conn.putheader("X-Signature-256", "sha256=é".encode("latin-1"))
    conn.endheaders(b"{}")
    server.handle_request()
    assert conn.getresponse().status == 401
    conn.close()
    server.server_close()
    assert [r["action"] for r in store.audit_rows()] == ["source_rejected"]


def test_empty_model_reply_becomes_draft_failed(tmp_path):
    from types import SimpleNamespace

    from multisource.runtime import LiveResponder

    live = LiveResponder.__new__(LiveResponder)  # skip provider resolution
    live.model = "fake"
    reply = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="  "))])
    live.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **_: reply))
    )
    store = Store(tmp_path / "agent.db")
    store.append(envelope("A", 1), "test")
    Runtime(store, default_channels(tmp_path), live).run()
    assert store.db.execute("SELECT step FROM task_state").fetchone()[0] == "draft_failed"
    assert default_channels(tmp_path)["mail"].deliveries() == []


def test_dkim_second_aligned_signature_counts():
    from multisource.adapters import dkim_aligned

    results = "mx; dkim=pass header.d=relay.example; dkim=pass header.d=customer.example"
    assert dkim_aligned("li.lei@customer.example", results)


@pytest.mark.parametrize(
    "extra",
    [{"references": [""]}, {"references": {}}, {"subject": "\ud800"}],
    ids=["blank-reference", "non-list-references", "lone-surrogate"],
)
def test_mailbox_rejects_bad_references_and_unencodable_text(tmp_path, extra):
    from multisource.adapters import mailbox_poll

    store = Store(tmp_path / "agent.db")
    inbox = tmp_path / "mailbox" / "INBOX"
    inbox.mkdir(parents=True)
    mail = {
        "message_id": "<m1@x>",
        "from": "a@x",
        "subject": "s",
        "body": "",
        "date": "t",
        "authentication_results": "mx; dkim=pass header.d=x",
        **extra,
    }
    (inbox / "1.json").write_text(json.dumps(mail))
    assert mailbox_poll(tmp_path, store, tmp_path / "mailbox") == 1
    assert store.count_events() == 0
    assert len(store.audit_rows("source_rejected")) == 1
