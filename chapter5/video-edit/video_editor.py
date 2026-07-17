"""
视频剪辑执行层。

书中原方案用 Blender Python API（bpy）驱动视频序列编辑器（VSE）完成剪辑；
本机未安装 Blender，故这里用 ffmpeg 完成等价操作，接口签名与 Blender 版保持一致，
方便读者切换（见文件末尾 "Blender 版接口位置" 说明与 README）。

支持的操作：
  - trim      裁剪 [start, end] 片段
  - subtitle  在片段上叠加字幕
  - slowmo    慢动作（放慢到 factor 倍时长）
所有操作最终产出一个标准 mp4（H.264 + AAC）。
"""
import os

from ffmpeg_utils import find_font, run


def _esc(text: str) -> str:
    """转义 drawtext/subtitles 文本中的特殊字符。"""
    return text.replace("\\", "\\\\").replace(":", r"\:").replace("'", r"\'")


def apply_edit(source: str, plan: dict, out_path: str) -> str:
    """
    按剪辑计划 plan 生成成片。

    plan 结构（由 Proposer Agent 产出）:
      {
        "start": float,          # 目标片段起点（秒）
        "end": float,            # 目标片段终点（秒）
        "effects": [             # 可选特效列表
          {"type": "subtitle", "text": "..."},
          {"type": "slowmo", "factor": 2.0}
        ]
      }
    """
    start, end = float(plan["start"]), float(plan["end"])
    if end <= start:
        raise ValueError(f"剪辑区间非法：start={start} >= end={end}")

    effects = plan.get("effects", []) or []
    vf_chain = []          # 视频滤镜链
    af_chain = []          # 音频滤镜链
    font = find_font()

    for eff in effects:
        etype = eff.get("type")
        if etype == "subtitle":
            txt = _esc(eff.get("text", ""))
            opts = [f"text='{txt}'", "fontsize=52", "fontcolor=white",
                    "x=(w-text_w)/2", "y=h-text_h-50",
                    "box=1", "boxcolor=black@0.6", "boxborderw=16"]
            if font:
                opts.insert(0, f"fontfile={font}")
            vf_chain.append("drawtext=" + ":".join(opts))
        elif etype == "slowmo":
            factor = float(eff.get("factor", 2.0))
            vf_chain.append(f"setpts={factor}*PTS")
            # atempo 只支持 0.5~2.0，用 1/factor 放慢音频。
            af_chain.append(f"atempo={max(0.5, min(1.0, 1.0 / factor))}")

    cmd = ["ffmpeg", "-y", "-ss", f"{start:.3f}", "-to", f"{end:.3f}", "-i", source]
    if vf_chain:
        cmd += ["-vf", ",".join(vf_chain)]
    if af_chain:
        cmd += ["-af", ",".join(af_chain)]
    cmd += ["-c:v", "libx264", "-c:a", "aac", "-pix_fmt", "yuv420p", out_path]

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    run(cmd, desc="ffmpeg 剪辑")
    return out_path


# --------------------------------------------------------------------------- #
# Blender 版接口位置（供读者切换）
# --------------------------------------------------------------------------- #
# 若已安装 Blender，可把上面的 apply_edit 换成生成一段 bpy 脚本并用
# `blender --background --python edit.py` 执行。等价骨架如下：
#
#   import bpy
#   scene = bpy.context.scene
#   se = scene.sequence_editor_create()
#   clip = se.sequences.new_movie("clip", source, channel=1, frame_start=1)
#   # 裁剪：设置 frame_offset_start / frame_final_duration（按 fps 换算秒→帧）
#   fps = scene.render.fps
#   clip.frame_offset_start = int(start * fps)
#   clip.frame_final_duration = int((end - start) * fps)
#   # 字幕：se.sequences.new_effect(type='TEXT', ...).text = "..."
#   # 慢动作：new_effect(type='SPEED', ...).speed_factor = 1/factor
#   scene.render.filepath = out_path
#   bpy.ops.render.render(animation=True)
#
# 核心的"两步 Vision 定位 + 提议者-审核者"逻辑与执行层解耦，
# 因此切换到 Blender 只需替换本文件，agents.py / demo.py 无需改动。
