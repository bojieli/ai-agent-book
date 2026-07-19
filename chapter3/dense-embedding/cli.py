#!/usr/bin/env python3
"""
稠密检索命令行工具（实验 3-4）

在一个小型示例语料上运行稠密嵌入检索，支持：
  - 自定义语料 / 查询 / top-k / 输出文件
  - --eval：在带标注的小型评测集上计算 recall@k / precision@k / MRR，
            直观展示"稠密嵌入读得懂同义表达"这一核心卖点
  - --compare-ann：复现书中实验 3-4 的重点——对比 ANNOY 与 HNSW 两种 ANN 后端
            相对精确暴力检索的召回率、建索引耗时与查询延迟（复用服务端 indexing.py）
  - --embedding-model：可切换嵌入模型；默认 BAAI/bge-m3，离线可用已缓存的
            sentence-transformers/all-MiniLM-L6-v2

不带任何参数运行时，等价于书中实验 3-4 的默认演示（查询 "a cat playing"）。
--compare-ann 使用合成向量、无需任何模型，可在完全离线环境下复现 ANN 对比。
"""

import argparse
import json
import sys
import time
from typing import Dict, List, Optional, Set

import numpy as np

from indexing import AnnoyIndex, HNSWIndex


# ---------------------------------------------------------------------------
# 内置示例语料与标注（英文，与常见句向量模型能力一致，可完全离线复现）
# 语料刻意加入了"同义表达"文档（kitten / feline 表示 cat，distillation 的两种写法），
# 用来展示稠密检索在语义匹配上的强项——这些正是稀疏 BM25（实验 3-5）会漏召回的场景。
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
    {"doc_id": "doc_11", "title": "Deep Learning",
     "text": "Deep learning stacks many layers of neurons to extract hierarchical features from raw data."},
    {"doc_id": "doc_12", "title": "Gradient Descent",
     "text": "Gradient descent minimizes a loss function by iteratively updating the model parameters."},
]

# query -> 相关文档 doc_id 集合（人工标注的 ground truth）
# 这些查询大多不与相关文档共享字面关键词，只在语义上相关——考的正是稠密检索的语义能力。
DEFAULT_LABELS: Dict[str, List[str]] = {
    # kitten / feline 都不含字面 "cat"，稠密检索应凭语义召回，稀疏 BM25 则会漏
    "a cat playing": ["doc_7", "doc_8"],
    # "蒸馏"的两种写法，语义同一主题
    "model distillation": ["doc_3", "doc_4"],
    # 语义相关，字面不含 "neural network training"
    "training neural networks": ["doc_11", "doc_12"],
    "self attention in sequence models": ["doc_10"],
    "web server resource not found": ["doc_6"],
}

DEFAULT_QUERY = "a cat playing"

DEFAULT_MODEL = "BAAI/bge-m3"
OFFLINE_HINT_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ---------------------------------------------------------------------------
# 稠密嵌入编码器：用 transformers 的 AutoModel 直接算句向量（mean / cls 池化 + L2 归一化）
# 这样既能加载书中默认的 BAAI/bge-m3（bge 系用 cls 池化），也能加载离线已缓存的
# sentence-transformers/all-MiniLM-L6-v2（mean 池化），无需依赖 FlagEmbedding。
# ---------------------------------------------------------------------------
class DenseEncoder:
    def __init__(self, model_name: str, pooling: str = "auto",
                 device: str = "cpu", max_length: int = 512):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.model_name = model_name
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModel.from_pretrained(model_name)
        self.model.eval().to(device)
        self.device = device
        self.max_length = max_length
        if pooling == "auto":
            # bge / bge-m3 的稠密向量取 [CLS]；多数 sentence-transformers 模型用平均池化
            pooling = "cls" if "bge" in model_name.lower() else "mean"
        self.pooling = pooling

    def encode(self, texts: List[str], batch_size: int = 16) -> np.ndarray:
        vecs: List[np.ndarray] = []
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            enc = self.tokenizer(batch, padding=True, truncation=True,
                                 max_length=self.max_length, return_tensors="pt").to(self.device)
            with self.torch.no_grad():
                out = self.model(**enc)
            if self.pooling == "cls":
                emb = out.last_hidden_state[:, 0]
            else:
                mask = enc["attention_mask"].unsqueeze(-1).float()
                emb = (out.last_hidden_state * mask).sum(1) / mask.sum(1).clamp(min=1e-9)
            emb = self.torch.nn.functional.normalize(emb, p=2, dim=1)
            vecs.append(emb.cpu().numpy().astype("float32"))
        return np.vstack(vecs)


