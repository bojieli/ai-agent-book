"""
主协调器（Coordinator）与子 Agent（Worker）
===========================================

实现实验 10-6 的核心协调机制：

1. 并行派发：Coordinator 同时启动 N 个同构 Worker，各搜一个"网站/来源"。
2. 消息总线：Worker 与 Coordinator 全部通过 ``MessageBus`` 用信封通信。
3. 实时监控（push 范式）：Worker 执行中主动 ``status_update`` 上报，
   Coordinator 维护任务状态表并实时刷新打印。
4. 级联终止：某 Worker 命中目标后，Coordinator 广播 ``terminate``，
   其余 Worker 在循环安全点检查到信号后 ack 并优雅退出。
5. 竞态处理：多个 Worker 可能几乎同时命中，Coordinator 用 ``asyncio.Lock``
   + 幂等标志保证**只结算一次、只广播一轮终止**。

状态机：submitted -> running -> (needs_input) -> succeeded / failed / terminated
"""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional

from llm import judge_answer, llm_available
from message_bus import BROADCAST, MessageBus, _now
from sources import Source


class TaskState(str, Enum):
    SUBMITTED = "已提交"
    RUNNING = "执行中"
    NEEDS_INPUT = "需要输入"
    SUCCEEDED = "已完成"
    FAILED = "失败"
    TERMINATED = "已终止"


@dataclass
class TaskRecord:
    """Coordinator 状态表里的一行：一个 Worker 的实时状态。"""

    worker_id: str
    source_name: str
    state: TaskState = TaskState.SUBMITTED
    note: str = ""
    updated: float = field(default_factory=_now)


# ————————————————————————————— 子 Agent —————————————————————————————
class WorkerAgent:
    """
    一个同构子 Agent：负责抓取并搜索单个来源。
    通过消息总线接收 task_assigned / terminate，上报 status_update / result / ack。
    """

    def __init__(self, worker_id: str, source: Source, bus: MessageBus, question: str):
        self.id = worker_id
        self.source = source
        self.bus = bus
        self.question = question
        # 订阅：只关心发给自己或广播的 task_assigned 与 terminate
        self.sub = bus.subscribe(worker_id, types=["task_assigned", "terminate"])
        self._terminated = asyncio.Event()

    async def _report(self, state: TaskState, note: str = "", type: str = "status_update"):
        """向 Coordinator 推送一条状态更新（实时监控的 push 范式）。"""
        await self.bus.send(
            self.id,
            "coordinator",
            type,
            {"state": state.value, "note": note, "source": self.source.name},
        )

    async def _drain_signals(self) -> bool:
        """
        在安全点检查是否收到 terminate 信号（非阻塞）。
        收到则 ack 并返回 True，调用方据此优雅退出。
        """
        while not self.sub.inbox.empty():
            env = self.sub.inbox.get_nowait()
            if env.type == "terminate":
                self._terminated.set()
        if self._terminated.is_set():
            await self.bus.send(
                self.id, "coordinator", "ack",
                {"acked": "terminate", "source": self.source.name},
            )
            await self._report(TaskState.TERMINATED, "收到终止信号，安全退出")
            return True
        return False

    async def run(self):
        """
        Worker 主循环：分多步"抓取 + 搜索"，每步之间都检查终止信号。
        把单次抓取切成多步，是为了模拟真实 Computer Use Agent 的多轮操作，
        也给级联终止提供"安全检查点"。
        """
        # 等待 Coordinator 派发任务（task_assigned）
        env = await self.sub.get()
        while env.type != "task_assigned":
            env = await self.sub.get()
        await self._report(TaskState.RUNNING, "开始抓取来源")

        steps = 3  # 把抓取拆成 3 步，制造可被中断的检查点
        per_step = max(self.source.latency / steps, 0.05)
        collected = ""
        for i in range(1, steps + 1):
            # —— 安全检查点：先看有没有被要求终止 ——
            if await self._drain_signals():
                return
            # —— 执行一步抓取（模拟 Computer Use 的一轮操作耗时）——
            await asyncio.sleep(per_step)
            collected = self.source.content  # 抓到的文本，最后一步再判断是否命中
            await self._report(TaskState.RUNNING, f"抓取进度 {i}/{steps}")

        # 再次检查终止（可能在最后一步耗时里收到）
        if await self._drain_signals():
            return

        # —— 用（可选）LLM 或关键词判断是否命中答案 ——
        answer = await judge_answer(self.question, collected)
        if answer:
            # 命中：把结果发回 Coordinator（可能与别的 Worker 竞态）
            await self.bus.send(
                self.id, "coordinator", "result",
                {"found": True, "answer": answer, "source": self.source.name},
            )
            await self._report(TaskState.SUCCEEDED, f"命中：{answer}")
        else:
            await self.bus.send(
                self.id, "coordinator", "result",
                {"found": False, "source": self.source.name},
            )
            await self._report(TaskState.FAILED, "该来源未找到答案")


