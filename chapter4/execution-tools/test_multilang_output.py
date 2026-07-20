import asyncio
import pytest
from multilang_executor import get_all_output, LanguageExecutor, ExecutionStatus


@pytest.mark.asyncio
async def test_get_all_output_reads_full_payload():
    class FakeStream:
        def __init__(self, data: bytes):
            self._data = data
            self._done = False

        async def read(self, n: int = -1):
            if self._done:
                return b""
            self._done = True
            return self._data

    payload = b"hello world" * 1000
    out = await get_all_output(FakeStream(payload))
    assert out == payload.decode()


@pytest.mark.asyncio
async def test_execute_captures_stdout():
    exe = LanguageExecutor()
    result = await exe.execute_code("print('ok-from-executor')", "python", timeout=10)
    assert result["status"] == ExecutionStatus.SUCCESS
    assert "ok-from-executor" in result["stdout"]
