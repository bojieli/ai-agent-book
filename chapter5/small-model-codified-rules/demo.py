"""
实验 5-3 主程序：小模型靠"代码化规则"追平大模型的可靠性

三方对照（核心主张）：
    A. 小模型 + 代码化规则（实验组，三重保障）
    B. 小模型 · 纯自然语言（控制组）
    C. 大模型 · 纯自然语言（可选基线，--big-model 开启）
预期：A 的任务成功率 ≈ C，且都显著高于 B —— 即"把业务规则写成代码化守卫"，
能让一个小模型在复杂政策执行上追平大模型裸跑的可靠性。

指标：
    - 任务成功率：最终退款结果是否符合代码化政策真值。
    - 政策违规次数：多退款（该拒不拒） + 该退不退，两个方向都算。
    - 无效工具调用次数：被代码校验拒绝 / 未知预订等返回 error/rejected 的调用。
    - expected_* 自报值 vs 数据库真值 不一致比例（仅实验组，验证服务端真值校验的必要性）。

常用跑法见 `--help`；`--selftest` 无需 API Key，离线演示三层守卫的代码化校验逻辑。
"""

from __future__ import annotations

import argparse
import json
import os
import sys

try:
    from dotenv import load_dotenv
    load_dotenv()  # 若存在 .env 则加载 OPENAI_API_KEY / MODEL / BIG_MODEL
except ImportError:
    pass

from airline_env import AirlineEnv, is_refundable, SERVER_NOW
from agent import MODEL
from tasks import TASKS


ALT_KEYWORDS = ["改签", "信用", "credit", "保留", "替代", "积分", "凭证", "备选"]


def judge(task, env, final_text) -> dict:
    """基于环境真值（状态即真值）做规则判据评分。"""
    refunded = env.res.refund_issued > 0
    expect_refundable = task.expect_refundable

    wrongful_refund = (not expect_refundable) and refunded      # 该拒不拒
    wrongful_refusal = expect_refundable and (not refunded)     # 该退不退
    violation = wrongful_refund or wrongful_refusal
    success = not violation

    offered_alt = any(k.lower() in final_text.lower() for k in ALT_KEYWORDS)

    return {
        "task_id": task.task_id,
        "expect_refundable": expect_refundable,
        "refunded": refunded,
        "success": success,
        "wrongful_refund": wrongful_refund,
        "wrongful_refusal": wrongful_refusal,
        "invalid_tool_calls": env.invalid_tool_calls,
        "offered_alt": offered_alt if not expect_refundable else None,
        "checklist_records": env.checklist_records,
    }


# ---------------------------------------------------------------------------
# 对照臂（arm）：每一臂是 (模式, 模型) 的组合
# ---------------------------------------------------------------------------
def build_arms(small_model: str, big_model: str | None, mode: str) -> list[dict]:
    """按 --mode / --big-model 组装本次要跑的对照臂。默认（both、无大模型）
    与旧版行为一致：控制组 + 实验组，均在小模型上。"""
    arms: list[dict] = []
    if mode in ("control", "both"):
        arms.append({"key": "small_control", "mode": "control", "model": small_model,
                     "label": "小模型·纯自然语言", "role": "控制组"})
    if mode in ("codified", "both"):
        arms.append({"key": "small_codified", "mode": "codified", "model": small_model,
                     "label": "小模型+代码化规则", "role": "实验组"})
    if big_model:  # 可选第三臂：大模型裸跑基线（纯自然语言）
        arms.append({"key": "big_control", "mode": "control", "model": big_model,
                     "label": "大模型·纯自然语言", "role": "大模型基线"})
    return arms


