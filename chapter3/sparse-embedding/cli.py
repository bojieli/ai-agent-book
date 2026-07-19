#!/usr/bin/env python3
"""
稀疏检索命令行工具（实验 3-5）

在一个小型示例语料上运行 BM25 稀疏检索，支持：
  - 自定义语料 / 查询 / top-k / 输出文件
  - --explain 复现书中"逐词 IDF / TF / BM25 贡献"的日志
  - --eval 在带标注的小型评测集上计算 recall@k / precision@k / MRR
  - --method splade 学习型稀疏检索（需要下载模型，离线环境会给出提示）

不带任何参数运行时，等价于书中实验 3-5 的默认演示（查询"model distillation"）。
"""

import argparse
import json
import logging
import sys
from typing import Dict, List, Optional, Set, Tuple

from bm25_engine import SparseSearchEngine


# ---------------------------------------------------------------------------
# 内置示例语料与标注（英文，与引擎的分词器能力一致，可完全离线复现）
# 语料刻意混合了：普通词、专有代码、技术缩写、以及只有"同义表达"的文档，
# 用来同时展示 BM25 在精确关键词匹配上的强项与在同义词上的短板。
# ---------------------------------------------------------------------------
DEFAULT_CORPUS: List[Dict] = [
    {"doc_id": "doc_1", "title": "Python Language",
     "text": "Python is a high-level programming language known for readability and a simple syntax."},
    {"doc_id": "doc_2", "title": "JavaScript Runtime",
     "text": "JavaScript runs in the browser and on servers via Node.js for full-stack web development."},
    {"doc_id": "doc_3", "title": "Model Distillation",
     "text": "Model distillation compresses a large teacher model into a smaller student model while preserving accuracy."},
    {"doc_id": "doc_4", "title": "Knowledge Distillation",
     "text": "Knowledge distillation transfers knowledge from a big neural network to a compact model for efficient inference."},
    {"doc_id": "doc_5", "title": "BM25 Ranking",
     "text": "BM25 is a probabilistic ranking function using term frequency and inverse document frequency."},
    {"doc_id": "doc_6", "title": "HTTP Errors",
     "text": "The HTTP 404 error code means the requested resource was not found on the web server."},
    {"doc_id": "doc_7", "title": "A Playful Kitten",
     "text": "A cute kitten chased a ball of yarn across the living room floor all afternoon."},
    {"doc_id": "doc_8", "title": "Silent Hunter",
     "text": "The feline predator stalked its prey silently through the tall grass at dusk."},
    {"doc_id": "doc_9", "title": "Hardware Fault",
     "text": "Error code XK9-2B4-7Q1 indicates a hardware fault in the storage controller board."},
    {"doc_id": "doc_10", "title": "Transformers",
     "text": "Transformer models use self-attention to process input sequences in parallel efficiently."},
]

# query -> 相关文档 doc_id 集合（人工标注的 ground truth）
DEFAULT_LABELS: Dict[str, List[str]] = {
    "model distillation": ["doc_3", "doc_4"],
    "HTTP 404 error": ["doc_6"],
    "XK9-2B4-7Q1": ["doc_9"],
    "BM25 ranking function": ["doc_5"],
    # 相关文档用 kitten / feline 表达"猫"，故意不含字面 "cat"，
    # 用于演示稀疏检索读不懂同义词的短板（BM25 会漏召回）。
    "cat": ["doc_7", "doc_8"],
}

DEFAULT_QUERY = "model distillation"


def _quiet_logging(verbose: bool) -> None:
    """默认压低引擎日志；--verbose / --explain 时放开到 DEBUG 以展示计算过程。"""
    level = logging.DEBUG if verbose else logging.WARNING
    logging.getLogger().setLevel(level)
    logging.getLogger("bm25_engine").setLevel(level)


