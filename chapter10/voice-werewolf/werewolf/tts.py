# -*- coding: utf-8 -*-
"""可选的语音合成（TTS）——把玩家公开发言合成为语音。

语音是本实验的**可选增强**，不是跑通的必需：默认文本模式即可完整跑完一局并
验证信息隔离。加 --voice 时才启用，用 OpenAI tts-1 把每条公开发言合成 mp3，
存到 audio/ 目录；在 macOS 上可用 afplay 顺带播放（--play）。
"""

import os
import subprocess

from .agent import get_client


# 给不同玩家分配不同音色，便于区分
_VOICES = ["alloy", "echo", "fable", "onyx", "nova", "shimmer", "coral"]


class TTS:
    def __init__(self, out_dir: str, play: bool = False):
        self.out_dir = out_dir
        self.play = play
        os.makedirs(out_dir, exist_ok=True)
        self._idx = 0

    def synth(self, speaker: str, text: str, round_no: int):
        voice = _VOICES[(int(speaker.lstrip("P")) - 1) % len(_VOICES)]
        path = os.path.join(self.out_dir, f"r{round_no}_{speaker}_{self._idx}.mp3")
        self._idx += 1
        try:
            resp = get_client().audio.speech.create(
                model="tts-1", voice=voice, input=text)
            resp.stream_to_file(path)
            print(f"    [TTS] {speaker} 发言已合成语音（音色 {voice}）→ {path}")
            if self.play:
                # macOS 自带 afplay；其它平台请自行改播放器
                subprocess.run(["afplay", path], check=False)
        except Exception as e:
            print(f"    [TTS] 合成失败（不影响游戏进行）：{e}")
