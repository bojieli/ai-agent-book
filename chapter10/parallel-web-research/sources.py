"""
模拟的"多个网站/信息源"
=======================

实验 10-6 强调的是"多个同构 Agent 并行搜索 + 中心协调"，浏览器本身不是重点，
因此这里用一批**可控的模拟数据源**代替真实浏览器：

- 每个 Source 对应一个"网站"，有名字、内容、以及一个可控的访问延迟；
- ``fetch()`` 模拟"打开网站并抓取"，用 ``asyncio.sleep`` 制造不同的耗时，
  让"谁先命中"变得可复现（也让级联终止/竞态现象稳定出现）；
- 是否包含目标答案由 ``holds_answer`` 决定。

延迟是刻意设计的：让两个源几乎同时命中，以此稳定地触发"竞态"演示。
"""

from __future__ import annotations

import asyncio
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Source:
    name: str            # "网站"名字
    latency: float       # 单步抓取延迟（秒），模拟网络/渲染耗时
    content: str         # 该网站的可搜索文本
    holds_answer: bool   # 该网站是否真的包含目标答案

    async def fetch(self) -> str:
        """模拟一次抓取：等待 latency 后返回内容。"""
        await asyncio.sleep(self.latency)
        return self.content


# —— 演示任务：并行查找"世界上最高的山峰是哪座、海拔多少" ——
# 只有部分源包含准确答案；两个正确源的延迟被设计得很接近，用来制造竞态。
QUESTION = "世界上海拔最高的山峰是哪座？海拔约多少米？"
ANSWER_KEYWORDS = ["珠穆朗玛", "珠峰", "Everest", "8848"]

DEMO_SOURCES: List[Source] = [
    Source("baike-wiki", 0.9, "百科条目：喜马拉雅山脉横亘于青藏高原南缘。", False),
    Source("news-portal", 1.1, "新闻门户：近期多支登山队计划攀登高海拔山峰。", False),
    Source("geo-journal", 0.6, "地理期刊：世界最高峰为珠穆朗玛峰，海拔约 8848 米，位于中尼边境。", True),
    Source("travel-blog", 1.4, "旅行博客：作者分享了在尼泊尔徒步大本营的见闻。", False),
    # 与 geo-journal 完全相同的延迟：两个正确源会几乎同一时刻命中，稳定触发竞态。
    Source("forum-qa", 0.6, "问答社区：网友讨论最高峰其实是珠穆朗玛峰，官方海拔 8848.86 米。", True),
    Source("edu-site", 1.2, "教育网站：介绍板块运动如何抬升出高大的山脉。", False),
    Source("gov-data", 1.6, "政府数据：发布了若干山峰的测绘参数与坐标信息。", False),
    Source("random-blog", 0.8, "个人博客：随笔记录了一次雪山摄影旅行。", False),
    Source("science-mag", 1.3, "科普杂志：解释高海拔缺氧对人体的影响。", False),
    Source("map-service", 1.0, "地图服务：可查询各山峰的等高线与地形剖面。", False),
]


def keyword_judge(text: str) -> Optional[str]:
    """
    可控的"判断是否命中答案"逻辑（不依赖 LLM）：
    命中任一关键词即认为找到了答案，返回抽取到的答案句子；否则返回 None。
    """
    for kw in ANSWER_KEYWORDS:
        if kw in text:
            # 简单地把包含关键词的那句话当作答案返回
            for sentence in text.replace("。", "。\n").splitlines():
                if kw in sentence:
                    return sentence.strip("：: ")
            return text
    return None


def build_sources(n: int) -> List[Source]:
    """
    构造 n 个并行来源，供命令行 ``--agents N`` 动态调整并行 Agent 数量。

    设计约束（保证演示始终可复现）：
    - n == 10 时**原样返回** ``DEMO_SOURCES``，默认行为与之前完全一致；
    - n >= 2 时始终包含两个"含答案且延迟相同"的源（geo-journal / forum-qa），
      从而稳定触发命中、竞态与级联终止；
    - 其余用无答案的填充源补齐；n 超过内置源数量时循环生成并加序号后缀。
    """
    if n < 1:
        raise ValueError("并行 Agent 数量至少为 1")
    if n == len(DEMO_SOURCES):
        return list(DEMO_SOURCES)

    answer_pool = [s for s in DEMO_SOURCES if s.holds_answer]
    filler_pool = [s for s in DEMO_SOURCES if not s.holds_answer]
    k_answer = min(len(answer_pool), 2 if n >= 2 else 1)
    n_filler = n - k_answer

    fillers: List[Source] = []
    seen: dict = {}
    for i in range(n_filler):
        base = filler_pool[i % len(filler_pool)]
        seen[base.name] = seen.get(base.name, 0) + 1
        name = base.name if seen[base.name] == 1 else f"{base.name}-{seen[base.name]}"
        fillers.append(Source(name, base.latency, base.content, False))

    sources = fillers
    # 把含答案的源插入到确定的位置（沿用默认布局：靠前但不在最前，便于观察并行推进）
    for j, src in enumerate(answer_pool[:k_answer]):
        pos = min(2 + 2 * j, len(sources))
        sources.insert(pos, Source(src.name, src.latency, src.content, src.holds_answer))
    return sources