def run_arm(arm: dict, tasks, verbose: bool) -> list[dict]:
    # 延迟导入 run_agent：仅在真正要调用模型时才需要（--selftest 不走这里）
    from agent import run_agent

    print(f"\n{'='*72}\n运行 [{arm['role']}] {arm['label']}  模型={arm['model']}\n{'='*72}")
    results = []
    for task in tasks:
        env = AirlineEnv(task.reservation)
        out = run_agent(env, task.user_message, arm["mode"], verbose=verbose, model=arm["model"])
        r = judge(task, env, out["final_text"])
        r["final_text"] = out["final_text"]
        r["transcript"] = out["transcript"]
        results.append(r)
        flag = "✅" if r["success"] else "❌"
        detail = "多退款" if r["wrongful_refund"] else ("该退未退" if r["wrongful_refusal"] else "")
        print(f"  {flag} {task.task_id:<26} 应退={str(r['expect_refundable']):<5} 实退={str(r['refunded']):<5} "
              f"无效调用={r['invalid_tool_calls']} {detail}")
    return results


def summarize(results: list[dict]) -> dict:
    n = len(results)
    succ = sum(r["success"] for r in results)
    violations = sum(r["wrongful_refund"] + r["wrongful_refusal"] for r in results)
    invalid = sum(r["invalid_tool_calls"] for r in results)
    # expected_* vs 真值 一致性（合并所有 checklist 记录）
    records = [rec for r in results for rec in r["checklist_records"]]
    mism = sum(1 for rec in records if not rec["match"])
    return {
        "n": n, "success": succ, "success_rate": succ / n if n else 0.0,
        "violations": violations, "invalid": invalid,
        "checklist_total": len(records), "checklist_mismatch": mism,
    }


def print_comparison(arms: list[dict], summaries: list[dict]):
    print(f"\n{'#'*72}\n# 指标对比（{len(arms)} 臂）\n{'#'*72}")
    col = 24
    label_w = 20
    # 表头
    header = f"{'指标':<{label_w}}" + "".join(f"{a['label']:<{col}}" for a in arms)
    print(header)
    print("-" * (label_w + col * len(arms)))
    # 任务成功率
    rate_cells = ["{}/{} = {:.0f}%".format(s["success"], s["n"], s["success_rate"] * 100) for s in summaries]
    print(f"{'任务成功率':<{label_w}}" + "".join(f"{c:<{col}}" for c in rate_cells))
    print(f"{'政策违规次数':<{label_w}}" + "".join(f"{str(s['violations']):<{col}}" for s in summaries))
    print(f"{'无效工具调用次数':<{label_w}}" + "".join(f"{str(s['invalid']):<{col}}" for s in summaries))

    # 核心主张的一句话解读（当同时有 实验组 与 大模型基线 时）
    by_role = {a["role"]: s for a, s in zip(arms, summaries)}
    if "实验组" in by_role and "大模型基线" in by_role:
        exp, big = by_role["实验组"], by_role["大模型基线"]
        print(f"\n[核心主张] 小模型+代码化规则 成功率 {exp['success_rate']*100:.0f}% "
              f"vs 大模型裸跑 {big['success_rate']*100:.0f}%"
              + ("（追平/超过）" if exp["success_rate"] >= big["success_rate"] else "（尚有差距）"))

    # expected_* 一致性（仅实验组存在 checklist）
    exp_summ = by_role.get("实验组")
    if exp_summ and exp_summ["checklist_total"]:
        ratio = exp_summ["checklist_mismatch"] / exp_summ["checklist_total"]
        print(f"\n[实验组] expected_* 自报值 vs 数据库真值：共 {exp_summ['checklist_total']} 次带 checklist 的取消调用，"
              f"其中 {exp_summ['checklist_mismatch']} 次与真值不一致 —— 不一致比例 = {ratio*100:.0f}%")
        print("  （说明：模型自我认知会出错；若无服务端真值校验，这些错误会直接变成违规操作。）")


