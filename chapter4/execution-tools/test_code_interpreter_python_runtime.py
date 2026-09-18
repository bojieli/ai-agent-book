import asyncio
import subprocess
import sys
from pathlib import Path

from multilang_executor import ExecutionStatus, LanguageExecutor

TEST_TEMP_ROOT = Path(__file__).with_name(".test-runtime-tmp")


class FixedTemporaryDirectory:
    def __init__(self, path: Path):
        self.name = str(path)

    def __enter__(self):
        Path(self.name).mkdir(parents=True, exist_ok=True)
        return self.name

    def __exit__(self, exc_type, exc, tb):
        return False


def run_async(coro):
    return asyncio.run(coro)


def case_dir(name: str) -> Path:
    path = TEST_TEMP_ROOT / name
    path.mkdir(parents=True, exist_ok=True)
    return path


def test_python_docker_command_uses_mount_syntax_for_windows_paths(monkeypatch):
    root = case_dir("docker mount")
    executor = LanguageExecutor(workspace_dir=str(root))
    commands = []

    monkeypatch.setattr(executor, "_is_docker_available", lambda: True)
    monkeypatch.setattr(
        "multilang_executor.Config.PYTHON_DOCKER_IMAGE",
        "example/python-science:latest",
    )
    monkeypatch.setattr(
        executor,
        "_temporary_dir",
        lambda prefix: FixedTemporaryDirectory(root / "python_case"),
    )

    async def fake_run_command(command, timeout, stdin=None, cwd=None, shell=True):
        commands.append(command)
        return {
            "status": ExecutionStatus.SUCCESS,
            "returncode": 0,
            "stdout": "ok\n",
            "stderr": "",
            "execution_time": 0.01,
        }

    monkeypatch.setattr(executor, "_run_command", fake_run_command)

    result = run_async(
        executor.execute_code("print('ok')", "python", timeout=3)
    )

    assert result["status"] == ExecutionStatus.SUCCESS
    assert commands, "Docker command was not executed"
    assert " --mount " in commands[0]
    assert " -v " not in commands[0]
    expected_mount = (
        f"type=bind,source={(root / 'python_case').resolve().as_posix()},"
        "target=/workspace"
    )
    assert expected_mount in commands[0]
    assert "example/python-science:latest" in commands[0]


def test_python_falls_back_to_current_interpreter_when_docker_unavailable(monkeypatch):
    root = case_dir("local_fallback")
    executor = LanguageExecutor(workspace_dir=str(root))
    commands = []

    monkeypatch.setattr(executor, "_is_docker_available", lambda: False)
    monkeypatch.setattr(
        executor,
        "_temporary_dir",
        lambda prefix: FixedTemporaryDirectory(root / "python_case"),
    )

    async def fake_run_command(command, timeout, stdin=None, cwd=None, shell=True):
        commands.append(command)
        return {
            "status": ExecutionStatus.SUCCESS,
            "returncode": 0,
            "stdout": "local ok\n",
            "stderr": "",
            "execution_time": 0.01,
        }

    monkeypatch.setattr(executor, "_run_command", fake_run_command)

    result = run_async(
        executor.execute_code("print('local ok')", "python", timeout=3)
    )

    assert result["status"] == ExecutionStatus.SUCCESS
    assert result["sandbox"] == {"kind": "local-process", "degraded": True}
    assert commands
    assert Path(sys.executable).as_posix() in commands[0]
    assert "python3 " not in commands[0]


def test_python_does_not_fall_back_when_docker_image_lacks_package(monkeypatch):
    root = case_dir("docker_missing_package")
    executor = LanguageExecutor(workspace_dir=str(root))
    commands = []

    monkeypatch.setattr(executor, "_is_docker_available", lambda: True)
    monkeypatch.setattr(
        executor,
        "_temporary_dir",
        lambda prefix: FixedTemporaryDirectory(root / "python_case"),
    )

    async def fake_run_command(command, timeout, stdin=None, cwd=None, shell=True):
        commands.append(command)
        return {
            "status": ExecutionStatus.FAILED,
            "returncode": 1,
            "stdout": "",
            "stderr": "ModuleNotFoundError: No module named 'numpy'\n",
            "execution_time": 0.01,
        }

    monkeypatch.setattr(executor, "_run_command", fake_run_command)

    result = run_async(
        executor.execute_code("import numpy as np\nprint('numpy ok')", "python", timeout=3)
    )

    assert result["status"] == ExecutionStatus.FAILED
    assert len(commands) == 1
    assert "docker run" in commands[0]
    assert result["sandbox"] == {
        "kind": "docker",
        "image": "python:3.11-slim",
        "network": "none",
        "rootfs": "read-only",
        "memory": "256m",
        "cpus": 1,
        "pids_limit": 64,
    }


def test_python_temp_directory_is_created_under_workspace(monkeypatch):
    root = case_dir("workspace_temp")
    executor = LanguageExecutor(workspace_dir=str(root))

    def fake_temporary_directory(prefix, dir, ignore_cleanup_errors):
        assert ignore_cleanup_errors is True
        return FixedTemporaryDirectory(Path(dir) / f"{prefix}case")

    monkeypatch.setattr(
        "multilang_executor.tempfile.TemporaryDirectory",
        fake_temporary_directory,
    )

    with executor._temporary_dir(prefix="python_") as tmp_dir:
        assert Path(tmp_dir).parent == (root.resolve() / ".execution-tmp")


def test_docker_availability_returns_false_on_timeout(monkeypatch):
    executor = LanguageExecutor()

    monkeypatch.setattr("multilang_executor.shutil.which", lambda name: "docker")

    def fake_run(*_args, **_kwargs):
        raise subprocess.TimeoutExpired(["docker", "info"], timeout=5)

    monkeypatch.setattr("multilang_executor.subprocess.run", fake_run)

    assert executor._is_docker_available() is False
