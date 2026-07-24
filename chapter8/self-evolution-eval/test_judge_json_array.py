"""Judge JSON that is an array must not AttributeError in rubric scoring."""
from harness import _parse_judge_json, _rubric_dimension_total


def test_json_array_parses_as_none():
    raw = (
        '[{"error_handling":3,"input_validation":2,'
        '"documentation":2,"robustness":3,"comment":"ok"}]'
    )
    assert _parse_judge_json(raw) is None


def test_json_object_still_parses():
    raw = (
        '{"error_handling":3,"input_validation":2,'
        '"documentation":1,"robustness":3,"comment":"ok"}'
    )
    rubric = _parse_judge_json(raw)
    assert isinstance(rubric, dict)
    assert _rubric_dimension_total(rubric) == 9


def test_embedded_object_in_prose_still_parses():
    raw = '点评如下：\n{"error_handling":1,"input_validation":1,"documentation":1,"robustness":1}\n完'
    rubric = _parse_judge_json(raw)
    assert rubric is not None
    assert _rubric_dimension_total(rubric) == 4
