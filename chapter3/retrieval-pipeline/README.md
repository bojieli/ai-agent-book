# Hybrid Retrieval Pipeline with Neural Reranking / 混合检索流水线与神经重排序

关键词检索擅长精确词项，向量检索擅长语义相近表达。混合检索尝试结合两者，再用重排序模型细看候选。本实验按阶段观察文档如何进入、离开最终结果列表。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

流水线先召回候选，再融合不同来源的排名，最后重排。后续阶段通常只能处理已有候选，因此前面漏掉的文档难以靠重排补回。把最终指标拆到各阶段，才能知道应该改召回还是排序。

### 一条查询如何经过四个阶段

以产品编号 `XR-7003` 为例，BM25 利用准确的编号匹配，稠密检索可能把相邻型号也排在前面。融合阶段汇总两路候选，重排阶段再对已经召回的候选逐项评分。重排不能找回从未进入候选集合的文档，因此应先检查召回，再分析排序。

RRF 使用排名而不是直接相加两种检索器的原始分数。文档在第 `r` 名时，该路贡献为 `1 / (k + r)`；本例使用 `k=60`。加权融合则先处理分数量纲，再决定两路权重。下面两种方法的配置与输出都保留了，比较时只改变融合方法即可观察它们的差别。

### 教学目标

1. **稠密 vs 稀疏**：各自擅长场景  
2. **混合检索**：多路互补  
3. **神经重排序**：用 Transformer 重排候选  
4. **并行处理**：多服务索引/检索  
5. **工程模式**：API 与错误处理

### 架构

检索流水线服务监听 4242 端口，负责文档管理、融合与重排；稠密和稀疏检索服务分别监听 4240、4241 端口。客户端只需向流水线提交查询，流水线再组织两路调用。英文部分还保留了完整架构图。

### 关键概念

**稠密检索（BGE-M3）**把查询与文档表示为向量，适合语义接近、跨语言或同义改写的查询。但表示相近也可能把不同产品编码混在一起，并带来模型推理的计算开销。  
**稀疏检索（BM25）**依据词项匹配打分，适合精确名称、编号和 ID，计算通常较轻。它不直接建模语义相似，因此没有共同词项的同义改写可能难以命中。  
**融合（`fusion.py`）**：RRF（`k=60`）或 min-max 后加权求和。  
**重排**：服务用 BGE-Reranker-v2-M3；`evaluate.py` 用 `BAAI/bge-reranker-base`。

<a id="learning-1"></a>

## 准备环境与输入

先从本地示例开始。依赖安装可能需要联网，但下面标明的离线路径不需要模型 API Key。若随后切换到真实模型，请再完成相应的服务配置。

### 前置与安装

Python 3.12 与根目录 `ch3` extra，建议 ≥8GB 内存，约 5GB 模型空间。

```bash
# 在仓库根目录使用统一的第 3 章环境
uv sync --locked --python 3.12 --extra ch3

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch3]"

cd chapter3/retrieval-pipeline

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt
```

<a id="learning-2"></a>

## 按照步骤完成实验

先运行仅含 BM25 的离线路径，建立可理解的基线。然后按下文启动稠密检索服务和重排模型，逐个加入阶段。每次只改一项，并保留同一查询的候选列表。

### 先做一个小规模观察

以下命令从本实验目录执行。先完成前面的环境准备，再观察这条路径的输入和输出。

```bash
python evaluate.py --no-dense --no-rerank
```

### 启动服务

```bash
./start_all_services.sh
```

或分别：

```bash
cd ../dense-embedding && python main.py --port 4240
cd ../sparse-embedding && python server.py --port 4241
cd ../retrieval-pipeline && python main.py --port 4242
```

### 带服务测试

```bash
python test_client.py
python demo.py
# http://localhost:4242/docs
```

### 离线评测 CLI（`evaluate.py`）

**单进程、可离线**跑通 chunk → embed → retrieve → fuse → rerank。

