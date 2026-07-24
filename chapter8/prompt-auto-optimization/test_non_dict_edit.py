"""Non-dict items in edits must not AttributeError on .get."""
from coding_agent import _apply_edits_from_args


def test_string_edit_item_skipped_with_error():
    working, applied, errors, edits = _apply_edits_from_args(
        "hello world",
        {"edits": ["bad", {"old_str": "hello", "new_str": "hi"}]},
    )
    assert working == "hi world"
    assert applied == 1
    assert any("对象" in e for e in errors)
    assert len(edits) == 2


def test_null_edit_item_skipped_with_error():
    working, applied, errors, _ = _apply_edits_from_args(
        "hello world",
        {"edits": [None]},
    )
    assert working == "hello world"
    assert applied == 0
    assert any("对象" in e for e in errors)


def test_null_edits_list_still_empty():
    working, applied, errors, edits = _apply_edits_from_args(
        "hello world", {"edits": None}
    )
    assert working == "hello world"
    assert applied == 0
    assert errors == []
    assert edits == []
