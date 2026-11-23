"""Regression: exit() / sys.exit() in code_interpreter snippets must end the
snippet, not the agent process, and must not close the agent's stdin."""

import io
import json
import sys
from types import SimpleNamespace
from unittest.mock import MagicMock

import pytest
from agent import SystemHintAgent, SystemHintConfig


def make_agent():
    config = SystemHintConfig(
        enable_timestamps=False,
        enable_tool_counter=False,
        enable_todo_list=False,
        enable_detailed_errors=False,
        enable_system_state=False,
        save_trajectory=False,
    )
    return SystemHintAgent(api_key="test-key", provider="kimi", config=config, verbose=False)


@pytest.mark.parametrize(
    "code, exit_code, success",
    [
        ("print('hello')\nexit()", 0, True),
        ("print('hello')\nquit()", 0, True),
        ("import sys\nprint('hello')\nsys.exit(0)", 0, True),
        ("import sys\nprint('hello')\nsys.exit(2)", 2, False),
        ("print('hello')\nexit(True)", 1, False),
        ("import sys\nprint('hello')\nraise SystemExit('bad input')", 1, False),
    ],
)
def test_exit_ends_the_snippet_only(code, exit_code, success):
    result = make_agent()._tool_code_interpreter(code)
    assert result["success"] is success
    assert result["stdout"] == "hello\n"
    assert result["exit_code"] == exit_code


def test_exit_message_is_reported_on_stderr():
    result = make_agent()._tool_code_interpreter("raise SystemExit('bad input')")
    assert "bad input" in result["stderr"]


def test_exit_does_not_close_stdin(monkeypatch):
    stdin = io.StringIO("next task\n")
    monkeypatch.setattr(sys, "stdin", stdin)
    make_agent()._tool_code_interpreter("exit()")
    assert not stdin.closed


def test_execute_task_survives_exit_in_snippet():
    agent = make_agent()
    args = json.dumps({"code": "print('hello')\nexit()"})
    call = SimpleNamespace(
        id="c1", function=SimpleNamespace(name="code_interpreter", arguments=args)
    )
    tool_msg = SimpleNamespace(
        content=None,
        tool_calls=[call],
        model_dump=lambda: {
            "role": "assistant",
            "content": None,
            "tool_calls": [
                {
                    "id": "c1",
                    "type": "function",
                    "function": {"name": "code_interpreter", "arguments": args},
                }
            ],
        },
    )
    final_msg = SimpleNamespace(
        content="FINAL ANSWER: done",
        tool_calls=None,
        model_dump=lambda: {"role": "assistant", "content": "FINAL ANSWER: done"},
    )
    agent.client = MagicMock()
    agent.client.chat.completions.create = MagicMock(
        side_effect=[
            SimpleNamespace(choices=[SimpleNamespace(message=tool_msg)]),
            SimpleNamespace(choices=[SimpleNamespace(message=final_msg)]),
        ]
    )

    result = agent.execute_task("print hello", max_iterations=5)

    assert "done" in str(result.get("final_answer"))
    tool_msgs = [m for m in agent.conversation_history if m.get("role") == "tool"]
    assert "hello" in tool_msgs[0]["content"]
