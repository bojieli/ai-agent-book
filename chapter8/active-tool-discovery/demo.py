"""
实验 8-4 演示：主动工具发现 vs 检索预筛选 vs 全量注入

对同一组跨领域任务，在 126 个工具的工具库上分别用三种"工具发现"策略运行，
并在一次运行里输出可对比的表格（准确率 / 注入 token / 延迟）：

- full_injection    全量注入：126 个工具 schema 一次性进上下文（对照组，书中控制组）。
- retrieval_prefilter 检索预筛选：按初始查询做**一次性**语义检索，只注入 top-n 候选工具。
- active_discovery  主动发现：少量基础工具 + discover_tools 元工具，执行中按需检索加载。

核心论点（第 8 章）：当工具规模达到上百个时，"把所有工具塞进上下文"在 token 上昂贵、
且对小模型的指令遵循是灾难；主动发现按需加载，token 大幅下降、选择更精准。

用法（详见 --help）：
    python demo.py                         # 默认：全部任务 × 三种策略（需 OPENAI_API_KEY）
    python demo.py --offline               # 离线自检：本地嵌入 + mock 模型，无需任何 key
    python demo.py --tasks finance+news,crypto+news
    python demo.py --strategies full,discovery --tool-set-size 30
    python demo.py --query "查一下英伟达股价再搜点相关新闻" --offline
    python demo.py --offline --output results/offline.json
"""

import argparse
import json
import os
import sys
import time

from tools_library import TASKS, grade, select_tools, ALL_TOOLS


def _to_openrouter_model(model: str) -> str:
    """把常见模型名映射到 OpenRouter 命名空间（用于无 OPENAI_API_KEY 的兜底路径）。"""
    if not model:
        return "openai/gpt-5.6-luna"
    if "/" in model:
        return model
    if model.startswith("gpt-"):
        return "openai/" + model
    if model.startswith("claude-"):
        return "anthropic/claude-opus-4.8"
    return "openai/gpt-5.6-luna"


# 策略注册表：key -> (中文名, 需要 index 吗)
STRATEGIES = {
    "full": ("全量注入", False),
    "prefilter": ("检索预筛选", True),
    "discovery": ("主动发现", True),
}
STRATEGY_ORDER = ["full", "prefilter", "discovery"]


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="demo.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="实验 8-4：主动工具发现 vs 检索预筛选 vs 全量注入。\n"
                    "在 126 个工具的工具库上，对多任务一次性输出『准确率 / 注入 token / 延迟』对比表，\n"
                    "验证第 8 章论点：上百工具场景下，主动按需发现优于把全部工具塞进上下文。",
        epilog="示例：\n"
               "  python demo.py --offline                 # 无需 key 的离线机制自检\n"
               "  python demo.py --strategies full,discovery --tasks finance+news\n"
               "  python demo.py --query '查英伟达股价并搜相关新闻' --offline\n")
    ap.add_argument("--query", metavar="TEXT",
                    help="临时单任务：直接给一句自然语言需求，跳过内置任务集（判分槽位按关键词自动推断）。")
    ap.add_argument("--tasks", metavar="IDS",
                    help="逗号分隔的内置任务 id（见 tools_library.TASKS），缺省跑全部 8 个任务。"
                         "含括号的 id 记得加引号，如 'opinion(诱导)'。")
    ap.add_argument("--strategies", metavar="LIST", default="full,prefilter,discovery",
                    help="逗号分隔的策略，取值 full/prefilter/discovery，缺省三者全跑并对比。")
    ap.add_argument("--tool-set-size", type=int, default=None, metavar="N",
                    help="把工具库截取为 N 个工具（始终保留基础/通用/任务相关工具）。"
                         "缺省用全部 126 个——用小 N 可对比『工具集越大，全量注入越吃亏』。")
    ap.add_argument("--top-k", type=int, default=4, metavar="K",
                    help="主动发现中 discover_tools 每次返回的候选工具数（默认 4）。")
    ap.add_argument("--prefilter-n", type=int, default=10, metavar="N",
                    help="检索预筛选一次性注入的候选工具数（默认 10）。")
    ap.add_argument("--model", default=os.getenv("MODEL", "gpt-5.6-luna"), metavar="NAME",
                    help="对话模型名（默认取环境变量 MODEL 或 gpt-5.6-luna）；离线模式下忽略。")
    ap.add_argument("--embed-model", default=os.getenv("EMBED_MODEL", "text-embedding-3-small"),
                    metavar="NAME", help="嵌入模型名（默认 text-embedding-3-small）；离线模式下忽略。")
    ap.add_argument("--max-steps", type=int, default=10, metavar="N",
                    help="单个任务的 ReAct 最大步数（默认 10）。")
    ap.add_argument("--offline", action="store_true",
                    help="离线机制自检：用本地哈希嵌入 + 脚本化 mock 模型，无需任何 API key。"
                         "token/延迟为真实测量，准确率仅反映启发式路由、不代表真实模型能力。")
    ap.add_argument("--output", metavar="PATH",
                    help="把逐任务、逐策略的结构化结果写入该 JSON 文件。")
    return ap


