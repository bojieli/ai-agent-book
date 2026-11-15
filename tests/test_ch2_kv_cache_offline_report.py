"""Regression tests for mixed input files in the chapter 2 KV cache report."""

import json
import os
from pathlib import Path
import subprocess
import sys

import pytest


REPORT = Path(__file__).resolve().parents[1] / "chapter2" / "kv-cache" / "main.py"


@pytest.mark.parametrize("unrelated_json", [[], [{"event": "tool_call"}], None, 42])
def test_report_skips_non_object_json_and_keeps_valid_runs(tmp_path, unrelated_json):
    wrong = tmp_path / "result_0_trace.json"
    single = tmp_path / "result_1_single.json"
    comparison = tmp_path / "comparison_2_saved.json"
    wrong.write_text(json.dumps(unrelated_json), encoding="utf-8")
    single.write_text(
        json.dumps({"mode": "correct", "iterations": 1, "metrics": {"prompt_tokens": 200}}),
        encoding="utf-8",
    )
    comparison.write_text(
        json.dumps({"sliding_window": {"iterations": 2, "metrics": {"prompt_tokens": 400}}}),
        encoding="utf-8",
    )

    result = subprocess.run(
        [sys.executable, "-X", "utf8", str(REPORT), "--report", "--input", str(tmp_path)],
        cwd=tmp_path,
        env={**os.environ, "MOONSHOT_API_KEY": "", "KIMI_API_KEY": "", "OPENROUTER_API_KEY": ""},
        capture_output=True,
        encoding="utf-8",
        timeout=20,
    )

    assert result.returncode == 0, result.stderr
    assert single.name in result.stdout
    assert comparison.name in result.stdout
    assert wrong.name not in result.stdout
    assert wrong.name in result.stderr
    assert "expected a JSON object" in result.stderr