def print_interception_example(exp_results):
    """找一例：实验组模型自报可退(expected_refundable=True)，但数据库真值不可退，被代码拦截。"""
    for r in exp_results:
        for rec in r["checklist_records"]:
            if rec["expected_refundable"] is True and rec["actual_refundable"] is False:
                print(f"\n{'*'*72}\n* 代码化校验拦截示例（{r['task_id']}）\n{'*'*72}")
                print(f"模型 checklist 自报：expected_refundable=True（认为可退）")
                print(f"数据库真值        ：refundable=False，原因={rec['actual_reason']}")
                for step in r["transcript"]:
                    if step["tool"] == "cancel_reservation":
                        print(f"\n模型发起取消调用：{step['args']}")
                        print(f"工具代码化校验返回：status={step['result'].get('status')}，"
                              f"reason={step['result'].get('reason')}")
                        print(f"  → {step['result'].get('message')}")
                        break
                print(f"\n模型最终回复用户（被拦截后转为解释/提议替代）：\n  {r['final_text'][:400]}")
                return True
    return False


# ---------------------------------------------------------------------------
# 离线自检：无需 API Key，直接演示"三层守卫"里的第三层——服务端代码化校验
# ---------------------------------------------------------------------------
def run_selftest(tasks) -> None:
    print(f"{'='*72}\n离线自检（无需 API Key）：代码化退款政策 + 工具内真值校验\n"
          f"服务端时钟 SERVER_NOW = {SERVER_NOW.isoformat()}\n{'='*72}")
    for task in tasks:
        r = task.reservation
        truth, reason = is_refundable(r, SERVER_NOW)
        print(f"\n[{task.task_id}] 舱位={r.cabin} 下单={r.booked_at.isoformat()} 航班状态={r.flight_status}")
        print(f"  政策真值 is_refundable -> refundable={truth}, reason={reason}")

        # 控制组"天真工具"：无条件退款（代表没有代码化规则的系统）
        env_naive = AirlineEnv(r)
        naive = env_naive.cancel_reservation_naive(r.reservation_id)
        print(f"  [控制组·天真工具] status={naive['status']} 退款={env_naive.res.refund_issued}"
              f"  {'← 违规！政策不可退却退了' if (not truth and env_naive.res.refund_issued > 0) else ''}")

        # 实验组"代码化工具"：故意灌入与真值相反的 expected_refundable，看是否被拦截
        env_cod = AirlineEnv(r)
        wrong_expected = not truth  # 模拟"模型自我认知出错"
        cod = env_cod.cancel_reservation_codified(
            r.reservation_id, expected_refundable=wrong_expected, expected_reason="airline_caused")
        outcome = ("退款执行" if cod["status"] == "ok" else f"拒绝({cod.get('reason')})")
        print(f"  [实验组·代码化] 模型自报expected_refundable={wrong_expected} -> status={cod['status']} "
              f"[{outcome}] 退款={env_cod.res.refund_issued}")
        rec = env_cod.checklist_records[-1] if env_cod.checklist_records else None
        if rec:
            print(f"      expected_* 校验：自报={rec['expected_refundable']} vs 真值={rec['actual_refundable']} "
                  f"-> {'一致' if rec['match'] else '不一致（已记录告警）'}")
    print(f"\n{'='*72}\n结论：无论模型自报什么，实验组一律以数据库真值裁决——"
          f"不可退的一律被拦截，可退的才放行。\n{'='*72}")


def select_tasks(patterns: list[str] | None, quick: bool):
    tasks = TASKS
    if patterns:
        picked = [t for t in tasks if any(p.lower() in t.task_id.lower() for p in patterns)]
        if not picked:
            sys.exit(f"错误：--task {patterns} 未匹配任何 case。可用 task_id：\n  "
                     + "\n  ".join(t.task_id for t in TASKS))
        return picked
    if quick:
        return tasks[:4]
    return tasks


