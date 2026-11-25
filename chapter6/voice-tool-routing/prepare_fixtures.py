#!/usr/bin/env python3
"""Regenerate the fixed user-speech recordings (synthetic voice, macOS `say`).

Each utterance is synthesised with the built-in Tingting (zh_CN) voice, converted
to 16 kHz mono int16 PCM with ffmpeg, trimmed of leading/trailing silence and
gain-normalised to -27 dBFS RMS (the centre of the level range the Doubao
realtime API documents for input speech).  The committed WAV files and their
SHA-256 in fixtures/audio/manifest.json are the canonical inputs; a different
macOS version may render slightly different audio.
"""

from __future__ import annotations

import argparse
import array
import hashlib
import json
import math
import platform
import shutil
import subprocess
import tempfile
import wave
from pathlib import Path

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "fixtures" / "audio"
VOICE = "Tingting"
RATE_WPM = 190
TARGET_DBFS = -27.0
SILENCE_THRESHOLD = 300  # int16 amplitude

# `[[slnc N]]` is the `say` markup for N ms of silence.
UTTERANCES = {
    "weather": "明天杭州天气怎么样？",
    "memory": "你还记得我的常旅客卡号吗？",
    "web_search": "帮我搜一下，从上海虹桥机场到国家会展中心，怎么走最快？",
    "flight_search": "帮我查一下十二月三号北京到上海的航班。",
    "self_correction": "帮我查一下下周三[[slnc 700]]不，下周四，北京到上海的航班。",
    "barge_change_date": "等一下，改成十二月四号的。",
    "booking_select": "就订九点整起飞的那一班，经济舱，要可以退改的，再加一件二十三公斤的托运行李。乘机人和联系人都用我本人的信息。",
    "booking_confirm": "确认，下单吧。",
    # Extension scenario: the passenger's name, passport number and phone are dictated (fictional person).
    "booking_dictated": (
        "就订九点整起飞的那一班，经济舱，要可以退改的，再加一件二十三公斤的托运行李。"
        "乘机人是我同事陈嘉怡，耳东陈，嘉奖的嘉，怡然的怡。"
        "她的护照号是，E，五八三零七一九四，手机号是，一三九，零零零零，七二四六。联系人用我本人的信息。"
    ),
}


def synthesise(text: str) -> bytes:
    with tempfile.TemporaryDirectory() as tmp:
        aiff = Path(tmp) / "u.aiff"
        raw = Path(tmp) / "u.pcm"
        subprocess.run(["say", "-v", VOICE, "-r", str(RATE_WPM), "-o", str(aiff), text], check=True)
        subprocess.run(
            ["ffmpeg", "-loglevel", "error", "-y", "-i", str(aiff), "-ac", "1", "-ar", "16000", "-f", "s16le", str(raw)],
            check=True,
        )
        return raw.read_bytes()


def trim_and_normalise(pcm: bytes) -> bytes:
    samples = array.array("h")
    samples.frombytes(pcm[: len(pcm) // 2 * 2])
    voiced = [i for i, s in enumerate(samples) if abs(s) > SILENCE_THRESHOLD]
    samples = samples[max(0, voiced[0] - 320) : voiced[-1] + 320]
    loud = [s for s in samples if abs(s) > SILENCE_THRESHOLD]
    rms = math.sqrt(sum(s * s for s in loud) / len(loud))
    gain = (32768 * 10 ** (TARGET_DBFS / 20)) / rms
    out = array.array("h", (max(-32768, min(32767, int(s * gain))) for s in samples))
    return out.tobytes()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--only", nargs="+", choices=list(UTTERANCES), help="synthesise only these clips and keep the others untouched")
    args = parser.parse_args()
    for tool in ("say", "ffmpeg"):
        if not shutil.which(tool):
            raise SystemExit(f"{tool} is required to regenerate fixtures (macOS)")
    AUDIO.mkdir(parents=True, exist_ok=True)
    previous = json.loads((AUDIO / "manifest.json").read_text(encoding="utf-8")) if (AUDIO / "manifest.json").exists() else {"clips": {}}
    manifest = {
        "synthesis": {
            "engine": "macOS say",
            "voice": VOICE,
            "rate_wpm": RATE_WPM,
            "macos": platform.mac_ver()[0],
            "format": "16 kHz mono int16 WAV",
            "normalisation": f"voiced RMS {TARGET_DBFS} dBFS, silence trimmed to 20 ms",
        },
        "clips": dict(previous["clips"]) if args.only else {},
    }
    for name, text in UTTERANCES.items():
        if args.only and name not in args.only:
            continue
        pcm = trim_and_normalise(synthesise(text))
        path = AUDIO / f"{name}.wav"
        with wave.open(str(path), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(pcm)
        manifest["clips"][name] = {
            "file": path.name,
            "say_text": text,
            "seconds": round(len(pcm) / 32000, 3),
            "sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        }
        print(path.name, manifest["clips"][name]["seconds"])
    (AUDIO / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
