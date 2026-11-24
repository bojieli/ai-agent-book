"""Named fault points and a helper that kills a process when it reaches one.

A fault is a real ``SIGKILL`` from another process, not an exception: no
``finally`` block, no ``atexit`` handler and no buffered write gets a chance to
run. The child only announces that it reached the point and waits; the
parent does the killing.

Fault points:

* ``sqs_after_log``       -- SQS adapter: event logged, message not yet deleted
* ``runtime_after_send``  -- runtime: reply sent, receipt not yet recorded
"""

from __future__ import annotations

import os
import queue
import subprocess
import sys
import threading
import time
from pathlib import Path

FAULT_ENV = "MULTISOURCE_FAULT"
MARKER = "FAULT-POINT"
EXPERIMENT_ROOT = Path(__file__).resolve().parents[1]


def fault_point(name: str) -> None:
    if os.environ.get(FAULT_ENV) == name:
        print(f"{MARKER} {name} pid={os.getpid()}", flush=True)
        while True:  # wait for the parent's SIGKILL
            time.sleep(60)


def module_command(*args: str) -> list[str]:
    return [sys.executable, "-m", "multisource", *args]


def run_cli(args: list[str], fault: str | None = None, timeout: float = 60) -> dict:
    """Run ``python -m multisource ARGS``. If ``fault`` names a point that is
    reached, kill the process with SIGKILL there.

    Returns {"killed": bool, "returncode": int, "output": str}.
    """
    env = {**os.environ, "PYTHONUNBUFFERED": "1"}
    env.pop(FAULT_ENV, None)
    if fault:
        env[FAULT_ENV] = fault
    proc = subprocess.Popen(
        module_command(*args),
        cwd=EXPERIMENT_ROOT,
        env=env,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
    )
    lines: queue.Queue[str | None] = queue.Queue()

    def pump() -> None:
        assert proc.stdout is not None
        for line in proc.stdout:
            lines.put(line)
        lines.put(None)

    threading.Thread(target=pump, daemon=True).start()
    output, killed = [], False
    deadline = time.monotonic() + timeout
    while True:
        try:
            line = lines.get(timeout=max(0.0, deadline - time.monotonic()))
        except queue.Empty:
            proc.kill()
            raise TimeoutError(f"{args} did not finish in {timeout}s") from None
        if line is None:
            break
        output.append(line)
        if line.startswith(MARKER) and not killed:
            proc.kill()  # SIGKILL on POSIX, TerminateProcess on Windows
            killed = True
    proc.wait(timeout=timeout)
    return {"killed": killed, "returncode": proc.returncode, "output": "".join(output)}
