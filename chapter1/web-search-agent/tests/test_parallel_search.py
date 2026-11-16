"""Offline regression tests for the opt-in Parallel search route."""

import json
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import main as cli
from config import Config


@pytest.mark.parametrize("key_env", ["MOONSHOT_API_KEY", "OPENROUTER_API_KEY"])
def test_parallel_cli_passes_search_evidence_to_the_model(
    key_env, monkeypatch, tmp_path, make_choice, make_tool_call
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

    def first_turn(tools, **kwargs):
        assert len(tools) == 1
        tool = tools[0]
        assert tool["type"] == "function"
        assert tool["function"]["name"] == "web_search"
        params = tool["function"]["parameters"]
        assert params["properties"]["query"]["type"] == "string"
        assert "query" in params["required"]
        return make_choice(
            finish_reason="tool_calls",
            tool_calls=[
                make_tool_call(name="unexpected", call_id="unknown"),
                make_tool_call(arguments={"query": query}, call_id="search"),
            ],
        )

    def final_turn(messages, **kwargs):
        unknown, evidence = messages[-2:]
        assert unknown["role"] == "tool"
        assert unknown["tool_call_id"] == "unknown"
        assert "unexpected" in unknown["content"]
        assert evidence["role"] == "tool"
        assert evidence["tool_call_id"] == "search"
        assert json.loads(evidence["content"]) == results
        source = json.loads(evidence["content"])["results"][0]
        return make_choice(content=f'{source["excerpts"][0]} {source["url"]}')

    model_turns = iter([first_turn, final_turn])

    def complete(**kwargs):
        return SimpleNamespace(choices=[next(model_turns)(**kwargs)])

    client = Mock()
    client.chat.completions.create.side_effect = complete
    monkeypatch.setattr("agent.OpenAI", Mock(return_value=client))
    output = tmp_path / "search.json"

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

    assert client.chat.completions.create.call_count == 2
    search.assert_called_once()
    assert search.call_args.args == ({"query": query},)
    assert search.call_args.kwargs["timeout"] > 0
    formula_declaration.assert_not_called()
    formula_execution.assert_not_called()
    payload = json.loads(output.read_text(encoding="utf-8"))
    assert payload["answer"] == f"{excerpt} {url}"
    assert [step["type"] for step in payload["trace"]] == [
        "action",
        "observation",
        "action",
        "observation",
        "answer",
    ]
    assert payload["trace"][2]["args"] == {"query": query}
    assert json.loads(payload["trace"][3]["content"]) == results


def test_parallel_cli_requires_a_model_key(monkeypatch):
    monkeypatch.setattr(Config, "MOONSHOT_API_KEY", "")
    model_client = Mock()
    monkeypatch.setattr("agent.OpenAI", model_client)

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["question", "--provider", "parallel"])

    assert exit_info.value.code == 1
    model_client.assert_not_called()
