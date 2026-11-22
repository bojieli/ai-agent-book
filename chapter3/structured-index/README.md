# Structured Indexing: RAPTOR & GraphRAG / 结构化索引：RAPTOR 与 GraphRAG

## 实验 3-7：找到相关页，能否解释处理器的能力？

程序查到处理器支持 AVX，是否就能使用相应的寄存器状态？在一本技术手册里，介绍指令、处理器特性和操作系统支持的段落可能相隔几十页。本实验从 Intel 手册选了 14 页，为相同的 8 个问题做了两种教学版索引。RAPTOR 侧生成三组父摘要和一份根摘要，在各层节点中检索；GraphRAG 侧沿实体的邻居、关系及社区摘要寻找材料。先看每种方法究竟取回哪些页，再决定读哪些原文。

打开[逐题结果](validation/runs/20260729T200642Z-3_7-4d2d5f9c/evidence.json)，找到 `relation_cpuid_insufficient` 的两条记录。这题的标注页是 323、363、364，两种方法都漏掉 323 页，来源页覆盖率同为 2/3。文件中的 `explicit_multi_hop_paths` 还列出一条可以沿着阅读的线索：CPUID 指令 → XSAVE 特性 → CR4.OSXSAVE → XCR0 → YMM 寄存器状态。检索到实体名称后，要回到标注页，逐项核实处理器报告了什么、操作系统需要支持什么，以及回答中是否交代了这些条件。

换一道 `concept_sse_environment` 题。它问的是 SSE 编程环境，标注依据为第 254 至 257 页。层次摘要返回的节点合计关联全部 14 页，实体关系索引返回的条目合计关联 7 页，两者都覆盖了这 4 页，得分同为 4/4。一份摘要提及很多页就能得满分，可读者接下来要翻的材料明显不同。八题中其余七题都找齐标注页，因此两种方法的平均覆盖率同为 (7 + 2/3) / 8 ≈ 95.8%。要进一步解释差别，可以读 `retrieval_trace`、`answer` 并核对原页。[运行索引](validation/latest.json)与[请求记录](validation/runs/20260729T200642Z-3_7-4d2d5f9c/)保留了本次配置。下文的离线 ADDPS 示例适合练手，它走的是预设路径。

