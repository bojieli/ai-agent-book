"""Regression tests: _normalize must coerce non-scalar LLM-provided JSON values
(e.g. lists/dicts for a numeric factor) to None instead of raising TypeError."""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from extractor import _normalize

FACTORS = [{"key": "amount", "kind": "numeric", "values": []}]


def test_numeric_list_value_becomes_none():
    out = _normalize({"amount": ["约10万元"]}, "盗窃罪", FACTORS)
    assert out == {"charge": "盗窃罪", "amount": None}


def test_numeric_dict_value_becomes_none():
    out = _normalize({"amount": {"value": 5}}, "盗窃罪", FACTORS)
    assert out["amount"] is None


def test_numeric_string_extracts_digits():
    out = _normalize({"amount": "约105000元"}, "盗窃罪", FACTORS)
    assert out["amount"] == 105000


def test_numeric_plain_int_unchanged():
    out = _normalize({"amount": 5000}, "盗窃罪", FACTORS)
    assert out["amount"] == 5000


def test_numeric_null_stays_none():
    out = _normalize({"amount": None}, "盗窃罪", FACTORS)
    assert out["amount"] is None
