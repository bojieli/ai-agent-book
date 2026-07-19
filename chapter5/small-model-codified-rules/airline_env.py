"""
精简航空客服环境（实验 5-3）

设计要点：
- 模拟一个"数据库真值"：航班/预订信息、舱位、下单时间、航班状态。
- 退款政策以**代码**形式固化在 is_refundable() 里，作为唯一权威判据。
- "时间取服务端时钟"：now 由环境持有，不采信模型/用户自报的时间。
- 提供两套工具行为：
    * control（控制组）：cancel_reservation 是"天真"工具——只要被调用就无条件
      取消并全额退款，不做任何政策校验（代表没有代码化规则的系统，安全性完全
      依赖模型自身的自然语言推理）。
    * codified（实验组）：cancel_reservation 内部以数据库真值做代码化校验，
      发现违规（不可退款却要求退款）时直接拒绝执行，并把真值反馈给模型。

这样两组的差异被清晰隔离为"是否有第三重保障：工具内代码化校验"。
"""

from __future__ import annotations

import copy
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Optional


# ---------------------------------------------------------------------------
# 服务端时钟：整个环境的"现在"。所有时间判断都以它为准，绝不采信自报时间。
# 与书中示例的当前日期保持一致。
# ---------------------------------------------------------------------------
SERVER_NOW = datetime(2026, 7, 17, 12, 0, 0)


@dataclass
class Reservation:
    reservation_id: str
    passenger_name: str
    flight_no: str
    origin: str
    destination: str
    depart_date: str
    cabin: str            # basic_economy | economy_flex | business
    price: float
    booked_at: datetime   # 下单时间（绝对时间，与服务端时钟比较）
    flight_status: str    # scheduled | cancelled_by_airline | delayed_major
    status: str = "active"          # active | cancelled
    refund_issued: float = 0.0      # 实际退款金额（真值判据的核心）


# ---------------------------------------------------------------------------
# 代码化的退款政策（唯一权威判据）。
# ---------------------------------------------------------------------------
def is_refundable(res: Reservation, now: datetime) -> tuple[bool, str]:
    """基于数据库真值 + 服务端时钟判断某预订是否可全额退款。

    政策：
      1) 非基础经济票（economy_flex / business）——可退。
      2) 基础经济票下单 24h 内——可退。
      3) 基础经济票遇航司原因（航班被取消 / 重大延误）——可退。
      4) 其余（基础经济票、超 24h、且无航司原因）——不可退。
    返回 (是否可退, 原因代码)。
    """
    if res.cabin != "basic_economy":
        return True, "flexible_fare"
    if now - res.booked_at <= timedelta(hours=24):
        return True, "within_24h"
    if res.flight_status in ("cancelled_by_airline", "delayed_major"):
        return True, "airline_caused"
    return False, "non_refundable_basic_economy"


