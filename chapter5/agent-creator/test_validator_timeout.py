from __future__ import annotations

from validator import validate_agent


def test_hanging_generated_test_fails_the_tests_gate(tmp_path):
    (tmp_path / "test_hang.py").write_text(
        "import time\n\n\ndef test_hang():\n    print('started', flush=True)\n    time.sleep(30)\n",
        encoding="utf-8",
    )

    report = validate_agent(tmp_path, timeout=3)

    assert report.tests_ok is False
    assert any("timed out after 3s" in error for error in report.errors)
