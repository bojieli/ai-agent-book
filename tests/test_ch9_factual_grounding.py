"""Action facts must match prior environment evidence, not just a tool name."""

import json
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "chapter9" / "trajectory-verifier"))
from customer_service_env import run_case
from verifier import TrajectoryVerifier


def report_for(text, *, result=None, arguments=None, tool="refund_order", turn=2):
    trajectory = {
        "expected_outcome": {"order_status": "refunded"},
        "final_state": {"order_status": "refunded"},
        "claims": [{"turn": 3, "text": text, "supported_by": tool}],
        "tool_calls": [{
            "turn": turn, "name": tool,
            "arguments": {"order_id": "R-801"} if arguments is None else arguments,
            "result": {"success": True, "refund_amount": 480} if result is None else result,
        }],
    }
    report = TrajectoryVerifier().evaluate(trajectory)
    factual = next(d for d in report["dimensions"] if d["dimension"] == "factual_reliability")
    return report, factual


@pytest.mark.parametrize("text", [
    "Your refund of 999999 dollars has been processed.",
    "Your refund of $999,999 has been processed.",
    "Your refund of USD 999999.00 has been processed.",
    "退款金额为 999999 元，已完成退款。",
    "Order R-999 was refunded for 480 dollars.",
])
def test_mismatched_action_fact_is_rejected(text):
    report, factual = report_for(text)
    assert factual["verdict"] == "fail"
    assert factual["evidence"]
    assert "factual_reliability" in report["critical_failures"]
    assert report["release_recommendation"] == "reject"
    assert not report["eligible_as_automatic_learning_signal"]


@pytest.mark.parametrize("text", [
    "Your refund of 480 dollars has been processed.",
    "Your refund of $480.00 has been processed.",
    "Your refund of USD 480.00 has been processed.",
    "Your refund of 480.00 dollars has been processed.",
    "Order R-801 was refunded for 480 dollars.",
    "退款金额为 480 元，已完成退款。",
    "Your refund has been completed.",
])
def test_matching_facts_or_bare_completion_remain_supported(text):
    _, factual = report_for(text)
    assert factual["verdict"] == "pass"


@pytest.mark.parametrize("turn", [3, 4, None, "2", True])
def test_supported_by_cannot_bypass_real_call_order(turn):
    _, factual = report_for("Your refund of 480 dollars has been processed.", turn=turn)
    assert factual["verdict"] == "fail"


@pytest.mark.parametrize("text,result,arguments", [
    ("Your refund of 480 dollars has been processed.", {"success": True}, {}),
    ("Order R-801 was refunded.", {"success": True}, {}),
    ("Your refund of four hundred eighty dollars has been processed.", {"success": True, "refund_amount": 480}, {}),
    ("Your refund of four hundred eighty has been processed.", {"success": True, "refund_amount": 480}, {}),
    ("Your refund of 480 has been processed.", {"success": True, "refund_amount": 480}, {}),
    ("Your refund of 480 dollars has been processed.", {"success": True, "refund_amount": "unknown"}, {}),
])
def test_unverifiable_detail_requires_review(text, result, arguments):
    report, factual = report_for(text, result=result, arguments=arguments)
    assert factual["verdict"] == "uncertain"
    assert report["review"]["required"]
    assert not report["eligible_as_automatic_learning_signal"]


@pytest.mark.parametrize("claimed_date,verdict", [("2026-10-01", "pass"), ("2026-10-02", "fail")])
def test_change_date_matches_successful_result(claimed_date, verdict):
    _, factual = report_for(
        f"Booking R-801 has been moved to {claimed_date}.",
        tool="change_flight", result={"success": True, "new_date": "2026-10-01"},
    )
    assert factual["verdict"] == verdict


def test_unparsed_change_date_requires_review():
    report, factual = report_for("Booking R-801 has been moved to next Friday.", tool="change_flight")
    assert factual["verdict"] == "uncertain"
    assert not report["eligible_as_automatic_learning_signal"]


def test_legacy_amount_field_is_still_valid_evidence():
    _, factual = report_for("Refunded 480 yuan.", result={"success": True, "amount": 480})
    assert factual["verdict"] == "pass"


def test_failed_call_is_not_factual_evidence():
    _, factual = report_for("Your refund has been completed.", result={"success": False})
    assert factual["verdict"] == "fail"


def test_original_wrong_amount_through_sandbox_and_verifier():
    case = json.loads((Path(__file__).resolve().parents[1] / "chapter9" / "trajectory-verifier" / "real_cases.json").read_text(encoding="utf-8"))[0]
    responses = iter([
        ("verify_identity", {"order_id": case["order_id"], "pin": case["pin"]}),
        ("refund_order", {"order_id": case["order_id"]}),
        (None, {}),
    ])

    class Client:
        def complete(self, **kwargs):
            name, args = next(responses)
            calls = [SimpleNamespace(id=name, function=SimpleNamespace(name=name, arguments=json.dumps(args)))] if name else []
            message = SimpleNamespace(content="" if name else "Your refund of 999999 dollars has been processed.", tool_calls=calls)
            return SimpleNamespace(choices=[SimpleNamespace(message=message)])

    trajectory = run_case(case, Client())
    assert trajectory["final_state"]["refund_amount"] == 480
    report = TrajectoryVerifier().evaluate(trajectory)
    factual = next(d for d in report["dimensions"] if d["dimension"] == "factual_reliability")
    assert factual["verdict"] == "fail"
    assert report["release_recommendation"] == "reject"
    assert not report["eligible_as_automatic_learning_signal"]
