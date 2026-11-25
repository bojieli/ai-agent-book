"""Thin client for the Doubao realtime voice model 3.0 (Seeduplex) JSON event protocol.

Protocol reference (read 2026-11-25):
https://www.volcengine.com/docs/doubao-voice/end-to-end-real-time-voice-full-duplex-version

The client does three things the experiment depends on:

* paces 16 kHz mono int16 PCM upstream in real time (20 ms frames, silence when
  no clip is queued), because the server rejects streams that are faster or
  slower than real time and uses the upstream audio as keep-alive;
* timestamps every upstream and downstream event against one monotonic clock;
* writes a JSONL trace with audio payloads replaced by byte counts.  The API key
  only ever lives in the WebSocket handshake header and is never written.
"""

from __future__ import annotations

import asyncio
import base64
import json
import time
from collections import deque
from pathlib import Path
from typing import Any, Awaitable, Callable

import websockets

ENDPOINT = "wss://openspeech.bytedance.com/api/v3/duplex/realtime/dialogue"
FRONT_MODEL = "1.2.6.1"
DEFAULT_VOICE = "zh_female_xiaohe_jupiter_bigtts"
INPUT_RATE = 16000
OUTPUT_RATE = 24000
FRAME_SECONDS = 0.02
FRAME_BYTES = int(INPUT_RATE * FRAME_SECONDS) * 2  # 640
SILENCE = b"\x00" * FRAME_BYTES

EventHandler = Callable[[dict[str, Any], float], Awaitable[None] | None]


