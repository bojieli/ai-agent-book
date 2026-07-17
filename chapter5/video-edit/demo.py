"""
实验 5-6：基于 API 的智能视频剪辑（两步 Vision 定位 + 提议者-审核者）

一条命令跑通：
  python demo.py                 # 默认需求"把冲浪的部分剪出来"
  python demo.py "把滑雪部分剪出来，并加上字幕 Winter"   # 自定义需求

流程：
  1. 程序化生成含 4 个明显不同场景的测试视频（HIKING/SURFING/SKIING/CYCLING）；
  2. Proposer 解析自然语言需求 → 目标场景 + 特效；
  3. 视频分析子 Agent 两步定位（粗粒度每 10s → 细粒度每 1s）找到精确边界；
  4. Proposer 用 ffmpeg 剪出片段（可含字幕/慢动作）；
  5. Reviewer 检查成片关键帧，给出反馈；不合格则 Proposer 修正边界重剪，迭代。

依赖：ffmpeg/ffprobe（本机剪辑）、OPENAI_API_KEY（gpt-4o 视觉 + 文本）。
"""
import os
import shutil
import sys

from dotenv import load_dotenv

load_dotenv()

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "output")
SOURCE_VIDEO = os.path.join(OUT_DIR, "source.mp4")   # 换真实视频：改这里（见 README）
FINAL_VIDEO = os.path.join(OUT_DIR, "final.mp4")
MAX_ROUNDS = 3  # Reviewer 反馈后最多重剪次数

DEFAULT_REQUEST = "把冲浪的部分剪出来"


def banner(title):
    print("\n" + "=" * 74)
    print(f"  {title}")
    print("=" * 74)


def preflight():
    """启动自检：给出清晰中文报错，而非 traceback。"""
    from ffmpeg_utils import ensure_ffmpeg
    if not os.getenv("OPENAI_API_KEY"):
        print("\n[错误] 未检测到 OPENAI_API_KEY。\n"
              "  请复制 env.example 为 .env 并填入有效的 OpenAI Key，或执行：\n"
              "    export OPENAI_API_KEY=sk-...\n"
              "  本实验用 gpt-4o 做视觉定位与审查，必须提供有效 Key。")
        sys.exit(1)
    try:
        ensure_ffmpeg()
    except RuntimeError as e:
        print(f"\n[错误] {e}")
        sys.exit(1)


