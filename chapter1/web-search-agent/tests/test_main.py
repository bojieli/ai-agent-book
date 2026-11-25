"""Tests for CLI parsing, offline dispatch, and JSON output."""

import json
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest

import main as cli
from config import Config


def test_parser_defers_search_provider_selection_for_interactive_mode():
    args = cli.build_parser().parse_args([])

    assert args.query == []
    assert args.provider is None
    assert args.model == Config.DEFAULT_MODEL
    assert args.max_steps == Config.MAX_SEARCH_ITERATIONS
    assert args.base_url == Config.KIMI_BASE_URL
    assert args.output is None
    assert args.quiet is False


@pytest.mark.parametrize(
    ("primary_key", "extra_args", "backend", "search_provider"),
    [
        ("moonshot-key", [], "moonshot", "kimi"),
        ("moonshot-key", ["--model", "gpt-5"], "openrouter", "parallel"),
        ("", [], "openrouter", "parallel"),
        ("", ["--provider", "kimi"], "openrouter", "kimi"),
    ],
)
def test_cli_selects_search_from_resolved_backend(
    primary_key,
    extra_args,
    backend,
    search_provider,
    monkeypatch,
    tmp_path,
    make_choice,
):
    monkeypatch.setattr(Config, "MOONSHOT_API_KEY", primary_key)
    monkeypatch.setenv("OPENROUTER_API_KEY", "router-key")
    model = Mock()
    chat = model.return_value.chat.completions.create
    chat.return_value = SimpleNamespace(choices=[make_choice(content="Direct answer")])
    monkeypatch.setattr("agent.OpenAI", model)
    search = Mock()
    monkeypatch.setattr("agent.search_impl", search)
    formula_tool = {"type": "function", "function": {"name": "web_search"}}
    formula = Mock()
    formula.return_value.json.return_value = {"tools": [formula_tool]}
    monkeypatch.setattr("agent.requests.get", formula)
    output_path = tmp_path / "answer.json"

    cli.main(["question", "--quiet", "--output", str(output_path), *extra_args])

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    assert payload["provider"] == backend
    assert payload["search_provider"] == search_provider
    assert payload["answer"] == "Direct answer"
    request = chat.call_args.kwargs
    if backend == "moonshot":
        formula.assert_called_once()
        assert request["tools"] == [formula_tool]
    else:
        formula.assert_not_called()
        if search_provider == "kimi":
            assert "tools" not in request
        else:
            assert request["tools"][0]["function"]["name"] == "web_search"
    search.assert_not_called()


def test_parser_accepts_cli_overrides():
    args = cli.build_parser().parse_args(
        [
            "first",
            "question",
            "--provider",
            "offline-demo",
            "--model",
            "custom-model",
            "--max-steps",
            "3",
            "--base-url",
            "https://provider.test/v1",
            "--api-key",
            "explicit-key",
            "--output",
            "result.json",
            "--quiet",
        ]
    )

    assert args.query == ["first", "question"]
    assert args.provider == "offline-demo"
    assert args.model == "custom-model"
    assert args.max_steps == 3
    assert args.base_url == "https://provider.test/v1"
    assert args.api_key == "explicit-key"
    assert args.output == "result.json"
    assert args.quiet is True


def test_offline_cli_writes_utf8_json_without_api_credentials(tmp_path, capsys):
    output_path = tmp_path / "offline-result.json"

    cli.main(
        [
            "한국어",
            "질문",
            "--provider",
            "offline-demo",
            "--quiet",
            "--output",
            str(output_path),
        ]
    )

    payload = json.loads(output_path.read_text(encoding="utf-8"))
    output = capsys.readouterr().out
    assert payload["question"] == "한국어 질문"
    assert set(payload) == {"question", "trace", "answer"}
    assert payload["trace"][-1]["type"] == "answer"
    assert payload["answer"] == payload["trace"][-1]["content"]
    assert "💭" not in output
    assert "结果已保存到" in output


def test_offline_cli_uses_default_question_when_query_is_omitted(capsys, monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "unused-key")
    model = Mock()
    monkeypatch.setattr("agent.OpenAI", model)

    cli.main(["--provider", "offline-demo", "--quiet"])

    output = capsys.readouterr().out
    assert "Moonshot AI 的 Context Caching 是什么技术？" in output
    model.assert_not_called()


def test_script_entry_point_reads_command_line_arguments(tmp_path):
    output = tmp_path / "result.json"
    subprocess.run(
        [
            sys.executable,
            str(Path(cli.__file__).resolve()),
            "脚本入口",
            "--provider",
            "offline-demo",
            "--quiet",
            "--output",
            str(output),
        ],
        cwd=tmp_path,
        check=True,
        capture_output=True,
        text=True,
        timeout=30,
    )
    assert json.loads(output.read_text(encoding="utf-8"))["question"] == "脚本入口"
