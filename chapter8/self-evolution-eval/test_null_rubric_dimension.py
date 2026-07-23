"""Judge rubric dimensions that are JSON null must score as 0, not int(None)."""
from pathlib import Path


def _score_rubric(rubric: dict) -> tuple[int, float]:
    """Mirrors harness.layer3_tool_quality scoring after JSON parse."""
    dims = ["error_handling", "input_validation", "documentation", "robustness"]
    total = sum(int(rubric.get(d) or 0) for d in dims)
    score = round(total / (3 * len(dims)), 3)
    return total, score


def test_null_rubric_dimension_coerced():
    rubric = {
        "error_handling": None,
        "input_validation": 2,
        "documentation": 1,
        "robustness": 3,
        "comment": "ok",
    }
    total, score = _score_rubric(rubric)
    assert total == 6
    assert score == 0.5


def test_missing_dimension_still_zero():
    total, score = _score_rubric({"input_validation": 3})
    assert total == 3
    assert score == 0.25


def test_pristine_int_none_raises():
    """Old pattern int(rubric.get(d, 0)) still blows up on explicit null."""
    rubric = {"error_handling": None}
    try:
        int(rubric.get("error_handling", 0))
        raised = False
    except TypeError:
        raised = True
    assert raised


def test_source_uses_or_zero():
    src = Path(__file__).with_name("harness.py").read_text(encoding="utf-8")
    assert "int(rubric.get(d) or 0)" in src
    assert "int(rubric.get(d, 0))" not in src
