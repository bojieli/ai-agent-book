"""Null files on apply_edits return must be safe to iterate (demo write path)."""
import pytest

from agent import normalize_apply_edits_args, EDITABLE_FILES


def test_null_files_normalized_for_demo_iteration():
    out = normalize_apply_edits_args({"summary": "x", "files": None})
    assert out["files"] == []
    assert out["summary"] == "x"
    written = []
    for f in out["files"]:
        written.append(f["path"])
    assert written == []


def test_files_preserved_and_whitelisted():
    path = next(iter(EDITABLE_FILES))
    out = normalize_apply_edits_args({
        "files": [{"path": path, "content": "ok"}],
    })
    assert out["files"][0]["path"] == path
    assert out["files"][0]["content"] == "ok"


def test_non_whitelist_rejected():
    with pytest.raises(RuntimeError, match="非白名单"):
        normalize_apply_edits_args({
            "files": [{"path": "/tmp/evil.py", "content": "x"}],
        })
