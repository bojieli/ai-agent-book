# -*- coding: utf-8 -*-
"""信息可见性审计（Information Visibility Audit）。

这是本实验「信息权限控制可验证」的核心工具：法官每向某个（或某些）玩家的
上下文投递一条信息时，都会在这里登记一条记录——这条信息属于哪个类别、内容
摘要是什么、**进入了谁的上下文**。游戏结束后打印这张审计表，即可客观证明
信息隔离是否正确（例如「狼人队友身份」只进狼人上下文、「预言家查验结果」只进
预言家本人上下文、「公开发言」进所有人上下文）。
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class AuditRecord:
    round_no: int          # 第几回合
    phase: str             # 阶段（夜晚/白天/...）
    category: str          # 信息类别（如「狼人队友身份」「预言家查验结果」「公开发言」）
    content: str           # 信息内容摘要
    visible_to: List[str]  # 该信息进入了哪些玩家的上下文（玩家名列表）


@dataclass
class AuditLog:
    records: List[AuditRecord] = field(default_factory=list)

    def add(self, round_no, phase, category, content, visible_to):
        self.records.append(AuditRecord(round_no, phase, category, content, list(visible_to)))

    def print_table(self, all_players):
        """打印完整的信息可见性审计表。"""
        print("\n" + "=" * 78)
        print("信息可见性审计表（每条信息进入了谁的上下文）")
        print("=" * 78)
        header = f"{'回合':<4}{'阶段':<6}{'类别':<14}{'可见玩家':<20}内容"
        print(header)
        print("-" * 78)
        for r in self.records:
            vis = "所有人" if set(r.visible_to) == set(all_players) else "、".join(r.visible_to)
            content = r.content if len(r.content) <= 30 else r.content[:29] + "…"
            print(f"{r.round_no:<5}{r.phase:<7}{r.category:<15}{vis:<21}{content}")
        print("=" * 78)