def load_corpus(path: Optional[str]) -> List[Dict]:
    """加载语料。支持 .json（文档数组）与 .jsonl（每行一个文档）。"""
    if not path:
        return DEFAULT_CORPUS
    docs: List[Dict] = []
    with open(path, "r", encoding="utf-8") as f:
        if path.endswith(".jsonl"):
            for line in f:
                line = line.strip()
                if line:
                    docs.append(json.loads(line))
        else:
            data = json.load(f)
            docs = data["documents"] if isinstance(data, dict) else data
    if not docs:
        raise ValueError(f"语料文件为空：{path}")
    return docs


def load_labels(path: Optional[str]) -> Dict[str, List[str]]:
    """加载评测标注：{query: [relevant_doc_id, ...]}。"""
    if not path:
        return DEFAULT_LABELS
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def build_engine(corpus: List[Dict], k1: float, b: float) -> SparseSearchEngine:
    """把语料灌进引擎；用给定的 k1/b 重建 BM25。"""
    engine = SparseSearchEngine()
    engine.index_batch([
        {"text": d["text"],
         "doc_id": d.get("doc_id"),
         "metadata": {"title": d.get("title", "")}}
        for d in corpus
    ])
    # index_batch 内部每篇都会重建 BM25，这里再显式用目标参数固定一次
    from bm25_engine import BM25
    engine.bm25 = BM25(engine.index, k1=k1, b=b)
    return engine


def explain_result(engine: SparseSearchEngine, query: str, doc_id: str) -> List[Tuple[str, int, int, float, float]]:
    """复现书中日志：对命中文档，逐个查询词给出 TF / 文档长度 / IDF / BM25 贡献。"""
    from bm25_engine import TextProcessor
    internal = engine.external_to_internal[doc_id]
    terms = TextProcessor().tokenize(query)
    rows = []
    for term in terms:
        tf = engine.index.term_frequency[internal].get(term, 0)
        if tf == 0:
            continue
        dl = engine.index.doc_lengths[internal]
        idf = engine.bm25.calculate_idf(term)
        contrib = engine.bm25.calculate_term_score(term, internal)
        rows.append((term, tf, dl, idf, contrib))
    return rows


def run_search(engine: SparseSearchEngine, query: str, top_k: int,
               explain: bool) -> List[Dict]:
    """执行单条查询并打印结果，返回结构化结果供 --output 落盘。"""
    results = engine.search(query, top_k=top_k)
    print(f"\n查询: '{query}'  (BM25, top-{top_k})")
    print("-" * 60)
    if not results:
        print("  没有命中任何文档（所有查询词都不在倒排索引中）。")
        return []
    out = []
    for rank, r in enumerate(results, 1):
        title = r["metadata"].get("title", "")
        print(f"  #{rank}  {r['doc_id']}  score={r['score']:.4f}  {title}")
        print(f"       命中词: {r['debug']['matched_terms']}")
        print(f"       预览: {r['text'][:80]}...")
        if explain:
            rows = explain_result(engine, query, r["doc_id"])
            for term, tf, dl, idf, contrib in rows:
                print(f"         └ '{term}': TF={tf}, 文档长度={dl}词, "
                      f"IDF={idf:.4f}, BM25贡献={contrib:.4f}")
        out.append({
            "rank": rank,
            "doc_id": r["doc_id"],
            "score": r["score"],
            "title": title,
            "matched_terms": r["debug"]["matched_terms"],
        })
    return out


def _metrics_for_query(retrieved: List[str], relevant: Set[str], k: int) -> Dict:
    """单条查询的 recall@k / precision@k / 命中排名（用于 MRR）。"""
    topk = retrieved[:k]
    hits = [d for d in topk if d in relevant]
    recall = len(set(hits)) / len(relevant) if relevant else 0.0
    precision = len(hits) / len(topk) if topk else 0.0
    rr = 0.0
    for i, d in enumerate(retrieved, 1):
        if d in relevant:
            rr = 1.0 / i
            break
    return {"recall": recall, "precision": precision, "rr": rr,
            "hits": hits, "retrieved": topk}


