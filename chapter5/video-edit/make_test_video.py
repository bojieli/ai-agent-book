"""
程序化生成一段"含多个明显不同场景"的测试视频（无需任何素材文件）。

每个场景 = 一种纯色背景 + 一个大号运动标题（场景英文名）+ 时间码水印。
标题让 Vision LLM 能仅凭画面就准确判断"这是哪个场景"，从而验证两步定位。
换成真实视频时：把 demo.py 里的 SOURCE_VIDEO 指向你自己的 mp4 即可（见 README）。
"""
import os

from ffmpeg_utils import find_font, run

# 每个场景：(名称, 背景色, 起始秒, 时长秒)。刻意让每段 > 10s，
# 使"每 10s 一张"的粗粒度采样必然命中每个场景。
SCENES = [
    ("HIKING",  "0x1E6B3A", 0,  15),   # 森林绿
    ("SURFING", "0x1565C0", 15, 15),   # 海洋蓝
    ("SKIING",  "0xE0E0E0", 30, 12),   # 雪地白
    ("CYCLING", "0xE65100", 42, 12),   # 落日橙
]
TOTAL = SCENES[-1][2] + SCENES[-1][3]  # 54s
W, H, FPS = 1280, 720, 30


def _drawtext(text, size, y_expr, color="white", box=False):
    font = find_font()
    parts = [f"text='{text}'", f"fontsize={size}", f"fontcolor={color}",
             "x=(w-text_w)/2", f"y={y_expr}"]
    if font:
        parts.insert(0, f"fontfile={font}")
    if box:
        parts += ["box=1", "boxcolor=black@0.4", "boxborderw=20"]
    return "drawtext=" + ":".join(parts)


def make(out_path: str) -> str:
    """生成测试视频，返回路径。幂等：每次覆盖，保证从干净状态开始。"""
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    clip_paths = []
    tmp_dir = os.path.dirname(out_path)

    for i, (name, color, start, dur) in enumerate(SCENES):
        clip = os.path.join(tmp_dir, f"_scene_{i}.mp4")
        # 让标题上下缓慢漂移，制造真实"运动画面"，避免纯静止帧。
        title = _drawtext(name, 140, "(h-text_h)/2 + 60*sin(t)", box=True)
        # 左上角时间码：t 为片段内相对时间，加 start 得到全局时间。
        # drawtext 里表达式含冒号，必须转义为 \: 否则被当成选项分隔符。
        clock = _drawtext(rf"t=%{{eif\:t+{start}\:d}}s", 48,
                          "40", color="yellow")
        vf = f"{title},{clock}"
        run(
            ["ffmpeg", "-y",
             "-f", "lavfi", "-i", f"color=c={color}:s={W}x{H}:d={dur}:r={FPS}",
             "-f", "lavfi", "-i", f"sine=frequency={220 + i * 110}:duration={dur}",
             "-vf", vf, "-pix_fmt", "yuv420p",
             "-c:v", "libx264", "-c:a", "aac", "-shortest", clip],
            desc=f"生成场景 {name}",
        )
        clip_paths.append(clip)

    # 用 concat demuxer 无缝拼接成完整原始素材。
    list_file = os.path.join(tmp_dir, "_concat_list.txt")
    with open(list_file, "w") as f:
        for c in clip_paths:
            f.write(f"file '{os.path.abspath(c)}'\n")
    run(
        ["ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", list_file,
         "-c", "copy", out_path],
        desc="拼接测试视频",
    )

    # 清理中间片段。
    for c in clip_paths:
        os.remove(c)
    os.remove(list_file)
    return out_path


# 供 demo / README 引用：场景真值表，用于验证定位误差。
GROUND_TRUTH = {name.lower(): (start, start + dur) for name, _, start, dur in SCENES}
