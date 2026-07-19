"""离线对比实验：智能体化 RAG（多轮/分解检索）vs 非智能体化 RAG（单次检索）。

本脚本**完全离线运行**——只做检索、不调用任何 LLM、不依赖外部检索服务，
因此无需 API Key 即可复现。它在一个小型中文司法问答集（evaluation/offline_qa.json）
上，量化对比两种检索范式的『证据召回率』：

  - 非智能体化：把用户原始问题作为唯一查询做一次检索（single-shot）；
  - 智能体化：模拟 Agent 分解/改写问题后发起多次检索，再对结果取并集。

金标准（gold_articles）为回答每个问题所必需的法条编号；某法条被判定为『命中』
当且仅当检索结果中存在一个以该法条编号开头的分块。证据召回率 = 命中金标准法条数
/ 金标准法条总数。这一检索层指标是回答质量的上界：检索不到证据，生成阶段就无从
谈起。生成阶段的端到端评测（需要 LLM API）见 evaluation/evaluate.py。
"""

import os
import re
import sys
import json
import time
import argparse
from typing import List, Dict, Any

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from offline_retriever import OfflineRetriever, _ARTICLE_RE


def _leading_article(text: str) -> str:
    """抽取分块开头的法条编号（如『第二百三十五条』），无则返回空串。"""
    m = _ARTICLE_RE.match(text.strip())
    return m.group(0) if m else ""


def _covered(retrieved: List[Dict[str, Any]], gold_articles: List[str]) -> List[str]:
    """返回被检索结果命中的金标准法条列表。"""
    hit_markers = {_leading_article(r["text"]) for r in retrieved}
    hit_markers.discard("")
    return [g for g in gold_articles if g in hit_markers]


def run_case(retriever: OfflineRetriever, case: Dict[str, Any], top_k: int) -> Dict[str, Any]:
    gold = case["gold_articles"]

    # 非智能体化：单次检索，查询即用户原始问题。
    naive_query = case.get("naive_query", case["question"])
    naive_hits = retriever.search(naive_query, top_k)
    naive_covered = _covered(naive_hits, gold)

    # 智能体化：分解为多个子查询，逐一检索后取并集。
    subqueries = case.get("subqueries") or [case["question"]]
    agentic_hits: List[Dict[str, Any]] = []
    seen = set()
    for sq in subqueries:
        for r in retriever.search(sq, top_k):
            if r["chunk_id"] not in seen:
                seen.add(r["chunk_id"])
                agentic_hits.append(r)
    agentic_covered = _covered(agentic_hits, gold)

    return {
        "id": case["id"],
        "question": case["question"],
        "difficulty": case.get("difficulty", "unknown"),
        "gold_articles": gold,
        "naive": {
            "num_searches": 1,
            "covered": naive_covered,
            "recall": len(naive_covered) / len(gold) if gold else 0.0,
        },
        "agentic": {
            "num_searches": len(subqueries),
            "covered": agentic_covered,
            "recall": len(agentic_covered) / len(gold) if gold else 0.0,
        },
    }


