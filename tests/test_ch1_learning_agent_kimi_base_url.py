"""Regression test for the chapter1 LLM learning agent ignoring KIMI_BASE_URL.

The agent handed a hardcoded public endpoint to ``resolve_llm_backend``, so a
reader who pointed ``KIMI_BASE_URL`` at a proxy or a regional deployment -- the
override the shared provider registry declares for the ``kimi`` provider --
still sent every request, and their key, to ``api.moonshot.cn``. The failure
surfaced as an authentication error from the public host, which gives no hint
that the configured endpoint was never used.

The dashscope path already resolves its endpoint through
``resolve_backend`` and therefore honours ``DASHSCOPE_BASE_URL``; the last test
pins that asymmetry so it cannot be "fixed" in the wrong direction.
"""

import sys
from pathlib import Path

import pytest

pytest.importorskip("openai")

# chapter1/learning-from-experience is an experiment directory, not an
# installed package, so it has to be importable by path.
CH1_DIR = (
    Path(__file__).resolve().parent.parent / "chapter1" / "learning-from-experience"
).resolve()
if str(CH1_DIR) not in sys.path:
    sys.path.insert(0, str(CH1_DIR))

from llm_agent import LLMAgent  # noqa: E402

PUBLIC_MOONSHOT_BASE_URL = "https://api.moonshot.cn/v1"
PROXY_BASE_URL = "https://proxy.example.com/v1"


@pytest.fixture(autouse=True)
def clean_provider_env(monkeypatch):
    """Start every test from a known provider environment."""
    for var in (
        "LLM_PROVIDER",
        "MOONSHOT_API_KEY",
        "KIMI_API_KEY",
        "KIMI_BASE_URL",
        "OPENROUTER_API_KEY",
        "OPENROUTER_MODEL",
        "DASHSCOPE_API_KEY",
        "DASHSCOPE_BASE_URL",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("MOONSHOT_API_KEY", "test-key")


def test_kimi_base_url_reaches_the_client(monkeypatch):
    monkeypatch.setenv("KIMI_BASE_URL", PROXY_BASE_URL)

    agent = LLMAgent()

    assert agent.base_url == PROXY_BASE_URL
    assert str(agent.client.base_url).rstrip("/") == PROXY_BASE_URL


def test_public_endpoint_remains_the_default():
    agent = LLMAgent()

    assert agent.base_url == PUBLIC_MOONSHOT_BASE_URL


def test_explicit_base_url_wins_over_the_environment(monkeypatch):
    monkeypatch.setenv("KIMI_BASE_URL", PROXY_BASE_URL)

    agent = LLMAgent(base_url="https://explicit.example.com/v1")

    assert agent.base_url == "https://explicit.example.com/v1"


def test_dashscope_keeps_honouring_its_own_override(monkeypatch):
    monkeypatch.delenv("MOONSHOT_API_KEY", raising=False)
    monkeypatch.setenv("DASHSCOPE_API_KEY", "test-key")
    dashscope_url = "https://dashscope-intl.aliyuncs.com/compatible-mode/v1"
    monkeypatch.setenv("DASHSCOPE_BASE_URL", dashscope_url)

    agent = LLMAgent(provider="dashscope")

    assert agent.base_url == dashscope_url
