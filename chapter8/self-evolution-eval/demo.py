"""
实验 8-6 一键演示：python demo.py

流程：
1) 打印数据集概览与几条"不暗示工具名"的任务示例。
2) 用 strong 参考 Agent 在 2-3 个任务上跑完四层验证（含真实 LLM-as-a-Judge 打分）。
3) 用 weak 参考 Agent 做对照，展示四层的区分度。
4) 复用层对照：strong 第二次相似任务直接检索已注册工具；weak 则重复搜索创建。
5) 最后打印一张"每任务 × 每层"的结果表，横向对比各任务在四层上的得分。

用法：
    python demo.py                       # 默认：strong 跑 3 个任务 + weak 对照 1 个任务
    python demo.py --quick               # 快速演示：strong / weak 各只跑 1 个任务，省时省钱
    python demo.py --tasks task-01,task-07   # 指定要评估的任务 id（逗号分隔）
    python demo.py --all --offline       # 无 Key 离线跑完全部 20 个任务的确定性层（L1/L2/L4）
    python demo.py --layers L1,L2,L4     # 只跑指定层（不含 L3 即无需联网）
    python demo.py --output results.json # 把完整评分结果写出为 JSON

完整参数见 python demo.py --help。
"""

import argparse
import json
import os
import sys
import unicodedata

from agent import STRONG, WEAK, SelfEvolutionAgent, ToolRegistry
from config import Config
from harness import ALL_LAYERS, FourLayerEvaluator

HERE = os.path.dirname(os.path.abspath(__file__))
DEMO_TASK_IDS = ["task-01", "task-17", "task-07"]  # 多媒体 / 地理空间 / 天气
_PROFILES = {"strong": STRONG, "weak": WEAK}


def load_dataset():
    with open(os.path.join(HERE, "dataset.json"), encoding="utf-8") as f:
        return json.load(f)


def fmt(x):
    return "N/A" if x is None else f"{x:.3f}"


def _disp_w(s: str) -> int:
    """考虑中日韩全角字符的显示宽度，用于表格对齐。"""
    return sum(2 if unicodedata.east_asian_width(c) in "WF" else 1 for c in str(s))


def _pad(s: str, width: int) -> str:
    s = str(s)
    return s + " " * max(0, width - _disp_w(s))


def print_dataset_overview(ds):
    tasks = ds["tasks"]
    print("=" * 78)
    print(f"数据集：{ds['meta']['name']}  共 {len(tasks)} 个任务，覆盖领域：")
    domains = [t["domain"] for t in tasks]
    print("  " + " | ".join(domains))
    print("-" * 78)
    print("任务示例（注意：只说目标，不暗示工具名 / 库名）：")
    for t in tasks[:4]:
        print(f"  [{t['id']}] ({t['domain']}) {t['goal']}")
    print("=" * 78 + "\n")


def print_report(rep):
    L = rep["layers"]
    print(f"■ 任务 {rep['task_id']} ({rep['domain']}) | 画像={rep['profile']}")
    print(f"  L1 任务正确性     : {fmt(L['L1']['score'])}  | {L['L1']['detail']}")
    print(f"  L2 工具发现有效性 : {fmt(L['L2']['score'])}  | {L['L2']['detail']}")
    l3 = L["L3"]
    print(f"  L3 工具创造质量   : {fmt(l3['score'])}  | {l3['detail']}")
    if l3.get("rubric"):
        r = l3["rubric"]
        print(f"       Rubric: 错误处理={r.get('error_handling')} 参数校验={r.get('input_validation')} "
              f"文档={r.get('documentation')} 健壮性={r.get('robustness')}")
        print(f"       LLM-Judge 点评: {r.get('comment', '')}")
    print(f"  L4 工具复用能力   : {fmt(L['L4']['score'])}  | {L['L4']['detail']}")
    print(f"  >> 总评 overall   : {fmt(rep['summary']['overall'])}  (计入层: {rep['summary']['used_layers']})")
    print()


def print_results_table(reports):
    """打印'每任务 × 每层'结果表：横向对比各任务在 L1-L4 与总评上的得分。"""
    if not reports:
        return
    headers = ["任务", "领域", "画像", "L1", "L2", "L3", "L4", "总评"]
    rows = []
    for rep in reports:
        L = rep["layers"]
        rows.append([
            rep["task_id"],
            rep["domain"],
            rep.get("profile") or "-",
            fmt(L["L1"]["score"]), fmt(L["L2"]["score"]),
            fmt(L["L3"]["score"]), fmt(L["L4"]["score"]),
            fmt(rep["summary"]["overall"]),
        ])
    widths = [max(_disp_w(headers[i]), *(_disp_w(r[i]) for r in rows)) for i in range(len(headers))]
    print("=" * 78)
    print("每任务 × 每层 结果表（N/A = 该层不适用或未选择）")
    print("-" * 78)
    print("  ".join(_pad(headers[i], widths[i]) for i in range(len(headers))))
    for r in rows:
        print("  ".join(_pad(r[i], widths[i]) for i in range(len(r))))
    print("=" * 78 + "\n")


