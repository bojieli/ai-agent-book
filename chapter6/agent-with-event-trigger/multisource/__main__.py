"""Command line: one process per role, so a fault can kill exactly one of them.

    python -m multisource webhook      --workdir W [--port 0]
    python -m multisource sqs-poll     --workdir W [--once] [--visibility-timeout 1]
    python -m multisource mailbox-poll --workdir W
    python -m multisource runtime      --workdir W [--live --provider kimi]

Set MULTISOURCE_FAULT=<point> to stop a process at a fault point (see faults.py).
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path

from .adapters import WEBHOOK_PATH, mailbox_poll, make_webhook_server, sqs_poll_once
from .channels import default_channels
from .fake_sqs import FakeSQS
from .runtime import LiveResponder, Runtime, ScriptedResponder, single_runtime
from .store import Store

DEFAULT_WEBHOOK_SECRET = "demo-webhook-secret"


def positive_float(text: str) -> float:
    value = float(text)
    if not 0 < value < float("inf"):
        raise argparse.ArgumentTypeError("must be a positive number of seconds")
    return value


def paths(workdir: Path) -> dict[str, Path]:
    return {
        "store": workdir / "agent.db",
        "sqs": workdir / "sqs.db",
        "mailbox": workdir / "mailbox",
    }


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m multisource",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    sub = parser.add_subparsers(dest="command", required=True)
    for name in ("webhook", "sqs-poll", "mailbox-poll", "runtime"):
        p = sub.add_parser(name)
        p.add_argument("--workdir", type=Path, required=True)
        if name == "webhook":
            p.add_argument("--port", type=int, default=0, help="0 picks a free port")
        if name == "sqs-poll":
            p.add_argument("--once", action="store_true", help="receive at most one message")
            p.add_argument("--visibility-timeout", type=positive_float, default=1.0)
        if name == "runtime":
            p.add_argument(
                "--live",
                action="store_true",
                help="draft replies with a real model instead of the script",
            )
            p.add_argument("--provider", default=os.environ.get("LLM_PROVIDER", "kimi"))
            p.add_argument("--model", default=os.environ.get("LLM_MODEL"))
    args = parser.parse_args(argv)

    p = paths(args.workdir)
    store = Store(p["store"])
    if args.command == "webhook":
        secret = os.environ.get("WEBHOOK_SECRET", DEFAULT_WEBHOOK_SECRET)
        server = make_webhook_server(args.workdir, store, secret, args.port)
        print(f"LISTENING http://127.0.0.1:{server.server_port}{WEBHOOK_PATH}", flush=True)
        server.serve_forever()
    elif args.command == "sqs-poll":
        sqs = FakeSQS(p["sqs"])
        while sqs_poll_once(args.workdir, store, sqs, args.visibility_timeout) and not args.once:
            pass
        print(f"sqs-poll done; queue {sqs.stats()}", flush=True)
    elif args.command == "mailbox-poll":
        n = mailbox_poll(args.workdir, store, p["mailbox"])
        print(f"mailbox-poll read {n} new message(s)", flush=True)
    elif args.command == "runtime":
        responder = LiveResponder(args.provider, args.model) if args.live else ScriptedResponder()
        with single_runtime(args.workdir):
            Runtime(store, default_channels(args.workdir), responder).run()
        print("runtime pass complete", flush=True)


if __name__ == "__main__":
    main()
