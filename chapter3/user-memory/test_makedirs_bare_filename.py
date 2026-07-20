"""Regression tests: os.makedirs(os.path.dirname(p)) must not raise
FileNotFoundError when p is a bare filename with no directory component
(e.g. LOG_FILE=debug.log, or an empty storage dir env var)."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import Config
from conversation_history import ConversationHistory
from memory_manager import NotesMemoryManager


def test_create_directories_with_bare_log_file(tmp_path, monkeypatch):
    """LOG_FILE='debug.log' (no dir) used to crash create_directories()."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "LOG_FILE", "debug.log")
    monkeypatch.setattr(Config, "MEMORY_STORAGE_DIR", str(tmp_path / "mem"))
    monkeypatch.setattr(Config, "CONVERSATION_HISTORY_DIR", str(tmp_path / "conv"))
    monkeypatch.setattr(Config, "LOCOMO_OUTPUT_DIR", str(tmp_path / "locomo"))
    Config.create_directories()  # must not raise


def test_save_memory_with_empty_storage_dir(tmp_path, monkeypatch):
    """MEMORY_STORAGE_DIR='' makes memory_file a bare filename; save must persist."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "MEMORY_STORAGE_DIR", "")
    mgr = NotesMemoryManager("u1")
    assert mgr.memory_file == "u1_memory.json"
    mgr.add_memory("favorite color is blue", session_id="s1")
    assert (tmp_path / "u1_memory.json").exists()


def test_save_history_with_empty_history_dir(tmp_path, monkeypatch):
    """CONVERSATION_HISTORY_DIR='' makes history_file a bare filename; save must persist."""
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(Config, "CONVERSATION_HISTORY_DIR", "")
    hist = ConversationHistory("u1")
    assert hist.history_file == "u1_history.json"
    hist.add_turn("s1", "hi", "hello")
    assert (tmp_path / "u1_history.json").exists()
