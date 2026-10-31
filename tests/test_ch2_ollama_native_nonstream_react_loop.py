"""OllamaNativeAgent.chat(stream=False) must keep calling tools until the
model gives a final answer (issue #1192). Runs offline with a scripted client.
"""

import json
import sys
import types
from pathlib import Path

ch2_dir = Path(__file__).resolve().parent.parent / "chapter2" / "local_llm_serving"

# Stub `ollama` and the experiment's `tools` so the test needs neither, then
# restore sys.path/sys.modules: other chapters define their own `tools`.
_saved_path = list(sys.path)
_saved_modules = dict(sys.modules)
_ollama = types.ModuleType("ollama")
_ollama.Client = object
_ollama.ResponseError = type("ResponseError", (Exception,), {})
_tools = types.ModuleType("tools")
_tools.ToolRegistry = object
sys.modules.update(ollama=_ollama, tools=_tools)
sys.path.insert(0, str(ch2_dir))
try:
    from ollama_native import OllamaNativeAgent  # noqa: E402
finally:
    for name in set(sys.modules) - set(_saved_modules):
        del sys.modules[name]
    sys.modules.update(_saved_modules)
    sys.path[:] = _saved_path


def _tool_call(name, **arguments):
    return {"function": {"name": name, "arguments": arguments}}


class ScriptedClient:
    """Returns the scripted responses in order and records each request."""

    def __init__(self, responses):
        self._responses = iter(responses)
        self.requests = []

    def chat(self, **kwargs):
        self.requests.append(kwargs)
        return {"message": next(self._responses)}


class RecordingRegistry:
    def __init__(self):
        self.calls = []

    def get_tool_schemas(self):
        return [{"type": "function", "function": {"name": "get_weather"}}]

    def execute_tool(self, name, arguments):
        self.calls.append((name, arguments))
        return json.dumps({"tool": name, "success": True})


def _make_agent(responses):
    # Bypass __init__, which connects to a local Ollama server.
    agent = OllamaNativeAgent.__new__(OllamaNativeAgent)
    agent.model = "fake-model"
    agent.client = ScriptedClient(responses)
    agent.tool_registry = RecordingRegistry()
    agent.conversation_history = []
    agent._think_disabled = set()
    return agent


def test_executes_tool_calls_requested_after_a_tool_result():
    agent = _make_agent(
        [
            {
                "content": "",
                "tool_calls": [_tool_call("get_current_time", city="Vancouver")],
            },
            {
                "content": "",
                "tool_calls": [_tool_call("get_weather", city="Vancouver")],
            },
            {"content": "It is 10:00 and sunny in Vancouver."},
        ]
    )

    answer = agent.chat("Time and weather in Vancouver?")

    assert answer == "It is 10:00 and sunny in Vancouver."
    assert [name for name, _ in agent.tool_registry.calls] == [
        "get_current_time",
        "get_weather",
    ]
    assert len(agent.client.requests) == 3
    assert all(req["tools"] for req in agent.client.requests)
    assert [m["role"] for m in agent.conversation_history] == [
        "user",
        "assistant",
        "tool",
        "assistant",
        "tool",
        "assistant",
    ]
    assert "tool_calls" not in agent.conversation_history[-1]


def test_answer_without_tools_is_returned_and_think_tags_stripped():
    agent = _make_agent([{"content": "<think>hmm</think>Hello!"}])

    assert agent.chat("Hi") == "Hello!"
    assert agent.tool_registry.calls == []
    assert agent.conversation_history[-1] == {"role": "assistant", "content": "Hello!"}


def test_stops_after_max_iterations_when_model_never_stops_calling_tools():
    looping = {"content": "", "tool_calls": [_tool_call("get_weather", city="X")]}
    agent = _make_agent([looping] * 20)

    answer = agent.chat("Loop forever")

    assert answer == "Error: Maximum iterations reached in ReAct loop"
    assert len(agent.client.requests) == 10