def main():
    nl_request = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_REQUEST
    preflight()

    # 延迟导入：确保 preflight 的报错优先于任何 SDK 初始化。
    from agents import (ProposerAgent, ReviewerAgent, VideoAnalyzerAgent,
                        TokenMeter, TEXT_MODEL, VISION_MODEL)
    from ffmpeg_utils import format_probe, probe_duration
    from make_test_video import make as make_test_video, GROUND_TRUTH
    from video_editor import apply_edit

    # 幂等：每次从干净的 output/ 开始。
    if os.path.isdir(OUT_DIR):
        shutil.rmtree(OUT_DIR)
    os.makedirs(OUT_DIR, exist_ok=True)

    banner("步骤 0 | 生成测试视频（4 个明显不同的场景）")
    make_test_video(SOURCE_VIDEO)
    total_dur = probe_duration(SOURCE_VIDEO)
    print(f"已生成 {SOURCE_VIDEO}，时长 {total_dur:.1f}s")
    print(f"场景真值（用于核对定位误差）：{GROUND_TRUTH}")
    print(f"文本模型={TEXT_MODEL}  视觉模型={VISION_MODEL}")

    # 分离的 token 计量：主 Agent（Proposer+Reviewer）vs 子 Agent（截图定位）。
    main_meter = TokenMeter()
    sub_meter = TokenMeter()
    proposer = ProposerAgent(main_meter)
    reviewer = ReviewerAgent(main_meter)
    analyzer = VideoAnalyzerAgent(sub_meter)

    banner("步骤 1 | Proposer 解析自然语言需求")
    print(f"用户需求：{nl_request}")
    intent = proposer.parse_request(nl_request)
    target_query = intent["target_query"]
    effects = intent.get("effects", [])
    print(f"解析结果：目标场景='{target_query}'  特效={effects}")

    banner("步骤 2 | 视频分析子 Agent：两步 Vision 定位")
    start, end, trace = analyzer.locate(
        SOURCE_VIDEO, target_query,
        coarse_interval=10.0, fine_interval=1.0,
        frame_dir=os.path.join(OUT_DIR, "frames"),
    )
    c = trace["coarse"]
    print(f"  [粗粒度] 每 10s 采样 {len(c['timestamps'])} 帧 → Vision 得区间 "
          f"[{c['start']:.0f}, {c['end']:.0f}]s（依据：{c['reason']}）")
    f = trace["fine"]
    print(f"  [细粒度] 窗口 {f['window']} 内每 1s 采样 {f['timestamps_count']} 帧 → "
          f"精确边界 [{f['start']:.1f}, {f['end']:.1f}]s（依据：{f['reason']}）")
    print(f"  >>> 最终定位：起 {start:.1f}s  止 {end:.1f}s")

    # 与真值对比，打印定位误差（验收：误差 ≤ ±3s）。
    key = _match_ground_truth(target_query, GROUND_TRUTH)
    if key:
        gs, ge = GROUND_TRUTH[key]
        print(f"  真值 [{gs}, {ge}]s → 起点误差 {abs(start - gs):.1f}s，"
              f"终点误差 {abs(end - ge):.1f}s（验收要求 ≤ 3s）")

    banner("步骤 3-4 | Proposer 剪辑 + Reviewer 审查（迭代）")
    plan = {"start": start, "end": end, "effects": effects}
    final_path = None
    for rnd in range(1, MAX_ROUNDS + 1):
        print(f"\n--- 第 {rnd} 轮 ---")
        clip = os.path.join(OUT_DIR, f"cut_round{rnd}.mp4")
        apply_edit(SOURCE_VIDEO, plan, clip)
        cdur = probe_duration(clip)
        print(f"  Proposer 剪出片段 [{plan['start']:.1f}, {plan['end']:.1f}]s，"
              f"成片时长 {cdur:.1f}s")

        review = reviewer.review(clip, target_query,
                                 frame_dir=os.path.join(OUT_DIR, "review_frames"))
        print(f"  Reviewer：pass={review['pass']} score={review.get('score')} "
              f"检查帧={['%.1f' % t for t in review['frames_checked']]}")
        print(f"  Reviewer 反馈：{review['feedback']}")

        if review.get("pass"):
            final_path = clip
            print("  ✓ 审核通过。")
            break
        if rnd == MAX_ROUNDS:
            final_path = clip
            print("  达到最大轮数，采用当前成片。")
            break
        # 未通过：Proposer 据反馈修正边界后重剪。
        ns, ne = proposer.revise_bounds(plan["start"], plan["end"],
                                        review["feedback"], total_dur)
        print(f"  Proposer 据反馈修正边界：[{ns:.1f}, {ne:.1f}]s")
        plan["start"], plan["end"] = ns, ne

    shutil.copy(final_path, FINAL_VIDEO)

    banner("步骤 5 | 成片信息（ffprobe）")
    print(format_probe(FINAL_VIDEO))

    banner("Token 统计（子 Agent 隔离截图，主上下文不被污染）")
    print(f"  主 Agent（Proposer+Reviewer）：{main_meter.total()} tokens "
          f"(prompt={main_meter.prompt}, completion={main_meter.completion})")
    print(f"  子 Agent（两步定位截图）    ：{sub_meter.total()} tokens "
          f"(prompt={sub_meter.prompt}, completion={sub_meter.completion})")
    print(f"\n完成：{FINAL_VIDEO}")


def _match_ground_truth(query, gt):
    q = query.lower()
    for key in gt:
        if key in q:
            return key
    # 中文关键词兜底映射。
    zh = {"冲浪": "surfing", "徒步": "hiking", "滑雪": "skiing", "骑": "cycling",
          "hik": "hiking", "surf": "surfing", "ski": "skiing", "cycl": "cycling"}
    for k, v in zh.items():
        if k in q:
            return v
    return None


if __name__ == "__main__":
    main()