def load_encoder(model_name: str, pooling: str, device: str) -> Optional["DenseEncoder"]:
    """加载稠密编码器。离线且模型未缓存时给出清晰提示并返回 None（不影响参数解析验证）。"""
    try:
        import torch  # noqa: F401
        from transformers import AutoModel  # noqa: F401
    except Exception as e:
        print("\n[稠密编码] 需要依赖 transformers 与 torch，当前环境缺失：", e)
        print("        安装：pip install torch transformers")
        print("        （--compare-ann 使用合成向量，无需任何模型，可完全离线运行）")
        return None
    try:
        print(f"正在加载嵌入模型 {model_name}（pooling={pooling}, device={device}）...")
        t0 = time.time()
        encoder = DenseEncoder(model_name, pooling=pooling, device=device)
        print(f"模型加载完成，耗时 {time.time() - t0:.1f}s，池化方式 ={encoder.pooling}")
        return encoder
    except Exception as e:
        print(f"\n[稠密编码] 无法加载模型 {model_name}：{e}")
        print(f"        离线环境无法下载 {model_name} 权重（BGE-M3 约 2.3GB）。")
        print(f"        可改用已缓存的小模型：--embedding-model {OFFLINE_HINT_MODEL}")
        print("        或先在联网环境预缓存目标模型；--compare-ann 则完全无需模型。")
        return None


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


# ---------------------------------------------------------------------------
# 稠密检索（精确暴力，用于单条查询与检索质量评测）
# ---------------------------------------------------------------------------
def dense_rank(query_vec: np.ndarray, doc_matrix: np.ndarray) -> List[int]:
    """向量已 L2 归一化，余弦相似度即点积；返回按相似度降序的文档下标。"""
    sims = doc_matrix @ query_vec
    return list(np.argsort(-sims)), sims