def build_parser() -> argparse.ArgumentParser:
    ap = argparse.ArgumentParser(
        prog="demo.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "实验 5-3：小模型通过代码化业务规则，追平大模型裸跑的政策执行可靠性。\n"
            "基于 τ-bench 航空客服取消/退款场景，做三方对照实验。"),
        epilog=(
            "示例：\n"
            "  python demo.py                         # 默认：控制组 vs 实验组（均用小模型），跑全部 8 个 case\n"
            "  python demo.py --quick -v              # 只跑前 4 个 case，并打印每步工具调用\n"
            "  python demo.py --task R009             # 只跑匹配 'R009' 的 case（核心拦截样例）\n"
            "  python demo.py --big-model gpt-5.6-luna  # 加入第三臂：大模型裸跑基线，验证'小模型+规则≈大模型'\n"
            "  python demo.py --mode codified         # 只跑实验组（with 代码化规则）\n"
            "  python demo.py --mode control          # 只跑控制组（without 代码化规则）\n"
            "  python demo.py --small-model qwen3-4b --output result.json   # 指定小模型并保存结果\n"
            "  python demo.py --selftest              # 离线演示代码化校验逻辑（无需 API Key）\n"),
    )
    ap.add_argument("--mode", choices=["control", "codified", "both"], default="both",
                    help="跑哪一组：control=纯自然语言(without 代码化规则)，codified=三重保障(with 代码化规则)，"
                         "both=两组都跑（默认）")
    ap.add_argument("--task", "--tasks", dest="task", nargs="+", metavar="ID",
                    help="只跑 task_id 匹配给定子串的 case（可多个，如 --task R003 R009）")
    ap.add_argument("--small-model", default=MODEL, metavar="NAME",
                    help=f"用作'小模型'的模型名（默认 {MODEL}，也可用环境变量 MODEL 覆盖）")
    ap.add_argument("--big-model", default=os.environ.get("BIG_MODEL"), metavar="NAME",
                    help="用作'大模型基线'的模型名（可选；给定后加跑第三臂：大模型裸跑纯自然语言）")
    ap.add_argument("--quick", action="store_true", help="只跑前 4 个 case（省钱快看）")
    ap.add_argument("-v", "--verbose", action="store_true", help="打印每步工具调用")
    ap.add_argument("--output", metavar="PATH", help="把逐 case 结果与汇总指标写入 JSON 文件")
    ap.add_argument("--selftest", action="store_true",
                    help="离线自检：无需 API Key，直接演示代码化退款政策与工具内真值校验")
    return ap


def main():
    args = build_parser().parse_args()

    tasks = select_tasks(args.task, args.quick)

    # 离线自检：不需要 API Key，先处理
    if args.selftest:
        run_selftest(tasks)
        return

    if not (os.environ.get("OPENAI_API_KEY") or os.environ.get("OPENROUTER_API_KEY")):
        sys.exit("错误：未设置 OPENAI_API_KEY（或 OPENROUTER_API_KEY 兜底），请复制 env.example 为 .env 并填入，或直接 export。"
                 "\n（提示：想离线看代码化校验逻辑，可跑 `python demo.py --selftest`，无需 Key。）")

    arms = build_arms(args.small_model, args.big_model, args.mode)
    if not arms:
        sys.exit("错误：没有可运行的对照臂，请检查 --mode / --big-model 组合。")

    print(f"实验 5-3：小模型通过代码化知识提升执行规则的准确性")
    print(f"共 {len(tasks)} 个 case（可退 {sum(t.expect_refundable for t in tasks)} / "
          f"不可退 {sum(not t.expect_refundable for t in tasks)}），{len(arms)} 个对照臂："
          + "、".join(f"{a['label']}({a['model']})" for a in arms))

    arm_results = [run_arm(arm, tasks, args.verbose) for arm in arms]
    summaries = [summarize(res) for res in arm_results]

    print_comparison(arms, summaries)

    # 拦截样例（取第一个实验组臂）
    for arm, res in zip(arms, arm_results):
        if arm["mode"] == "codified":
            if not print_interception_example(res):
                print("\n（本次运行实验组未出现 expected=可退/真值=不可退 的拦截样例；"
                      "可重跑或调高温度观察。）")
            break

    if args.output:
        payload = {
            "config": {
                "small_model": args.small_model, "big_model": args.big_model,
                "mode": args.mode, "task_ids": [t.task_id for t in tasks],
            },
            "arms": [
                {**{k: arm[k] for k in ("key", "mode", "model", "label", "role")},
                 "summary": summ, "results": res}
                for arm, summ, res in zip(arms, summaries, arm_results)
            ],
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n结果已写入 {args.output}")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        sys.exit(130)
