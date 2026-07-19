"""
实验 10-6 演示入口：同时从多个网站搜集信息的 Agent
=================================================

一条命令即可运行：

    python demo.py

演示内容（对应书中强调的机制）：
  (a) 消息总线的发布/订阅：日志里可见带信封的消息流（BUS 前缀）；
  (b) N 个子 Agent 并行执行，主协调器实时刷新任务状态表；
  (c) 某子 Agent 命中后触发级联终止，其余 Agent 收到 terminate 并优雅退出（ack）；
  (d) 多个子 Agent 几乎同时命中时，只结算一次、只广播一轮终止（幂等 + 加锁）；
  (e) （--compare）并行 vs 串行的墙钟耗时实测对比，验证并行化的性能收益。

默认使用离线的关键词判断，保证结果可复现；
若配置了 OPENAI_API_KEY 且未设 USE_LLM=0，子 Agent 会改用真实 LLM 做判断。

命令行参数详见 `python demo.py --help`；不传任何参数即为原有默认行为
（10 个子 Agent、内置问题、离线关键词判断、详细 BUS 日志）。
"""

from __future__ import annotations

import argparse
import asyncio
import json
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:  # noqa: BLE001 —— 没装 python-dotenv 也能跑
    pass

from agents import Coordinator, WorkerAgent, run_sequential
from llm import llm_available
from message_bus import MessageBus
from sources import DEMO_SOURCES, QUESTION, build_sources


def _parse_args() -> argparse.Namespace:
    """解析命令行参数；不传任何参数时行为与之前完全一致（10 Agent、离线、详细日志）。"""
    parser = argparse.ArgumentParser(
        prog="demo.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "实验 10-6：多个同构子 Agent 并行搜索 + 中心协调的演示。\n"
            "展示消息总线发布/订阅、并行派发、实时状态监控、级联终止与竞态处理；\n"
            "默认离线关键词判断（结果可复现），不传参数即为原有默认行为。"
        ),
        epilog=(
            "示例：\n"
            "  python demo.py                     # 默认：10 个 Agent、内置问题、离线可复现\n"
            "  python demo.py --agents 6          # 改为 6 个并行 Agent\n"
            "  python demo.py --compare           # 额外实测并行 vs 串行的墙钟耗时\n"
            "  python demo.py --output result.json  # 把结论写入 JSON 文件\n"
            "  python demo.py --use-llm --model gpt-5.6-luna  # 用真实 LLM 判断（需配 key）"
        ),
    )
    parser.add_argument(
        "-q",
        "--query",
        default=QUESTION,
        metavar="问题",
        help="研究问题（默认使用内置问题）。注意：离线关键词判断是针对内置来源调校的，"
        "自定义问题通常应搭配 --use-llm 的真实 LLM 判断才有意义。",
    )
    parser.add_argument(
        "-n",
        "--agents",
        type=int,
        default=len(DEMO_SOURCES),
        metavar="N",
        help=f"并行子 Agent 的数量（默认 {len(DEMO_SOURCES)}，对应书中约 10 个并行 Agent）。"
        "N>=2 时始终包含两个含答案的源以稳定演示竞态与级联终止。",
    )
    parser.add_argument(
        "--model",
        default=None,
        metavar="MODEL",
        help="LLM 模型名（等价于设置环境变量 OPENAI_MODEL；仅在 --use-llm 且配置了 "
        "OPENAI_API_KEY 或 OPENROUTER_API_KEY 时生效）。默认沿用环境变量或 gpt-5.6-luna。",
    )
    parser.add_argument(
        "-o",
        "--output",
        default=None,
        metavar="PATH",
        help="把最终结论（含并行/串行耗时、winner、竞态统计）以 JSON 写入该路径。默认不写文件。",
    )
    parser.add_argument(
        "--compare",
        action="store_true",
        help="并行运行结束后，再实测一遍串行基线并打印墙钟耗时对比（验证并行化收益）。默认不运行串行基线。",
    )
    parser.add_argument(
        "--use-llm",
        action="store_true",
        help="强制启用真实 LLM 判断（等价于环境变量 USE_LLM=1；仍需配置 "
        "OPENAI_API_KEY 才会真正生效，否则自动回退离线关键词判断）。默认不启用。",
    )
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="减少消息总线的逐条 BUS 日志打印（任务状态表/结论/自检不受影响）。默认打印全部日志。",
    )
    return parser.parse_args()


