"""Regression tests for issue #493's cross-session history leak."""

import os
import sys
from types import SimpleNamespace

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from conversational_agent import ConversationConfig, ConversationalAgent
from conversation_history import ConversationHistory, ConversationTurn


class StubMemoryManager:
    def __init__(self, context: str):
        self.context = context
        self.load_count = 0

    def load_memory(self):
        self.load_count += 1

    def get_context_string(self) -> str:
        return self.context


def make_agent(history: ConversationHistory, session_id: str):
    """Build the prompt-only portion of an agent without an API client."""
    agent = ConversationalAgent.__new__(ConversationalAgent)
    agent.config = ConversationConfig()
    agent.memory_manager = StubMemoryManager("Preferred editor: VS Code")
    agent.conversation_history = history
    agent.session_id = session_id
    return agent


def test_chat_sends_current_history_once_and_excludes_previous_sessions(tmp_path):
    history = ConversationHistory.__new__(ConversationHistory)
    history.user_id = "test-user"
    history.history_file = str(tmp_path / "history.json")
    history.dify_client = None
    history.conversations = [
        ConversationTurn(
            "session-old",
            "My private detail from the old session",
            "I will remember that detail",
            "2026-07-28T10:00:00",
            1,
        )
    ]
    agent = make_agent(history, "session-current")
    agent.verbose = False
    agent.model = "test-model"
    agent.conversation = []
    sent = []

    def complete(**kwargs):
        sent.append(kwargs["messages"])
        return [SimpleNamespace(choices=[SimpleNamespace(delta=SimpleNamespace(content="Done"))])]

    agent.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=complete)))
    assert agent.chat("Please remember this turn") == "Done"
    assert agent.chat("What did we discuss?") == "Done"

    previous_user, previous_assistant, current_user = sent[-1]
    assert previous_user == {"role": "user", "content": "Please remember this turn"}
    assert previous_assistant == {"role": "assistant", "content": "Done"}
    assert current_user["content"].startswith("What did we discuss?")
    assert "Preferred editor: VS Code" in current_user["content"]
    assert "Please remember this turn" not in current_user["content"]
    assert "My private detail from the old session" not in current_user["content"]
    assert [turn.user_message for turn in history.get_session_turns("session-current")] == [
        "Please remember this turn",
        "What did we discuss?",
    ]


def test_new_session_uses_structured_memory_without_old_raw_history():
    history = ConversationHistory.__new__(ConversationHistory)
    history.conversations = [
        ConversationTurn(
            "session-old",
            "I work at TechCorp",
            "Thanks for sharing",
            "2026-07-28T10:00:00",
            1,
        )
    ]
    agent = make_agent(history, "session-new")

    context = agent._get_memory_context()

    assert "Preferred editor: VS Code" in context
    assert "I work at TechCorp" not in context
    assert "CURRENT SESSION HISTORY" not in context
    assert agent.memory_manager.load_count == 1
