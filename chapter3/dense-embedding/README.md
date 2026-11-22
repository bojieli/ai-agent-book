# Vector Similarity Search Service (Dense Embedding) / 稠密向量相似性搜索服务

## 实验 3-4：近似索引找回了几个真正的近邻？

给定一个查询，先对库中每个向量计算相似度，记下最相近的 10 篇文档。再让索引从同一批向量里返回 10 篇。如果有 8 篇相同，这个查询的索引召回率就是 8/10。实验用 20 个查询分别计算这个比例，再取平均。即使每次都找到全部 10 篇，也仍需对照问题和文档内容判断它们能否回答问题。

[正文所用运行记录](validation/runs/20260729T182946Z-3_4-2555ea60/evidence.json)使用 Qwen3-Embedding-0.6B，把按 20 个主题构造的 300 段文本和 20 个查询编码成 1024 维向量。先用 **240 段**建库，与这 240 段的精确 top-10 比较，两种索引的平均召回率都是 1.0。再加入剩余 **60 段**，ANNOY 重建，HNSW 增量插入；此时用全部 300 段重新计算精确近邻，两者的更新后召回率也都是 1.0。每个查询重复计时 5 次，召回率仍按 20 个不同查询统计。

初建 240 段时，ANNOY 用时约 13 ms，HNSW 约 78 ms；序列化后的索引文件分别约 1.40 MB 和 1.02 MB。ANNOY 在 Linux 容器中运行，HNSW 在宿主机运行，若要比较哪种方法更快，需在相同环境下重新计时。文件大小只衡量落盘空间。可以在 [运行索引](validation/latest.json) 找到证据文件与对应版本。

用户的问题与文档用词不同，仍可能表达相同含义。稠密检索把文本编码成向量，再根据向量之间的距离寻找候选内容。本实验让你分别观察语义表示和近似搜索的作用。

