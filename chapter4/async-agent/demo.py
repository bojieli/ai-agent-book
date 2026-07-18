"""实验 4-5 命令行入口：带并行执行、打断/取消与状态管理的异步 Agent。

本脚本提供两类演示，用子命令区分：

  【离线演示】不需要任何 API key，直接测量异步运行时的底层行为——
      python demo.py parallel     并行 vs 串行工具调用的墙钟时间对比（打印加速比）
      python demo.py interrupt    长任务运行中被打断/取消，随后系统恢复
      python demo.py state        Agent 状态检查点持久化 + 跨会话恢复并校验
      python demo.py offline       依次运行上面全部三个离线演示（默认行为）

  【LLM 场景】需要 OPENAI_API_KEY（或 MOONSHOT/ARK），由真实模型做决策——
      python demo.py scenarios              依次运行书中四个验证场景
      python demo.py scenarios --scenario 1  只跑场景 1（异步执行 + 即时提问）
      python demo.py scenarios --scenario 3  只跑场景 3（打断机制）

不带任何子命令时运行【离线演示】，因此开箱即用、无需联网。
为兼容旧用法，`python demo.py --scenario N` 等价于 `scenarios --scenario N`。
"""

from __future__ import annotations

import argparse
import asyncio
import os
import sys
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from async_demos import OFFLINE_DEMOS, banner
from runtime import AgentRuntime

# openai 仅在运行 LLM 场景时才惰性导入；离线演示不碰它，保证无 key/无 openai 也能跑。


def make_client():
    """按 LLM_PROVIDER 选择可用的模型服务（默认 openai）。"""
    from openai import AsyncOpenAI  # 惰性导入：离线演示无需安装 openai
    provider = os.getenv("LLM_PROVIDER", "openai").lower()
    if provider == "moonshot":
        key = os.environ["MOONSHOT_API_KEY"]
        model = os.getenv("LLM_MODEL", "moonshot-v1-8k")
        return AsyncOpenAI(api_key=key, base_url="https://api.moonshot.cn/v1"), model
    if provider == "ark":
        key = os.environ["ARK_API_KEY"]
        model = os.getenv("LLM_MODEL")  # ARK 需要填 endpoint id
        if not model:
            raise SystemExit("使用 ARK 时请设置 LLM_MODEL 为你的推理接入点 ID")
        return AsyncOpenAI(api_key=key, base_url="https://ark.cn-beijing.volces.com/api/v3"), model
    key = os.getenv("OPENAI_API_KEY")
    if not key:
        raise SystemExit("未找到 OPENAI_API_KEY，请配置后重试（或设置 LLM_PROVIDER=moonshot/ark）。")
    model = os.getenv("LLM_MODEL", "gpt-4o-mini")
    base = os.getenv("OPENAI_BASE_URL")
    return AsyncOpenAI(api_key=key, base_url=base) if base else AsyncOpenAI(api_key=key), model


async def run_runtime(rt: AgentRuntime):
    """在后台跑事件循环。"""
    return asyncio.create_task(rt.serve())


# ------------------------------- 四个场景 -------------------------------

async def scenario_1(client, model):
    banner("场景 1｜异步工具执行：长任务运行期间即时回应插入的提问")
    rt = AgentRuntime(client, model)
    serve = await run_runtime(rt)

    # 用户下达一个耗时的日志分析任务
    await rt.submit_user_message(
        "请运行终端命令 `python analyze_logs.py`（这是耗时的日志分析），完成后给我分析结论。",
        urgency="immediate")
    await asyncio.sleep(2.2)  # 任务已在后台跑

    # 期间用户插入一个即时问题
    await rt.submit_user_message("现在几点了？")  # 带问号 -> 立即回应

    await rt.wait_until_idle()
    await rt.stop(); await serve


async def scenario_2(client, model):
    banner("场景 2｜事件队列与批量处理：非紧急指令累积，任务完成时一次性处理")
    rt = AgentRuntime(client, model)
    serve = await run_runtime(rt)

    await rt.submit_user_message(
        "请运行终端命令 `python analyze_logs.py`（耗时日志分析），完成后把分析结论告诉我。",
        urgency="immediate")
    await asyncio.sleep(1.5)

    # 连续发两条补充性指令（无问号 -> 非紧急，进入排队缓冲）
    await rt.submit_user_message("记得最后用日语回复")
    await asyncio.sleep(0.4)
    await rt.submit_user_message("把结果整理成一个网页(HTML)")

    await rt.wait_until_idle()
    await rt.stop(); await serve


