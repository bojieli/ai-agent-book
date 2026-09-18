"""Unit tests for model mapping and provider selection."""

import os
import subprocess
import sys
from pathlib import Path

import pytest
from config import map_model_to_openrouter, resolve_llm_backend


@pytest.mark.parametrize(
    ("model", "expected"),
    [
        ("openai/gpt-5.6-luna", "openai/gpt-5.6-luna"),
        ("gpt-5.6-luna", "openai/gpt-5.6-luna"),
        ("o3-mini", "openai/o3-mini"),
        ("claude-sonnet-4.6", "anthropic/claude-sonnet-4.6"),
        ("claude-haiku-4.5", "anthropic/claude-haiku-4.5"),
        ("claude-opus-4.8", "anthropic/claude-opus-4.8"),
        ("kimi-k3", "moonshotai/kimi-k2.6"),
    ],
)
def test_map_model_to_openrouter(model, expected):
    assert map_model_to_openrouter(model) == expected


def test_unknown_model_uses_configured_openrouter_default(monkeypatch):
    """Substitution is opt-in, for callers that cannot send an unmapped id."""
    monkeypatch.setenv("OPENROUTER_MODEL", "vendor/fallback-model")

    mapped = map_model_to_openrouter("unknown-model", substitute_unknown=True)
    assert mapped == "vendor/fallback-model"


def test_unknown_model_is_kept_when_not_substituting(monkeypatch):
    """Rerouting for credential reasons keeps the model the reader asked for."""
    monkeypatch.setenv("OPENROUTER_MODEL", "vendor/fallback-model")

    assert map_model_to_openrouter("unknown-model") == "unknown-model"


def test_primary_provider_is_preserved_when_its_key_exists():
    assert resolve_llm_backend(
        "moonshot-key", "https://moonshot.test/v1", "kimi-k3"
    ) == (
        "moonshot-key",
        "https://moonshot.test/v1",
        "kimi-k3",
        False,
    )


def test_openrouter_is_used_when_primary_key_is_missing(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-key")
    monkeypatch.setenv("OPENROUTER_BASE_URL", "https://openrouter.test/v1")

    assert resolve_llm_backend(None, "https://moonshot.test/v1", "kimi-k3") == (
        "openrouter-key",
        "https://openrouter.test/v1",
        "moonshotai/kimi-k2.6",
        True,
    )


def test_gpt5_prefers_openrouter_when_both_keys_exist(monkeypatch):
    monkeypatch.setenv("OPENROUTER_API_KEY", "openrouter-key")

    resolved = resolve_llm_backend(
        "primary-key", "https://primary.test/v1", "gpt-5.6-luna"
    )

    assert resolved == (
        "openrouter-key",
        "https://openrouter.ai/api/v1",
        "openai/gpt-5.6-luna",
        True,
    )


def test_provider_resolution_requires_a_key():
    with pytest.raises(ValueError, match="No API key found"):
        resolve_llm_backend(None, "https://moonshot.test/v1", "kimi-k3")


def _resolved_base_url(env_overrides):
    """Read ``Config.KIMI_BASE_URL`` in a fresh interpreter.

    It is a class attribute evaluated at import time, so probing it without a
    module reload needs its own process.
    """
    completed = subprocess.run(
        [sys.executable, "-c", "import config; print(config.Config.KIMI_BASE_URL)"],
        cwd=Path(__file__).resolve().parents[1],
        env={**os.environ, **env_overrides},
        capture_output=True,
        text=True,
        check=True,
    )
    return completed.stdout.strip()


def test_kimi_base_url_is_read_from_the_environment():
    """env.example and the README document KIMI_BASE_URL, so it must take effect."""
    assert _resolved_base_url({"KIMI_BASE_URL": "https://proxy.example.com/v1"}) == (
        "https://proxy.example.com/v1"
    )


def test_blank_kimi_base_url_keeps_the_public_endpoint():
    """A present-but-empty value means "not configured", not "no endpoint"."""
    assert _resolved_base_url({"KIMI_BASE_URL": ""}) == "https://api.moonshot.cn/v1"