def run_search(encoder: "DenseEncoder", corpus: List[Dict], doc_matrix: np.ndarray,
               query: str, top_k: int) -> List[Dict]:
    """执行单条稠密查询并打印结果，返回结构化结果供 --output 落盘。"""
    q = encoder.encode([query])[0]
    order, sims = dense_rank(q, doc_matrix)
    print(f"\n查询: '{query}'  (稠密检索, top-{top_k})")
    print("-" * 60)
    out = []
    for rank, idx in enumerate(order[:top_k], 1):
        d = corpus[idx]
        title = d.get("title", "")
        print(f"  #{rank}  {d.get('doc_id')}  cos={float(sims[idx]):.4f}  {title}")
        print(f"       预览: {d['text'][:80]}...")
        out.append({
            "rank": rank,
            "doc_id": d.get("doc_id"),
            "score": float(sims[idx]),
            "title": title,
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


def run_eval(encoder: "DenseEncoder", corpus: List[Dict], doc_matrix: np.ndarray,
             labels: Dict[str, List[str]], k: int) -> Dict:
    """在标注集上做稠密检索评测，打印每条查询指标 + 宏平均。"""
    doc_ids = [d.get("doc_id") for d in corpus]
    print(f"\n{'=' * 60}")
    print(f"稠密检索质量评测 (recall@{k} / precision@{k} / MRR)")
    print(f"{'=' * 60}")
    per_query = {}
    sum_recall = sum_prec = sum_rr = 0.0
    q_vecs = encoder.encode(list(labels.keys()))
    for (query, rel_list), qv in zip(labels.items(), q_vecs):
        relevant = set(rel_list)
        order, _ = dense_rank(qv, doc_matrix)
        retrieved = [doc_ids[i] for i in order]
        m = _metrics_for_query(retrieved, relevant, k)
        per_query[query] = m
        sum_recall += m["recall"]
        sum_prec += m["precision"]
        sum_rr += m["rr"]
        flag = "" if m["recall"] > 0 else "   <- 漏召回"
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
    print(f"\n{'-' * 60}")
    print(f"宏平均  recall@{k}={macro['recall@k']:.3f}  "
          f"precision@{k}={macro['precision@k']:.3f}  "
          f"MRR={macro['mrr']:.3f}  漏召回率(1-recall@{k})={macro['miss_rate@k']:.3f}")
    return {"k": k, "per_query": {q: {kk: vv for kk, vv in m.items() if kk != "retrieved"}
                                  for q, m in per_query.items()},
            "macro": macro}


# ---------------------------------------------------------------------------
# ANN 后端对比（实验 3-4 的重点）：复用服务端 indexing.py 里的 ANNOY / HNSW 实现，
# 在一批合成单位向量上对比二者相对"精确暴力检索"的召回率、建索引耗时与查询延迟。
# 用合成向量而非真实文本嵌入，是为了 (a) 完全离线、无需下载模型；(b) 语料足够大时
# ANN 的"近似"才会显现出与精确检索的差距，从而看清两类算法的取舍。
# ---------------------------------------------------------------------------
def _exact_topk(queries: np.ndarray, base: np.ndarray, k: int) -> List[Set[int]]:
    """精确暴力最近邻（余弦），作为 ANN 召回率的 ground truth。"""
    sims = queries @ base.T
    idx = np.argsort(-sims, axis=1)[:, :k]
    return [set(row.tolist()) for row in idx]


def _sanity_ok(index, base: np.ndarray) -> bool:
    """自检：用库中已存在的向量查询，应能召回它自己。用于识别环境中损坏的索引后端。"""
    probe = min(5, len(base))
    for i in range(probe):
        ids, _ = index.search(base[i], min(10, len(base)))
        if f"v{i}" not in set(ids):
            return False
    return True


def compare_ann(base: np.ndarray, queries: np.ndarray, top_k: int, backends: List[str],
                annoy_n_trees: int, hnsw_M: int, hnsw_ef_search: int,
                hnsw_ef_construction: int) -> Dict:
    dim = base.shape[1]
    n = len(base)
    exact_sets = _exact_topk(queries, base, top_k)

    print(f"\n{'=' * 60}")
    print(f"ANN 后端对比：{n} 条 {dim} 维向量，{len(queries)} 条查询，top-{top_k}")
    print(f"指标：recall@{top_k} 相对精确暴力检索 / 建索引耗时 / 平均查询延迟")
    print(f"{'=' * 60}")

    report: Dict[str, Dict] = {}
    for backend in backends:
        if backend == "annoy":
            index = AnnoyIndex(dimension=dim, n_trees=annoy_n_trees,
                               metric="angular", logger=None)
        else:
            index = HNSWIndex(dimension=dim, max_elements=n + 16,
                              ef_construction=hnsw_ef_construction, M=hnsw_M,
                              ef_search=hnsw_ef_search, space="cosine", logger=None)

        t0 = time.time()
        for i, v in enumerate(base):
            index.add_item(f"v{i}", v)
        if backend == "annoy":
            index.rebuild_index()
        build_time = time.time() - t0

        healthy = _sanity_ok(index, base)

        recalls: List[float] = []
        qtimes: List[float] = []
        for qi, q in enumerate(queries):
            ts = time.time()
            ids, _ = index.search(q, top_k)
            qtimes.append(time.time() - ts)
            got = {int(d[1:]) for d in ids}
            recalls.append(len(got & exact_sets[qi]) / top_k)

        mean_recall = float(np.mean(recalls))
        mean_qms = float(np.mean(qtimes) * 1000)
        params = (f"n_trees={annoy_n_trees}" if backend == "annoy"
                  else f"M={hnsw_M}, ef_search={hnsw_ef_search}, ef_construction={hnsw_ef_construction}")
        report[backend] = {
            "recall@k": mean_recall,
            "build_time_s": build_time,
            "mean_query_ms": mean_qms,
            "params": params,
            "healthy": healthy,
        }
        warn = "" if healthy else "  [警告] 该后端连自身向量都召回不到，疑似当前环境下损坏，下列数字不可信"
        print(f"\n[{backend.upper()}]  {params}{warn}")
        print(f"  recall@{top_k} = {mean_recall:.3f}")
        print(f"  建索引耗时   = {build_time * 1000:.1f} ms")
        print(f"  平均查询延迟 = {mean_qms:.3f} ms")

    if "annoy" in report and "hnsw" in report:
        print(f"\n{'-' * 60}")
        print("小结：HNSW 图结构通常召回率更高、支持增量插入，代价是更高内存与建索引开销；")
        print("      ANNOY 树结构建索引快、内存省，但删除需重建，召回随 n_trees 调节。")
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="cli.py",
        description="稠密检索命令行工具（实验 3-4）：在小型语料上运行稠密嵌入检索并评测检索质量，"
                    "并对比 ANNOY / HNSW 两种 ANN 索引后端。",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""示例：
  python cli.py                                       # 默认演示（查询 "a cat playing"，需嵌入模型）
  python cli.py -q "model distillation" -k 3          # 单条稠密查询
  python cli.py --eval                                # 在标注集上算 recall/precision/MRR
  python cli.py --embedding-model sentence-transformers/all-MiniLM-L6-v2 --eval   # 离线小模型
  python cli.py --compare-ann                         # ANNOY vs HNSW 召回率对比（合成向量，无需模型）
  python cli.py --compare-ann --ann-base 5000 --annoy-n-trees 5 -k 10 -o ann.json
""",
    )
    parser.add_argument("-q", "--query", default=DEFAULT_QUERY,
                        help=f"查询字符串（默认: '{DEFAULT_QUERY}'）")
    parser.add_argument("-c", "--corpus", default=None,
                        help="语料文件路径（.json 文档数组 或 .jsonl 每行一篇）；缺省用内置示例语料")
    parser.add_argument("-k", "--top-k", type=int, default=5,
                        help="返回前 k 条结果（默认: 5）")
    parser.add_argument("-o", "--output", default=None,
                        help="把结果/评测指标以 JSON 写入该文件")
    parser.add_argument("--embedding-model", default=DEFAULT_MODEL,
                        help=f"稠密嵌入模型名（默认: {DEFAULT_MODEL}）；"
                             f"离线可用已缓存的 {OFFLINE_HINT_MODEL}")
    parser.add_argument("--pooling", choices=["auto", "mean", "cls"], default="auto",
                        help="句向量池化方式：auto(bge*用cls，其余用mean) / mean / cls")
    parser.add_argument("--device", default="cpu",
                        help="推理设备（cpu / cuda / mps，默认: cpu）")
    parser.add_argument("--eval", action="store_true",
                        help="在标注集上评测 recall@k / precision@k / MRR，而非只跑单条查询")
    parser.add_argument("--labels", default=None,
                        help="评测标注文件 {query: [相关doc_id,...]}；缺省用内置标注")

    ann = parser.add_argument_group("ANN 后端对比（--compare-ann）")
    ann.add_argument("--compare-ann", action="store_true",
                     help="对比 ANNOY 与 HNSW 的召回率/耗时（复用 indexing.py，用合成向量，无需模型）")
    ann.add_argument("--backend", choices=["annoy", "hnsw", "both"], default="both",
                     help="参与对比的 ANN 后端（默认: both）")
    ann.add_argument("--ann-base", type=int, default=3000,
                     help="合成底库向量数量（默认: 3000，越大 ANN 近似误差越明显）")
    ann.add_argument("--ann-queries", type=int, default=100,
                     help="合成查询向量数量（默认: 100）")
    ann.add_argument("--ann-dim", type=int, default=128,
                     help="合成向量维度（默认: 128）")
    ann.add_argument("--annoy-n-trees", type=int, default=10,
                     help="ANNOY 树数量（默认: 10；越多越准越慢）")
    ann.add_argument("--hnsw-M", type=int, default=16,
                     help="HNSW 每节点连接数 M（默认: 16；越大召回越高越占内存）")
    ann.add_argument("--hnsw-ef-search", type=int, default=20,
                     help="HNSW 查询期动态候选表大小 ef_search（默认: 20）")
    ann.add_argument("--hnsw-ef-construction", type=int, default=100,
                     help="HNSW 建索引期动态候选表大小 ef_construction（默认: 100）")
    ann.add_argument("--seed", type=int, default=42,
                     help="合成向量随机种子（默认: 42）")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    args = build_parser().parse_args(argv)
    payload: Dict = {"top_k": args.top_k}

    # --- ANN 后端对比：合成向量，无需嵌入模型，完全离线 ---
    if args.compare_ann:
        rng = np.random.default_rng(args.seed)
        base = rng.standard_normal((args.ann_base, args.ann_dim)).astype("float32")
        base /= np.linalg.norm(base, axis=1, keepdims=True)
        queries = rng.standard_normal((args.ann_queries, args.ann_dim)).astype("float32")
        queries /= np.linalg.norm(queries, axis=1, keepdims=True)
        backends = ["annoy", "hnsw"] if args.backend == "both" else [args.backend]
        payload["compare_ann"] = compare_ann(
            base, queries, args.top_k, backends,
            annoy_n_trees=args.annoy_n_trees, hnsw_M=args.hnsw_M,
            hnsw_ef_search=args.hnsw_ef_search, hnsw_ef_construction=args.hnsw_ef_construction)
        if args.output:
            with open(args.output, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            print(f"\n已写入结果：{args.output}")
        return 0

    # --- 稠密检索 / 评测：需要嵌入模型 ---
    corpus = load_corpus(args.corpus)
    print(f"已加载语料：{len(corpus)} 篇文档"
          + ("（内置示例）" if not args.corpus else f"（来自 {args.corpus}）"))

    encoder = load_encoder(args.embedding_model, args.pooling, args.device)
    if encoder is None:
        return 0  # 已给出模型缺失提示，视为正常退出（参数解析已验证）

    doc_matrix = encoder.encode([d["text"] for d in corpus])
    payload["embedding_model"] = args.embedding_model
    payload["query"] = args.query

    if args.eval:
        labels = load_labels(args.labels)
        payload["eval"] = run_eval(encoder, corpus, doc_matrix, labels, args.top_k)
    else:
        payload["results"] = run_search(encoder, corpus, doc_matrix, args.query, args.top_k)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n已写入结果：{args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