async def main(args: argparse.Namespace):
    if args.agents < 1:
        raise SystemExit("错误：--agents 至少为 1")

    if args.use_llm:
        # 仅设置意图开关；是否真正调用 LLM 仍取决于 llm.llm_available()
        # （还需配置 OPENAI_API_KEY），未配置时会自动回退离线关键词判断。
        os.environ["USE_LLM"] = "1"
    if args.model:
        os.environ["OPENAI_MODEL"] = args.model

    sources = build_sources(args.agents)

    print("=" * 78)
    print("实验 10-6 · 同时从多个网站搜集信息的 Agent（并行搜索 + 中心协调）")
    print("=" * 78)
    print(f"任务问题：{args.query}")
    print(f"并行来源数：{len(sources)} 个模拟'网站'（子 Agent 数 = 来源数）")
    answer_srcs = [s.name for s in sources if s.holds_answer]
    print(f"含答案的源：{answer_srcs}（其中前两个延迟相同，用于演示竞态）")
    print("-" * 78)

    bus = MessageBus(verbose=not args.quiet)
    coordinator = Coordinator(bus, args.query)

    # 并行装配 N 个同构子 Agent，每个绑定一个来源
    for i, src in enumerate(sources):
        w = WorkerAgent(f"worker-{i:02d}", src, bus, args.query)
        coordinator.add_worker(w)

    result = await coordinator.run()

    print("=" * 78)
    print("演示结论（自动校验）")
    print("=" * 78)
    total_msgs = len(bus.history)
    print(f"1) 消息总线共传递 {total_msgs} 条带信封消息（发布/订阅正常工作）。")
    print(f"2) {len(coordinator.workers)} 个子 Agent 并行执行，状态表全程实时刷新。")
    print(f"3) 首个命中并结算的 Worker：{result['winner']}")
    print(f"   答案：{result['answer']}")
    print(f"   收到 terminate 并 ack 的 Worker：{result['acks']}")
    print(f"4) terminate 广播轮数：{result['terminate_broadcasts']}（应为 1，证明只广播一轮）")
    print(f"   迟到/并发的重复命中被忽略：{result['duplicate_hits'] or '无（本次无并发迟到命中）'}")
    print(f"   是否只结算一次：{result['settled_once']}")
    print(f"5) 并行执行墙钟耗时：{result['parallel_seconds']:.2f}s（含收敛静默期）")

    # —— (e) 并行 vs 串行的墙钟对比：实测，绝不伪造 ——
    seq = None
    if args.compare:
        print("-" * 78)
        print("并行 vs 串行 墙钟对比（--compare，串行基线为实测）")
        print("-" * 78)
        seq = await run_sequential(sources, args.query)
        print(
            f"   串行：命中前逐个抓取了 {seq['fetched']}/{seq['total']} 个源，"
            f"墙钟耗时 {seq['seconds']:.2f}s，winner={seq['winner']}"
        )
        print(f"   并行：墙钟耗时 {result['parallel_seconds']:.2f}s，winner={result['winner']}")
        if seq["seconds"] > 0 and result["parallel_seconds"] > 0:
            speedup = seq["seconds"] / result["parallel_seconds"]
            saved = seq["seconds"] - result["parallel_seconds"]
            print(f"   加速比 ≈ {speedup:.2f}×，节省约 {saved:.2f}s（并行让最快的源立即结束全局搜索）。")

    # —— 结论落盘（可选）——
    if args.output:
        summary = {
            "question": args.query,
            "num_agents": len(coordinator.workers),
            "sources": [s.name for s in sources],
            "judge_mode": "llm" if llm_available() else "keyword_offline",
            "total_bus_messages": total_msgs,
            "winner": result["winner"],
            "answer": result["answer"],
            "duplicate_hits": result["duplicate_hits"],
            "acks": result["acks"],
            "settled_once": result["settled_once"],
            "terminate_broadcasts": result["terminate_broadcasts"],
            "parallel_seconds": round(result["parallel_seconds"], 3),
            "sequential_baseline": (
                {
                    "seconds": round(seq["seconds"], 3),
                    "fetched": seq["fetched"],
                    "winner": seq["winner"],
                }
                if seq
                else None
            ),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        print(f"\n[已写入] 结论 JSON -> {args.output}")

    # —— 断言式自检：仅在离线可复现模式下强断言（LLM 模式命中与否取决于模型）——
    if not llm_available():
        assert result["winner"] is not None, "应至少有一个 Worker 命中"
        assert result["terminate_broadcasts"] == 1, "级联终止只能广播一轮"
        assert result["settled_once"] is True, "必须完成且只结算一次"
        print("\n[自检通过] 单次结算 + 单轮终止广播 + 级联 ack 均符合预期。")
    else:
        print("\n[提示] 当前为真实 LLM 判断模式，是否命中取决于模型，不做强断言。")


if __name__ == "__main__":
    asyncio.run(main(_parse_args()))
