from agent import _editable_files


def test_null_files_like_empty():
    assert _editable_files({"files": None}) == []


def test_missing_files_like_empty():
    assert _editable_files({}) == []


def test_files_preserved():
    files = [{"path": "a.py", "content": "x"}]
    assert _editable_files({"files": files}) == files
