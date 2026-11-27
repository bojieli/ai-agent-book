from multilang_executor import LanguageExecutor


def test_files_outside_sandbox_are_not_written(tmp_path):
    sandbox = tmp_path / "sandbox" / "python_run"
    sandbox.mkdir(parents=True)
    outside = tmp_path / "outside.txt"
    absolute = tmp_path / "absolute.txt"

    LanguageExecutor(workspace_dir=str(tmp_path))._write_files(
        str(sandbox),
        {
            "../../outside.txt": "escaped\n",
            str(absolute): "escaped\n",
            "pkg/data.txt": "kept\n",
            "pkg/../top.txt": "kept\n",
        },
    )

    assert not outside.exists()
    assert not absolute.exists()
    assert (sandbox / "pkg" / "data.txt").read_text(encoding="utf-8") == "kept\n"
    assert (sandbox / "top.txt").read_text(encoding="utf-8") == "kept\n"
