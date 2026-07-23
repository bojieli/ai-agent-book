"""search_history(limit=0) must return [], not the first match."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from conversation_history import ConversationHistory, ConversationTurn


def test_limit_zero_returns_empty(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "CONVERSATION_HISTORY_DIR", str(tmp_path))
    monkeypatch.setattr(Config, "ENABLE_HISTORY_SEARCH", False)
    hist = ConversationHistory("u1")
    hist.dify_client = None
    hist.conversations = [
        ConversationTurn("s", "hello world", "hi", "t0", 1),
        ConversationTurn("s", "hello again", "yo", "t1", 2),
    ]
    assert hist.search_history("hello", limit=0) == []


def test_positive_limit_still_caps_matches(tmp_path, monkeypatch):
    monkeypatch.setattr(Config, "CONVERSATION_HISTORY_DIR", str(tmp_path))
    monkeypatch.setattr(Config, "ENABLE_HISTORY_SEARCH", False)
    hist = ConversationHistory("u1")
    hist.dify_client = None
    t1 = ConversationTurn("s", "hello world", "hi", "t0", 1)
    t2 = ConversationTurn("s", "hello again", "yo", "t1", 2)
    t3 = ConversationTurn("s", "goodbye", "bye", "t2", 3)
    hist.conversations = [t1, t2, t3]
    assert hist.search_history("hello", limit=1) == [t1]
