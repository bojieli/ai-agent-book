# Structured Indexing: RAPTOR & GraphRAG / 结构化索引：RAPTOR 与 GraphRAG

有些问题只需一个段落，有些问题却要跨越多个章节。把文档切成平坦片段未必足够。本实验比较层次摘要与知识关系图，学习怎样为不同问题组织检索路径。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

RAPTOR 将片段逐层聚合成摘要，便于从全局主题走向细节；GraphRAG 将实体与关系连接起来，便于沿关联追踪证据。两者都依赖构建阶段的质量，结构本身不能保证摘要或关系正确。

### 概述

面向大型技术文档的两种结构化索引：

1. **RAPTOR** — 递归摘要的层次树  
2. **GraphRAG** — 实体/关系/社区与多跳遍历

### 功能

**RAPTOR：** 多层抽象、递归摘要、自根到叶检索、GMM 聚类、UMAP。  
**GraphRAG：** LLM 抽实体关系、社区发现、社区摘要、多策略检索、**多跳关系遍历**（扁平向量难以表达的「A 与 B 如何相连」）。  
**HTTP API：** 构建/查询、上传、异步大文档、混合检索、状态统计。

### 工作原理

**RAPTOR：** 分块 → 嵌入 → 叶节点 → 聚类 → 父节点摘要 → 多层树 → 多层检索。  
**GraphRAG：** 实体 → 关系 → 图 → 社区 → 摘要 → 层次聚合 → 实体/社区检索（+ 多跳）。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

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

## 按照步骤完成实验

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

## 分析结果与形成判断

回答涉及多个概念时，追踪证据经过哪些节点。层次摘要可能压掉细节，关系抽取也可能引入不存在的联系。应能从最终答案回到原始片段，而不只停留在生成的摘要上。

### 检查自己的解释

“某功能在哪里定义”和“几种功能有什么共同设计”分别更适合怎样的检索入口？

<a id="learning-4"></a>

## 阅读实现与继续探索

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

## 排查问题与查阅资料

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