```bash
python evaluate.py --help
python evaluate.py
python evaluate.py --no-dense
python evaluate.py --no-rerank
python evaluate.py --query "XR-7003"
python evaluate.py --embed-model BAAI/bge-m3 --pooling cls
python evaluate.py --output result.json
```

| 阶段 | 默认组件 | 离线？ |
|------|----------|--------|
| chunk | 字符窗口切分 | ✅ 纯 Python |
| sparse | BM25 | ✅ 无需下载模型 |
| dense | MiniLM-L6-v2（~90MB） | ✅ HF 缓存 |
| fuse | RRF + weighted | ✅ 纯 Python |
| rerank | bge-reranker-base | ✅ 首次下载后缓存 |

> 若希望完全不加载机器学习模型，请同时使用 `--no-dense --no-rerank`：前者关闭稠密检索，后者关闭重排。Apple Silicon 上 MPS 出现 `NaN` 时，脚本会自动回退 CPU。

### 教学测试用例（需服务）

语义 / 精确人名 / 多语言 / 技术编码 / 概念词——分别观察稠密或稀疏胜出。

<a id="learning-3"></a>

## 分析结果与形成判断

比较候选覆盖、正确文档排名和耗时。若召回提高但首位结果变差，要检查融合权重与去重；若重排没有改善，先确认正确文档已经进入候选集。

### 真实输出解读

在这组已有输出中，近似编码使稠密检索混淆了相邻型号，没有词面重叠的改写则使 BM25 难以命中。这里记录的 **Hybrid-RRF 各项指标为 1.00**，说明融合在这组小语料和查询上弥补了两路检索的部分弱点。它不能证明混合检索在其他语料上总能满分。加权融合还受到分数尺度的影响；要判断重排的增益，应继续使用更大的候选集合和不同类型的自然语言查询进行对照。

单查询追踪：

```
$ python evaluate.py --query "XR-7003"
[BM25 (sparse)]
  1. xr_7003        ...
[Dense]
  1. xr_7001        ...   # 稠密先排到兄弟编码
  2. xr_7003        ...
[Hybrid-RRF]
  1. xr_7003        ...   # 融合把精确匹配推回第 1
```

### 性能与要点

- 时延量级：稠密 50–100ms，稀疏 10–30ms，重排约 100–200ms（20 文档）  
- 模型内存约 4GB  
- 没有单一最优；混合通常更好；重排提升相关性

### 检查自己的解释

应该优先增加候选数量，还是换更强的重排模型？你需要哪些阶段数据才能决定？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — **Experiment 3-6**: dense + sparse + fusion + rerank, with offline `evaluate.py`.  
> 配套《深入理解 AI Agent》第 3 章 **实验 3-6**：稠密 + 稀疏 + 融合 + 重排，含离线 `evaluate.py`。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

### API

```bash
POST /index
{"text": "Document content", "doc_id": "optional_id", "metadata": {"category": "example"}}

POST /search
{"query": "search terms", "mode": "hybrid", "top_k": 20, "rerank_top_k": 10}

GET /stats
GET /documents?limit=10&offset=0
```

响应含稠密/稀疏原始排名、重排结果、排名变化与重叠统计。

### 项目结构

```
retrieval-pipeline/
├── config.py, document_store.py, retrieval_client.py
├── reranker.py, fusion.py, retrieval_pipeline.py
├── evaluate.py, main.py, test_client.py, demo.py
├── requirements.txt, start_all_services.sh, stop_all_services.sh
└── README.md
```

### 代码阅读顺序

- **Run first:** `python evaluate.py --no-dense --no-rerank` (offline BM25 smoke; the full pipeline needs the two retrieval services and local models).
- **Start here:** `retrieval_pipeline.py::RetrievalPipeline.search` orchestrates retrieval, fusion and reranking.
- **Core behavior:** `retrieval_client.py::RetrievalClient.search`, `fusion.py::fuse` and `reranker.py::Reranker.rerank`.
- **State / protocol:** `document_store.py::DocumentStore`, `SearchResult`, `PipelineConfig` and `SearchMode`.
- **Verifier:** `evaluate.py` reports recall/MRR by stage; `test_pipeline.py` and `test_weighted_fusion_dedup.py` lock down ranking and deduplication.
- **Experiment variable:** dense/sparse/hybrid mode, fusion method, candidate `top_k` and `rerank_top_k`.
- **Skip on first pass:** service startup scripts, model downloads and HTTP error adapters.

