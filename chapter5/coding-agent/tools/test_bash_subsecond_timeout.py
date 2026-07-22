"""Regression: timeout values under 1000ms must not collapse to 0s."""
import time
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from tools.shell_session import ShellSession


def test_subsecond_timeout_allows_fast_command():
    session = ShellSession(session_id="t1", current_directory="/tmp")
    out, code = session.execute("echo hi", timeout=0.5)
    assert code == 0
    assert "hi" in out
    session.kill()


def test_subsecond_timeout_still_enforced():
    session = ShellSession(session_id="t2", current_directory="/tmp")
    t0 = time.time()
    out, code = session.execute("sleep 2", timeout=0.3)
    elapsed = time.time() - t0
    assert code == -1
    assert "timed out" in out.lower()
    assert elapsed < 1.5
    session.kill()
