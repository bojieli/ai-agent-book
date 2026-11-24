#!/usr/bin/env python3
"""Experiment 6-1 extension: multi-source ingress and fault injection.

Runs offline with no API key. Every role (Webhook server, SQS poller, mailbox
poller, runtime) is a separate OS process; faults 2 and 3 SIGKILL the process
at a named fault point.

    python multisource_demo.py                       # scripted replies, temp workdir
    python multisource_demo.py --workdir runs/demo   # keep the SQLite files and mailbox
    python multisource_demo.py --live --provider kimi   # draft replies with a real model
    python multisource_demo.py --evidence-dir validation/experiment_6_1_multisource/RUN

Exit status is 0 only when every check passes.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

from multisource.__main__ import DEFAULT_WEBHOOK_SECRET, paths
from multisource.adapters import sign
from multisource.channels import default_channels
from multisource.fake_sqs import FakeSQS
from multisource.faults import module_command, run_cli
from multisource.store import Store

VISIBILITY_TIMEOUT = 1.0
WEBHOOK_DELIVERY = "dlv_7f3a01"
COMPLAINT_ID = "<complaint-55501@customer.example>"


# --------------------------------------------------------------------------
# Inputs
# --------------------------------------------------------------------------


def seed_sources(workdir: Path) -> str:
    """Two related emails in the test mailbox, one order event on the queue."""
    inbox = paths(workdir)["mailbox"] / "INBOX"
    inbox.mkdir(parents=True, exist_ok=True)
    mails = [
        {
            "message_id": COMPLAINT_ID,
            "from": "li.lei@customer.example",
            "subject": "订单 55501 少发了一件",
            "body": "收到的包裹里少了一件衬衫，请尽快处理。",
            "date": "2026-11-23T09:00:00+08:00",
            "references": [],
            "authentication_results": "mx.agent.example; dkim=pass header.d=customer.example",
        },
        {
            "message_id": "<followup-55501@customer.example>",
            "from": "li.lei@customer.example",
            "subject": "Re: 订单 55501 少发了一件",
            "body": "补充：发票也请一起寄给我。",
            "date": "2026-11-23T09:05:00+08:00",
            "references": [COMPLAINT_ID],
            "authentication_results": "mx.agent.example; dkim=pass header.d=customer.example",
        },
    ]
    for uid, mail in enumerate(mails, 1):
        (inbox / f"{uid:06d}.json").write_text(json.dumps(mail, ensure_ascii=False), "utf-8")
    sqs = FakeSQS(paths(workdir)["sqs"])
    body = {
        "event": "order.shipped",
        "order_id": "67890",
        "carrier": "SF Express",
        "occurred_at": "2026-11-23T10:00:00+08:00",
    }
    message_id = sqs.send(json.dumps(body), group_id="order-67890", sender_id="order-service")
    sqs.close()
    return message_id


def webhook_body() -> bytes:
    return json.dumps(
        {
            "type": "refund.succeeded",
            "refund_id": "R-1",
            "order_id": "12345",
            "status": "succeeded",
            "occurred_at": "2026-11-23T14:30:00+08:00",
        }
    ).encode()


def post(url: str, body: bytes, delivery_id: str, signature: str) -> tuple[int, dict]:
    req = urllib.request.Request(
        url,
        data=body,
        method="POST",
        headers={
            "Content-Type": "application/json",
            "X-Delivery-Id": delivery_id,
            "X-Signature-256": signature,
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as err:
        return err.code, json.loads(err.read())


def audit_of(store: Store, ref: str, *actions: str) -> list[dict]:
    return [
        {
            "seq": r["seq"],
            "actor": r["actor"],
            "action": r["action"],
            "ref": r["ref"],
            "detail": r["detail"],
        }
        for r in store.audit_rows()
        if r["ref"] == ref and (not actions or r["action"] in actions)
    ]


# --------------------------------------------------------------------------
# Fault 1: duplicate Webhook delivery
# --------------------------------------------------------------------------


def fault_duplicate_delivery(workdir: Path) -> dict:
    server = subprocess.Popen(
        module_command("webhook", "--workdir", str(workdir)),
        cwd=Path(__file__).resolve().parent,
        text=True,
        stdout=subprocess.PIPE,
    )
    try:
        assert server.stdout is not None
        url = server.stdout.readline().split()[1]
        body = webhook_body()
        secret = os.environ.get("WEBHOOK_SECRET", DEFAULT_WEBHOOK_SECRET)  # as the server does
        good = sign(secret, WEBHOOK_DELIVERY, body)
        first = post(url, body, WEBHOOK_DELIVERY, good)
        second = post(url, body, WEBHOOK_DELIVERY, good)  # the payment service retries
        forged = post(url, body, "dlv_forged", sign(secret + "-wrong", "dlv_forged", body))
    finally:
        server.terminate()
        server.wait(timeout=10)

    key = f"webhook:payments:delivery:{WEBHOOK_DELIVERY}"
    store = Store(paths(workdir)["store"])
    evidence = {
        "responses": {"first": first, "second": second, "forged_signature": forged},
        "events_with_dedupe_key": store.count_events(key),
        "audit": audit_of(store, key) + audit_of(store, "delivery:dlv_forged"),
    }
    store.close()
    evidence["checks"] = {
        "both_deliveries_acked_2xx": first[0] == 200 and second[0] == 200,
        "second_delivery_deduplicated": second[1].get("deduplicated") is True,
        "one_event_in_log": evidence["events_with_dedupe_key"] == 1,
        "dedup_recorded_in_audit": any(a["action"] == "deduplicated" for a in evidence["audit"]),
        "forged_signature_rejected": forged[0] == 401,
    }
    return evidence


# --------------------------------------------------------------------------
# Fault 2: SQS adapter killed after the log write, before DeleteMessage
# --------------------------------------------------------------------------


def fault_crash_before_ack(workdir: Path, message_id: str) -> dict:
    poll = [
        "sqs-poll",
        "--workdir",
        str(workdir),
        "--once",
        "--visibility-timeout",
        str(VISIBILITY_TIMEOUT),
    ]
    key = f"sqs:orders.fifo:msg:{message_id}"
    first = run_cli(poll, fault="sqs_after_log")

    store, sqs = Store(paths(workdir)["store"]), FakeSQS(paths(workdir)["sqs"])
    after_kill = {"events_with_dedupe_key": store.count_events(key), "queue": sqs.stats()}
    time.sleep(VISIBILITY_TIMEOUT + 0.3)  # let the visibility timeout expire
    visible_again = sqs.stats()
    second = run_cli(poll)
    after_restart = {"events_with_dedupe_key": store.count_events(key), "queue": sqs.stats()}
    evidence = {
        "first_run": {"killed": first["killed"], "output": first["output"].strip()},
        "after_kill": after_kill,
        "after_visibility_timeout": {"queue": visible_again},
        "second_run": {"killed": second["killed"], "output": second["output"].strip()},
        "after_restart": after_restart,
        "audit": audit_of(store, key),
    }
    store.close()
    sqs.close()
    actions = [a["action"] for a in evidence["audit"]]
    redelivered = [a for a in evidence["audit"] if a["action"] == "redelivered"]
    evidence["checks"] = {
        "adapter_killed_at_fault_point": first["killed"],
        # The message must still exist; whether it is still hidden depends on
        # how long the kill took, so redelivery is checked separately below.
        "logged_but_not_deleted": after_kill["events_with_dedupe_key"] == 1
        and after_kill["queue"]["messages"] == 1,
        "message_visible_again": visible_again["visible"] == 1,
        "re_read_recorded": bool(redelivered) and redelivered[0]["detail"]["receive_count"] == 2,
        "still_one_event_in_log": after_restart["events_with_dedupe_key"] == 1,
        "dedup_recorded_in_audit": "deduplicated" in actions,
        "deleted_after_second_log_write": "acked" in actions
        and after_restart["queue"]["messages"] == 0,
    }
    return evidence


# --------------------------------------------------------------------------
# Fault 3: runtime killed after each send, before the receipt is recorded
# --------------------------------------------------------------------------


def fault_crash_before_receipt(workdir: Path, runtime_args: list[str]) -> dict:
    run_cli(["mailbox-poll", "--workdir", str(workdir)])
    runs = []
    for _ in range(10):  # at most one crash per reply; 4 replies in this scenario
        result = run_cli(
            ["runtime", "--workdir", str(workdir), *runtime_args], fault="runtime_after_send"
        )
        run = {"killed": result["killed"], "returncode": result["returncode"]}
        if not result["killed"] and result["returncode"] != 0:
            run["error"] = result["output"].strip()[-2000:]  # surface why it failed
        runs.append(run)
        if not result["killed"]:
            break

    store = Store(paths(workdir)["store"])
    outbox = [
        dict(r)
        for r in store.db.execute(
            "SELECT idempotency_key, channel, target, status FROM outbox ORDER BY rowid"
        )
    ]
    recovery_actions = (
        "reply_verified_not_resent",
        "reply_confirmed_by_idempotency_key",
        "reply_needs_manual_confirmation",
        "reply_resent_after_lookup_miss",
    )
    recovery = [
        {"seq": r["seq"], "action": r["action"], "ref": r["ref"], "detail": r["detail"]}
        for r in store.audit_rows()
        if r["action"] in recovery_actions
    ]
    deliveries = {name: len(ch.deliveries()) for name, ch in default_channels(workdir).items()}
    order = [
        (r["detail"]["thread"], r["detail"]["thread_seq"]) for r in store.audit_rows("reply_intent")
    ]
    store.close()

    by_action: dict[str, list] = {}
    for r in recovery:
        by_action.setdefault(r["action"], []).append(r)
    status = {o["channel"]: o["status"] for o in outbox}
    evidence = {
        "runtime_runs": runs,
        "outbox": outbox,
        "recovery_audit": recovery,
        "deliveries_per_channel": deliveries,
        "reply_order": order,
    }
    evidence["checks"] = {
        "runtime_killed_once_per_reply": sum(r["killed"] for r in runs) == len(outbox) == 4,
        "final_run_completed": not runs[-1]["killed"] and runs[-1]["returncode"] == 0,
        "mail_verified_via_sent_folder_not_resent": len(
            by_action.get("reply_verified_not_resent", [])
        )
        == 2
        and deliveries["mail"] == 2,
        "chat_confirmed_by_idempotency_key_no_duplicate": len(
            by_action.get("reply_confirmed_by_idempotency_key", [])
        )
        == 1
        and by_action["reply_confirmed_by_idempotency_key"][0]["detail"]["server_replayed_existing"]
        is True
        and deliveries["chat"] == 1,
        "sms_marked_for_manual_confirmation_not_resent": status.get("sms")
        == "needs_manual_confirmation"
        and deliveries["sms"] == 1
        and any(
            r["detail"]["channel"] == "sms"
            for r in by_action.get("reply_needs_manual_confirmation", [])
        ),
        # Both emails must land in one thread and be answered in order, across
        # the runtime restarts between them.
        "per_thread_order_kept": [s for t, s in order if t == f"mail:thread:{COMPLAINT_ID}"]
        == [1, 2],
    }
    return evidence


# --------------------------------------------------------------------------
# Printing and evidence
# --------------------------------------------------------------------------


def show_audit(rows: list[dict]) -> None:
    for a in rows:
        print(f"    audit #{a['seq']:<3} {a['action']:<36} {a['ref']}")
        print(f"               {json.dumps(a['detail'], ensure_ascii=False)}")


def show_checks(checks: dict) -> None:
    for name, ok in checks.items():
        print(f"    [{'PASS' if ok else 'FAIL'}] {name}")


def report(results: dict) -> None:
    f1, f2, f3 = results["fault_1"], results["fault_2"], results["fault_3"]
    print("\n== 故障 1：重复投递（Webhook 同一投递 ID 收到两次） ==")
    for name, (code, body) in f1["responses"].items():
        print(f"    POST {name:<17} -> HTTP {code} {json.dumps(body)}")
    print(f"    日志中该投递 ID 的事件数：{f1['events_with_dedupe_key']}")
    show_audit(f1["audit"])
    show_checks(f1["checks"])

    print("\n== 故障 2：确认前崩溃（SQS 适配器写日志后、删除消息前被 SIGKILL） ==")
    print(f"    第一次运行：{f2['first_run']['output']}")
    print(
        f"    被杀后：日志事件 {f2['after_kill']['events_with_dedupe_key']} 条，"
        f"队列 {f2['after_kill']['queue']}"
    )
    print(f"    可见性超时后：队列 {f2['after_visibility_timeout']['queue']}")
    print(f"    第二次运行：{f2['second_run']['output']}")
    print(
        f"    重启后：日志事件 {f2['after_restart']['events_with_dedupe_key']} 条，"
        f"队列 {f2['after_restart']['queue']}"
    )
    show_audit(f2["audit"])
    show_checks(f2["checks"])

    print("\n== 故障 3：回执前崩溃（运行时发出回复后、记录回执前被 SIGKILL） ==")
    for i, run in enumerate(f3["runtime_runs"], 1):
        print(
            f"    第 {i} 次启动运行时："
            + (
                "在 runtime_after_send 处被杀"
                if run["killed"]
                else "正常结束"
                if run["returncode"] == 0
                else f"异常退出（返回码 {run['returncode']}）"
            )
        )
        if "error" in run:
            print("      " + run["error"].replace("\n", "\n      "))
    for o in f3["outbox"]:
        print(f"    outbox {o['idempotency_key']:<24} {o['channel']:<5} -> {o['status']}")
    print(f"    各渠道实际送达条数：{f3['deliveries_per_channel']}")
    show_audit(f3["recovery_audit"])
    show_checks(f3["checks"])


def write_evidence(evidence_dir: Path, results: dict, live: bool) -> None:
    evidence_dir.mkdir(parents=True, exist_ok=True)
    generated_at = datetime.now(timezone.utc).isoformat()
    summary = {
        "experiment": "6-1-extension-multisource",
        "campaign_id": evidence_dir.name,
        "generated_at": generated_at,
        "mode": "live-model" if live else "offline-scripted-responder",
        "environment": {"python": platform.python_version(), "platform": platform.platform()},
        "sources": {
            "mailbox": "local test mailbox (JSON files)",
            "webhook": "stdlib http.server on 127.0.0.1, HMAC-SHA256",
            "sqs": "local file-backed FIFO queue simulation (multisource/fake_sqs.py)",
        },
        "faults": "SIGKILL from the parent process at a named fault point",
        "status": "passed" if all_passed(results) else "failed",
        "results": results,
    }
    (evidence_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", "utf-8"
    )
    data = (evidence_dir / "summary.json").read_bytes()
    manifest = {
        "experiment": summary["experiment"],
        "campaign_id": summary["campaign_id"],
        "generated_at": generated_at,
        "status": summary["status"],
        "files": [
            {"path": "summary.json", "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}
        ],
    }
    (evidence_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", "utf-8")


def all_passed(results: dict) -> bool:
    return all(all(r["checks"].values()) for r in results.values())


def run_all(workdir: Path, runtime_args: list[str] | None = None) -> dict:
    message_id = seed_sources(workdir)
    return {
        "fault_1": fault_duplicate_delivery(workdir),
        "fault_2": fault_crash_before_ack(workdir, message_id),
        "fault_3": fault_crash_before_receipt(workdir, runtime_args or []),
    }


def main() -> int:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("--workdir", type=Path, help="an empty or new directory (default: temp)")
    parser.add_argument("--evidence-dir", type=Path, help="write summary.json + manifest.json")
    parser.add_argument("--live", action="store_true", help="draft replies with a real model")
    parser.add_argument("--provider", default="kimi")
    parser.add_argument("--model")
    args = parser.parse_args()

    workdir = args.workdir or Path(tempfile.mkdtemp(prefix="exp6-1-multisource-"))
    if workdir.exists() and any(workdir.iterdir()):
        parser.error(f"--workdir {workdir} is not empty; pass a new directory")
    if args.evidence_dir and args.evidence_dir.exists():
        parser.error(
            f"--evidence-dir {args.evidence_dir} exists; recorded runs are not overwritten"
        )
    workdir.mkdir(parents=True, exist_ok=True)
    workdir = workdir.resolve()
    runtime_args = ["--live", "--provider", args.provider] if args.live else []
    if args.live and args.model:
        runtime_args += ["--model", args.model]

    print(f"workdir: {workdir}")
    results = run_all(workdir, runtime_args)
    report(results)
    if args.evidence_dir:
        write_evidence(args.evidence_dir, results, args.live)
        print(f"\nevidence: {args.evidence_dir}/summary.json")
    ok = all_passed(results)
    print("\nALL CHECKS PASSED" if ok else "\nSOME CHECKS FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
