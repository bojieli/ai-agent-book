"""Regression: the LLM approval reviewer must fail closed unless the model
returns a real JSON boolean true. A string like "false" is truthy in Python,
so returning it raw let callers' `if not approved:` run the operation."""

from types import SimpleNamespace

import pytest
from llm_helper import LLMHelper


def helper_replying(content):
    helper = LLMHelper()
    helper.model = "test-model"
    helper._ensure_client = lambda: None
    helper._record_receipt = lambda *args: None
    reply = SimpleNamespace(choices=[SimpleNamespace(message=SimpleNamespace(content=content))])
    helper.client = SimpleNamespace(
        chat=SimpleNamespace(completions=SimpleNamespace(create=lambda **kwargs: reply))
    )
    return helper


@pytest.mark.parametrize(
    "content",
    [
        '{"approved": "false", "reason": "deletes the root filesystem"}',
        '{"approved": "no", "reason": "risky"}',
        '{"approved": "true", "reason": "string, not a boolean"}',
        '{"approved": 1, "reason": "number, not a boolean"}',
        '{"approved": null, "reason": "undecided"}',
        '{"reason": "approved key missing"}',
        '["approved"]',
        '{"approved": false, "reason": "risky"}',
    ],
)
def test_anything_but_boolean_true_is_rejected(content):
    approved, reason = helper_replying(content).request_approval(
        "code_execution", {"code": "rm -rf /", "language": "bash"}
    )
    assert approved is False
    assert isinstance(reason, str)


def test_boolean_true_is_approved_with_reason():
    approved, reason = helper_replying(
        '```json\n{"approved": true, "reason": "read-only command"}\n```'
    ).request_approval("code_execution", {"code": "ls", "language": "bash"})
    assert approved is True
    assert reason == "read-only command"
