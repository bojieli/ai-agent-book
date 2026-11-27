"""Offline tests for the SpecStream search route."""

import json
from unittest.mock import Mock

import httpx
import pytest
import requests
from openai import OpenAI

import main as cli
import specstream_search
from agent import WebSearchAgent
from config import Config


def _response(status, payload):
    response = Mock(status_code=status, text=json.dumps(payload))
    response.json.return_value = payload
    return response


def test_search_sends_bearer_key_and_keeps_the_parallel_result_shape(monkeypatch):
    monkeypatch.setenv("SPECSTREAM_API_KEY", "ss-test")
    post = Mock(
        return_value=_response(
            200,
            {
                "data": {
                    "answer": None,
                    "sources": [
                        {
                            "title": "What's New In Python 3.13",
                            "url": "https://docs.python.org/3/whatsnew/3.13.html",
                            "snippet": "CPython now has experimental support for free threading.",
                        },
                        {"title": "no snippet", "url": "https://example.org"},
                        {"title": "no url"},
                    ],
                }
            },
        )
    )
    monkeypatch.setattr(specstream_search.requests, "post", post)

    data = specstream_search.search_impl(
        {"query": "  Python 3.13 free threading  "}, timeout=7
    )

    assert data == {
        "results": [
            {
                "title": "What's New In Python 3.13",
                "url": "https://docs.python.org/3/whatsnew/3.13.html",
                "excerpts": [
                    "CPython now has experimental support for free threading."
                ],
            },
            {"title": "no snippet", "url": "https://example.org", "excerpts": []},
        ]
    }
    (url,), kwargs = post.call_args
    assert url == "https://api.specstream.ai/v1/web-search"
    assert kwargs["headers"] == {"Authorization": "Bearer ss-test"}
    assert kwargs["json"] == {"q": "Python 3.13 free threading", "num": 5}
    assert kwargs["timeout"] == 7
    assert kwargs["allow_redirects"] is False


def test_search_passes_the_answer_through(monkeypatch):
    monkeypatch.setenv("SPECSTREAM_API_KEY", "ss-test")
    payload = {"data": {"answer": "Canberra", "sources": []}}
    monkeypatch.setattr(
        specstream_search.requests, "post", Mock(return_value=_response(200, payload))
    )

    assert specstream_search.search_impl({"query": "q"}, timeout=1) == {
        "answer": "Canberra",
        "results": [],
    }


@pytest.mark.parametrize(
    ("status", "payload", "message"),
    [
        (401, {"error": {"message": "key refused"}}, "HTTP 401: key refused"),
        (429, {"detail": "slow down"}, "HTTP 429"),
        (200, {"unexpected": True}, "未返回可用的搜索结果"),
        (200, {"data": {"sources": "not a list"}}, "未返回可用的搜索结果"),
    ],
)
def test_search_reports_api_failures(status, payload, message, monkeypatch):
    monkeypatch.setenv("SPECSTREAM_API_KEY", "ss-test")
    monkeypatch.setattr(
        specstream_search.requests,
        "post",
        Mock(return_value=_response(status, payload)),
    )

    with pytest.raises(RuntimeError, match=message):
        specstream_search.search_impl({"query": "q"}, timeout=1)


def test_search_wraps_transport_errors(monkeypatch):
    monkeypatch.setenv("SPECSTREAM_API_KEY", "ss-test")
    monkeypatch.setattr(
        specstream_search.requests,
        "post",
        Mock(side_effect=requests.ConnectionError("refused")),
    )

    with pytest.raises(RuntimeError, match="SpecStream 请求失败"):
        specstream_search.search_impl({"query": "q"}, timeout=1)


def test_search_without_key_or_query_sends_nothing(monkeypatch):
    post = Mock()
    monkeypatch.setattr(specstream_search.requests, "post", post)

    assert "error" in specstream_search.search_impl({"query": " "}, timeout=1)
    with pytest.raises(RuntimeError, match="SPECSTREAM_API_KEY"):
        specstream_search.search_impl({"query": "q"}, timeout=1)
    post.assert_not_called()


def test_agent_refuses_specstream_without_a_key():
    with pytest.raises(ValueError, match="SPECSTREAM_API_KEY"):
        WebSearchAgent(api_key="model-key", search_provider="specstream")


@pytest.mark.parametrize("key_env", ["MOONSHOT_API_KEY", "OPENROUTER_API_KEY"])
def test_specstream_cli_passes_search_evidence_to_the_model(
    key_env, monkeypatch, tmp_path
):
    monkeypatch.setattr(
        Config, "MOONSHOT_API_KEY", "test-key" if key_env == "MOONSHOT_API_KEY" else ""
    )
    monkeypatch.setenv(key_env, "test-key")
    monkeypatch.setenv("SPECSTREAM_API_KEY", "ss-test")
    url = "https://docs.python.org/3/whatsnew/3.13.html"
    query = "Python 3.13 free threading"
    results = {
        "results": [{"title": "3.13", "url": url, "excerpts": ["free-threaded"]}]
    }
    search = Mock(return_value=results)
    monkeypatch.setattr("agent.specstream_search.search_impl", search)
    parallel = Mock()
    monkeypatch.setattr("agent.search_impl", parallel)
    formula_declaration = Mock()
    monkeypatch.setattr("agent.requests.get", formula_declaration)

    model_requests = []

    def complete(request):
        payload = json.loads(request.content)
        model_requests.append(payload)
        if len(model_requests) == 1:
            assert [tool["function"]["name"] for tool in payload["tools"]] == [
                "web_search"
            ]
            message = {
                "role": "assistant",
                "content": None,
                "tool_calls": [
                    {
                        "id": "search",
                        "type": "function",
                        "function": {
                            "name": "web_search",
                            "arguments": json.dumps({"query": query}),
                        },
                    }
                ],
            }
            finish_reason = "tool_calls"
        else:
            evidence = payload["messages"][-1]
            assert evidence["tool_call_id"] == "search"
            assert json.loads(evidence["content"]) == results
            message = {"role": "assistant", "content": f"free-threaded {url}"}
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
                "What changed for threads in Python 3.13?",
                "--provider",
                "specstream",
                "--quiet",
                "--output",
                str(output),
            ]
        )

    assert len(model_requests) == 2
    search.assert_called_once()
    assert search.call_args.args == ({"query": query},)
    assert search.call_args.kwargs["timeout"] > 0
    parallel.assert_not_called()
    formula_declaration.assert_not_called()
    saved = json.loads(output.read_text(encoding="utf-8"))
    assert saved["search_provider"] == "specstream"
    assert saved["answer"] == f"free-threaded {url}"
