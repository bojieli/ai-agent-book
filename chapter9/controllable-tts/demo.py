"""
实验 9-5 演示：控制标记驱动的可控 TTS
======================================

演示两件事：
  1) 三种配置对比（书中要求）：同一段带控制标记的文本，分别用
     A. 无控制标记（流畅但机械）
     B. 单一参考语音（自然但情感单调）
     C. 多参考语音库（按控制标记切换情感/语速/停顿，接近真人客服）
  2) 同一句文本、不同控制标记 -> 合成出多个不同风格的音频。

运行：python demo.py
输出：output/*.mp3
"""

import argparse
import os
import re
import subprocess

from dotenv import load_dotenv

from markup import parse, format_marker_reference
from tts import synthesize_segments, PREFERRED_MODEL
from voice_library import VOICE_LIBRARY, BASE_VOICE, EMOTIONS, SPEEDS, STYLES

load_dotenv()

OUT_DIR = os.path.join(os.path.dirname(__file__), "output")
TMP_DIR = os.path.join(OUT_DIR, ".tmp")

# 书中给出的 LLM 输出示例（带控制标记）
DEMO_TEXT = ("[EMO:happy][SPEED:fast]太好了！您的订单已确认。"
             "[THINKING]嗯，让我查一下发货时间..."
             "[EMO:neutral][SPEED:normal]预计明天下午送达。")

# 同一句文本 + 不同控制标记 -> 不同风格
STYLE_VARIANTS = {
    "variant_happy_fast":  "[情感=高兴][语速=快]您的订单已确认，预计明天下午送达。",
    "variant_frustrated":  "[情感=沮丧][语速=慢]您的订单已确认，预计明天下午送达。",
    "variant_thinking":    "[THINKING]您的订单已确认，[PAUSE]预计明天下午送达。",
    "variant_casual_laugh": "[情感=高兴][风格=轻松]您的订单已确认<laugh>，预计明天下午送达。",
    "variant_emphasis":    "您的订单<emphasis>已确认</emphasis>，预计<emphasis>明天下午</emphasis>送达。",
}


def strip_markers(text: str) -> str:
    """去掉所有控制标记，得到纯文本（用于「无控制标记」基线）。"""
    return re.sub(r"\[[^\]]*\]|<[^>]+>", "", text).strip()


def ffprobe(path: str) -> str:
    """打印 mp3 的时长/格式/码率，证明音频真实生成。"""
    out = subprocess.run(
        ["ffprobe", "-v", "error", "-show_entries",
         "format=duration,format_name,bit_rate", "-of",
         "default=noprint_wrappers=1:nokey=0", path],
        capture_output=True, text=True,
    ).stdout.strip().replace("\n", "  ")
    size = os.path.getsize(path)
    return f"{out}  size={size}B"


def render(name: str, segments, print_info=True):
    """合成一个音频文件并打印其合成信息 + ffprobe。"""
    out_path = os.path.join(OUT_DIR, f"{name}.mp3")
    info = synthesize_segments(segments, out_path, os.path.join(TMP_DIR, name))
    if print_info:
        for seg in info:
            if seg["type"] == "silence":
                print(f"    · [静音 {seg['ms']}ms]")
            else:
                emph = " +强调" if "强调" in seg.get("instructions", "") else ""
                print(f"    · [{seg['profile']:26s}{emph}] {seg['model']:16s} "
                      f"voice={seg['voice']} text='{seg['text']}'")
    print(f"  => {os.path.relpath(out_path)}  |  {ffprobe(out_path)}")
    return out_path


def print_voice_library():
    """离线打印完整参考语音库（无需 API key）。"""
    print(f"参考语音库共 {len(VOICE_LIBRARY)} 条 = 情绪 {len(EMOTIONS)} × 语速 "
          f"{len(SPEEDS)} × 风格 {len(STYLES)}；全库固定 base voice = {BASE_VOICE}"
          f"（模拟 Fish Audio 的音色一致），仅 instructions 不同。\n")
    print(f"{'档案 (情绪_语速_风格)':<28} {'base voice':<11} instructions")
    print("-" * 100)
    for key, v in VOICE_LIBRARY.items():
        print(f"{key:<28} {v['base_voice']:<11} {v['instructions']}")