[English](#english)

[树形摘要与实体关系怎样组织证据](#learning-0) · [选择手册记录或本地示例](#learning-1) · [沿层次摘要和关系路径检索](#learning-2) · [核对答案引用的来源页](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 树形摘要与实体关系怎样组织证据

**层次摘要索引。** 同一段原文可以用不同的粗细来概括。先为手册的每一页生成摘要，把内容接近的页聚成组，再给每组和整棵树写摘要。正式实验把各层节点放在一起，与查询向量比较，取最相关的五个。因此，一次查询可能同时取回全局概览和某一页的细节。项目中的通用索引器还提供 GMM 聚类和 UMAP 降维。

**实体关系索引。** 建图时，模型从原文提取实体和关系，再为关联紧密的实体群生成社区摘要。正式实验先按查询选七个实体，再将它们的直接邻居、相关关系和最多两份社区摘要放入回答材料。部分关系题还给了两个端点。例如题目配置给出 `CPUID` 和 `YMM`，程序在图上寻找连接它们的最短路径，连同其他材料交给回答模型。读这条路径时，可以检验中间的每条边有没有原文依据；要检验系统能否从自然语言问题自己找出两个端点，还得拿掉提示再跑一次。[查询实现](campaign.py)

两种索引都可以通过 HTTP API 构建和查询。服务还支持上传文档、异步处理大文档、混合检索和查看状态统计。

<a id="learning-1"></a>

## 选择手册记录或本地示例

正文比较的是 Intel 手册中的 14 页。想先了解路径怎样连接，可以运行 `main.py demo`；要复核 95.8% 的来源页覆盖率，应读取本页开头的八题归档。

### 安装

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

cd chapter3/structured-index

# 精确复现旧版单项目环境，含可选 RAPTOR/GraphRAG/Azure 依赖：
# python -m pip install -r requirements.txt

cp env.example .env
```

<a id="learning-2"></a>

## 沿层次摘要和关系路径检索

先运行示例查询，观察它怎样从索引中找到相关材料，再阅读两种索引器的构建流程。准备自己的文档后，先检查少量节点和对应原文，确认结构没有失真，再扩展到完整索引。

### 从示意结构走向真实索引

`python main.py demo` 使用示意数据解释平坦检索、层次摘要和关系图的区别，不需要先构建真实索引。读懂示例后，再准备自己的文档，并按下面的构建命令接入模型。构建阶段需要核对摘要和实体关系是否忠实于原文；查询阶段则要检查返回的节点能否提供回答所需的具体证据。

### 命令行

所有子命令有中文 `--help`：

```
usage: main.py [-h] {build,query,demo,serve} ...
  build   从文档构建结构化索引（需要 OPENAI_API_KEY）
  query   查询已构建的索引
  demo    离线对比：结构化 vs 扁平（无需 API Key）
  serve   启动 HTTP API
```

#### 0. 离线对比演示（推荐先跑）

```bash
python main.py demo
python main.py demo --query "VADDPS 用到哪个寄存器"
python main.py demo --output demo_result.json
```

示例输出见 English 节：扁平只能召回词面片段；图检索可经 `ADDPS → SSE → CR4.OSFXSR` 多跳得到答案。

#### 1–3. 构建 / 查询 / 服务

```bash
python main.py build path/to/document.pdf
python main.py build path/to/document.pdf --type raptor
python main.py build path/to/document.pdf --type graphrag
python main.py build path/to/document.pdf --output stats.json

python main.py query "What are the MOV instruction variants?"
python main.py query "explain SSE instructions" --type raptor --top-k 10
python main.py query "SSE registers" --type graphrag --multi-hop 2
python main.py query "control registers" --output result.json

python main.py serve
```

HTTP 示例与端点表与 English 节相同。

<a id="learning-3"></a>

## 核对答案引用的来源页

在本实验目录运行以下代码，只需 Python 标准库。先把这道 AVX 题的标注页与检索结果作差，再看回答有没有得到评审模型的认可。

```python
import json
from pathlib import Path

record = Path("validation/runs/20260729T200642Z-3_7-4d2d5f9c/evidence.json")
results = json.loads(record.read_text(encoding="utf-8"))["results"]
for row in results:
    if row["query_id"] != "relation_cpuid_insufficient":
        continue
    missing = set(row["gold_pages"]) - set(row["retrieved_pages"])
    print(row["method"], "缺页", sorted(missing), "答案判对", row["external_judge"]["correct"])
    if row["method"] == "graphrag":
        path = row["retrieval_trace"]["explicit_paths"][0]
        print("给定端点", path["hints"], "找到的路径", " → ".join(path["nodes"]))
```

两组都缺第 323 页，两份回答却都被评审模型判对。这两个结果可以同时成立：覆盖率检查取回的节点关联了哪些手册页，评审模型则对照参考答案检查解释。若要判断回答中的某个条件是否有充分依据，仍要回到相关页，找到支持它的那段话。

### 检查自己的解释

“某功能在哪里定义”和“几种功能有什么共同设计”分别更适合怎样的检索入口？

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — **Experiment 3-7**: hierarchical RAPTOR trees vs GraphRAG knowledge graphs, plus offline structured-vs-flat demo.  
> 配套《深入理解 AI Agent》第 3 章 **实验 3-7**：RAPTOR 层次树 vs GraphRAG 知识图谱，含离线「结构化 vs 扁平」演示。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 项目结构

```
structured-index/
├── config.py, raptor_indexer.py, graphrag_indexer.py
├── document_processor.py, api_service.py
├── structured_vs_flat_demo.py
├── main.py, requirements.txt, env.example
├── indexes/{raptor,graphrag}/, cache/
```

<a id="learning-5"></a>

## 排错与参考

### 性能与排错

大文档耗时；注意限流与内存。OOM 减小 chunk；检查 API Key。

### 参考

[RAPTOR](https://arxiv.org/abs/2401.18059) · [GraphRAG](https://github.com/microsoft/graphrag) · [Intel SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

Chat LLM for RAPTOR summarization and GraphRAG entity extraction can use OpenRouter when `OPENROUTER_API_KEY` is set. **Embeddings stay local SentenceTransformers (all-MiniLM-L6-v2)** and are unaffected.

## English

### Overview

Two advanced approaches for large technical documents (e.g. Intel® SDM-style manuals):

1. **RAPTOR** — hierarchical tree with recursive abstractive summarization  
2. **GraphRAG** — entities, relations, communities, multi-hop traversal  

### Features

**RAPTOR:** multi-level abstraction; recursive summaries; root→leaf search; GMM clustering; UMAP.

**GraphRAG:** LLM entity/relation extract; community detection; community summaries; multi-strategy search; **`GraphRAGIndexer.multi_hop_search`** for “how is A connected to B” questions flat vector search cannot express.

**HTTP API:** build/query, uploads, async large docs, hybrid search, stats.

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

cd chapter3/structured-index

# Exact legacy parity path, including optional RAPTOR/GraphRAG/Azure packages:
# python -m pip install -r requirements.txt

cp env.example .env
# API keys and preferences
```

### CLI

Chinese `--help` on all subcommands: `python main.py --help`, `python main.py demo --help`, etc.

```
usage: main.py [-h] {build,query,demo,serve} ...
  build   Build structured indexes (needs OPENAI_API_KEY)
  query   Query existing indexes (needs key + built indexes)
  demo    Offline structured vs flat compare (no API key)
  serve   Start HTTP API
```

#### 0. Offline demo (no API key — recommended first)

Hand-curated small Intel x86 SIMD knowledge base; three query types: multi-hop, cross-node synthesis, multi-level navigation.

```bash
python main.py demo
python main.py demo --query "VADDPS 用到哪个寄存器"
python main.py demo --output demo_result.json
```

Example (multi-hop; flat fails, graph succeeds):

```
【查询 1｜多跳关系推理】运行 ADDPS 指令前，操作系统必须把哪个控制寄存器位置 1？
-- 扁平检索（按词面相似度返回独立片段）--
  1. [control-bit] CR4.OSFXSR  (score=0.459)
  ...
  ✗ 只能召回词面相近的孤立片段，无法把 ADDPS 与某个控制位「连」起来。
-- 结构化图检索（沿关系边多跳遍历）--
  ADDPS --属于--> SSE --需要启用--> CR4.OSFXSR
  ✓ 答案：CR4.OSFXSR（从 ADDPS 经 2 跳可达）
```

> `build` / `query` need real indexes (LLM for entities/summaries) → `OPENAI_API_KEY` (embeddings: local SentenceTransformers). `demo` uses hand-authored structure so readers see the point without keys.

#### 1. Build (needs OPENAI_API_KEY)

```bash
python main.py build path/to/document.pdf
python main.py build path/to/document.pdf --type raptor
python main.py build path/to/document.pdf --type graphrag
python main.py build path/to/document.pdf --output stats.json
```

#### 2. Query

```bash
python main.py query "What are the MOV instruction variants?"
python main.py query "explain SSE instructions" --type raptor --top-k 10
python main.py query "SSE registers" --type graphrag --multi-hop 2
python main.py query "control registers" --output result.json
```

#### 3. Serve

```bash
python main.py serve
# http://localhost:4242
```

### HTTP API examples

```bash
curl -X POST "http://localhost:4242/upload" \
  -F "file=@path/to/intel_manual.pdf" \
  -F "index_type=both"

curl -X POST "http://localhost:4242/build" \
  -H "Content-Type: application/json" \
  -d '{"file_path": "/path/to/document.pdf", "index_type": "both", "force_rebuild": false}'

curl -X POST "http://localhost:4242/query" \
  -H "Content-Type: application/json" \
  -d '{"query": "What are vector instructions?", "index_type": "hybrid", "top_k": 5}'

curl http://localhost:4242/status
curl http://localhost:4242/statistics
```

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API info |
| `/build` | POST | Build from text/file |
| `/upload` | POST | Upload + build |
| `/query` | POST | Query indexes |
| `/status` | GET | Status |
| `/statistics` | GET | Stats |
| `/indexes` | DELETE | Clear |

### Project structure

```
structured-index/
├── config.py, raptor_indexer.py, graphrag_indexer.py
├── document_processor.py, api_service.py
├── structured_vs_flat_demo.py   # offline demo
├── main.py, requirements.txt, env.example
├── indexes/{raptor,graphrag}/, cache/
```

### How it works

**RAPTOR:** chunk → embed → leaves → GMM cluster → parent summaries → multi-level tree → multi-level search.

**GraphRAG:** entity extract → relations → NetworkX graph → communities → summaries → hierarchical merge → entity/community search (+ multi-hop).

### Advanced params (see `config.py`)

RAPTOR: `chunk_size`, `chunk_overlap`, `tree_depth`, `summarization_length`.  
GraphRAG: `chunk_size`, `max_knowledge_triples`, community algorithm, summarization model.

### Performance / troubleshooting

Large manuals take time; watch API rate limits and memory. Cache speeds re-queries. OOM → smaller chunks; check keys; start with smaller models for tests.

### Integration

Backend for agentic-rag style projects; see related chapter labs.

### References

- [RAPTOR](https://arxiv.org/abs/2401.18059)  
- [GraphRAG](https://github.com/microsoft/graphrag)  
- [Intel SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)  

---
