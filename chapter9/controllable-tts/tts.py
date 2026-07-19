"""
TTS 合成层（OpenAI TTS）
========================

Provider 适配：书中实验用 Fish Audio 的控制标记 + 声音克隆参考语音库。
Fish Audio 无可用 key，这里改用 OpenAI TTS 演示相同思路：

  - 首选 gpt-4o-mini-tts：支持 `instructions` 参数，可用一段风格提示词精确
    控制情感 / 语速 / 口吻，最贴近「控制标记 -> 风格化语音」的语义；
  - 若该模型不可用，自动兜底到 tts-1：不支持 instructions，改用多 voice +
    `speed` 参数 + 文本级停顿近似。

一段控制标记文本被解析成多个片段后：
  - speech 片段：各自用对应参考语音（同一 base voice + 不同 instructions）合成；
  - silence 片段：用 ffmpeg 生成真实静音；
最后用 ffmpeg 把所有片段按顺序拼成一个 mp3（音色一致、韵律/情感/停顿不同）。
"""

import os
import subprocess
import tempfile

from openai import OpenAI

from voice_library import VOICE_LIBRARY, BASE_VOICE, build_instructions, speed_factor, profile_key

# 可用 TTS_MODEL 环境变量覆盖；默认首选 gpt-4o-mini-tts
PREFERRED_MODEL = os.getenv("TTS_MODEL", "gpt-4o-mini-tts")
FALLBACK_MODEL = "tts-1"

_client = None
_active_model = None  # 首次调用后确定实际使用的模型


def _get_client():
    global _client
    if _client is None:
        # timeout + 自动重试：单次网络/SSL 抖动不至于让整段合成崩溃
        _client = OpenAI(timeout=60.0, max_retries=3)
    return _client


def _synth_call(model, text, voice, instructions, speed, out_path):
    """真正调用 OpenAI TTS。gpt-4o-mini-tts 用 instructions；tts-1 用 speed。"""
    client = _get_client()
    kwargs = dict(model=model, voice=voice, input=text, response_format="mp3")
    if model == "tts-1":
        # tts-1 不支持 instructions，用 speed 参数近似语速控制
        kwargs["speed"] = max(0.25, min(4.0, speed))
    else:
        kwargs["instructions"] = instructions
    with client.audio.speech.with_streaming_response.create(**kwargs) as resp:
        resp.stream_to_file(out_path)


def synth_speech(text, emotion, speed, style, emphasis, out_path):
    """
    合成一个 speech 片段，返回实际使用的 (model, voice, instructions/speed) 供打印。
    音色固定 = BASE_VOICE，保证整段音色一致（模拟 Fish Audio 的音色一致性）。
    """
    global _active_model
    key = profile_key(emotion, speed, style)
    profile = VOICE_LIBRARY.get(key)
    voice = profile["base_voice"] if profile else BASE_VOICE
    instructions = build_instructions(emotion, speed, style, emphasis)
    spd = speed_factor(speed)

    model = _active_model or PREFERRED_MODEL
    try:
        _synth_call(model, text, voice, instructions, spd, out_path)
        _active_model = model
    except Exception as e:
        # 首选模型不可用时兜底到 tts-1
        if model != FALLBACK_MODEL:
            print(f"  [warn] 模型 {model} 调用失败({repr(e)[:80]})，兜底到 {FALLBACK_MODEL}")
            _synth_call(FALLBACK_MODEL, text, voice, instructions, spd, out_path)
            _active_model = FALLBACK_MODEL
            model = FALLBACK_MODEL
        else:
            raise
    return {"model": model, "voice": voice, "profile": key,
            "instructions": instructions, "speed_factor": spd}


def make_silence(ms, out_path):
    """用 ffmpeg 生成一段真实静音 mp3（会计入总时长，可被 ffprobe 验证）。"""
    subprocess.run(
        ["ffmpeg", "-y", "-f", "lavfi", "-i", "anullsrc=r=24000:cl=mono",
         "-t", f"{ms/1000:.3f}", "-q:a", "9", out_path],
        check=True, capture_output=True,
    )


def concat_mp3(part_paths, out_path):
    """用 ffmpeg concat demuxer 把多个 mp3 片段按顺序拼接（统一重编码，避免时基问题）。"""
    with tempfile.NamedTemporaryFile("w", suffix=".txt", delete=False) as f:
        for p in part_paths:
            f.write(f"file '{os.path.abspath(p)}'\n")
        list_path = f.name
    try:
        subprocess.run(
            ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_path,
             "-ar", "24000", "-ac", "1", "-b:a", "64k", out_path],
            check=True, capture_output=True,
        )
    finally:
        os.unlink(list_path)


def synthesize_segments(segments, out_path, workdir):
    """
    把 parse() 得到的片段列表合成为一个完整 mp3。
    返回每个片段的合成信息列表（供打印验证）。
    """
    os.makedirs(workdir, exist_ok=True)
    parts, info = [], []
    for i, seg in enumerate(segments):
        part_path = os.path.join(workdir, f"seg_{i:02d}.mp3")
        if seg["type"] == "silence":
            make_silence(seg["ms"], part_path)
            info.append({"type": "silence", "ms": seg["ms"]})
        else:
            meta = synth_speech(seg["text"], seg["emotion"], seg["speed"],
                                seg["style"], seg.get("emphasis", False), part_path)
            meta["type"] = "speech"
            meta["text"] = seg["text"]
            info.append(meta)
        parts.append(part_path)

    if len(parts) == 1:
        os.replace(parts[0], out_path)
    else:
        concat_mp3(parts, out_path)
    return info