class FrontSession:
    def __init__(
        self,
        api_key: str,
        *,
        instructions: str,
        tools: list[dict[str, Any]],
        trace_path: Path | None = None,
        voice: str = DEFAULT_VOICE,
        model: str = FRONT_MODEL,
        endpoint: str = ENDPOINT,
        keep_output_audio: bool = False,
    ) -> None:
        self._api_key = api_key
        self.instructions = instructions
        self.tools = tools
        self.voice = voice
        self.model = model
        self.endpoint = endpoint
        self.trace_path = trace_path
        self._trace_file = None
        self.ws = None
        self.t0 = time.monotonic()
        self.logid: str | None = None
        self.session_id: str | None = None
        self.events: list[dict[str, Any]] = []
        self.handlers: list[EventHandler] = []
        self._clips: deque[tuple[str, bytes]] = deque()
        self._current: tuple[str, bytes, int] | None = None
        self._tasks: list[asyncio.Task] = []
        self._closed = asyncio.Event()
        self._event_seq = 0
        self.keep_output_audio = keep_output_audio
        self.output_audio = bytearray()
        self.frames_sent = 0
        self.error: dict[str, Any] | None = None

    # ------------------------------------------------------------------ utils
    def now(self) -> float:
        return round(time.monotonic() - self.t0, 4)

    def log(self, direction: str, record: dict[str, Any]) -> dict[str, Any]:
        entry = {"t": self.now(), "dir": direction, **record}
        self.events.append(entry)
        if self._trace_file is not None:
            self._trace_file.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return entry

    def _next_event_id(self) -> str:
        self._event_seq += 1
        return f"evt_{self._event_seq}"

    # ------------------------------------------------------------- lifecycle
    async def start(self) -> None:
        if self.trace_path is not None:
            self.trace_path.parent.mkdir(parents=True, exist_ok=True)
            self._trace_file = self.trace_path.open("w", encoding="utf-8")
        self.t0 = time.monotonic()
        self.ws = await websockets.connect(
            self.endpoint,
            additional_headers={"X-Api-Key": self._api_key},
            ping_interval=None,
            max_size=None,
        )
        try:
            self.logid = self.ws.response.headers.get("X-Tt-Logid")
        except Exception:  # pragma: no cover - header access differs by version
            self.logid = None
        self.log("local", {"type": "ws.connected", "logid": self.logid, "endpoint": self.endpoint})
        await self.send(
            {
                "type": "session.create",
                "session": {
                    "model": self.model,
                    "instructions": self.instructions,
                    "audio": {
                        "input": {"format": {"type": "pcm", "rate": INPUT_RATE}},
                        "output": {
                            "format": {"type": "pcm_s16le", "rate": OUTPUT_RATE},
                            "voice": self.voice,
                        },
                    },
                    "tools": self.tools,
                },
                "extension": {"asr": {}, "tts": {}, "dialog": {}},
            }
        )
        while True:
            event = await self._recv_one()
            if event.get("type") == "session.created":
                self.session_id = (event.get("session") or {}).get("id")
                break
            if event.get("type") == "error":
                raise RuntimeError(f"session.create failed: {json.dumps(event, ensure_ascii=False)[:500]}")
        self._tasks = [asyncio.create_task(self._pump()), asyncio.create_task(self._receive())]

    async def close(self) -> None:
        for task in self._tasks[:1]:
            task.cancel()
        try:
            if self.ws is not None:
                await self.send({"type": "session.close"})
                try:
                    await asyncio.wait_for(self._closed.wait(), timeout=3)
                except asyncio.TimeoutError:
                    self.log("local", {"type": "session.close.timeout"})
        except Exception as exc:  # noqa: BLE001 - closing must not mask run errors
            self.log("local", {"type": "close.error", "error": repr(exc)})
        for task in self._tasks:
            task.cancel()
        await asyncio.gather(*self._tasks, return_exceptions=True)
        if self.ws is not None:
            await self.ws.close()
        if self._trace_file is not None:
            self._trace_file.close()
            self._trace_file = None

    # ---------------------------------------------------------------- upstream
    async def send(self, event: dict[str, Any], *, log: bool = True) -> None:
        event.setdefault("event_id", self._next_event_id())
        if log:
            self.log("up", event)
        await self.ws.send(json.dumps(event, ensure_ascii=False, separators=(",", ":")))

    def queue_clip(self, name: str, pcm: bytes) -> None:
        """Queue a PCM clip; it starts on the next 20 ms frame boundary."""
        self._clips.append((name, pcm))

    @property
    def speaking(self) -> bool:
        return self._current is not None or bool(self._clips)

    async def _pump(self) -> None:
        start = time.monotonic()
        n = 0
        while True:
            frame = SILENCE
            if self._current is None and self._clips:
                name, pcm = self._clips.popleft()
                self._current = (name, pcm, 0)
                self.log("local", {"type": "user_audio.start", "clip": name, "bytes": len(pcm)})
            ended: str | None = None
            if self._current is not None:
                name, pcm, pos = self._current
                frame = pcm[pos : pos + FRAME_BYTES]
                pos += FRAME_BYTES
                if len(frame) < FRAME_BYTES:
                    frame = frame + b"\x00" * (FRAME_BYTES - len(frame))
                if pos >= len(pcm):
                    self._current = None
                    ended = name
                else:
                    self._current = (name, pcm, pos)
            await self.ws.send(
                json.dumps(
                    {"type": "input_audio_buffer.append", "audio": base64.b64encode(frame).decode("ascii")},
                    separators=(",", ":"),
                )
            )
            self.frames_sent += 1
            if ended is not None:
                # The last voiced frame of the clip has just left the client.
                self.log("local", {"type": "user_audio.end", "clip": ended})
            n += 1
            delay = start + n * FRAME_SECONDS - time.monotonic()
            if delay > 0:
                await asyncio.sleep(delay)

    # -------------------------------------------------------------- downstream
    async def _recv_one(self) -> dict[str, Any]:
        frame = await self.ws.recv()
        if isinstance(frame, bytes):
            frame = frame.decode("utf-8")
        event = json.loads(frame)
        record = dict(event)
        if event.get("type") == "response.output_audio.delta":
            audio = base64.b64decode(event.get("delta") or "")
            if self.keep_output_audio:
                self.output_audio.extend(audio)
            record["delta"] = None
            record["audio_bytes"] = len(audio)
        entry = self.log("down", record)
        event["_t"] = entry["t"]
        return event

    async def _receive(self) -> None:
        try:
            while True:
                event = await self._recv_one()
                kind = event.get("type")
                if kind == "error":
                    self.error = event
                for handler in list(self.handlers):
                    result = handler(event, event["_t"])
                    if asyncio.iscoroutine(result):
                        await result
                if kind == "session.closed":
                    self._closed.set()
                    return
        except asyncio.CancelledError:
            raise
        except websockets.ConnectionClosed as exc:
            self.log("local", {"type": "ws.closed", "detail": str(exc)[:300]})
            self.error = self.error or {"type": "ws.closed", "detail": str(exc)[:300]}
            self._closed.set()

    # ------------------------------------------------------------ conveniences
    async def send_tool_results(self, items: list[tuple[str, str]]) -> None:
        await self.send(
            {
                "type": "conversation.item.create",
                "items": [
                    {
                        "type": "message",
                        "role": "tool",
                        "call_id": call_id,
                        "content": [{"type": "input_text", "text": text}],
                    }
                    for call_id, text in items
                ],
            }
        )

    async def update_instructions(self, instructions: str) -> None:
        self.instructions = instructions
        await self.send(
            {
                "type": "session.update",
                "session": {"id": self.session_id, "model": self.model, "instructions": instructions, "tools": self.tools},
            }
        )
