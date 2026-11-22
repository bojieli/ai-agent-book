"""Regression tests for #1068: the executors must not hard-code /bin/bash.

On native Windows there is no /bin/bash, so every code_interpreter and
virtual_terminal call used to die with FileNotFoundError. The executor now
looks bash up (Git Bash / WSL on Windows), reports a clear error when it is
missing, and runs local Python through the current interpreter instead of a
`python3` that Windows does not have on PATH.
"""
import asyncio
import sys
from pathlib import Path

import pytest

import multilang_executor as ml
from multilang_executor import (
    BASH_MISSING_ERROR,
    ExecutionStatus,
    LanguageExecutor,
    find_bash,
)


def test_find_bash_posix_prefers_bin_bash(monkeypatch):
    monkeypatch.setattr(ml.os, "name", "posix")
    monkeypatch.setattr(ml.os.path, "exists", lambda p: p == "/bin/bash")
    monkeypatch.setattr(ml.shutil, "which", lambda name: None)
    assert find_bash() == "/bin/bash"


def test_find_bash_windows_uses_bash_on_path(monkeypatch):
    monkeypatch.setattr(ml.os, "name", "nt")
    monkeypatch.setattr(
        ml.shutil, "which",
        lambda name: r"C:\Program Files\Git\bin\bash.exe" if name == "bash" else None,
    )
    assert find_bash() == r"C:\Program Files\Git\bin\bash.exe"


def test_find_bash_missing_returns_none(monkeypatch):
    monkeypatch.setattr(ml.os, "name", "nt")
    monkeypatch.setattr(ml.shutil, "which", lambda name: None)
    assert find_bash() is None


def test_run_command_reports_missing_bash_instead_of_raising(monkeypatch):
    monkeypatch.setattr(ml, "find_bash", lambda: None)
    result = asyncio.run(LanguageExecutor()._run_command("echo hi", timeout=5))
    assert result["status"] == ExecutionStatus.ERROR
    assert result["error"] == BASH_MISSING_ERROR


def test_local_python_uses_current_interpreter(monkeypatch):
    captured = {}

    async def fake_run(self, command, timeout, stdin=None, cwd=None, shell=True):
        captured["command"] = command
        return {"status": ExecutionStatus.SUCCESS, "returncode": 0,
                "stdout": "", "stderr": "", "execution_time": 0.0}

    monkeypatch.setattr(ml.shutil, "which", lambda name: None)  # no docker -> local path
    monkeypatch.setattr(LanguageExecutor, "_run_command", fake_run)
    asyncio.run(LanguageExecutor()._run_python("print(1)", 5, 5, None, {}))
    assert Path(sys.executable).as_posix() in captured["command"]
    assert "python3 -I" not in captured["command"]
    assert "\\" not in captured["command"]


@pytest.mark.skipif(find_bash() is None, reason="needs a bash to run")
def test_bash_roundtrip_with_real_bash():
    result = asyncio.run(LanguageExecutor()._run_command("echo ok", timeout=10))
    assert result["status"] == ExecutionStatus.SUCCESS
    assert result["stdout"].strip() == "ok"


@pytest.mark.skipif(find_bash() is None, reason="needs a bash to run")
def test_python_roundtrip_with_real_interpreter(monkeypatch):
    monkeypatch.setattr(ml.shutil, "which", lambda name: find_bash() if name == "bash" else None)
    result = asyncio.run(LanguageExecutor()._run_python("print(2 + 2)", 10, 10, None, {}))
    assert result["status"] == ExecutionStatus.SUCCESS, result
    assert result["stdout"].strip() == "4"
    assert result["sandbox"]["kind"] == "local-process"
