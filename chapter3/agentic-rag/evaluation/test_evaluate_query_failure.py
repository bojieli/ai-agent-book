"""The evaluator must distinguish model failures from model answers."""
from types import SimpleNamespace

import pytest

from evaluate import RAGEvaluator
from agent import AgenticRAG
from config import Config


def failing_agent():
    agent = AgenticRAG.__new__(AgenticRAG)
    agent.config = Config()
    agent.model = "fake-model"
    agent.tools = []
    agent.conversation_history = []
    agent._build_messages = lambda query: [{"role": "user", "content": query}]
    agent.kb_tools = SimpleNamespace(knowledge_base_search=lambda query: [])

    def fail(**kwargs):
        raise RuntimeError("provider unavailable")

    agent.client = SimpleNamespace(chat=SimpleNamespace(completions=SimpleNamespace(create=fail)))
    return agent


@pytest.mark.parametrize("mode", ["agentic", "non_agentic"])
def test_provider_failure_is_failed_case(mode):
    evaluator = RAGEvaluator.__new__(RAGEvaluator)
    evaluator.agent = failing_agent()
    evaluator.agent.conversation_history.append({"role": "user", "content": "earlier"})
    result = evaluator.run_test_case({"id": "case-1", "question": "What happened?"}, mode)
    assert result["success"] is False
    assert "provider unavailable" in result["error"]
    assert evaluator.agent.conversation_history == []
    assert evaluator.compute_aggregate_metrics([result])["failed_cases"] == 1


@pytest.mark.parametrize("backend", ["LOCAL", "DIFY", "RAPTOR", "GRAPHRAG"])
def test_backend_connection_failures_propagate(backend, monkeypatch):
    import requests
    from config import KnowledgeBaseType
    from tools import KnowledgeBaseTools

    config = Config().knowledge_base
    config.type = getattr(KnowledgeBaseType, backend)
    config.dify_api_key = "test-key"
    kb = KnowledgeBaseTools.__new__(KnowledgeBaseTools)
    kb.config = config

    def unavailable(*args, **kwargs):
        raise requests.ConnectionError("unavailable")

    monkeypatch.setattr(requests, "post", unavailable)
    with pytest.raises(requests.ConnectionError, match="unavailable"):
        kb.knowledge_base_search("query")


def test_empty_successful_search_remains_empty(monkeypatch):
    from config import KnowledgeBaseType
    from tools import KnowledgeBaseTools

    config = Config().knowledge_base
    config.type = KnowledgeBaseType.LOCAL
    kb = KnowledgeBaseTools.__new__(KnowledgeBaseTools)
    kb.config = config
    response = SimpleNamespace(raise_for_status=lambda: None, json=lambda: {})
    monkeypatch.setattr("requests.post", lambda *args, **kwargs: response)
    assert kb.knowledge_base_search("query") == []


def test_offline_failure_is_not_an_empty_result():
    from config import KnowledgeBaseType
    from tools import KnowledgeBaseTools

    config = Config().knowledge_base
    config.type = KnowledgeBaseType.OFFLINE
    kb = KnowledgeBaseTools.__new__(KnowledgeBaseTools)
    kb.config = config
    def fail(query):
        raise OSError("index unavailable")
    kb._search_offline = fail
    with pytest.raises(OSError, match="index unavailable"):
        kb.knowledge_base_search("query")


def test_missing_dify_key_is_an_error():
    from config import KnowledgeBaseType
    from tools import KnowledgeBaseTools

    config = Config().knowledge_base
    config.type = KnowledgeBaseType.DIFY
    config.dify_api_key = None
    kb = KnowledgeBaseTools.__new__(KnowledgeBaseTools)
    kb.config = config
    with pytest.raises(ValueError, match="Dify API key"):
        kb.knowledge_base_search("query")


def test_interactive_tool_reports_search_failure():
    agent = failing_agent()
    def unavailable(query):
        raise RuntimeError("retrieval unavailable")
    agent.kb_tools.knowledge_base_search = unavailable
    result = agent._execute_tool("knowledge_base_search", {"query": "question"})
    assert result == {"status": "error", "message": "retrieval unavailable"}


