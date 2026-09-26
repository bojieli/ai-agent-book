"""Regression: the OpenRouter fallback notice must only fire on a real fallback.

``Backend.using_openrouter`` is True whenever requests go to OpenRouter,
including when the reader picked ``--provider openrouter`` themselves. That is
not a fallback, so neither the agent nor main() may claim the key is missing.
"""
import logging
import sys

import pytest

import main
from agent import ContextAwareAgent, ContextMode
from config import PROVIDERS

NOTICE = "API key not set"


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    """Start every test with no provider keys, whatever the developer's .env holds."""
    for spec in PROVIDERS.values():
        for var in spec.key_vars:
            monkeypatch.delenv(var, raising=False)
    for var in ("OPENROUTER_API_KEY", "OPENROUTER_MODEL", "OPENROUTER_BASE_URL"):
        monkeypatch.delenv(var, raising=False)


def _notices(caplog):
    return [r.getMessage() for r in caplog.records if NOTICE in r.getMessage()]


# --- ContextAwareAgent --------------------------------------------------------

@pytest.mark.parametrize("explicit_key", ["sk-or-explicit", ""])
def test_agent_direct_openrouter_is_not_reported_as_fallback(
    monkeypatch, caplog, explicit_key
):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-env")
    caplog.set_level(logging.INFO)

    agent = ContextAwareAgent(explicit_key, ContextMode.FULL,
                              provider="openrouter", verbose=False)

    assert agent.using_openrouter
    assert _notices(caplog) == []


def test_agent_missing_provider_key_reports_fallback(monkeypatch, caplog):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-env")
    caplog.set_level(logging.INFO)

    agent = ContextAwareAgent("", ContextMode.FULL, provider="kimi", verbose=False)

    assert agent.using_openrouter
    assert _notices(caplog) == [
        f"kimi API key not set; routing via OpenRouter (model: {agent.model})"
    ]


def test_agent_with_own_provider_key_does_not_report_fallback(monkeypatch, caplog):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-moonshot")
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-env")
    caplog.set_level(logging.INFO)

    agent = ContextAwareAgent("", ContextMode.FULL, provider="kimi", verbose=False)

    assert not agent.using_openrouter
    assert _notices(caplog) == []


# --- main() -------------------------------------------------------------------

def _run_main(monkeypatch, *argv):
    """Run main() in interactive mode and return the api_key it hands on."""
    captured = {}

    def fake_interactive_mode(api_key, provider, model):
        captured["api_key"] = api_key

    monkeypatch.setattr(main, "interactive_mode", fake_interactive_mode)
    monkeypatch.setattr(sys, "argv", ["main.py", "--mode", "interactive", *argv])
    main.main()
    return captured["api_key"]


def test_main_direct_openrouter_is_not_reported_as_fallback(monkeypatch, caplog):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-env")
    caplog.set_level(logging.INFO)

    api_key = _run_main(monkeypatch, "--provider", "openrouter")

    assert _notices(caplog) == []
    # openrouter's own key is passed on, as for any provider with a key.
    assert api_key == "sk-or-env"


def test_main_missing_provider_key_reports_fallback(monkeypatch, caplog):
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-or-env")
    caplog.set_level(logging.INFO)

    api_key = _run_main(monkeypatch, "--provider", "kimi")

    assert len(_notices(caplog)) == 1
    # The OpenRouter key must not be handed on as if it were kimi's own.
    assert api_key == ""


def test_main_with_own_provider_key_does_not_report_fallback(monkeypatch, caplog):
    monkeypatch.setenv("MOONSHOT_API_KEY", "sk-moonshot")
    caplog.set_level(logging.INFO)

    api_key = _run_main(monkeypatch, "--provider", "kimi")

    assert _notices(caplog) == []
    assert api_key == "sk-moonshot"
