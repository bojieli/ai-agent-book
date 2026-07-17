"""实验 4-5 演示脚本：带并行执行与打断能力的异步 Agent。

用法：
    python demo.py                # 依次跑完四个验证场景
    python demo.py --scenario 1   # 只跑场景 1（异步工具执行 + 即时插入提问）
    python demo.py --scenario 2   # 只跑场景 2（非紧急事件批量处理）
    python demo.py --scenario 3   # 只跑场景 3（打断机制）
    python demo.py --scenario 4   # 只跑场景 4（并行工具的取消与状态查询）

依赖真实 LLM 决策：读取 OPENAI_API_KEY（默认 gpt-4o-mini）。
也可通过 LLM_PROVIDER=moonshot / ark 切换到 MOONSHOT_API_KEY / ARK_API_KEY。
"""

from __future__ import annotations

import argparse
import asyncio
import os
import time

try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

from openai import AsyncOpenAI

from runtime import AgentRuntime


def make_client() -> tuple[AsyncOpenAI, str]:
    """按 LLM_PROVIDER 选择可用的模型服务（默认 openai）。"""
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


def banner(title: str) -> None:
    print("\n" + "=" * 78)
    print(f"  {title}")
    print("=" * 78, flush=True)


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


async def main():
    parser = argparse.ArgumentParser(description="实验 4-5 异步 Agent 演示")
    parser.add_argument("--scenario", type=int, choices=[1, 2, 3, 4],
                        help="只运行指定场景；不填则依次运行全部四个场景")
    args = parser.parse_args()

    client, model = make_client()
    print(f"使用模型：{model}")

    if args.scenario:
        await SCENARIOS[args.scenario](client, model)
    else:
        for i in [1, 2, 3, 4]:
            await SCENARIOS[i](client, model)
            await asyncio.sleep(0.5)

    print("\n演示结束。")


if __name__ == "__main__":
    asyncio.run(main())