def print_marker_mapping(text: str):
    """离线打印控制标记映射表 + 对给定文本的解析过程（无需 API key）。"""
    print("控制标记 -> 动作 静态映射表：\n")
    print(format_marker_reference())
    print("\n" + "=" * 72)
    print("对示例文本的实时解析（标记 -> 参考语音 / 静音）：")
    print("文本:", text)
    print("=" * 72)
    trace = []
    segments = parse(text, trace=trace)
    print("-- 解析过程 --")
    for line in trace:
        print(line)
    print("-- 解析后的片段序列 --")
    for i, seg in enumerate(segments):
        if seg["type"] == "silence":
            print(f"  {i:02d}. [静音 {seg['ms']}ms]")
        else:
            profile = f"{seg['emotion']}_{seg['speed']}_{seg['style']}"
            emph = " +强调" if seg.get("emphasis") else ""
            print(f"  {i:02d}. [语音 {profile}{emph}] '{seg['text']}'")


def build_marked_text(text: str, emotion, speed, style) -> str:
    """把 --emotion/--speed/--style 拼成状态标记前缀加到 text 前（text 自带标记时叠加）。"""
    prefix = ""
    if emotion:
        prefix += f"[EMO:{emotion}]"
    if speed:
        prefix += f"[SPEED:{speed}]"
    if style:
        prefix += f"[STYLE:{style}]"
    return prefix + text


def parse_args():
    p = argparse.ArgumentParser(
        description="实验 9-5：控制标记驱动的可控 TTS。默认（无参数）对比"
                    "「无标记 / 单一参考语音 / 多参考语音库」三种配置，并合成多个"
                    "风格变体（输出 output/*.mp3）。也可只合成单条自定义文本，或"
                    "离线查看参考语音库 / 控制标记映射（无需 API key）。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="示例：\n"
               "  python demo.py                       # 跑完整对比 + 风格变体（需 API）\n"
               "  python demo.py --quick               # 只跑三种配置对比\n"
               "  python demo.py --list-voices         # 离线：打印 24 条参考语音库\n"
               "  python demo.py --dump-mapping        # 离线：打印控制标记映射表\n"
               "  python demo.py --text '[情感=高兴][语速=快]您的订单已确认。' -o out.mp3\n"
               "  python demo.py --text '您的订单已确认。' --emotion thinking --speed slow",
    )
    p.add_argument(
        "--text", metavar="文本",
        help="只合成这一段文本（可内嵌控制标记，如 [情感=高兴][THINKING]…）。"
             "不指定则跑默认的三种配置对比 + 风格变体。",
    )
    p.add_argument(
        "--emotion", choices=list(EMOTIONS.keys()),
        help="为 --text 指定情绪参考语音（等价于在文本前加 [EMO:x]）。",
    )
    p.add_argument(
        "--speed", choices=list(SPEEDS.keys()),
        help="为 --text 指定语速（等价于在文本前加 [SPEED:x]）。",
    )
    p.add_argument(
        "--style", choices=list(STYLES.keys()),
        help="为 --text 指定口吻风格（等价于在文本前加 [STYLE:x]）。",
    )
    p.add_argument(
        "-o", "--output", metavar="路径",
        help="--text 模式的输出 mp3 路径（默认 output/custom.mp3）。",
    )
    p.add_argument(
        "--list-voices", action="store_true",
        help="离线打印完整参考语音库（24 条档案及其 instructions），无需 API key。",
    )
    p.add_argument(
        "--dump-mapping", action="store_true",
        help="离线打印控制标记 -> 动作映射表，并对示例文本演示解析过程，无需 API key。",
    )
    p.add_argument(
        "--quick", action="store_true",
        help="仅跑三种配置对比（A/B/C），跳过 5 个风格变体，减少 TTS 调用与耗时。",
    )
    return p.parse_args()


