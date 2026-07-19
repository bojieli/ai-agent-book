"""
replay.py —— 回归测试重放框架

输入：Agent 生成的回归测试用例（结构化 JSON），引用轨迹 ID 与交互轮次。
过程：从原始轨迹取出该任务的输入，喂给被测系统（sut.run_task）重放，
      在重放产生的新轨迹上求值断言，给出 通过/失败。

一个测试用例的结构（Agent 需按此 DSL 生成）：
{
  "test_id": "RT-001",
  "trajectory_id": "T-1001",       # 引用的问题轨迹
  "focus_turn": 3,                 # 关键交互轮次（问题所在）
  "description": "退款前必须先做资格校验",
  "assertion": {"type": "step_present", "params": {"tool": "verify_refund_eligibility"}}
}

支持的断言类型（replay 框架内置，可被自动求值）：
- step_present   params.tool            某工具在轨迹中必须出现（如强制前置校验）
- tool_succeeds  params.tool            某工具最终必须成功、且不得出现连续失败后误报成功
- latency_under  params.tool, threshold_ms   某工具单次延迟必须低于阈值
- final_status_is params.value          任务最终状态必须等于给定值
"""

import json
import os
from typing import Dict, Any, List, Tuple

import sut

_DATA = os.path.join(os.path.dirname(__file__), "data", "trajectories.jsonl")


def load_trajectories(path: str = _DATA) -> Dict[str, Dict[str, Any]]:
    """读取生产轨迹集合，按 trajectory_id 索引。"""
    out = {}
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            t = json.loads(line)
            out[t["trajectory_id"]] = t
    return out


# ---------------- 断言求值器 ----------------

def _tool_turns(traj: Dict[str, Any], tool: str) -> List[Dict[str, Any]]:
    return [t for t in traj["turns"] if t.get("tool") == tool]


def _eval_assertion(assertion: Dict[str, Any], traj: Dict[str, Any]) -> Tuple[bool, str]:
    a_type = assertion.get("type")
    params = assertion.get("params", {})

    if a_type == "step_present":
        tool = params.get("tool") or params.get("step")
        ok = len(_tool_turns(traj, tool)) > 0
        return ok, f"工具 {tool} {'出现' if ok else '缺失'}"

    if a_type == "tool_succeeds":
        tool = params.get("tool")
        calls = _tool_turns(traj, tool)
        if not calls:
            return False, f"{tool} 未被调用"
        n_err = sum(1 for c in calls if c.get("status") == "error")
        last_ok = calls[-1].get("status") == "success"
        # 修复标准：最终成功，且不存在"多次失败后仍误报成功"（>=2 次失败视为未正确处理）
        ok = last_ok and n_err < 2
        return ok, f"{tool} 调用 {len(calls)} 次, 失败 {n_err} 次, 末次{'成功' if last_ok else '失败'}"

    if a_type == "latency_under":
        tool = params.get("tool")
        thr = params.get("threshold_ms") or params.get("threshold")
        calls = _tool_turns(traj, tool)
        if not calls:
            return False, f"{tool} 未被调用"
        worst = max(c.get("latency_ms", 0) for c in calls)
        ok = worst < thr
        return ok, f"{tool} 最大延迟 {worst}ms, 阈值 {thr}ms"

    if a_type == "final_status_is":
        want = params.get("value")
        ok = traj.get("final_status") == want
        return ok, f"final_status={traj.get('final_status')}, 期望={want}"

    return False, f"未知断言类型: {a_type}"


def run_test_case(tc: Dict[str, Any], trajectories: Dict[str, Any],
                  fixed: bool) -> Dict[str, Any]:
    """对单条测试用例：取原始轨迹输入 -> 重放被测系统 -> 求值断言。"""
    tid = tc.get("trajectory_id")
    src = trajectories.get(tid)
    if src is None:
        return {"test_id": tc.get("test_id"), "passed": False,
                "detail": f"引用的轨迹 {tid} 不存在"}

    replayed = sut.run_task(src["task_input"], fixed=fixed)
    passed, detail = _eval_assertion(tc.get("assertion", {}), replayed)
    return {
        "test_id": tc.get("test_id"),
        "trajectory_id": tid,
        "focus_turn": tc.get("focus_turn"),
        "passed": passed,
        "detail": detail,
        "replay_mode": "fixed" if fixed else "buggy",
    }


def run_suite(test_cases: List[Dict[str, Any]], fixed: bool,
              path: str = _DATA) -> List[Dict[str, Any]]:
    """跑完整套测试用例，返回结果列表。"""
    trajectories = load_trajectories(path)
    results = []
    for tc in test_cases:
        try:
            results.append(run_test_case(tc, trajectories, fixed))
        except Exception as e:  # 单条用例出错不影响整套
            results.append({"test_id": tc.get("test_id"), "passed": False,
                            "detail": f"用例执行异常: {e}",
                            "replay_mode": "fixed" if fixed else "buggy"})
    return results
