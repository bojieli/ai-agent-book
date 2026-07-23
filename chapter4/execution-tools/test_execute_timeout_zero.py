"""execute_command(timeout=0) must use the default timeout, not fail immediately."""
import sys
import tempfile
import shutil
from pathlib import Path

import pytest


class Config:
    WORKSPACE_DIR = Path(tempfile.mkdtemp())
    AUTO_VERIFY_CODE = False
    REQUIRE_APPROVAL_FOR_DANGEROUS_OPS = False


sys.modules["config"] = type(sys)("config")
sys.modules["config"].Config = Config

from terminal_controller import TerminalController


@pytest.fixture
def tc():
    Config.WORKSPACE_DIR = Path(tempfile.mkdtemp())
    controller = TerminalController()
    yield controller
    if Config.WORKSPACE_DIR.exists():
        shutil.rmtree(Config.WORKSPACE_DIR, ignore_errors=True)


@pytest.mark.asyncio
async def test_timeout_zero_runs_command_with_default(tc):
    result = await tc.execute_command("echo ok-timeout-zero", timeout=0)
    assert result["success"] is True
    assert "ok-timeout-zero" in result["stdout"]
    assert result["returncode"] == 0


@pytest.mark.asyncio
async def test_positive_timeout_still_works(tc):
    result = await tc.execute_command("echo ok-timeout-pos", timeout=5)
    assert result["success"] is True
    assert "ok-timeout-pos" in result["stdout"]
