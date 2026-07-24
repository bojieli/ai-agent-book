"""slowmo factor:null must not TypeError (skip like non-positive)."""
from blender_editor import _plan_fields, generate_bpy_script


def test_null_slowmo_factor_skipped_in_plan_fields():
    start, end, subtitle, slowmo = _plan_fields(
        {"start": 0.0, "end": 2.0, "effects": [{"type": "slowmo", "factor": None}]}
    )
    assert start == 0.0 and end == 2.0
    assert subtitle is None
    assert slowmo is None


def test_missing_slowmo_factor_still_defaults():
    _, _, _, slowmo = _plan_fields(
        {"start": 0.0, "end": 2.0, "effects": [{"type": "slowmo"}]}
    )
    assert slowmo == 2.0


def test_positive_slowmo_factor_kept():
    _, _, _, slowmo = _plan_fields(
        {"start": 0.0, "end": 2.0, "effects": [{"type": "slowmo", "factor": 3.0}]}
    )
    assert slowmo == 3.0


def test_generate_bpy_script_with_null_factor():
    script = generate_bpy_script(
        "/tmp/in.mp4",
        {"start": 0.0, "end": 1.0, "effects": [{"type": "slowmo", "factor": None}]},
        "/tmp/out.mp4",
    )
    assert "SLOWMO = None" in script
