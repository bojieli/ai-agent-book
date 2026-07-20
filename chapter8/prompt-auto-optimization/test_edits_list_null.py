from coding_agent import _edits_list


def test_null_edits_like_empty():
    assert _edits_list({"edits": None}) == []


def test_missing_edits_like_empty():
    assert _edits_list({}) == []


def test_edits_preserved():
    edits = [{"old_str": "a", "new_str": "b"}]
    assert _edits_list({"edits": edits}) == edits
