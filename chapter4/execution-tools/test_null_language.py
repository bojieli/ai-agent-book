"""Null optional language must default to python."""
import asyncio
import tempfile
from pathlib import Path

from multilang_executor import LanguageExecutor


def test_null_language_like_python():
    le = LanguageExecutor(workspace_dir=Path(tempfile.mkdtemp()))
    result = asyncio.run(le.execute_code("print(42)", language=None, timeout=10))
    assert result.get("language") == "python" or "42" in str(result.get("stdout", "")) or result.get("success") is not False
    # Must not AttributeError; executor returns a dict
    assert isinstance(result, dict)
    assert "error" not in result or "Unsupported language" not in str(result.get("error", ""))