def main():
    args = parse_args()

    # ---- 离线路径（无需 API key）：查看参考语音库 / 控制标记映射 ----
    if args.list_voices:
        print_voice_library()
        return
    if args.dump_mapping:
        print_marker_mapping(args.text or DEMO_TEXT)
        return

    if not os.getenv("OPENAI_API_KEY"):
        raise SystemExit("请先设置 OPENAI_API_KEY（见 env.example）；"
                         "或用 --list-voices / --dump-mapping 离线查看语音库与标记映射。")
    os.makedirs(OUT_DIR, exist_ok=True)

    # ---- 单条自定义文本合成 ----
    if args.text or args.emotion or args.speed or args.style:
        text = build_marked_text(args.text or "", args.emotion, args.speed, args.style)
        if not text.strip():
            raise SystemExit("请用 --text 提供要合成的文本。")
        out_path = args.output or os.path.join(OUT_DIR, "custom.mp3")
        print(f"首选模型: {PREFERRED_MODEL}（不可用时自动兜底 tts-1）\n")
        print("文本:", text)
        trace = []
        segs = parse(text, trace=trace)
        print("-- 控制标记解析过程 --")
        for line in trace:
            print(line)
        print("-- 合成片段 --")
        name = os.path.splitext(os.path.basename(out_path))[0]
        render(name, segs)
        if os.path.abspath(os.path.join(OUT_DIR, f"{name}.mp3")) != os.path.abspath(out_path):
            os.replace(os.path.join(OUT_DIR, f"{name}.mp3"), out_path)
            print(f"  => 已写出 {out_path}")
        return

    print(f"首选模型: {PREFERRED_MODEL}（不可用时自动兜底 tts-1）"
          f"{'  [--quick 模式：跳过风格变体]' if args.quick else ''}\n")

    # ================= 三种配置对比 =================
    print("=" * 72)
    print("对比实验：同一段带控制标记的文本，三种配置")
    print("原始文本:", DEMO_TEXT)
    print("=" * 72)

    # ---- 配置 A：无控制标记（基线，流畅但机械）----
    print("\n[A] 无控制标记（strip 掉所有标记，单次默认合成）")
    plain = strip_markers(DEMO_TEXT)
    print("    纯文本:", plain)
    seg_a = parse(plain)  # 无标记 -> 单个中性片段
    render("A_no_markers", seg_a)

    # ---- 配置 B：单一参考语音（自然但情感单调）----
    print("\n[B] 单一参考语音（去标记，全程用同一条中性/正常/正式参考语音）")
    seg_b = [dict(type="speech", text=plain, emotion="neutral",
                  speed="normal", style="formal", emphasis=False)]
    render("B_single_voice", seg_b)

    # ---- 配置 C：多参考语音库（按控制标记切换）----
    print("\n[C] 多参考语音库（解析控制标记 -> 逐段切换参考语音 + 停顿）")
    trace = []
    seg_c = parse(DEMO_TEXT, trace=trace)
    print("    -- 控制标记解析过程 --")
    for line in trace:
        print(line)
    print("    -- 合成片段 --")
    render("C_voice_library", seg_c)

    # ================= 同文本 / 不同控制标记 =================
    if not args.quick:
        print("\n" + "=" * 72)
        print("同一句文本 + 不同控制标记 -> 不同风格音频")
        print("=" * 72)
        for name, text in STYLE_VARIANTS.items():
            print(f"\n[{name}] {text}")
            trace = []
            segs = parse(text, trace=trace)
            for line in trace:
                print(line)
            render(name, segs)

    # ================= 汇总 =================
    print("\n" + "=" * 72)
    print("全部输出文件（ffprobe 时长对比）")
    print("=" * 72)
    for f in sorted(os.listdir(OUT_DIR)):
        if f.endswith(".mp3"):
            p = os.path.join(OUT_DIR, f)
            print(f"  {f:26s} {ffprobe(p)}")


if __name__ == "__main__":
    main()
