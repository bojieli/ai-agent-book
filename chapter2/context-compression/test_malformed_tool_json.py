"""Malformed tool-argument JSON must not abort execute_research."""
import sys
import types
from pathlib import Path
from unittest.mock import MagicMock, patch

# Optional deps used at import time by web_tools.
sys.modules.setdefault("html2text", types.ModuleType("html2text"))
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda: None))

sys.path.insert(0, str(Path(__file__).resolve().parent))

from compression_strategies import CompressionStrategy
from agent import ResearchAgent, ToolCall


def test_execute_research_survives_malformed_tool_arguments_json():
    with patch("agent.Config.resolve_llm", return_value=("k", "http://x", "m")), \
         patch("agent.OpenAI"), \
         patch("agent.WebTools"), \
         patch("agent.ContextCompressor"):
        agent = ResearchAgent(
            api_key="k",
            compression_strategy=CompressionStrategy.NO_COMPRESSION,
            verbose=False,
            enable_streaming=False,
        )

    bad_call = {
        "id": "call-bad",
        "type": "function",
        "function": {
            "name": "search_web",
            "arguments": '{"query": "openai",}',  # trailing comma
        },
    }
    tool_msg = {"role": "assistant", "content": "searching", "tool_calls": [bad_call]}
    final_msg = {"role": "assistant", "content": "FINAL ANSWER: ok", "tool_calls": None}

    agent._non_streaming_response = MagicMock(side_effect=[tool_msg, final_msg])
    agent._execute_tool = MagicMock(return_value=({"results": []}, None))

    result = agent.execute_research(max_iterations=3)

    assert result.get("error") is None
    agent._execute_tool.assert_called()
    assert agent._execute_tool.call_args[0][1] == {}
    assert agent._execute_tool.called
