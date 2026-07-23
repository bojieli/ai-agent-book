"""Judge rubric dimensions that are JSON null must score as 0, not int(None)."""
import pytest

from harness import _rubric_dimension_total


def test_null_rubric_dimension_coerced():
    rubric = {
        "error_handling": None,
        "input_validation": 2,
        "documentation": 1,
        "robustness": 3,
        "comment": "ok",
    }
    assert _rubric_dimension_total(rubric) == 6


def test_missing_dimension_still_zero():
    assert _rubric_dimension_total({"input_validation": 3}) == 3


def test_empty_string_score_rejected():
    with pytest.raises(ValueError):
        _rubric_dimension_total({"error_handling": ""})


def test_pristine_int_none_raises():
    """Old pattern int(rubric.get(d, 0)) still blows up on explicit null."""
    rubric = {"error_handling": None}
    with pytest.raises(TypeError):
        int(rubric.get("error_handling", 0))