# ————————————————————————————— 主协调器 —————————————————————————————
class Coordinator:
    """
    中心协调器：并行派发子 Agent、维护状态表、结算首个命中、广播级联终止。
    """

    def __init__(self, bus: MessageBus, question: str):
        self.bus = bus
        self.question = question
        # 订阅所有子 Agent 上报的消息类型
        self.sub = bus.subscribe("coordinator", types=["status_update", "result", "ack"])
        self.table: Dict[str, TaskRecord] = {}
        self.workers: List[WorkerAgent] = []

        # —— 竞态处理的关键状态 ——
        self._settle_lock = asyncio.Lock()   # 保证结算与终止广播互斥
        self._settled = False                # 幂等标志：是否已结算过
        self.winner: Optional[str] = None    # 第一个命中的 Worker
        self.answer: Optional[str] = None
        self.duplicate_hits: List[str] = []  # 记录"迟到的命中"，证明竞态被正确忽略

        self._acks: set[str] = set()
        self._expected_workers = 0

    def add_worker(self, worker: WorkerAgent):
        self.workers.append(worker)
        self.table[worker.id] = TaskRecord(worker.id, worker.source.name)

    def _print_table(self, reason: str):
        """实时刷新并打印任务状态表。"""
        print(f"\n  ── 任务状态表（{reason}） ──")
        for rec in self.table.values():
            print(
                f"     {rec.worker_id:<10} 源={rec.source_name:<12} "
                f"状态={rec.state.value:<5} {('| ' + rec.note) if rec.note else ''}"
            )
        print()

    async def _dispatch(self):
        """并行派发：给每个 Worker 发 task_assigned。"""
        self._expected_workers = len(self.workers)
        for w in self.workers:
            self.table[w.id].state = TaskState.SUBMITTED
            await self.bus.send(
                "coordinator", w.id, "task_assigned",
                {"question": self.question, "source": w.source.name},
            )
        self._print_table("已派发全部子 Agent")

    async def _settle_if_first(self, worker_id: str, answer: str) -> bool:
        """
        竞态处理核心：用锁 + 幂等标志保证只结算一次、只广播一轮终止。
        返回 True 表示本次是"首个有效命中"。
        """
        async with self._settle_lock:
            if self._settled:
                # 迟到的命中：已结算过，直接忽略（幂等）
                self.duplicate_hits.append(worker_id)
                print(
                    f"  [竞态] {worker_id} 也命中，但已由 {self.winner} 结算 —— "
                    f"忽略此次命中，不重复广播终止。"
                )
                return False
            # 首个命中：结算并广播一轮终止
            self._settled = True
            self.winner = worker_id
            self.answer = answer
            print(f"  [结算] 首个命中来自 {worker_id} —— 加锁结算，广播一轮 terminate。")
            await self.bus.send(
                "coordinator", BROADCAST, "terminate",
                {"reason": "answer_found", "winner": worker_id},
            )
            return True

    async def run(self, quiet_period: float = 2.5) -> dict:
        """
        协调主循环：派发 -> 监听上报 -> 结算首个命中 -> 收集 ack -> 汇总。
        """
        mode = "LLM 判断" if llm_available() else "关键词判断（离线可复现）"
        print(f"  [协调器] 判断模式：{mode}\n")
        t0 = time.monotonic()  # 记录并行执行的墙钟起点
        await self._dispatch()

        # 启动所有 Worker 协程
        worker_tasks = [asyncio.create_task(w.run()) for w in self.workers]

        done_states = {TaskState.SUCCEEDED, TaskState.FAILED, TaskState.TERMINATED}
        last_terminate_time: Optional[float] = None

        while True:
            env = await self.sub.get_nowait_or_wait(timeout=0.5)
            if env is None:
                # 没有新消息：若已结算且过了静默期，认为收敛，退出
                if self._settled and last_terminate_time is not None:
                    if _now() - last_terminate_time > quiet_period:
                        break
                # 全部 Worker 进入终态也退出
                if all(r.state in done_states for r in self.table.values()):
                    break
                continue

            rec = self.table.get(env.sender_id)

            if env.type == "status_update" and rec:
                prev = rec.state
                rec.state = TaskState(env.payload["state"])
                rec.note = env.payload.get("note", "")
                rec.updated = _now()
                # 仅在"状态机跳变"时刷新状态表，避免每一步抓取都刷屏
                if rec.state != prev:
                    self._print_table(f"{env.sender_id} -> {rec.state.value}")

            elif env.type == "result":
                if env.payload.get("found"):
                    is_first = await self._settle_if_first(
                        env.sender_id, env.payload["answer"]
                    )
                    if is_first:
                        last_terminate_time = _now()

            elif env.type == "ack":
                self._acks.add(env.sender_id)
                print(f"  [ack] {env.sender_id} 已确认终止（{len(self._acks)} 个已 ack）")

        # 等待所有 Worker 协程收尾
        await asyncio.gather(*worker_tasks, return_exceptions=True)
        elapsed = time.monotonic() - t0  # 并行执行的墙钟耗时（含收敛静默期）
        self._print_table("最终状态")

        return {
            "winner": self.winner,
            "answer": self.answer,
            "duplicate_hits": self.duplicate_hits,
            "acks": sorted(self._acks),
            "settled_once": self._settled,
            "terminate_broadcasts": sum(
                1 for e in self.bus.history if e.type == "terminate"
            ),
            "parallel_seconds": elapsed,
        }


# ————————————————————————— 串行基线（性能对比） —————————————————————————
async def run_sequential(sources: List[Source], question: str) -> dict:
    """
    串行基线：逐个来源"抓取 + 判断"，命中即止。

    用于对照并行执行的墙钟收益（对应书中实验要求"记录并对比并行/串行时间差异"）。
    这里真实地一个接一个 ``await source.fetch()``，因此耗时是**实测**而非估算——
    绝不伪造数据；命中判断复用与并行版本相同的 :func:`judge_answer`。
    """
    t0 = time.monotonic()
    winner: Optional[str] = None
    answer: Optional[str] = None
    fetched = 0
    for src in sources:
        fetched += 1
        text = await src.fetch()
        ans = await judge_answer(question, text)
        if ans:
            winner, answer = src.name, ans
            break
    return {
        "seconds": time.monotonic() - t0,
        "winner": winner,
        "answer": answer,
        "fetched": fetched,
        "total": len(sources),
    }
