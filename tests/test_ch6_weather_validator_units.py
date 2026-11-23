"""grounded_weather_answer gate of chapter6/claude-computer-use-native/validate_weather_run.py.

The gate must accept a temperature written with spelled-out units ("62 degrees
Fahrenheit"), not only the abbreviated "62°F" / "62 degrees F". Each case runs the
real validator on a temporary copy of the retained passing run, with only the
final answer replaced, so every other gate stays as recorded.
"""

import json
import shutil
import sys
from pathlib import Path

import pytest

EXPERIMENT = Path(__file__).resolve().parent.parent / "chapter6" / "claude-computer-use-native"
RUN = EXPERIMENT / "validation" / "runs" / "exp6-7-anthropic-native-20260803-v2"
if str(EXPERIMENT) not in sys.path:
    sys.path.insert(0, str(EXPERIMENT))

import validate_weather_run


def gates_for(final_answer, tmp_path, monkeypatch, capsys):
    run_dir = tmp_path / RUN.name
    shutil.copytree(RUN, run_dir)
    trajectory_path = run_dir / "trajectory.json"
    trajectory = json.loads(trajectory_path.read_text(encoding="utf-8"))
    trajectory["final_answer"] = final_answer
    trajectory_path.write_text(json.dumps(trajectory), encoding="utf-8")
    monkeypatch.setattr(sys, "argv", ["validate_weather_run.py", str(run_dir)])
    exit_code = validate_weather_run.main()
    capsys.readouterr()
    acceptance = json.loads((run_dir / "acceptance.json").read_text(encoding="utf-8"))
    return exit_code, acceptance["gates"]


def test_retained_answer_still_passes(tmp_path, monkeypatch, capsys):
    final = json.loads((RUN / "trajectory.json").read_text(encoding="utf-8"))["final_answer"]
    exit_code, gates = gates_for(final, tmp_path, monkeypatch, capsys)
    assert gates["grounded_weather_answer"] is True
    assert exit_code == 0


@pytest.mark.parametrize(
    "answer",
    [
        "It is 62 degrees Fahrenheit and sunny in San Francisco.",
        "Currently 17 degrees Celsius with clear skies.",
        "It is 62 degree fahrenheit, partly cloudy.",
        "It is 62°F and sunny.",
        "It is 62 degrees F and overcast.",
        "It is -3 °C and snowy.",
    ],
)
def test_temperature_with_units_is_grounded(answer, tmp_path, monkeypatch, capsys):
    exit_code, gates = gates_for(answer, tmp_path, monkeypatch, capsys)
    assert gates["grounded_weather_answer"] is True
    assert exit_code == 0


@pytest.mark.parametrize(
    "answer",
    [
        "It is sunny.",
        "It is 62 and sunny.",
        "It is 62 degrees and sunny.",
        "Wind at 62 degrees from the north, sunny.",
        "It is 62 degrees Fahrenheitish and sunny.",
    ],
)
def test_answer_without_a_temperature_unit_is_rejected(answer, tmp_path, monkeypatch, capsys):
    exit_code, gates = gates_for(answer, tmp_path, monkeypatch, capsys)
    assert gates["grounded_weather_answer"] is False
    assert exit_code == 1