def _fmt_grade(g):
    tag = "✅ 精确选对" if g["precise"] else ("⚠️ 完成但错选" if g["correct"] else "❌ 出错")
    detail = f"{g['filled_slots']}/{g['total_slots']} 能力槽位命中"
    extra = ""
    if g["missed_slots"]:
        extra += f"｜漏用: {[s[0] for s in g['missed_slots']]}"
    if g["used_generic_substitute"]:
        extra += f"｜错选通用工具: {g['used_generic_substitute']}"
    return f"{tag}（{detail}{extra}）"


def _make_task_from_query(query: str):
    """把临时 --query 包装成带判分槽位的任务（槽位按关键词推断）。"""
    from offline_backend import match_intents
    slots = [[tool] for tool, _ in match_intents(query)]
    return {"id": "adhoc", "prompt": query, "required_slots": slots}


def run_strategy(key, client, model, prompt, index, tools, args):
    """执行一种策略并返回 (result_dict, latency_s)。"""
    from agent import (run_active_discovery, run_full_injection,
                       run_retrieval_prefilter)
    t0 = time.perf_counter()
    if key == "full":
        res = run_full_injection(client, model, prompt, tools=tools, max_steps=args.max_steps)
    elif key == "prefilter":
        res = run_retrieval_prefilter(client, model, prompt, index,
                                      top_n=args.prefilter_n, tools=tools, max_steps=args.max_steps)
    else:
        res = run_active_discovery(client, model, prompt, index,
                                   top_k=args.top_k, tools=tools, max_steps=args.max_steps)
    return res, time.perf_counter() - t0


