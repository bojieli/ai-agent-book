"""Exercise dotenv lookup in fresh CLI processes so Config defaults are reloaded."""
import os
import shutil
import subprocess
import sys
from pathlib import Path


def test_env_provider_precedence(tmp_path):
    context = Path(__file__).resolve().parents[1]
    chapter = tmp_path / "chapter1" / "context"
    chapter.mkdir(parents=True)
    shutil.copyfile(context / "config.py", chapter / "config.py")
    probe = chapter / "probe.py"
    probe.write_text("from config import Config\nprint(Config.LLM_PROVIDER)\n")
    (tmp_path / ".env").write_text("LLM_PROVIDER=ollama\n")
    env = {**os.environ, "PYTHONPATH": str(context.parents[1])}
    env.pop("LLM_PROVIDER", None)

    def read_provider():
        return subprocess.check_output(
            [sys.executable, str(probe)], cwd=tmp_path, env=env, text=True
        ).strip()

    assert read_provider() == "ollama"
    (chapter / ".env").write_text("LLM_PROVIDER=kimi\n")
    assert read_provider() == "kimi"
    env["LLM_PROVIDER"] = "openrouter"
    assert read_provider() == "openrouter"