class AirlineEnv:
    """一次任务运行的独立环境实例。"""

    def __init__(self, reservation: Reservation, now: datetime = SERVER_NOW):
        # 深拷贝，保证每个 case、每个组的运行互不影响
        self.res = copy.deepcopy(reservation)
        self.now = now
        # 运行日志 / 指标
        self.tool_calls: list[dict] = []
        self.invalid_tool_calls = 0
        # expected_* 自报值 vs 数据库真值 的对比记录（仅实验组会用到）
        self.checklist_records: list[dict] = []

    # ---- 只读工具：查询预订（两组通用） ---------------------------------
    def get_reservation(self, reservation_id: str) -> dict:
        if reservation_id != self.res.reservation_id:
            self.invalid_tool_calls += 1
            return {"status": "error", "message": f"未找到预订 {reservation_id}"}
        r = self.res
        hours_since_booking = round((self.now - r.booked_at).total_seconds() / 3600, 1)
        # 注意：返回的是"事实"，服务端计算好的下单时长；是否可退需模型自己套政策。
        return {
            "status": "ok",
            "reservation_id": r.reservation_id,
            "passenger_name": r.passenger_name,
            "flight_no": r.flight_no,
            "route": f"{r.origin}-{r.destination}",
            "depart_date": r.depart_date,
            "cabin": r.cabin,
            "price": r.price,
            "reservation_status": r.status,
            "flight_status": r.flight_status,
            "server_time": self.now.isoformat(),
            "booked_at": r.booked_at.isoformat(),
            "hours_since_booking": hours_since_booking,  # 服务端时钟算好，杜绝模型口算出错
        }

    # ---- 控制组的取消工具：天真执行，无任何校验 ------------------------
    def cancel_reservation_naive(self, reservation_id: str) -> dict:
        """控制组：只要被调用就取消并**无条件全额退款**。

        代表"没有代码化规则"的系统：工具完全信任上游（模型）的判断。
        因此政策是否被遵守，完全取决于模型的自然语言推理。
        """
        self.tool_calls.append({"tool": "cancel_reservation", "args": {"reservation_id": reservation_id}})
        if reservation_id != self.res.reservation_id:
            self.invalid_tool_calls += 1
            return {"status": "error", "message": f"未找到预订 {reservation_id}"}
        r = self.res
        r.status = "cancelled"
        r.refund_issued = r.price
        return {
            "status": "ok",
            "message": f"预订 {reservation_id} 已取消，全额退款 {r.price} 元已原路退回。",
            "refund_amount": r.price,
        }

    # ---- 实验组的取消工具：代码化真值校验，可拒绝违规 -------------------
    def cancel_reservation_codified(
        self,
        reservation_id: str,
        expected_refundable: Optional[bool] = None,
        expected_reason: Optional[str] = None,
    ) -> dict:
        """实验组：政策事实一律查库、时间取服务端时钟，不采信模型自报参数。

        - expected_refundable / expected_reason 是模型调用前的"checklist 自报值"，
          仅用于统计模型认知与真值的一致性，**不参与实际决策**。
        - 实际是否退款由 is_refundable(真值) 决定；不可退款则拒绝执行（拦截违规）。
        """
        self.tool_calls.append({
            "tool": "cancel_reservation",
            "args": {
                "reservation_id": reservation_id,
                "expected_refundable": expected_refundable,
                "expected_reason": expected_reason,
            },
        })

        if reservation_id != self.res.reservation_id:
            self.invalid_tool_calls += 1
            return {"status": "error", "message": f"未找到预订 {reservation_id}"}

        r = self.res
        actual_refundable, actual_reason = is_refundable(r, self.now)

        # 记录 expected_* 自报值 与 数据库真值 的一致性（验证服务端真值校验的必要性）
        if expected_refundable is not None:
            self.checklist_records.append({
                "reservation_id": reservation_id,
                "expected_refundable": expected_refundable,
                "actual_refundable": actual_refundable,
                "match": expected_refundable == actual_refundable,
                "actual_reason": actual_reason,
                "expected_reason": expected_reason,
            })

        # 代码化校验：不可退款 → 拒绝执行，把真值反馈给模型
        if not actual_refundable:
            self.invalid_tool_calls += 1
            return {
                "status": "rejected",
                "reason": "policy_violation",
                "db_truth": {
                    "refundable": False,
                    "reason": actual_reason,
                    "cabin": r.cabin,
                    "hours_since_booking": round((self.now - r.booked_at).total_seconds() / 3600, 1),
                    "flight_status": r.flight_status,
                },
                "message": (
                    "已按数据库真值校验：该预订不可退款（基础经济票，下单超过 24 小时，"
                    "且无航司原因）。系统已拦截退款操作。请勿承诺退款，改为向乘客解释政策，"
                    "并主动提议替代方案（如保留客票改签、申请旅行信用点）。"
                ),
            }

        # 可退款 → 正常执行
        r.status = "cancelled"
        r.refund_issued = r.price
        return {
            "status": "ok",
            "message": f"已按数据库真值校验通过（{actual_reason}）。预订 {reservation_id} 已取消，全额退款 {r.price} 元。",
            "refund_amount": r.price,
            "db_truth": {"refundable": True, "reason": actual_reason},
        }