---

<a id="learning-5"></a>

## 排查问题与查阅资料

### 故障排查

检查 4240–4242 端口与模型下载；OOM 时减小 batch、改 CPU、开 FP16。

### 延伸阅读与许可

[BGE-M3](https://arxiv.org/abs/2402.03216) · [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) · 教学项目。

---

## Notes / 说明

- Upstream services: [`../dense-embedding/`](../dense-embedding/) (4240), [`../sparse-embedding/`](../sparse-embedding/) (4241).  
- 上游服务：[`../dense-embedding/`](../dense-embedding/)（4240）、[`../sparse-embedding/`](../sparse-embedding/)（4241）。

## English

### Educational goals

1. **Dense vs sparse**: when each wins and why  
2. **Hybrid search**: combining methods  
3. **Neural reranking**: reorder candidates with transformers  
4. **Parallel processing**: multi-service index/search  
5. **Production-ish patterns**: API design and error handling  

### Architecture

```
┌──────────────────────────────────────────────┐
│            Client Application                 │
└────────────────────┬─────────────────────────┘
                     ▼
┌──────────────────────────────────────────────┐
│         Retrieval Pipeline (Port 4242)        │
│  Document Store (In-Memory)                   │
│  BGE-Reranker-v2 (Local Model)                │
└────────┬──────────────────┬─────────────────┘
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  Dense Service  │  │  Sparse Service │
│   (Port 4240)   │  │   (Port 4241)   │
│   BGE-M3 Model  │  │   BM25 Engine   │
└─────────────────┘  └─────────────────┘
```

### Key concepts

**Dense (BGE-M3)**: semantic / cross-lingual / synonyms; may miss exact codes; costlier.  
**Sparse (BM25)**: exact terms / IDs; no semantics; fast.  
**Fusion (`fusion.py`)**: RRF `score(d)=Σ 1/(k+rank)` with `k=60` (rank-only, scale-free) or weighted sum after min-max normalize to `[0,1]`.  
**Rerank**: BGE-Reranker-v2-M3 (service); `BAAI/bge-reranker-base` in `evaluate.py`.

### Prerequisites

Python 3.12 with the root `ch3` extra, macOS M1/M2 (or adjust device), ≥8GB RAM, ~5GB disk for models.

### Installation

```bash
# From the repository root: use the shared Chapter 3 environment
uv sync --locked --python 3.12 --extra ch3

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch3]"

cd chapter3/retrieval-pipeline

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt
# First run downloads: BGE-M3 ~2.3GB, BGE-Reranker-v2-M3 ~1.1GB
```

### Running services

```bash
./start_all_services.sh
# Dense 4240, Sparse 4241, Pipeline 4242
```

Or individually:

```bash
# Terminal 1
cd ../dense-embedding && python main.py --port 4240
# Terminal 2
cd ../sparse-embedding && python server.py --port 4241
# Terminal 3
cd ../retrieval-pipeline && python main.py --port 4242
```

### Testing with services

```bash
python test_client.py   # educational cases
python demo.py          # interactive demo
# API docs: http://localhost:4242/docs
```

### Offline evaluation CLI (`evaluate.py`)

`test_client.py` / `demo.py` need ports 4240–4242. **`evaluate.py` runs the full pipeline in one process — no service startup needed, and fully offline once the models are cached**. Note: the first run still downloads the dense/rerank models from HuggingFace, so initial execution requires network access.

```bash
python evaluate.py --help          # Chinese help
python evaluate.py                 # full stage table (default)
python evaluate.py --no-dense      # BM25 only, no models
python evaluate.py --no-rerank
python evaluate.py --query "XR-7003"
python evaluate.py --embed-model BAAI/bge-m3 --pooling cls
python evaluate.py --output result.json
```

| Stage | Default component | Offline? |
|-------|-------------------|----------|
| chunk | character-window splitter | ✅ pure Python |
| sparse | BM25 (`rank_bm25`) | ✅ no model download |
| dense | `sentence-transformers/all-MiniLM-L6-v2` (~90MB) | ✅ cached HF |
| fuse | RRF + weighted (`fusion.py`) | ✅ pure Python |
| rerank | `BAAI/bge-reranker-base` (~1.1GB first download) | ✅ once cached |

> `--no-dense` needs no ML model. Dense/rerank models download from HuggingFace on first run (network required); after that they run from local cache, and `--offline` forces loading from the local cache only. On Apple Silicon, MPS `NaN` is detected and falls back to CPU.

### Real output (reproduced)

Hard clusters: near-duplicate codes (`XR-7001..`, `HTTP-400..`) break dense; zero-lexical paraphrases break BM25.

```
Stage / Method            Recall@3         MRR      nDCG@3
------------------------------------------------------------------------------
BM25 (sparse)               0.9000      0.8500      0.8631
Dense                       1.0000      0.9000      0.9262
Hybrid-RRF                  1.0000      1.0000      1.0000
Hybrid-Weighted             1.0000      0.9500      0.9631
Hybrid-RRF+Rerank           1.0000      0.9500      0.9631
```

**How to read it:** BM25 nails codes, fails paraphrases; Dense is the mirror; **Hybrid-RRF** reaches perfect 1.00 (headline of Exp. 3-6). Weighted can be less robust (scale alignment). On this toy 17-doc set RRF is already strong; rerank value grows on larger pools / NL queries.

```
$ python evaluate.py --query "XR-7003"
[BM25 (sparse)]
  1. xr_7003        score=  3.2260  Product model XR-7003 is a smartphone available now.
[Dense]
  1. xr_7001        score=  0.5247  Product model XR-7001 ...
  2. xr_7003        score=  0.5195  Product model XR-7003 ...
[Hybrid-RRF]
  1. xr_7003        score=  0.0325  Product model XR-7003 ...
```

### Educational test cases (with services)

1. Semantic (“kitty behavior” / feline) — dense wins  
2. Exact name (“Alexander Humphrey”) — sparse wins  
3. Multilingual (“人工智能”) — dense wins  
4. Codes (“HTTP-403”) — sparse wins  
5. Concepts (“happiness and excitement”) — dense wins  

### API

```bash
POST /index
{"text": "Document content", "doc_id": "optional_id", "metadata": {"category": "example"}}

POST /search
{"query": "search terms", "mode": "hybrid", "top_k": 20, "rerank_top_k": 10}

GET /stats
GET /documents?limit=10&offset=0
```

Response includes dense/sparse rankings, reranked results, rank changes, overlap stats.

### Project structure

```
retrieval-pipeline/
├── config.py, document_store.py, retrieval_client.py
├── reranker.py, fusion.py, retrieval_pipeline.py
├── evaluate.py, main.py, test_client.py, demo.py
├── requirements.txt, start_all_services.sh, stop_all_services.sh
└── README.md
```

### Performance / takeaways

- Latency ballpark: dense 50–100ms, sparse 10–30ms, rerank 100–200ms (20 docs)  
- Memory ~4GB models + docs  
- No single method wins; hybrid usually better; rerank improves relevance  

### Troubleshooting

Ports 4240–4242 free; models downloaded; Python 3.12 for the root `ch3` install. OOM → smaller batches, CPU, FP16. First run slow (downloads).

### Further reading

[BGE-M3](https://arxiv.org/abs/2402.03216) · [BM25](https://en.wikipedia.org/wiki/Okapi_BM25) · [Neural IR](https://arxiv.org/abs/2301.09191)

### License

Educational project for learning purposes.

---
