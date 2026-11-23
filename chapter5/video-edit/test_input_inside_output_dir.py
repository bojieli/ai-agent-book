"""Regression: demo.py clears output/ at the start of every run, so an --input
video inside output/ (e.g. re-editing a previous final.mp4) must be refused
before the directory is wiped, not deleted and then reported missing."""

import os
import sys

import demo
import pytest


@pytest.fixture
def out_dir(tmp_path, monkeypatch):
    out = tmp_path / "output"
    out.mkdir()
    monkeypatch.setattr(demo, "OUT_DIR", str(out))
    monkeypatch.setattr(demo, "preflight", lambda: None)
    return out


def run_demo(monkeypatch, *argv):
    monkeypatch.setattr(sys, "argv", ["demo.py", *argv])
    with pytest.raises(SystemExit) as exc:
        demo.main()
    return exc.value.code


def test_input_inside_output_dir_is_refused_and_kept(out_dir, monkeypatch, capsys):
    previous = out_dir / "final.mp4"
    previous.write_bytes(b"previous result")
    sibling = out_dir / "edit.py"
    sibling.write_text("# previous bpy script")

    assert run_demo(monkeypatch, "-i", str(previous)) == 1

    assert previous.read_bytes() == b"previous result"
    assert sibling.exists()
    assert "output" in capsys.readouterr().out


def test_relative_input_inside_output_dir_is_refused(out_dir, monkeypatch, capsys):
    previous = out_dir / "nested" / "clip.mp4"
    previous.parent.mkdir()
    previous.write_bytes(b"clip")
    monkeypatch.chdir(out_dir.parent)

    assert run_demo(monkeypatch, "-i", os.path.join("output", "nested", "clip.mp4")) == 1
    assert previous.exists()


def test_missing_input_is_reported_before_output_is_cleared(out_dir, monkeypatch, capsys):
    kept = out_dir / "final.mp4"
    kept.write_bytes(b"previous result")

    assert run_demo(monkeypatch, "-i", str(out_dir.parent / "missing.mp4")) == 1

    assert kept.exists()
    assert "missing.mp4" in capsys.readouterr().out