[English](#english)

[向量表示与索引各影响什么](#learning-0) · [准备向量与索引后端](#learning-1) · [用精确近邻校验近似索引](#learning-2) · [解释召回率与查询耗时](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 向量表示与索引各影响什么

嵌入模型决定文本怎样映射到空间；索引决定怎样高效寻找邻近向量。ANNOY 和 HNSW 等近似索引通过减少搜索工作提高速度，但可能漏掉精确搜索会返回的邻居。索引召回与问答质量不是同一个指标。

### 区分表示误差与近似搜索误差

向量模型先把文本变成表示，搜索算法再从向量集合中寻找邻居。即使穷举搜索找到了距离最近的向量，该文档也未必是问题的最佳答案；这属于表示与任务目标之间的差别。近似最近邻搜索则可能没有找到真正最近的向量。阅读 ANN 对比时，应分别检查近似搜索相对精确搜索的召回，以及最终结果对原问题是否有用。

### 概述

基于 BGE-M3 嵌入、可切换 ANNOY / HNSW 后端的教学型向量相似性搜索 HTTP 服务，外加实验 3-4 的离线 CLI 评测。

### 服务功能

- **BGE-M3**：稠密嵌入、多语言、长上下文（至 8192 tokens）  
- **双后端**：ANNOY（树）、HNSW（图）  
- **教学日志**、**REST API**、**纯内存**

### 架构

HTTP 服务先用嵌入模型把文档编码，再把向量和文档 ID 交给索引。查询时用同一模型编码问题，由索引找回近邻 ID，服务再按 ID 取出文档。

### 索引对比

**ANNOY** 使用多棵树搜索，适合建好后重复查询。增删文档后要重建索引；增加 `n_trees` 会改变索引体积、构建时间与召回。

**HNSW** 通过近邻图搜索，支持增量插入与软删除。建图时可调邻接数 `M` 与构建搜索范围 `ef_construction`；查询时可改变 `ef_search`，比较多看一些候选能多找回多少近邻。

### 内存与优化

模型约 2.3GB；一个 1024 维 float32 向量占 4096 字节，另需计入文档、索引结构和程序的内存。ANNOY 提高 `n_trees`；HNSW 提高 `M` / `ef_*`；可用 FP16 加速。

<a id="learning-1"></a>

## 准备向量与索引后端

比较两种索引时，给它们同一批向量、同一个查询和相同的返回条数。下面的 CLI 可以先算精确近邻，再比较近似搜索返回的文档编号。

### 安装

- Python 3.12 与根目录 `ch3` extra，macOS（M1/M2）或 Linux
- 内存 ≥4GB（建议 8GB）；可选 CUDA  

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

cd chapter3/dense-embedding

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt
```

HTTP 服务默认使用 BGE-M3（约 2.3 GB）。首次加载需要下载或预先准备权重；下面的合成向量对照可以直接运行。

### 配置（`VEC_` 环境变量）

```bash
export VEC_INDEX_TYPE=hnsw
export VEC_MODEL_NAME=BAAI/bge-m3
export VEC_USE_FP16=true
export VEC_MAX_SEQ_LENGTH=512
export VEC_MAX_DOCUMENTS=100000
export VEC_LOG_LEVEL=DEBUG
export VEC_ANNOY_N_TREES=50
export VEC_ANNOY_METRIC=angular
export VEC_HNSW_EF_CONSTRUCTION=200
export VEC_HNSW_M=32
export VEC_HNSW_EF_SEARCH=100
export VEC_HNSW_SPACE=cosine
```

教学日志：`python main.py --debug --show-embeddings`。

<a id="learning-2"></a>

## 用精确近邻校验近似索引

先运行合成向量上的索引比较，不需要下载嵌入模型。理解速度与召回的关系后，再按下文准备本地嵌入模型，使用自然语言查询示例语料。保持模型相同，比较不同索引的返回结果。

### 命令行工具：稠密检索与 ANN 对比（cli.py，实验 3-4）

以下命令均在 `chapter3/dense-embedding` 目录运行，无需先启动 HTTP 服务。

**先观察索引怎样取舍速度和召回。** 固定随机种子和合成向量，分别让 HNSW 搜索较少、较多候选。在同一台机器上对比输出文件中的 `compare_ann.hnsw`：

```bash
python cli.py --compare-ann --backend hnsw --hnsw-ef-search 20 -k 10 -o hnsw20.json
python cli.py --compare-ann --backend hnsw --hnsw-ef-search 200 -k 10 -o hnsw200.json
# 在同一组合成向量上再比较两种后端
python cli.py --compare-ann -k 10
```

**要复做正文的文本向量实验**，使用 [benchmark.py](benchmark.py)。下面把权重固定到原记录中的版本，首次下载需要联网。如果本机 ANNOY 健康检查发现返回条数不足，脚本会启动 Docker，并在 Linux 容器内安装依赖。

```bash
hf download Qwen/Qwen3-Embedding-0.6B --revision 97b0c614be4d77ee51c0cef4e5f07c00f9eb65b3 --local-dir ./qwen3-embedding-0.6b
python benchmark.py --model ./qwen3-embedding-0.6b --device cpu --docs 300 --top-k 10 --repeats 5 --seed 37
```

打开本次生成的 `validation/runs/<运行编号>/evidence.json`。在 `summary` 中比较两种索引的 `recall_at_k` 与 `incremental_update.recall_at_k_after_update`，分别对应初建与追加后的结果。脚本也会更新 `validation/latest.json`；本页开头的固定链接可随时对照原始记录。

**要检验文档与问题在语义上是否相关**，改用带人工标注的查询。默认使用 BGE-M3，也可指定较小的 MiniLM。两者均需相应权重已下载才能断网运行。

```bash
python cli.py -q "model distillation" -k 3
python cli.py --eval
python cli.py --embedding-model sentence-transformers/all-MiniLM-L6-v2 --eval
python cli.py --corpus my.json --labels my_labels.json --eval -o result.json
```

`python cli.py --help` 提供完整中文参数说明。

#### 常用参数

| 参数 | 说明 |
| --- | --- |
| `-q, --query` | 查询（默认 `a cat playing`） |
| `-c, --corpus` | 语料（`.json` / `.jsonl`）；缺省内置示例 |
| `-k, --top-k` | Top-k（默认 5） |
| `-o, --output` | 结果 / 指标 JSON |
| `--embedding-model` | 嵌入模型（默认 `BAAI/bge-m3`；离线可用 MiniLM） |
| `--pooling` | `auto` / `mean` / `cls` |
| `--eval` | 评测 recall@k / precision@k / MRR |
| `--compare-ann` | 对比 ANNOY / HNSW |
| `--ann-base / --ann-dim / --ann-queries` | 合成底库规模 / 维度 / 查询数 |
| `--annoy-n-trees / --hnsw-M / --hnsw-ef-search` | ANN 超参 |

#### 实测结果

**稠密检索质量**（12 篇文档、5 个有相关性标注的查询，`all-MiniLM-L6-v2`）。这里每个查询的召回率分母是该查询人工标出的相关文档数，precision@5 的分母是返回的 5 篇文档。5 个查询共标出了 8 个相关项，全部找回时，平均 precision@5 为 8/(5 × 5) = 0.32：

```
宏平均  recall@5=1.000  precision@5=0.320  MRR=1.000
```

具体看 `a cat playing`（一只正在玩耍的猫）。在上面的 MiniLM 示例中，两篇标为相关的文档排到了第一、二名。读一读原文：`doc_7` 描述小猫追着毛线球跑，`doc_8` 描述猫科动物在草丛中跟踪猎物。两篇都与猫有关，但如果用户要找的是“玩耍”的例子，第一篇更贴切。这道题把两篇都计为相关；读者若想评价动作是否吻合，还需把这条要求写进标注。

实验 3-5 默认用 `cat` 在 10 篇文档里做关键词检索。要比较两种方法，先统一输入。下面在本实验目录导出稠密示例的 12 篇文档，再让 BM25 搜同一句话。两条查询命令均使用正文内容建立索引，标题只用于显示。

```bash
python -c 'import json; from cli import DEFAULT_CORPUS; print(json.dumps(DEFAULT_CORPUS))' > cat-corpus.json
python ../sparse-embedding/cli.py --corpus cat-corpus.json -q "a cat playing" -k 5
python cli.py --corpus cat-corpus.json --embedding-model sentence-transformers/all-MiniLM-L6-v2 -q "a cat playing" -k 5
```

在这 12 篇文档上，BM25 返回空列表。小猫那篇的标题是 `A Playful Kitten`，被索引的正文写的是 `kitten chased a ball of yarn`。核对检索结果时，先看系统究竟把文档的哪些字段送进了索引。

**ANN 对比**（3000 条 128 维，100 查询，top-10）：

| 配置 | recall@10 | 平均查询延迟 |
| --- | --- | --- |
| HNSW `ef_search=20` | 0.562 | 0.05 ms |
| HNSW `ef_search=200` | 0.991 | 0.25 ms |

> **环境提示**：部分 macOS/arm64 上 `annoy==1.17.3` 预编译轮子有缺陷，工具会警告并标记不可信；HNSW 不受影响。完整 ANNOY vs HNSW 请在 annoy 正常的环境（如 Linux x86_64）运行。

### 启动服务

```bash
python main.py                              # 默认 HNSW
python main.py --index-type annoy
python main.py --index-type hnsw --host 0.0.0.0 --port 4242 --debug --show-embeddings
```

选项：`--index-type`、`--host`（默认 `0.0.0.0`）、`--port`（默认 `4240`）、`--debug`、`--show-embeddings`。

文档：http://localhost:4240/docs

### 测试

```bash
python test_client.py
python test_client.py --performance
```

```bash
curl -X POST http://localhost:4240/index \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test document about machine learning."}'

curl -X POST http://localhost:4240/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "top_k": 5}'
```

<a id="learning-3"></a>

## 解释召回率与查询耗时

合成向量实验只能解释索引行为，不能证明文本语义效果。文本查询还应检查相关片段是否被编码得足够接近，以及相似但事实不同的片段是否被误排在前面。

### 检查自己的解释

若索引几乎找回了全部近邻，最终检索结果仍不相关，问题可能出在哪一层？

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — **Experiment 3-4**: BGE-M3 dense search with ANNOY / HNSW, plus offline CLI metrics.  
> 配套《深入理解 AI Agent》第 3 章 **实验 3-4**：BGE-M3 稠密检索与 ANNOY / HNSW 对比，含可离线 CLI。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### API 端点

**POST `/index`** / **POST `/search`** / **DELETE `/index`** / **GET `/stats`** / **GET `/documents?limit=10`**  
请求体格式与 English 节 JSON 示例相同。

<a id="learning-5"></a>

## 排错与参考

### 故障排查

编码时内存不足，可以减小批量或输入长度，硬件支持时尝试 FP16。先分别计时编码和建索引：GPU 可以加速支持它的嵌入模型，本项目的 ANNOY 和 HNSW 索引使用 CPU。建索引慢，可调低 `ef_construction` 或 `n_trees`，再测召回损失。搜不到目标时，先用精确检索确认目标确实是近邻，再决定是否增加索引的搜索范围。

### 参考与许可

- [BGE-M3 论文](https://arxiv.org/abs/2402.03216) · [模型](https://huggingface.co/BAAI/bge-m3)  
- [ANNOY](https://github.com/spotify/annoy) · [HNSWlib](https://github.com/nmslib/hnswlib)  
- 教学项目，仅供学习。

---

## Notes / 说明

- Related: [`../sparse-embedding/`](../sparse-embedding/) (Exp. 3-5), [`../retrieval-pipeline/`](../retrieval-pipeline/) (Exp. 3-6).  
- 相关：[`../sparse-embedding/`](../sparse-embedding/)（实验 3-5）、[`../retrieval-pipeline/`](../retrieval-pipeline/)（实验 3-6）。

## English

### Overview

Educational HTTP service for vector similarity search using BGE-M3 embeddings with configurable ANNOY or HNSW backends, plus an offline `cli.py` for Experiment 3-4 metrics.

### CLI: dense retrieval & ANN comparison (`cli.py`, Experiment 3-4)

Besides the HTTP service, `cli.py` is **ready-to-run and offline-reproducible**—no need to start the server first:

1. **Semantic power of dense embeddings** — `recall@k / precision@k / MRR` on a small labelled corpus  
2. **ANN backend comparison** (focus of Exp. 3-4) — ANNOY / HNSW from `indexing.py` vs **exact brute-force**, measuring recall, build time, query latency  

#### Usage

```bash
# 1) Single dense query (default "a cat playing"; needs embedding model)
python cli.py -q "model distillation" -k 3

# 2) Retrieval quality: recall@k / precision@k / MRR
python cli.py --eval

# 2') Offline: small cached model (no 2.3GB BGE-M3 download)
python cli.py --embedding-model sentence-transformers/all-MiniLM-L6-v2 --eval

# 3) ANN backend compare (synthetic vectors; fully offline, no model)
python cli.py --compare-ann -k 10
python cli.py --compare-ann --backend hnsw --hnsw-ef-search 200 -k 10

# Custom corpus / labels / output
python cli.py --corpus my.json --labels my_labels.json --eval -o result.json
```

`python cli.py --help` has full Chinese flag docs.

#### Common flags

| Flag | Description |
| --- | --- |
| `-q, --query` | Query (default `a cat playing`) |
| `-c, --corpus` | Corpus (`.json` array or `.jsonl`); default built-in sample |
| `-k, --top-k` | Top-k (default 5) |
| `-o, --output` | Write results/metrics JSON |
| `--embedding-model` | Model (default `BAAI/bge-m3`; offline: `sentence-transformers/all-MiniLM-L6-v2`) |
| `--pooling` | `auto` / `mean` / `cls` |
| `--eval` | Evaluate recall@k / precision@k / MRR |
| `--compare-ann` | Compare ANNOY / HNSW (synthetic vectors) |
| `--ann-base / --ann-dim / --ann-queries` | Synthetic base size / dim / queries (default 3000 / 128 / 100) |
| `--annoy-n-trees / --hnsw-M / --hnsw-ef-search` | ANN hyperparameters |

#### Measured results (real runs)

**Dense quality** (12-doc built-in, `all-MiniLM-L6-v2`, offline):

```
宏平均  recall@5=1.000  precision@5=0.320  MRR=1.000
```

Query `a cat playing` ranks docs that only say `kitten` / `feline` (no literal “cat”) at ranks 1–2—semantic strength vs BM25 (Exp. 3-5 may miss them).

**ANN compare** (3000 × 128-d unit vectors, 100 queries, top-10); HNSW recall rises with `ef_search`:

| Config | recall@10 | Mean query latency |
| --- | --- | --- |
| HNSW `ef_search=20` | 0.562 | 0.05 ms |
| HNSW `ef_search=200` | 0.991 | 0.25 ms |

> **Environment note**: each backend is health-checked by self-querying. On some macOS/arm64 setups, prebuilt `annoy==1.17.3` is broken (even self-query only returns itself); the tool warns and marks those numbers untrusted. HNSW is unaffected. Full ANNOY vs HNSW: use an environment where Annoy works (e.g. Linux x86_64).

### Service features

- **BGE-M3**: dense embeddings, 100+ languages, long context (up to 8192 tokens)  
- **Dual backends**: ANNOY (tree), HNSW (graph)  
- **Educational logging**: embed, index ops, metrics, vector stats  
- **REST API**: index / delete / search / stats  
- **In-memory** (no persistence)  

### Architecture

```
┌──────────────────┐
│   HTTP Client    │
└────────┬─────────┘
         ▼
┌──────────────────┐
│  FastAPI Server  │
└────────┬─────────┘
    ┌────┴────┐
    ▼         ▼
┌──────────┐ ┌──────────────┐
│ Document │ │  Embedding   │
│  Store   │ │   Service    │
└──────────┘ │  (BGE-M3)    │
             └──────┬───────┘
          ┌─────────┴──────────┐
          ▼                    ▼
    ┌──────────┐        ┌──────────┐
    │  ANNOY   │        │   HNSW   │
    └──────────┘        └──────────┘
```

### Installation

- Python 3.12 with the root `ch3` extra, macOS (M1/M2 optimized) or Linux
- ≥4GB RAM (8GB recommended); optional CUDA GPU  

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

cd chapter3/dense-embedding

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt
```

BGE-M3 (~2.3GB) downloads on first use into the HuggingFace cache.

### Starting the service

```bash
python main.py                              # HNSW (default)
python main.py --index-type annoy
python main.py --index-type hnsw --host 0.0.0.0 --port 4242 --debug --show-embeddings
```

Options: `--index-type` (`annoy`|`hnsw`, default `hnsw`), `--host` (default `0.0.0.0`), `--port` (default `4240`), `--debug`, `--show-embeddings`.

Docs: http://localhost:4240/docs · OpenAPI: http://localhost:4240/openapi.json

### API endpoints

**POST `/index`**

```json
{
  "text": "Machine learning is a subset of artificial intelligence.",
  "doc_id": "doc_001",
  "metadata": {"category": "AI", "author": "John Doe"}
}
```

**POST `/search`**

```json
{
  "query": "What is deep learning?",
  "top_k": 5,
  "return_documents": true
}
```

**DELETE `/index`** — body `{"doc_id": "doc_001"}`  
**GET `/stats`** · **GET `/documents?limit=10`**

### Testing

```bash
python test_client.py
python test_client.py --performance
```

```bash
curl -X POST http://localhost:4240/index \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test document about machine learning."}'

curl -X POST http://localhost:4240/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "top_k": 5}'
```

### Index comparison

**ANNOY**: fast build, low memory, good for static/read-heavy; rebuild for delete; trade accuracy via `n_trees`.  
**HNSW**: high recall, incremental updates, soft delete; more memory, slower build; tune `M` / `ef_*`.

### Configuration (env `VEC_` prefix)

```bash
export VEC_INDEX_TYPE=hnsw
export VEC_MODEL_NAME=BAAI/bge-m3
export VEC_USE_FP16=true
export VEC_MAX_SEQ_LENGTH=512
export VEC_MAX_DOCUMENTS=100000
export VEC_LOG_LEVEL=DEBUG
export VEC_ANNOY_N_TREES=50
export VEC_ANNOY_METRIC=angular
export VEC_HNSW_EF_CONSTRUCTION=200
export VEC_HNSW_M=32
export VEC_HNSW_EF_SEARCH=100
export VEC_HNSW_SPACE=cosine
```

Educational logging: `python main.py --debug --show-embeddings`.

### Memory / optimization notes

- Model ~2.3GB; ~4KB per doc (1024-d float32)  
- ANNOY: raise `n_trees` for accuracy; `angular` for normalized vectors; batch then build  
- HNSW: raise `M` / `ef_construction` / `ef_search` for quality vs cost  
- FP16 faster with slight accuracy trade-off  

### Troubleshooting

OOM → smaller batches, FP16, lower `max_seq_length`, prefer ANNOY. Slow index → lower `ef_construction` / `n_trees`, use GPU. Poor quality → raise `n_trees` / `M` / `ef_search`.

### References

- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216) · [Model](https://huggingface.co/BAAI/bge-m3)  
- [ANNOY](https://github.com/spotify/annoy) · [HNSWlib](https://github.com/nmslib/hnswlib) · [FastAPI](https://fastapi.tiangolo.com/)

### License

Educational project for learning purposes.

---
