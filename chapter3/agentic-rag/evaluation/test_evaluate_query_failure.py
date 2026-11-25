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
    evaluator.agent._execute_tool = lambda name, arguments: {"status": "ok"}

    result = evaluator.run_test_case({"id": "case-3", "question": "Capital?"})
    assert result["success"] is False
    assert "more iterations" in result["error"]


@pytest.mark.parametrize("method_name", ["query", "query_non_agentic"])
def test_interactive_error_message_is_preserved(method_name):
    agent = failing_agent()
    method = getattr(agent, method_name)
    assert method("question", stream=False) == "Error processing query: provider unavailable"
    assert "".join(method("question", stream=True)) == "Error processing query: provider unavailable"