def run_eval(engine: SparseSearchEngine, labels: Dict[str, List[str]],
             k: int) -> Dict:
    """在标注集上做检索评测，打印每条查询指标 + 宏平均。"""
    print(f"\n{'='*60}")
    print(f"检索质量评测 (recall@{k} / precision@{k} / MRR)")
    print(f"{'='*60}")
    per_query = {}
    sum_recall = sum_prec = sum_rr = 0.0
    for query, rel_list in labels.items():
        relevant = set(rel_list)
        results = engine.search(query, top_k=max(k, 10))
        retrieved = [r["doc_id"] for r in results]
        m = _metrics_for_query(retrieved, relevant, k)
        per_query[query] = m
        sum_recall += m["recall"]
        sum_prec += m["precision"]
        sum_rr += m["rr"]
        flag = "" if m["recall"] > 0 else "   <- 漏召回(同义词短板)" if query == "cat" else "   <- 漏召回"
        print(f"\n查询 '{query}'  相关文档={sorted(relevant)}")
        print(f"  召回排序: {retrieved[:k]}")
        print(f"  recall@{k}={m['recall']:.2f}  precision@{k}={m['precision']:.2f}  RR={m['rr']:.2f}{flag}")
    n = len(labels)
    macro = {
        "recall@k": sum_recall / n,
        "precision@k": sum_prec / n,
        "mrr": sum_rr / n,
        "miss_rate@k": 1.0 - sum_recall / n,
    }
    print(f"\n{'-'*60}")
    print(f"宏平均  recall@{k}={macro['recall@k']:.3f}  "
          f"precision@{k}={macro['precision@k']:.3f}  "
          f"MRR={macro['mrr']:.3f}  漏召回率(1-recall@{k})={macro['miss_rate@k']:.3f}")
    return {"k": k, "per_query": {q: {kk: vv for kk, vv in m.items() if kk != "retrieved"}
                                  for q, m in per_query.items()},
            "macro": macro}


def run_splade(query: str, corpus: List[Dict], top_k: int) -> Optional[List[Dict]]:
    """学习型稀疏检索（SPLADE）。需要 transformers + torch + 预训练模型。

    离线环境无法下载模型时，会打印清晰提示并返回 None（不影响参数解析验证）。
    """
    model_name = "naver/splade-cocondenser-ensembledistil"
    try:
        import torch  # noqa: F401
        from transformers import AutoModelForMaskedLM, AutoTokenizer
    except Exception as e:
        print("\n[SPLADE] 需要依赖 transformers 与 torch，当前环境缺失：", e)
        print("        安装：pip install torch transformers")
        print("        （BM25 路径无需任何模型，可完全离线运行）")
        return None
    try:
        # 只用本地缓存加载，避免离线环境卡在无休止的网络下载上。
        print(f"\n[SPLADE] 尝试从本地缓存加载模型 {model_name} ...")
        tokenizer = AutoTokenizer.from_pretrained(model_name, local_files_only=True)
        model = AutoModelForMaskedLM.from_pretrained(model_name, local_files_only=True)
        model.eval()
    except Exception:
        print(f"\n[SPLADE] 本地缓存中没有模型 {model_name}，且离线环境无法下载权重。")
        print("        请先在联网环境执行一次以下命令把模型缓存到本地，再重跑本命令：")
        print(f"          huggingface-cli download {model_name}")
        print("        （BM25 路径不依赖任何模型，可完全离线复现书中实验 3-5）")
        return None

    import torch

    def encode(text: str) -> Dict[str, float]:
        inputs = tokenizer(text, return_tensors="pt", truncation=True, max_length=256)
        with torch.no_grad():
            logits = model(**inputs).logits  # [1, seq, vocab]
        # SPLADE: log(1+ReLU(logits)) 后在序列维做 max-pool，得到词表维稀疏权重
        weights = torch.max(
            torch.log1p(torch.relu(logits)) * inputs["attention_mask"].unsqueeze(-1),
            dim=1,
        ).values.squeeze(0)
        nz = torch.nonzero(weights).squeeze(-1)
        return {int(i): float(weights[i]) for i in nz}

    q_vec = encode(query)
    scored = []
    for d in corpus:
        d_vec = encode(d["text"])
        score = sum(w * d_vec.get(t, 0.0) for t, w in q_vec.items())
        scored.append((d.get("doc_id"), score, d.get("title", "")))
    scored.sort(key=lambda x: x[1], reverse=True)
    print(f"\n查询: '{query}'  (SPLADE, top-{top_k})")
    print("-" * 60)
    out = []
    for rank, (doc_id, score, title) in enumerate(scored[:top_k], 1):
        print(f"  #{rank}  {doc_id}  score={score:.4f}  {title}")
        out.append({"rank": rank, "doc_id": doc_id, "score": score, "title": title})
    return out


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="稀疏检索命令行工具（实验 3-5）：在小型语料上运行 BM25 / SPLADE 稀疏检索并评测检索质量。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  python cli.py                                  # 默认演示（查询 "model distillation"）
  python cli.py -q "HTTP 404 error" --explain    # 展示逐词 TF/IDF/BM25 贡献
  python cli.py --eval                           # 在标注集上算 recall/precision/MRR
  python cli.py -q "cat"                          # 观察 BM25 的同义词短板
  python cli.py --corpus my.json -q "..." -o out.json
  python cli.py --method splade -q "model distillation"   # 学习型稀疏检索（需模型）
