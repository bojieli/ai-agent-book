"""Tests for execution tools."""

import asyncio
import shlex
import shutil
import subprocess
import sys
import uuid
from pathlib import Path

import multilang_executor
from execution_tools import ExecutionTools
from llm_helper import LLMHelper
from multilang_executor import ExecutionStatus


TEST_TEMP_DIR = Path(__file__).with_name(".test-tmp")


def run_async(coro):
    return asyncio.run(coro)


class WritableTemporaryDirectory:
    def __init__(self, prefix=None, suffix=None, dir=None, ignore_cleanup_errors=False):
        base = Path(dir) if dir is not None else TEST_TEMP_DIR
        base.mkdir(parents=True, exist_ok=True)
        name = f"{prefix or 'tmp_'}{uuid.uuid4().hex}{suffix or ''}"
        self.name = str(base / name)
        self.ignore_cleanup_errors = ignore_cleanup_errors

    def __enter__(self):
        Path(self.name).mkdir(parents=True, exist_ok=False)
        return self.name

    def __exit__(self, exc_type, exc, tb):
        shutil.rmtree(self.name, ignore_errors=self.ignore_cleanup_errors)


def make_execution_tools(monkeypatch) -> ExecutionTools:
    TEST_TEMP_DIR.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(multilang_executor.tempfile, "TemporaryDirectory", WritableTemporaryDirectory)
    return ExecutionTools(LLMHelper())


def test_code_interpreter_executes_valid_python(monkeypatch):
    execution_tools = make_execution_tools(monkeypatch)

    async def fake_execute_code(**_kwargs):
        return {
            "status": ExecutionStatus.SUCCESS,
            "language": "python",
            "stdout": "Test successful\n2 + 2 = 4\n",
            "stderr": "",
            "returncode": 0,
            "execution_time": 0.01,
            "sandbox": {"kind": "test"},
        }

    monkeypatch.setattr(execution_tools.lang_executor, "execute_code", fake_execute_code)

    result = run_async(
        execution_tools.code_interpreter(
            code='print("Test successful")\nresult = 2 + 2\nprint(f"2 + 2 = {result}")',
            language="python",
            timeout=10,
        )
    )

    assert result["success"], f"Code execution failed: {result.get('error')}"
    assert "Test successful" in result["stdout"]
    assert "2 + 2 = 4" in result["stdout"]


def test_code_interpreter_reports_runtime_failure(monkeypatch):
    execution_tools = make_execution_tools(monkeypatch)

    async def fake_execute_code(**_kwargs):
        return {
            "status": ExecutionStatus.FAILED,
            "language": "python",
            "stdout": "",
            "stderr": "Traceback...\nZeroDivisionError: division by zero\n",
            "returncode": 1,
            "execution_time": 0.01,
            "sandbox": {"kind": "test"},
        }

    monkeypatch.setattr(execution_tools.lang_executor, "execute_code", fake_execute_code)

    result = run_async(
        execution_tools.code_interpreter(
            code="x = 1 / 0",
            language="python",
            timeout=10,
        )
    )

    assert not result["success"]
    assert result.get("returncode") not in (0, None)
    assert "ZeroDivisionError" in result.get("stderr", "")


def test_virtual_terminal_reports_success_and_failure(monkeypatch):
    execution_tools = make_execution_tools(monkeypatch)

    def fake_run(command, **_kwargs):
        command_text = command if isinstance(command, str) else " ".join(command)
        if "sys.exit(3)" in command_text:
            return subprocess.CompletedProcess(command, 3, "", "")
        return subprocess.CompletedProcess(command, 0, "Terminal test\n", "")

    monkeypatch.setattr("execution_tools.subprocess.run", fake_run)

    success = run_async(
        execution_tools.virtual_terminal(
            command=shlex.join(
                [Path(sys.executable).as_posix(), "-c", "print('Terminal test')"]
            ),
            timeout=10,
        )
    )

    assert success["success"], f"Command failed: {success.get('error')}"
    assert "Terminal test" in success["stdout"]

    failure = run_async(
        execution_tools.virtual_terminal(
            command=shlex.join(
                [Path(sys.executable).as_posix(), "-c", "import sys; sys.exit(3)"]
            ),
            timeout=10,
        )
    )

    assert not failure["success"]
    assert failure["returncode"] == 3


def test_syntax_verification_rejects_invalid_python(monkeypatch):
    execution_tools = make_execution_tools(monkeypatch)

    result = run_async(
        execution_tools.code_interpreter(
            code='print("Unclosed string',
            language="python",
        )
    )

    assert not result["success"]
    assert result["verification"] == "failed"
    assert "Syntax error" in result["error"]


def test_python3_is_normalized_before_syntax_verification(monkeypatch):
    execution_tools = make_execution_tools(monkeypatch)
    verified_languages = []

    def fake_verify_code_syntax(_code, language):
        verified_languages.append(language)
        return False, "invalid syntax"

    monkeypatch.setattr(
        execution_tools.llm_helper,
        "verify_code_syntax",
        fake_verify_code_syntax,
    )

    result = run_async(
        execution_tools.code_interpreter(
            code="not valid python",
            language="python3",
        )
    )

    assert verified_languages == ["python"]
    assert result["language"] == "python"
    assert result["verification"] == "failed"