def test_interactive_tool_distinguishes_empty_search():
    agent = failing_agent()
    result = agent._execute_tool("knowledge_base_search", {"query": "question"})
    assert result == {"status": "no_results", "message": "No relevant documents found"}


def test_interactive_non_agentic_search_failure_is_readable():
    agent = failing_agent()
    def unavailable(query):
        raise RuntimeError("retrieval unavailable")
    agent.kb_tools.knowledge_base_search = unavailable
    assert agent.query_non_agentic("question", stream=False) == (
        "Error processing query: retrieval unavailable"
    )


@pytest.mark.parametrize("mode", ["agentic", "non_agentic"])
def test_successful_answer_still_scored(mode):
    evaluator = RAGEvaluator.__new__(RAGEvaluator)
    evaluator.agent = failing_agent()
    answer = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content="Canberra", tool_calls=None))])
    evaluator.agent.client.chat.completions.create = lambda **kwargs: answer
    result = evaluator.run_test_case(
        {"id": "case-2", "question": "Capital?", "expected_keywords": ["Canberra"]}, mode
    )
    assert result["success"] is True
    assert result["metrics"]["keyword_recall"] == 1.0
    assert evaluator.agent.conversation_history == []


def test_exhausted_agent_iterations_are_a_failed_case():
    evaluator = RAGEvaluator.__new__(RAGEvaluator)
    evaluator.agent = failing_agent()
    evaluator.agent.config.agent.max_iterations = 1
    call = SimpleNamespace(id="call-1", type="function", function=SimpleNamespace(name="search", arguments="{}"))
    message = SimpleNamespace(content=None, tool_calls=[call])
    evaluator.agent.client.chat.completions.create = lambda **kwargs: SimpleNamespace(
        choices=[SimpleNamespace(message=message)]
    )
    evaluator.agent._execute_tool = lambda name, arguments, **kwargs: {"status": "ok"}

    result = evaluator.run_test_case({"id": "case-3", "question": "Capital?"})
    assert result["success"] is False
    assert "more iterations" in result["error"]


@pytest.mark.parametrize("method_name", ["query", "query_non_agentic"])
def test_interactive_error_message_is_preserved(method_name):
    agent = failing_agent()
    method = getattr(agent, method_name)
    assert method("question", stream=False) == "Error processing query: provider unavailable"
    assert "".join(method("question", stream=True)) == "Error processing query: provider unavailable"


@pytest.mark.parametrize("mode", ["agentic", "non_agentic"])
def test_retrieval_outage_is_not_a_successful_evaluation(mode, monkeypatch):
    import requests
    from config import KnowledgeBaseType
    from tools import KnowledgeBaseTools

    evaluator = RAGEvaluator.__new__(RAGEvaluator)
    evaluator.agent = failing_agent()
    evaluator.agent.config.knowledge_base.type = KnowledgeBaseType.LOCAL
    kb = KnowledgeBaseTools.__new__(KnowledgeBaseTools)
    kb.config = evaluator.agent.config.knowledge_base
    evaluator.agent.kb_tools = kb

    def fail_search(*args, **kwargs):
        raise requests.ConnectionError("retrieval unavailable")

    monkeypatch.setattr(requests, "post", fail_search)
    tool_call = SimpleNamespace(id="call-1", type="function", function=SimpleNamespace(
        name="knowledge_base_search", arguments='{"query": "Capital?"}'
    ))
    messages = iter([
        SimpleNamespace(content=None, tool_calls=[tool_call]),
        SimpleNamespace(content="No results", tool_calls=None),
    ]) if mode == "agentic" else iter([SimpleNamespace(content="No results", tool_calls=None)])
    evaluator.agent.client.chat.completions.create = lambda **kwargs: SimpleNamespace(
        choices=[SimpleNamespace(message=next(messages))]
    )
    result = evaluator.run_test_case({"id": "outage", "question": "Capital?"}, mode)
    assert result["success"] is False