""",
    )
    parser.add_argument("-q", "--query", default=DEFAULT_QUERY,
                        help=f"查询字符串（默认: '{DEFAULT_QUERY}'）")
    parser.add_argument("-c", "--corpus", default=None,
                        help="语料文件路径（.json 文档数组 或 .jsonl 每行一篇）；缺省用内置示例语料")
    parser.add_argument("-m", "--method", choices=["bm25", "splade"], default="bm25",
                        help="检索方法：bm25(默认,离线) 或 splade(学习型稀疏,需下载模型)")
    parser.add_argument("-k", "--top-k", type=int, default=5,
                        help="返回前 k 条结果（默认: 5）")
    parser.add_argument("-o", "--output", default=None,
                        help="把结果/评测指标以 JSON 写入该文件")
    parser.add_argument("--eval", action="store_true",
                        help="在标注集上评测 recall@k / precision@k / MRR，而非只跑单条查询")
    parser.add_argument("--labels", default=None,
                        help="评测标注文件 {query: [相关doc_id,...]}；缺省用内置标注")
    parser.add_argument("--explain", action="store_true",
                        help="对每条命中文档展示逐词 TF/IDF/BM25 贡献（复现书中日志）")
    parser.add_argument("--k1", type=float, default=1.5,
                        help="BM25 词频饱和参数 k1（默认: 1.5）")
    parser.add_argument("-b", "--b", type=float, default=0.75,
                        help="BM25 文档长度归一化参数 b（默认: 0.75）")
    parser.add_argument("-v", "--verbose", action="store_true",
                        help="打开引擎 DEBUG 日志（展示分词、倒排索引构建、打分全过程）")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    _quiet_logging(args.verbose)

    corpus = load_corpus(args.corpus)
    print(f"已加载语料：{len(corpus)} 篇文档"
          + ("（内置示例）" if not args.corpus else f"（来自 {args.corpus}）"))

    payload: Dict = {"method": args.method, "query": args.query, "top_k": args.top_k}

    if args.method == "splade":
        results = run_splade(args.query, corpus, args.top_k)
        if results is None:
            return 0  # 已给出模型缺失提示，视为正常退出
        payload["results"] = results
    else:
        engine = build_engine(corpus, k1=args.k1, b=args.b)
        print(f"BM25 参数：k1={args.k1}, b={args.b}, avgdl={engine.bm25.avgdl:.2f}")
        if args.eval:
            labels = load_labels(args.labels)
            payload["eval"] = run_eval(engine, labels, args.top_k)
        else:
            payload["results"] = run_search(engine, args.query, args.top_k, args.explain)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n已写入结果：{args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
