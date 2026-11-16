"""Offline regression tests for the opt-in Parallel search route."""

import json
from unittest.mock import Mock

import httpx
import pytest
from openai import OpenAI

import main as cli
from config import Config


@pytest.mark.parametrize("key_env", ["MOONSHOT_API_KEY", "OPENROUTER_API_KEY"])
def test_parallel_cli_passes_search_evidence_to_the_model(
    key_env, monkeypatch, tmp_path
):
    monkeypatch.setattr(
        Config, "MOONSHOT_API_KEY", "test-key" if key_env == "MOONSHOT_API_KEY" else ""
    )
    monkeypatch.setenv(key_env, "test-key")
    url = "https://www.python.org/downloads/release/python-3130/"
    query = "Python 3.13.0 release notes python.org"
    excerpt = "Python 3.13.0 is the stable release of Python 3.13."
    results = {
        "results": [{"title": "Python 3.13.0", "url": url, "excerpts": [excerpt]}]
    }
    search = Mock(return_value=results)
    monkeypatch.setattr("agent.search_impl", search)
    formula_declaration = Mock()
    formula_execution = Mock()
    monkeypatch.setattr("agent.requests.get", formula_declaration)
    monkeypatch.setattr("agent.WebSearchAgent._execute_formula", formula_execution)

    reasoning = (
        {"reasoning_content": "Find the official release notes first."}
        if key_env == "MOONSHOT_API_KEY"
        else {
            "reasoning_details": [
                {"type": "reasoning.text", "text": "Find the official release notes."},
                {"type": "reasoning.text", "text": "Then verify the release date."},
            ]
        }
    )

    def first_turn(tools):
        assert len(tools) == 1
        tool = tools[0]
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "web_search"
        params = tool["function"]["parameters"]
        assert params["properties"]["query"]["type"] == "string"
        assert "query" in params["required"]
        return {
            "role": "assistant",
            "content": None,
            **reasoning,
            "tool_calls": [
                {
                    "id": "unknown",
                    "type": "function",
                    "function": {"name": "unexpected", "arguments": "{}"},
                },
                {
                    "id": "search",
                    "type": "function",
                    "function": {
                        "name": "web_search",
                        "arguments": json.dumps({"query": query}),
                    },
                },
            ],
        }

    def final_turn(messages):
        unknown, evidence = messages[-2:]
        assert unknown["role"] == "tool"
        assert unknown["tool_call_id"] == "unknown"
        assert "unexpected" in unknown["content"]
        assert evidence["role"] == "tool"
        assert evidence["tool_call_id"] == "search"
        assert json.loads(evidence["content"]) == results
        source = json.loads(evidence["content"])["results"][0]
        return {
            "role": "assistant",
            "content": f'{source["excerpts"][0]} {source["url"]}',
        }

    model_requests = []

    def complete(request):
        payload = json.loads(request.content)
        model_requests.append(payload)
        if len(model_requests) == 1:
            message = first_turn(payload["tools"])
            finish_reason = "tool_calls"
        else:
            message = final_turn(payload["messages"])
            finish_reason = "stop"
        return httpx.Response(
            200,
            json={
                "id": "mock-chat",
                "object": "chat.completion",
                "created": 0,
                "model": payload["model"],
                "choices": [
                    {"index": 0, "finish_reason": finish_reason, "message": message}
                ],
            },
        )

    output = tmp_path / "search.json"
    with httpx.Client(transport=httpx.MockTransport(complete)) as http_client:
        monkeypatch.setattr(
            "agent.OpenAI", lambda **kwargs: OpenAI(http_client=http_client, **kwargs)
        )
        cli.main(
            [
                "Where are the official Python 3.13.0 release notes?",
                "--provider",
                "parallel",
                "--quiet",
                "--output",
                str(output),
            ]
        )

    assert len(model_requests) == 2
    assistant = model_requests[1]["messages"][-3]
    assert {key: assistant.get(key) for key in reasoning} == reasoning
    assert assistant["content"] is None
    search.assert_called_once()
    assert search.call_args.args == ({"query": query},)
    assert search.call_args.kwargs["timeout"] > 0
    formula_declaration.assert_not_called()
    formula_execution.assert_not_called()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["answer"] == f"{excerpt} {url}"
    steps = [step for step in payload["trace"] if step["type"] != "thought"]
    assert [step["type"] for step in steps] == [
        "action",
        "observation",
        "action",
        "observation",
        "answer",
    ]
    assert steps[2]["args"] == {"query": query}
    assert json.loads(steps[3]["content"]) == results


def test_parallel_cli_requires_a_model_key(monkeypatch):
    monkeypatch.setattr(Config, "MOONSHOT_API_KEY", "")
    model_client = Mock()
    monkeypatch.setattr("agent.OpenAI", model_client)

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["question", "--provider", "parallel"])

    assert exit_info.value.code == 1
    model_client.assert_not_called()