def _mean(xs: List[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def _pad(text: str, width: int) -> str:
    """按显示宽度左对齐（一个中文字符按两个宽度计）。"""
    display = sum(2 if ord(c) > 127 else 1 for c in text)
    return text + " " * max(0, width - display)


def summarize(results: List[Dict[str, Any]]) -> Dict[str, Any]:
    def agg(subset):
        return {
            "count": len(subset),
            "naive_recall": _mean([r["naive"]["recall"] for r in subset]),
            "agentic_recall": _mean([r["agentic"]["recall"] for r in subset]),
            "naive_searches": _mean([r["naive"]["num_searches"] for r in subset]),
            "agentic_searches": _mean([r["agentic"]["num_searches"] for r in subset]),
        }

    summary = {"overall": agg(results)}
    for diff in ("easy", "hard"):
        subset = [r for r in results if r["difficulty"] == diff]
        if subset:
            summary[diff] = agg(subset)
    return summary


def print_table(results: List[Dict[str, Any]], summary: Dict[str, Any]):
    print("\n" + "=" * 78)
    print("离线检索对比：证据召回率（Evidence Recall）")
    print("=" * 78)
    print(_pad("问题", 30) + _pad("难度", 8) + _pad("单次检索", 12)
          + _pad("分解检索", 12) + "检索次数")
    print("-" * 78)
    for r in results:
        q = (r["question"][:13] + "…") if len(r["question"]) > 13 else r["question"]
        naive = f"{r['naive']['recall']:.0%}"
        agentic = f"{r['agentic']['recall']:.0%}"
        searches = f"1 → {r['agentic']['num_searches']}"
        print(_pad(q, 30) + _pad(r["difficulty"], 8) + _pad(naive, 12)
              + _pad(agentic, 12) + searches)
    print("-" * 78)

    def row(name, s):
        print(_pad(name, 30) + _pad("", 8) + _pad(f"{s['naive_recall']:.0%}", 12)
              + _pad(f"{s['agentic_recall']:.0%}", 12)
              + f"{s['naive_searches']:.1f} → {s['agentic_searches']:.1f}")

    print("聚合指标（平均证据召回率）:")
    row("  全部", summary["overall"])
    if "easy" in summary:
        row("  简单题", summary["easy"])
    if "hard" in summary:
        row("  复杂题", summary["hard"])
    print("=" * 78)
    ov = summary["overall"]
    lift = ov["agentic_recall"] - ov["naive_recall"]
    print(f"结论：分解式多轮检索将整体证据召回率从 {ov['naive_recall']:.0%} "
          f"提升到 {ov['agentic_recall']:.0%}（+{lift:.0%}），"
          f"代价是平均检索次数由 {ov['naive_searches']:.1f} 增至 {ov['agentic_searches']:.1f}。")
    if "hard" in summary:
        hv = summary["hard"]
        print(f"      复杂题上的差距最为显著：{hv['naive_recall']:.0%} → {hv['agentic_recall']:.0%}。")
    print("=" * 78)


def main():
    parser = argparse.ArgumentParser(
        description="离线对比智能体化 RAG（多轮分解检索）与非智能体化 RAG（单次检索）的证据召回率；纯检索、无需 LLM 与外部服务。",
        formatter_class=argparse.RawTextHelpFormatter,
    )
    parser.add_argument("--dataset", type=str, default="evaluation/offline_qa.json",
                        help="离线问答数据集路径（默认：evaluation/offline_qa.json）")
    parser.add_argument("--corpus", type=str, default="laws",
                        help="法律语料目录，用于构建离线 BM25 索引（默认：laws）")
    parser.add_argument("--top-k", type=int, default=5,
                        help="每次检索返回的分块数量，即检索深度（默认：5）")
    parser.add_argument("--output", type=str, default=None,
                        help="将详细结果写入的 JSON 文件路径（默认：不落盘，仅打印）")
    args = parser.parse_args()

    print(f"[离线对比] 构建 BM25 索引，语料目录：{args.corpus} …")
    t0 = time.time()
    retriever = OfflineRetriever(args.corpus)
    print(f"[离线对比] 索引完成：{len(retriever.chunks)} 个法条分块 / "
          f"{len(retriever.documents)} 篇文档，用时 {time.time() - t0:.1f}s")

    with open(args.dataset, "r", encoding="utf-8") as f:
        dataset = json.load(f)
    cases = dataset["cases"]

    results = [run_case(retriever, c, args.top_k) for c in cases]
    summary = summarize(results)
    print_table(results, summary)

    if args.output:
        payload = {
            "dataset": args.dataset,
            "corpus": args.corpus,
            "top_k": args.top_k,
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": results,
            "summary": summary,
        }
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n详细结果已保存至：{args.output}")


if __name__ == "__main__":
    main()
