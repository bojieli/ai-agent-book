"""Regression: empty test set must not ZeroDivisionError on parse-rate summary."""
from eval_metrics import parse_rate


def test_parse_rate_empty_total_is_zero():
    assert parse_rate(0, 0) == 0.0


def test_parse_rate_nonzero_total():
    assert parse_rate(8, 10) == 0.8