def run_profile(name, profile, tasks, evaluator, offline=False, verbose=True):
    """跑一个画像下的全部任务，返回每个任务的四层评分报告列表。"""
    if verbose:
        print("#" * 78)
        print(f"# 用 {name} 参考 Agent 评估（每个任务：先做首次任务，再做相似任务测复用）")
        print("#" * 78 + "\n")
    registry = ToolRegistry()  # 每个画像独立的注册表
    agent = SelfEvolutionAgent(registry=registry, model=Config.AGENT_MODEL, offline=offline)
    reports = []
    for task in tasks:
        first = agent.run(task, profile, use_variant=False)   # 首次：发现+创造+注册（strong 真调 LLM 生成工具）
        variant = agent.run(task, profile, use_variant=True)  # 第二次相似任务：测复用
        rep = evaluator.evaluate(task, first, variant)
        reports.append(rep)
        if verbose:
            print_report(rep)
            # 展示复用层的轨迹差异证据
            v_actions = [s["action"] for s in variant["steps"]]
            print(f"    [复用探针] 第二次相似任务的动作序列: {v_actions}")
            print()
    return reports


def parse_args():
    ap = argparse.ArgumentParser(
        description="实验 8-6：为自我进化 Agent 设计评估数据集 · 四层验证演示",
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=(
            "示例：\n"
            "  python demo.py                       默认：strong 跑 3 个任务 + weak 对照 1 个\n"
            "  python demo.py --quick               strong / weak 各只跑 1 个任务，省时省钱\n"
            "  python demo.py --tasks task-01,task-07   指定要评估的任务 id\n"
            "  python demo.py --all --offline       无 Key 离线跑完全部 20 个任务的确定性层\n"
            "  python demo.py --layers L1,L2,L4     只跑指定层（不含 L3 即无需联网）\n"
            "  python demo.py --profile both --table 两个画像都跑，只看结果表\n"
            "  python demo.py --output results.json 把完整评分结果写出为 JSON"
        ),
    )
    # ---- 任务选择 ----
    ap.add_argument("--quick", action="store_true",
                    help="快速演示：strong / weak 各只跑 1 个任务，减少 API 调用与耗时。")
    ap.add_argument("--all", action="store_true",
                    help="评估数据集中全部 20 个任务（默认自动切到结果表输出）。")
    ap.add_argument("--tasks", metavar="IDS",
                    help="逗号分隔的任务 id（如 task-01,task-07），缺省用内置的示例任务。")
    # ---- 层与画像选择 ----
    ap.add_argument("--layers", metavar="L1,L2,...",
                    help="选择运行哪些验证层，逗号分隔（默认四层全跑）。\n"
                         "仅 L3 需联网调用 LLM，去掉 L3 即可纯离线运行。")
    ap.add_argument("--profile", choices=["strong", "weak", "both"],
                    help="被测参考 Agent 画像：strong / weak / both。\n"
                         "缺省保留默认行为（strong 跑全部选中任务 + weak 只跑第一个）。")
    ap.add_argument("--offline", action="store_true",
                    help="离线模式：不调用任何 LLM（strong 用离线工具模板），\n"
                         "并自动跳过 L3。用于无 API Key 时演示 L1/L2/L4 确定性层。")
    # ---- 模型 / 供应商 ----
    ap.add_argument("--provider", choices=["openai", "moonshot", "ark"],
                    help="覆盖 PROVIDER（默认读环境变量，缺省 openai）。")
    ap.add_argument("--agent-model", metavar="MODEL",
                    help="覆盖被测 Agent 造工具用的模型（默认读 AGENT_MODEL）。")
    ap.add_argument("--judge-model", metavar="MODEL",
                    help="覆盖 L3 LLM-as-a-Judge 用的模型（默认读 JUDGE_MODEL）。")
    # ---- 输出 ----
    ap.add_argument("--table", action="store_true",
                    help="只打印'每任务 × 每层'结果表，不打印逐任务的详细分层报告。")
    ap.add_argument("--output", metavar="PATH",
                    help="把完整评分结果（含各层明细）写出为 JSON 文件。")
    return ap.parse_args()