async def scenario_3(client, model):
    banner("场景 3｜打断机制：用户'取消'立即终止执行流并取消异步工具")
    rt = AgentRuntime(client, model)
    serve = await run_runtime(rt)

    await rt.submit_user_message(
        "请运行终端命令 `python analyze_logs.py`（耗时日志分析），完成后给我结论。",
        urgency="immediate")
    await asyncio.sleep(4.0)  # 等后台任务确实跑起来（跑到一半左右）

    await rt.submit_user_message("取消")  # 打断关键词 -> 立即取消

    await rt.wait_until_idle(stable=1.0)
    await rt.stop(); await serve


async def scenario_4(client, model):
    banner("场景 4｜并行工具的取消与状态查询：三脚本竞速 + 按 50% 阈值取消 + 整合报告")
    rt = AgentRuntime(client, model)
    serve = await run_runtime(rt)

    await rt.submit_user_message(
        "同时运行这三个分析脚本：`python analyze_fast.py`、`python analyze_mid.py`、`python analyze_slow.py`。"
        "哪个脚本先完成，你就查询另外两个脚本的进度；如果某个脚本进度还没超过 50%，就取消它；"
        "其余脚本完成后，把所有已完成脚本的结果整合成一份报告给我。",
        urgency="immediate")

    await rt.wait_until_idle(stable=1.5, timeout=60)
    await rt.stop(); await serve


SCENARIOS = {1: scenario_1, 2: scenario_2, 3: scenario_3, 4: scenario_4}


# ------------------------------- 子命令实现 -------------------------------

async def run_offline(names: list[str]) -> None:
    """运行离线演示（无需 API key）。"""
    for name in names:
        await OFFLINE_DEMOS[name]()


async def run_scenarios(which: int | None) -> None:
    """运行 LLM 驱动的验证场景（需要 API key）。"""
    client, model = make_client()
    print(f"使用模型：{model}")
    todo = [which] if which else [1, 2, 3, 4]
    for i in todo:
        await SCENARIOS[i](client, model)
        await asyncio.sleep(0.5)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="实验 4-5：带并行执行、打断/取消与状态管理的异步 Agent 演示。",
        epilog=(
            "示例：\n"
            "  python demo.py                     # 默认：依次运行三个离线演示（无需 API key）\n"
            "  python demo.py parallel            # 并行 vs 串行的墙钟时间对比（打印加速比）\n"
            "  python demo.py interrupt           # 长任务运行中被打断/取消，随后恢复\n"
            "  python demo.py state               # 状态检查点持久化 + 跨会话恢复并校验\n"
            "  python demo.py scenarios --scenario 3   # LLM 场景 3：打断机制（需 API key）\n"
            "\n离线演示不联网、不需要任何 key；scenarios 子命令需要 OPENAI_API_KEY（或 MOONSHOT/ARK）。"
        ),
    )
    sub = parser.add_subparsers(dest="command", metavar="<子命令>")

    sub.add_parser("parallel", help="并行 vs 串行工具调用的墙钟时间对比（离线，无需 key）")
    sub.add_parser("interrupt", help="长任务运行中被打断/取消，随后系统恢复（离线，无需 key）")
    sub.add_parser("state", help="Agent 状态检查点持久化与跨会话恢复（离线，无需 key）")
    sub.add_parser("offline", help="依次运行上面三个离线演示（默认行为）")

    ps = sub.add_parser("scenarios", help="书中四个 LLM 验证场景（需要 API key）")
    ps.add_argument("--scenario", type=int, choices=[1, 2, 3, 4],
                    help="只运行指定场景（1 异步执行 / 2 批量处理 / 3 打断 / 4 并行取消）；不填则全部")
    return parser


async def main() -> None:
    # 兼容旧用法：`python demo.py --scenario N` 等价于 `scenarios --scenario N`
    argv = sys.argv[1:]
    if argv and argv[0].startswith("-") and argv[0] not in ("-h", "--help"):
        argv = ["scenarios"] + argv

    args = build_parser().parse_args(argv)
    cmd = args.command or "offline"

    if cmd == "scenarios":
        await run_scenarios(args.scenario)
    elif cmd == "offline":
        await run_offline(["parallel", "interrupt", "state"])
    else:  # parallel / interrupt / state
        await run_offline([cmd])

    print("\n演示结束。")


if __name__ == "__main__":
    asyncio.run(main())
