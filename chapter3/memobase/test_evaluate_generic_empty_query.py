"""Regression tests: benchmark evaluation must not raise ZeroDivisionError on
tasks with an empty/whitespace query (e.g. loaded from tasks.json) that fall
through to the generic evaluator."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from locomo_benchmark import BenchmarkTask, LOCOMOBenchmark

LONG_RESPONSE = (
    "This is a reasonably long agent response. It has several sentences. "
    "And it keeps going with more detail. Even more detail here."
)


def _suite():
    return LOCOMOBenchmark.__new__(LOCOMOBenchmark)


def test_evaluate_generic_empty_query():
    task = BenchmarkTask(id="t1", category="custom_category", query="")
    score = _suite()._evaluate_generic(task, LONG_RESPONSE)
    assert 0.0 <= score <= 1.0


def test_evaluate_response_whitespace_query_unknown_category():
    task = BenchmarkTask(id="t2", category="custom_category", query="   ")
    result = _suite().evaluate_response(
        task, response=LONG_RESPONSE, execution_time=1.0, memory_usage={}
    )
    assert 0.0 <= result.score <= 1.0


def test_evaluate_generic_normal_query_unchanged():
    task = BenchmarkTask(id="t3", category="custom_category", query="weather forecast analysis")
    score = _suite()._evaluate_generic(task, LONG_RESPONSE.replace("agent", "weather"))
    assert score > 0.0