def resolve_layers(args):
    """根据 --layers / --offline 决定实际运行哪些层。"""
    if args.layers:
        want = [x.strip().upper() for x in args.layers.split(",") if x.strip()]
        bad = [x for x in want if x not in ALL_LAYERS]
        if bad:
            print(f"[错误] 未知的层：{bad}，可选：{list(ALL_LAYERS)}")
            sys.exit(1)
        layers = tuple(x for x in ALL_LAYERS if x in want)  # 归一到 L1..L4 顺序
    elif args.offline:
        layers = ("L1", "L2", "L4")  # 离线默认跳过需联网的 L3
    else:
        layers = ALL_LAYERS
    if args.offline and "L3" in layers:
        print("[提示] 离线模式无法运行 L3（需联网 LLM 裁判），已自动从本次层中移除 L3。\n")
        layers = tuple(x for x in layers if x != "L3")
    return layers


def main():
    args = parse_args()

    # 应用供应商 / 模型的命令行覆盖（优先级高于环境变量）
    if args.provider:
        Config.PROVIDER = args.provider
    if args.agent_model:
        Config.AGENT_MODEL = args.agent_model
    if args.judge_model:
        Config.JUDGE_MODEL = args.judge_model

    layers = resolve_layers(args)

    # 非离线模式：strong 画像造工具会真的调 LLM、L3 也需联网，因此需要可用的客户端。
    if not args.offline:
        try:
            Config.get_client()
        except Exception as e:
            print(f"[配置错误] {e}")
            print("提示：若只想演示确定性层，可用 `python demo.py --offline`（无需 API Key）。")
            sys.exit(1)

    mode = "离线(offline)" if args.offline else "联网(online)"
    print(f"运行模式={mode}  PROVIDER={Config.PROVIDER}  "
          f"AGENT_MODEL={Config.resolve_default_model()}  JUDGE_MODEL={Config.JUDGE_MODEL}")
    print(f"本次运行的验证层：{list(layers)}\n")

    ds = load_dataset()
    print_dataset_overview(ds)

    by_id = {t["id"]: t for t in ds["tasks"]}
    # 任务选择：--tasks 指定 > --all 全部 > --quick 取 1 个 > 默认 3 个示例任务
    if args.tasks:
        want = [i.strip() for i in args.tasks.split(",") if i.strip()]
        missing = [i for i in want if i not in by_id]
        if missing:
            print(f"[错误] 数据集中不存在这些任务 id：{missing}")
            sys.exit(1)
        task_ids = want
    elif args.all:
        task_ids = [t["id"] for t in ds["tasks"]]
    elif args.quick:
        task_ids = DEMO_TASK_IDS[:1]
    else:
        task_ids = DEMO_TASK_IDS
    tasks = [by_id[i] for i in task_ids]
    evaluator = FourLayerEvaluator(judge_model=Config.JUDGE_MODEL, layers=layers)

    # 任务较多（--all）时默认只出结果表，避免逐任务详报刷屏
    verbose = not (args.table or (args.all and not args.tasks))

    all_reports = []
    if args.profile in (None, "strong", "both"):
        # strong：好发现 + 高质量工具（离线用模板 / 联网调 LLM）+ 复用
        strong_tasks = tasks
        all_reports += run_profile("STRONG(强)", STRONG, strong_tasks, evaluator,
                                   offline=args.offline, verbose=verbose)
    if args.profile in ("weak", "both"):
        weak_tasks = tasks
        all_reports += run_profile("WEAK(弱)", WEAK, weak_tasks, evaluator,
                                   offline=args.offline, verbose=verbose)
    elif args.profile is None:
        # 默认行为：weak 只跑第一个任务，凸显四层区分度
        all_reports += run_profile("WEAK(弱)", WEAK, tasks[:1], evaluator,
                                   offline=args.offline, verbose=verbose)

    print_results_table(all_reports)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump({"layers": list(layers), "reports": all_reports}, f,
                      ensure_ascii=False, indent=2)
        print(f"[已写出] 完整评分结果 -> {args.output}\n")

    print("=" * 78)
    print("结论：四层验证对'强/弱'两种被测 Agent 给出了不同分数；")
    print("其中 L2 依据搜索关键词/选库判定发现有效性，L3 由 LLM-as-a-Judge 按 Rubric 对")
    print("工具代码打分，L4 通过第二次相似任务的动作序列区分'复用'与'重复搜索'。")
    print("=" * 78)


if __name__ == "__main__":
    main()