def main():
    args = build_parser().parse_args()

    strategies = [s.strip() for s in args.strategies.split(",") if s.strip()]
    bad = [s for s in strategies if s not in STRATEGIES]
    if bad:
        print(f"未知策略: {bad}，可选: {list(STRATEGIES)}")
        sys.exit(2)
    strategies.sort(key=STRATEGY_ORDER.index)

    # ---- 任务集 ----
    if args.query:
        tasks = [_make_task_from_query(args.query)]
    else:
        tasks = TASKS
        if args.tasks:
            want = set(args.tasks.split(","))
            tasks = [t for t in TASKS if t["id"] in want]
        if not tasks:
            print(f"没有匹配的任务 id：{args.tasks}")
            sys.exit(2)

    tools = select_tools(args.tool_set_size, tasks)
    need_index = any(STRATEGIES[s][1] for s in strategies)

    # ---- 后端（在线 OpenAI / 离线 mock）----
    if args.offline:
        from offline_backend import LocalEmbedder, MockChatClient
        from discovery import ToolIndex
        client = MockChatClient()
        model = "mock-offline"
        embedder = LocalEmbedder()
        print("=" * 92)
        print("离线机制自检模式：本地哈希嵌入 + 脚本化 mock 模型（无需 API key）。")
        print("  · token / 延迟为真实测量；准确率仅反映启发式路由，不代表真实模型能力。")
        print("  · 观察点：三种策略的 token 差距，以及『检索预筛选一次性匹配』的结构性漏工具。")
        print("=" * 92)
    else:
        try:
            from dotenv import load_dotenv
            from openai import OpenAI
        except ImportError:
            print("缺少 openai / python-dotenv，请先 pip install -r requirements.txt，"
                  "或改用 --offline 离线自检。")
            sys.exit(1)
        load_dotenv()
        from discovery import OpenAIEmbedder, ToolIndex
        if os.getenv("OPENAI_API_KEY"):
            # 直连 OpenAI：chat + embeddings 都走 OpenAI
            client = OpenAI()
            model = args.model
            embedder = OpenAIEmbedder(client, model=args.embed_model)
        elif os.getenv("OPENROUTER_API_KEY"):
            # 统一兜底：OpenRouter 只代理 chat completions，没有 embeddings 接口，
            # 因此对话走 OpenRouter（真实模型），工具检索改用本地哈希嵌入。
            from offline_backend import LocalEmbedder
            client = OpenAI(api_key=os.getenv("OPENROUTER_API_KEY"),
                            base_url="https://openrouter.ai/api/v1")
            model = _to_openrouter_model(args.model)
            embedder = LocalEmbedder()
            print("未检测到 OPENAI_API_KEY，改走 OpenRouter 兜底：")
            print(f"  · 对话模型: {model}（真实调用）")
            print("  · 工具检索: 本地哈希嵌入（OpenRouter 无 embeddings 接口）。")
        else:
            print("请设置 OPENAI_API_KEY 或 OPENROUTER_API_KEY（见 env.example），"
                  "或改用 --offline 离线自检。")
            sys.exit(1)

    index = ToolIndex(embedder, tools=tools) if need_index else None

    print(f"模型: {model}  |  嵌入: {embedder.name}  |  工具库: {len(tools)} 个  "
          f"|  任务数: {len(tasks)}  |  策略: {[STRATEGIES[s][0] for s in strategies]}\n")

    # ---- 逐任务运行 ----
    records = []           # 每条: {task, strategy, result, grade, latency}
    for task in tasks:
        print("=" * 92)
        print(f"任务 [{task['id']}]: {task['prompt']}")
        print("-" * 92)
        for key in strategies:
            res, latency = run_strategy(key, client, model, task["prompt"], index, tools, args)
            g = grade(task, res["called"])
            records.append({"task": task["id"], "strategy": key, "result": res,
                            "grade": g, "latency_s": round(latency, 3)})
            cname = STRATEGIES[key][0]
            print(f"[{cname}] 注入 {res['injected_tokens']:>6} tokens "
                  f"（暴露 {res['num_tools_exposed']} 个工具）  延迟 {latency:5.2f}s")
            if key == "prefilter":
                print(f"           预筛选命中: {res['prefiltered']}")
            if key == "discovery":
                for line in res["trace"]:
                    if line.startswith("[discover_tools]"):
                        print(f"           {line}")
                print(f"           发现并加载: {res['discovered']}")
            print(f"           调用轨迹: {res['called']}")
            print(f"           判定: {_fmt_grade(g)}")
        print()

    _print_summary(tasks, strategies, records)

    if args.output:
        os.makedirs(os.path.dirname(os.path.abspath(args.output)), exist_ok=True)
        payload = {"model": model, "embedder": embedder.name, "tool_set_size": len(tools),
                   "offline": args.offline, "strategies": strategies,
                   "records": records}
        json.dump(payload, open(args.output, "w", encoding="utf-8"),
                  ensure_ascii=False, indent=2)
        print(f"\n结构化结果已写入: {args.output}")


def _print_summary(tasks, strategies, records):
    n = len(tasks)
    print("=" * 92)
    print("汇总对比（『精确选对』= 覆盖全部能力槽位 且 未错选通用兜底工具）")
    print("=" * 92)
    header = f"{'策略':<14}{'精确选对':>10}{'任务完成':>10}{'平均注入token':>16}{'总注入token':>14}{'平均延迟(s)':>12}"
    print(header)
    print("-" * 92)
    for key in strategies:
        rs = [r for r in records if r["strategy"] == key]
        precise = sum(int(r["grade"]["precise"]) for r in rs)
        correct = sum(int(r["grade"]["correct"]) for r in rs)
        tok = [r["result"]["injected_tokens"] for r in rs]
        lat = [r["latency_s"] for r in rs]
        avg_tok = sum(tok) / len(tok) if tok else 0
        avg_lat = sum(lat) / len(lat) if lat else 0
        print(f"{STRATEGIES[key][0]:<12}{f'{precise}/{n}':>10}{f'{correct}/{n}':>10}"
              f"{avg_tok:>16.0f}{sum(tok):>14}{avg_lat:>12.3f}")
    print("-" * 92)
    if "full" in strategies and "discovery" in strategies:
        ft = sum(r["result"]["injected_tokens"] for r in records if r["strategy"] == "full")
        at = sum(r["result"]["injected_tokens"] for r in records if r["strategy"] == "discovery")
        if at:
            print(f"注入 token：全量注入 {ft} vs 主动发现 {at}，平均每任务精简约 {ft/at:.1f} 倍。")


if __name__ == "__main__":
    main()
