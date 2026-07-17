"""模拟的异步"终端命令"与任务管理器。

为了安全（绝不真跑危险命令）与可复现，长任务用"带进度输出的模拟脚本"实现：
每个模拟脚本以固定的"每（模拟）秒进度百分比"推进，直到 100% 完成。

时间轴加速：真实世界里每 TICK_REAL 秒代表 1 个"模拟秒"。
默认 TICK_REAL=0.25，即 4 倍速——保留"3%/2%/1% 的速度差 + 是否过 50% 的判定"逻辑，
但把几十秒的等待压缩到几秒，方便演示复现。
"""

from __future__ import annotations

import asyncio
import os
from dataclasses import dataclass, field
from typing import Awaitable, Callable, Dict, Optional

# 1 个"模拟秒"对应的真实秒数（可用环境变量覆盖）。
# 默认 0.4（2.5 倍速）：既压缩了等待，又给模型的"查询-判定-取消"决策留足时间窗口，
# 保证场景 4 里"慢脚本尚未过 50% 就被取消"能稳定复现。
TICK_REAL = float(os.getenv("FLUX_TICK_REAL", "0.4"))

# 不同脚本的"每模拟秒进度%"档位。实验 4-5 场景 4 需要 3% / 2% / 1% 的速度差。
_SCRIPT_RATES = [
    ("fast", 3.0),
    ("mid", 2.0),
    ("slow", 1.0),
]
_DEFAULT_RATE = 4.5  # 场景 1/2/3 的普通长任务（约 22 模拟秒 ≈ 5.5 真实秒完成）


def resolve_rate(command: str) -> float:
    """根据命令字符串推断该模拟脚本的推进速度（%/模拟秒）。"""
    low = command.lower()
    for key, rate in _SCRIPT_RATES:
        if key in low:
            return rate
    return _DEFAULT_RATE


@dataclass
class TaskState:
    """一个异步终端任务的实时状态。"""

    task_id: str
    command: str
    rate: float
    progress: float = 0.0
    status: str = "running"          # running | completed | cancelled
    result: str = ""
    _task: Optional[asyncio.Task] = field(default=None, repr=False)


class TaskManager:
    """管理所有异步终端任务：启动、查询进度、取消。

    on_complete 回调会在任务自然完成时被调用（用于把真实结果作为"新事件"注入对话）。
    """

    def __init__(self, on_complete: Callable[[TaskState], Awaitable[None]],
                 log: Callable[[str, str], None]):
        self._on_complete = on_complete
        self._log = log
        self._tasks: Dict[str, TaskState] = {}
        self._counter = 0

    def start(self, command: str) -> TaskState:
        """启动一个异步终端命令，立即返回其状态（含 task_id 占位符）。"""
        self._counter += 1
        task_id = f"T{self._counter}"
        state = TaskState(task_id=task_id, command=command, rate=resolve_rate(command))
        self._tasks[task_id] = state
        state._task = asyncio.create_task(self._run(state))
        self._log("TASK", f"启动异步任务 {task_id}: `{command}` (速度 {state.rate:.0f}%/模拟秒)")
        return state

    async def _run(self, state: TaskState) -> None:
        """后台推进进度，直到完成或被取消。"""
        next_milestone = 20.0
        try:
            while state.progress < 100.0:
                await asyncio.sleep(TICK_REAL)
                state.progress = min(100.0, state.progress + state.rate)
                if state.progress >= next_milestone:
                    self._log("TASK", f"{state.task_id} `{state.command}` 进度 {state.progress:.0f}%")
                    next_milestone += 20.0
            state.status = "completed"
            state.result = (f"命令 `{state.command}` 执行完毕：共扫描 12,840 条记录，"
                            f"发现 3 个异常峰值、1 处可疑错误码（HTTP 503 突增），"
                            f"平均响应时间 128ms。")
            self._log("TASK", f"{state.task_id} 完成 ✅")
            await self._on_complete(state)
        except asyncio.CancelledError:
            # 被取消：标记状态并静默退出（不再注入完成结果）
            state.status = "cancelled"
            self._log("TASK", f"{state.task_id} 已被取消 🛑（进度停在 {state.progress:.0f}%）")
            raise

    def query(self, task_id: str) -> Optional[TaskState]:
        return self._tasks.get(task_id)

    def cancel(self, task_id: str) -> bool:
        """按 ID 取消单个任务。"""
        state = self._tasks.get(task_id)
        if state and state.status == "running":
            state.status = "cancelled"
            if state._task:
                state._task.cancel()
            return True
        return False

    def cancel_all(self) -> list[str]:
        """取消所有仍在运行的任务，返回被取消的 task_id 列表。"""
        cancelled = []
        for tid, state in self._tasks.items():
            if state.status == "running":
                state.status = "cancelled"
                if state._task:
                    state._task.cancel()
                cancelled.append(tid)
        return cancelled

    def any_running(self) -> bool:
        return any(s.status == "running" for s in self._tasks.values())
