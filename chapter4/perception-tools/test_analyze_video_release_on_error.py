"""Regression test: analyze_video_ai must release the VideoCapture even when a
per-frame Vision API call raises mid-loop.

The capture was previously released only on the success path, so a failing
Vision call (network / rate-limit / auth) leaked the native decoder/file handle
until GC. Release now happens in a finally.
"""
import asyncio
import json
import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Optional runtime deps for importing the chapter module in unit tests.
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda: None))
mcp = types.ModuleType("mcp")
mcp_types = types.ModuleType("mcp.types")


class TextContent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)


mcp_types.TextContent = TextContent
sys.modules["mcp"] = mcp
sys.modules["mcp.types"] = mcp_types

import cv2
import numpy as np

import media_processing_tools
from media_processing_tools import analyze_video_ai


class _FakeCapture:
    """Minimal VideoCapture stand-in that yields a few frames and records
    whether release() was called."""

    def __init__(self):
        self.released = False
        self._frames = 3
        self._i = 0

    def get(self, prop):
        if prop == cv2.CAP_PROP_FPS:
            return 10.0
        if prop == cv2.CAP_PROP_FRAME_COUNT:
            return float(self._frames)
        return 0.0

    def isOpened(self):
        return True

    def read(self):
        if self._i < self._frames:
            self._i += 1
            return True, np.zeros((48, 64, 3), dtype=np.uint8)
        return False, None

    def release(self):
        self.released = True


def test_analyze_video_ai_releases_capture_when_vision_call_raises(monkeypatch):
    fake = _FakeCapture()
    monkeypatch.setattr(media_processing_tools.cv2, "VideoCapture", lambda _path: fake)

    def _boom(**kwargs):
        raise RuntimeError("vision backend unavailable")

    client = types.SimpleNamespace(
        chat=types.SimpleNamespace(completions=types.SimpleNamespace(create=_boom))
    )
    monkeypatch.setattr(
        media_processing_tools, "_make_vision_client", lambda: (client, "fake-model")
    )
    # validate_file_path would reject a non-existent path before we reach the
    # capture; stub it to pass the path through unchanged.
    from pathlib import Path

    monkeypatch.setattr(media_processing_tools, "validate_file_path", lambda p: Path(p))

    result = asyncio.run(analyze_video_ai("some_clip.mp4", num_frames=2))
    payload = json.loads(result.text)

    assert payload["success"] is False
    assert fake.released is True
