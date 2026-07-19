"""
ffmpeg / ffprobe 薄封装：所有对外部进程的调用都集中在这里，统一做错误检查。

设计要点：
  - run() 捕获非零退出码并抛出带 stderr 的清晰异常（而非让 traceback 泄漏）；
  - 提供 probe_duration / probe_streams，供 Reviewer 与验证环节读取成片信息；
  - extract_frame 把某一时间点抽成一张 PNG（缩放到 512 宽以节省 Vision token）。
"""
import json
import os
import shutil
import subprocess

# macOS 自带字体；换平台时改这里即可（Linux 常见 DejaVuSans.ttf）。
FONT_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
    "/Library/Fonts/Arial.ttf",
]


def find_font() -> str:
    for p in FONT_CANDIDATES:
        if os.path.exists(p):
            return p
    return ""  # drawtext 会退化为默认字体


def ensure_ffmpeg():
    """启动前自检：ffmpeg / ffprobe 是否可用，给出清晰中文报错。"""
    for tool in ("ffmpeg", "ffprobe"):
        if shutil.which(tool) is None:
            raise RuntimeError(
                f"未找到 {tool}，本项目用 ffmpeg 完成实际剪辑。\n"
                f"  macOS: brew install ffmpeg\n"
                f"  Ubuntu: sudo apt install ffmpeg"
            )


def run(cmd, desc="ffmpeg 命令"):
    """执行命令，失败时抛出带 stderr 尾部的异常。"""
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        tail = "\n".join(proc.stderr.strip().splitlines()[-8:])
        raise RuntimeError(f"{desc} 执行失败（exit={proc.returncode}）：\n{tail}")
    return proc


def probe_duration(path: str) -> float:
    """返回视频时长（秒）。"""
    proc = run(
        ["ffprobe", "-v", "error", "-show_entries", "format=duration",
         "-of", "default=noprint_wrappers=1:nokey=1", path],
        desc="ffprobe 读取时长",
    )
    return float(proc.stdout.strip())


def probe_streams(path: str) -> dict:
    """返回 ffprobe 的 JSON（format + streams），用于打印成片信息。"""
    proc = run(
        ["ffprobe", "-v", "error", "-show_format", "-show_streams",
         "-of", "json", path],
        desc="ffprobe 读取流信息",
    )
    return json.loads(proc.stdout)


def format_probe(path: str) -> str:
    """把成片信息格式化成一行行的人类可读文本（用于验证输出）。"""
    info = probe_streams(path)
    fmt = info.get("format", {})
    lines = [
        f"  文件: {os.path.basename(path)}",
        f"  时长: {float(fmt.get('duration', 0)):.2f}s",
        f"  容器: {fmt.get('format_name', '?')}",
        f"  大小: {int(fmt.get('size', 0)) / 1024:.1f} KB",
    ]
    for s in info.get("streams", []):
        if s.get("codec_type") == "video":
            lines.append(
                f"  视频流: {s.get('codec_name')} {s.get('width')}x{s.get('height')} "
                f"@ {s.get('r_frame_rate')} fps"
            )
        elif s.get("codec_type") == "audio":
            lines.append(
                f"  音频流: {s.get('codec_name')} {s.get('sample_rate')}Hz "
                f"{s.get('channels')}ch"
            )
    return "\n".join(lines)


def extract_frame(video: str, t: float, out_png: str, width: int = 512):
    """抽取 t 秒处的一帧，缩放到 width 宽存为 PNG。"""
    run(
        ["ffmpeg", "-y", "-ss", f"{t:.3f}", "-i", video,
         "-frames:v", "1", "-vf", f"scale={width}:-1", out_png],
        desc=f"抽帧 t={t:.1f}s",
    )
    return out_png
