#!/usr/bin/env python3
"""对照三个策略臂在 τ²-bench telecom 迁移集上的结果。

除通过率外，还统计三项与提炼规则直接相关的行为指标：
转人工率、误调用用户侧工具的次数、空参数调用次数。
"""
import argparse
import json
from pathlib import Path

SIM = Path(__file__).resolve().parents[2] / "chapter7/tau2-bench/data/simulations"
USER_TOOLS = set(
    (Path(__file__).resolve().parent / "tool_inventory.txt")
    .read_text(encoding="utf-8").split("USER_TOOLS:")[1]
    .replace(chr(10), " ").replace(",", " ").split()
)

def stats(name, path):
    with path.open(encoding="utf-8") as source:
        sims = json.load(source)["simulations"]
    out = {"arm": name, "n": len(sims), "pass": 0, "escalated": 0,
           "misdirected_user_tool_calls": 0, "empty_arg_calls": 0,
           "tool_errors": 0, "by_task": {}}
    for s in sims:
        r = s["reward_info"]["reward"]
        out["pass"] += int(r == 1.0)
        out["by_task"][s["task_id"]] = int(r == 1.0)
        for m in s["messages"]:
            # tau2 的消息里 requestor 恒为 None，调用方要看 role：
            # role == "user" 是用户在自己设备上执行，属于双控的正常行为；
            # role == "assistant" 调用用户侧工具才是 Agent 越界。
            for t in (m.get("tool_calls") or []):
                if t["name"] in USER_TOOLS and m.get("role") != "user":
                    out["misdirected_user_tool_calls"] += 1
                if any(v == "" for v in (t.get("arguments") or {}).values()):
                    out["empty_arg_calls"] += 1
            if m.get("role") == "tool" and "Error" in (m.get("content") or ""):
                out["tool_errors"] += 1
        if any(t["name"] == "transfer_to_human_agents"
               for m in s["messages"] for t in (m.get("tool_calls") or [])):
            out["escalated"] += 1
    return out

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--archived", action="store_true", help="读取随书轨迹，只打印统计结果")
    parser.add_argument("arms", nargs="*", help="要比较的策略臂名称")
    args = parser.parse_args()
    arms = args.arms or ["armA-baseline", "armB-evolved-v1", "armC-evolved-v2"]
    directory = Path(__file__).resolve().parent / "validation/runs" if args.archived else SIM
    suffix = ".trajectories.json" if args.archived else ".json"
    res = []
    for arm in arms:
        path = directory / (arm + suffix)
        if not path.is_file():
            parser.error(f"找不到轨迹 {path}。复算随书结果可使用 --archived。")
        res.append(stats(arm, path))
    print(f"{'臂':22s} {'n':>4s} {'通过':>6s} {'通过率':>7s} {'转人工率':>8s} "
          f"{'误调用户工具':>12s} {'空参调用':>8s} {'工具报错':>8s}")
    for r in res:
        n = r["n"] or 1
        print(f"{r['arm']:22s} {r['n']:4d} {r['pass']:6d} {r['pass']/n:7.1%} "
              f"{r['escalated']/n:8.1%} {r['misdirected_user_tool_calls']:12d} "
              f"{r['empty_arg_calls']:8d} {r['tool_errors']:8d}")
    # 配对比较：只在三臂都跑过的任务上算
    if len(res) >= 2:
        common = set(res[0]["by_task"])
        for r in res[1:]: common &= set(r["by_task"])
        print(f"\n共同任务 {len(common)} 条上的配对结果：")
        for r in res:
            p = sum(r["by_task"][t] for t in common)
            print(f"  {r['arm']:22s} {p:3d}/{len(common)} = {p/max(len(common),1):.1%}")
        if len(res) >= 2:
            a, b = res[0], res[-1]
            b_only = [t for t in common if b["by_task"][t] and not a["by_task"][t]]
            a_only = [t for t in common if a["by_task"][t] and not b["by_task"][t]]
            print(f"\n  {b['arm']} 修好而 {a['arm']} 失败: {len(b_only)} 条")
            print(f"  {a['arm']} 通过而 {b['arm']} 失败: {len(a_only)} 条")
    if not args.archived:
        output = Path(__file__).resolve().parent / "validation/arm_stats.json"
        with output.open("w", encoding="utf-8") as target:
            json.dump(res, target, ensure_ascii=False, indent=1)

if __name__ == "__main__":
    main()
