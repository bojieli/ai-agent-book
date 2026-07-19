"""
参考语音库（Reference Voice Library）
=====================================

书中实验 9-5 使用 Fish Audio 的声音克隆：为同一个虚拟人准备 24 条不同
情绪 / 语速 / 风格的参考语音（情绪 4 × 语速 3 × 风格 2），执行层根据控制标记
选择最匹配的参考语音，Fish Audio 保证不同参考语音之间「音色一致」，
只是韵律和情感有所变化。

由于 Fish Audio 无可用 key，本项目用 OpenAI TTS 演示同一套思路：
  - 「音色一致」  -> 全库固定使用同一个 base voice（如 alloy），保证音色不变；
  - 「韵律/情感变化」-> 每条参考语音对应一段不同的 instructions（风格提示词），
                       gpt-4o-mini-tts 会据此改变语气、语速、情感。

因此这里的「一条参考语音」= 一个 (情绪 × 语速 × 风格) 组合对应的
(base_voice + instructions[+speed_factor]) 档案。整个库由维度笛卡尔积生成。
"""

# ---------------------------------------------------------------------------
# 三个控制维度的取值，以及每个取值对应的中文 instructions 片段
# ---------------------------------------------------------------------------

# 情绪维度：控制标记 [EMO:x] / [情感=x]
# 与书中实验 9-5 列出的四种情绪一致：中性 / 高兴 / 沮丧 / 思考
EMOTIONS = {
    "neutral":    "语气平稳、中性、不带明显情绪",
    "happy":      "语气欢快、上扬，带一点笑意",
    "frustrated": "语气低沉、略显疲惫和无奈",
    "thinking":   "语气迟疑、若有所思，带轻微的犹豫和停顿感",
}

# 语速维度：控制标记 [SPEED:x] / [语速=x]
SPEEDS = {
    "normal": ("语速正常",       1.0),
    "fast":   ("语速偏快、干脆利落", 1.25),
    "slow":   ("语速偏慢、从容",   0.80),
}

# 风格维度：控制标记 [STYLE:x] / [风格=x]
STYLES = {
    "formal": "用正式、专业的客服口吻",
    "casual": "用轻松、亲切、口语化的口吻",
}

# 全库统一的 base voice —— 用它来模拟 Fish Audio 的「音色一致」
BASE_VOICE = "alloy"

# 强调（[强调].../<emphasis>...）追加的 instructions 片段
EMPHASIS_HINT = "并对句中的关键信息加重语气、突出强调"


def build_instructions(emotion: str, speed: str, style: str, emphasis: bool = False) -> str:
    """把三个维度拼成一段 gpt-4o-mini-tts 的 instructions（风格提示词）。"""
    emo = EMOTIONS.get(emotion, EMOTIONS["neutral"])
    spd = SPEEDS.get(speed, SPEEDS["normal"])[0]
    sty = STYLES.get(style, STYLES["formal"])
    text = f"请以中文朗读。{sty}，{emo}，{spd}。"
    if emphasis:
        text += EMPHASIS_HINT + "。"
    return text


def speed_factor(speed: str) -> float:
    """语速倍率，仅在 tts-1 兜底路径（不支持 instructions）时用作 speed 参数。"""
    return SPEEDS.get(speed, SPEEDS["normal"])[1]


def profile_key(emotion: str, speed: str, style: str) -> str:
    return f"{emotion}_{speed}_{style}"


def build_voice_library() -> dict:
    """生成完整的参考语音库：情绪 × 语速 × 风格 的笛卡尔积。"""
    lib = {}
    for emotion in EMOTIONS:
        for speed in SPEEDS:
            for style in STYLES:
                key = profile_key(emotion, speed, style)
                lib[key] = {
                    "emotion": emotion,
                    "speed": speed,
                    "style": style,
                    "base_voice": BASE_VOICE,
                    "instructions": build_instructions(emotion, speed, style),
                    "speed_factor": speed_factor(speed),
                }
    return lib


VOICE_LIBRARY = build_voice_library()


if __name__ == "__main__":
    print(f"参考语音库共 {len(VOICE_LIBRARY)} 条（情绪 {len(EMOTIONS)} × 语速 "
          f"{len(SPEEDS)} × 风格 {len(STYLES)}），全部固定 base voice = {BASE_VOICE}")
    for k, v in list(VOICE_LIBRARY.items())[:6]:
        print(f"  {k:28s} -> {v['instructions']}")
    print("  ...")
