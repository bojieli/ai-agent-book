"""
sut.py —— System Under Test（被测系统的确定性仿真）

回归测试的核心是"用相同输入重放，断言修复后系统能产生正确行为"。
这里用一个**确定性**的仿真器来扮演线上 Agent 系统：

- run_task(task_input, fixed=False)：复现线上（有 bug）的行为，
  产出的轨迹会带上和生产轨迹一致的三类已知问题。
- run_task(task_input, fixed=True)：模拟"修复后"的系统，
  正确执行前置校验 / 重试退避 / 库存降级。

replay.py 会分别对 fixed=False / fixed=True 重放同一输入，
从而演示同一条回归测试用例的"失败(复现bug)"与"通过(验证修复)"。

轨迹结构与 data/trajectories.jsonl 完全一致，便于对比。
"""

from typing import Dict, Any


def run_task(task_input: Dict[str, Any], fixed: bool = False) -> Dict[str, Any]:
    """给定任务输入，确定性地跑一遍被测系统，返回一条轨迹。"""
    intent = task_input.get("intent")
    order_id = task_input.get("order_id", "UNKNOWN")
    turns = []
    idx = 0

    def add(**kw):
        nonlocal idx
        kw["index"] = idx
        idx += 1
        turns.append(kw)

    # 0. 用户输入 & 意图识别
    add(role="user", content=f"task={intent}, order={order_id}")
    add(role="assistant", module="intent_parser", content=f"意图={intent}")

    final_status = "success"

    if intent == "refund":
        # 查询订单
        add(role="tool", module="order_service", tool="query_order",
            input={"order_id": order_id},
            output={"status": task_input.get("order_status", "paid")},
            status="success", latency_ms=210)

        # R1：退款前置资格校验（仅修复版本执行）
        if fixed:
            add(role="tool", module="order_service", tool="verify_refund_eligibility",
                input={"order_id": order_id},
                output={"eligible": True}, status="success", latency_ms=120)

        # R2：支付重试 + 退避
        if task_input.get("payment_flaky") and not fixed:
            # 线上 bug：无退避，连续失败后误报成功
            for _ in range(3):
                add(role="tool", module="payment_service", tool="process_refund",
                    input={"order_id": order_id},
                    output={"error": "gateway_timeout"},
                    status="error", latency_ms=3000)
            add(role="assistant", module="payment_service",
                content="多次失败，仍按成功结束（bug）")
            final_status = "success"  # 误报成功
        elif task_input.get("payment_flaky") and fixed:
            # 修复：一次失败后带退避重试成功
            add(role="tool", module="payment_service", tool="process_refund",
                input={"order_id": order_id},
                output={"error": "gateway_timeout"}, status="error", latency_ms=1500)
            add(role="assistant", module="payment_service", content="退避 800ms 后重试")
            add(role="tool", module="payment_service", tool="process_refund",
                input={"order_id": order_id, "retry": 1},
                output={"refund_id": "R-OK"}, status="success", latency_ms=600)
        else:
            add(role="tool", module="payment_service", tool="process_refund",
                input={"order_id": order_id},
                output={"refund_id": "R-OK"}, status="success", latency_ms=540)

    elif intent == "order_status":
        add(role="tool", module="order_service", tool="query_order",
            input={"order_id": order_id},
            output={"status": "paid", "sku": task_input.get("sku")},
            status="success", latency_ms=220)

        # R3：库存查询延迟
        if task_input.get("slow_inventory") and not fixed:
            # 线上 bug：超时仍阻塞等待，不降级
            add(role="tool", module="inventory_service", tool="check_stock",
                input={"sku": task_input.get("sku")},
                output={"stock": 12}, status="success", latency_ms=8300)
        elif task_input.get("slow_inventory") and fixed:
            # 修复：超过阈值走降级路径，快速返回
            add(role="tool", module="inventory_service", tool="check_stock",
                input={"sku": task_input.get("sku"), "degraded": True},
                output={"stock": "cached:12", "degraded": True},
                status="success", latency_ms=400)
        else:
            add(role="tool", module="inventory_service", tool="check_stock",
                input={"sku": task_input.get("sku")},
                output={"stock": 5}, status="success", latency_ms=300)

    # R4：通知用户
    add(role="tool", module="notification_service", tool="notify_user",
        input={"final_status": final_status},
        output={"sent": True}, status="success", latency_ms=60)

    return {
        "trajectory_id": f"REPLAY::{order_id}::{'fixed' if fixed else 'buggy'}",
        "task_input": task_input,
        "final_status": final_status,
        "turns": turns,
    }
