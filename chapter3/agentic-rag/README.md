# Agentic RAG System / Agentic RAG 系统

一次检索往往只能回答问题的一部分。Agentic RAG 让模型根据当前证据决定是否追加检索、改写问题或查看相关条目。本实验关注多步取证与一次性检索的区别。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

每次检索都会改变模型下一轮能看到的信息。关键不是“检索次数多”，而是新检索是否填补了明确的证据缺口。若没有停止条件，Agent 也可能反复查找同一内容。

### 检索结果怎样决定下一步行动

普通问答常在一次检索后直接回答；这里的 Agent 可以根据已有证据决定继续检索或停止。先为一个问题列出回答必须具备的事实，再沿轨迹检查每次查询是否补齐了缺口。多检索几次并不自动更好：重复查询、没有依据的停止以及对无关片段的过度解释，都需要在轨迹中定位。

### 功能特性

- **Agentic RAG（ReAct）** 与 **非 Agentic RAG** 对照  
- 多 LLM 提供商；知识库：**离线 BM25** / 本地检索流水线 / Dify  
- 分块、中文法条评测、多轮对话、详细日志

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 安装与配置

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

cd chapter3/agentic-rag

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt
```

环境变量见 English 节（`MOONSHOT_API_KEY` 等；`KB_TYPE=offline|local|dify`）。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读离线比较程序中的问题和目标证据，再运行下文中的离线路径。选一道需要多个片段的问题，按轮次记录找到什么、还缺什么。之后配置模型和知识库，比较真实生成过程。

### 用法

#### 0. 零依赖离线对比（推荐先跑）

```bash
python compare_offline.py
```

实测证据召回表见 English 节：简单题两种范式均约 100%；复杂题 **8% → 100%**。也可用：

```bash
python main.py --kb-type offline --query "醉酒过失致人重伤且有盗窃前科如何量刑"
python main.py --kb-type offline --query "故意杀人罪判几年" --mode compare
```

#### 1–4. 流水线、索引、运行、评测

```bash
cd ../retrieval-pipeline && python main.py

python index_local_laws.py
python index_local_laws.py --categories 宪法 民法典
python main.py --index path/to/documents/ --chunk-size 2048

python main.py
python main.py --mode non-agentic
python main.py --query "宪法第一条是什么？" --mode agentic
python main.py --query "故意杀人罪判几年？" --mode compare
python main.py --batch queries.txt --output results.json
python main.py --provider openai --model gpt-5.6-luna

cd evaluation && python dataset_builder.py && python evaluate.py
```

交互命令：`quit`/`exit`、`clear`、`mode`。

<a id="learning-3"></a>

## 分析结果与形成判断

离线证据召回反映是否找到了指定材料，不能替代回答正确性。对于示例法律文本，还应核对来源与适用条件；这里练习的是检索方法，不应把模型输出直接作为现实事务的处理依据。

### 结果解读

检索层见 §0 表；生成层用 `evaluation/evaluate.py`（需 API）。Agentic 覆盖更全、更慢；Non-Agentic 更快、对复杂/歧义问题更弱。

### 检查自己的解释

模型应凭什么判断已经找齐证据，而不是因为输出长度或调用次数到了上限就结束？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — **Experiment 3-8**: ReAct agentic vs non-agentic RAG on Chinese legal Q&A; offline multi-hop evidence recall.  
> 配套《深入理解 AI Agent》第 3 章 **实验 3-8**：ReAct 式 Agentic vs 非 Agent 式 RAG 司法问答；离线多跳证据召回对比。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 项目结构与原理

与 English 节相同：`offline_retriever.py` / `compare_offline.py` / `laws/` / `evaluation/`。  
Agentic：多轮检索+引用；Non-Agentic：单次检索注入 prompt。

<a id="learning-5"></a>

## 排查问题与查阅资料

### 故障排查

检查 `http://localhost:4242/health`、是否已 `index_local_laws.py`、API Key 与 UTF-8 编码。

### 许可

教学项目。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

Primary provider keys take precedence; else `OPENROUTER_API_KEY` routes chat via OpenRouter with model id mapping. See `env.example`. Related: [`../agentic-rag-for-user-memory/`](../agentic-rag-for-user-memory/).

## English

### Canonical live campaign

`python campaign.py` runs the acceptance experiment, not just the offline
mechanism demo. It keeps the 288-file law corpus, labeled questions, BM25
depth, answer model, and external judge identical while changing only one-shot
retrieval versus live ReAct search. Exact chunks, citations, generated search
queries, latency/usage, ARK/Moonshot request-response receipts, and corpus file
hashes are written under `validation/runs/<run-id>/`; the auditable pointer is
`validation/latest.json`.

### Features

- **Agentic RAG (ReAct)**: iterative reason + tool search  
- **Non-agentic RAG**: single retrieve + answer (for compare)  
- **LLM providers**: Alibaba Cloud Model Studio / Bailian (Qwen), Kimi/Moonshot, Doubao, SiliconFlow, OpenAI, OpenRouter, Groq, Together, DeepSeek
- **Knowledge bases**:  
  - **Offline BM25** (built-in, zero deps) over bundled `laws/` — no server/API for retrieval  
  - Local retrieval pipeline (`../retrieval-pipeline`)  
  - Dify KB API  
- Chunking with paragraph respect; evaluation on Chinese legal data; conversation history; verbose logs  

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

cd chapter3/agentic-rag

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt
```

### Configuration

```bash
# LLM keys (set the ones you use)
MOONSHOT_API_KEY=...
ARK_API_KEY=...
SILICONFLOW_API_KEY=...
DASHSCOPE_API_KEY=...  # Alibaba Cloud Model Studio / Bailian (Qwen)
# DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=...
OPENROUTER_API_KEY=...
GROQ_API_KEY=...
TOGETHER_API_KEY=...
DEEPSEEK_API_KEY=...

KB_TYPE=local  # "offline" | "local" | "dify"
DIFY_API_KEY=...
DIFY_DATASET_ID=...

LLM_PROVIDER=kimi
LLM_MODEL=kimi-k3
```

### Usage

#### 0. Zero-dep offline compare (recommended first; no API / no external service)

Core claim: **for complex questions, agent-style multi-hop / decomposed retrieval recalls evidence much better than a single query**. `compare_offline.py` uses built-in offline BM25 (`offline_retriever.py` over `laws/`) on a small Chinese judicial QA set—**fully offline, no API key**:

```bash
python compare_offline.py
# optional: --corpus laws  --top-k 5  --dataset evaluation/offline_qa.json  --output result.json
```

Real output (measured; 21372 law chunks / 288 docs):

```
问题                          难度    单次检索    分解检索    检索次数
------------------------------------------------------------------------------
故意伤害致人重伤的，如何处…  easy    100%        100%        1 → 1
正当防卫是怎么规定的？        easy    100%        100%        1 → 1
醉酒驾驶机动车如何处罚？      easy    100%        100%        1 → 1
故意杀人罪判几年？            hard    0%          100%        1 → 1
盗窃罪的立案标准是什么？      hard    0%          100%        1 → 1
诈骗罪的量刑标准是什么？      hard    0%          100%        1 → 1
醉酒过失致人重伤且有盗窃前…  hard    33%         100%        1 → 3
------------------------------------------------------------------------------
聚合指标（平均证据召回率）:
  全部                                48%         100%        1.0 → 1.3
  简单题                              100%        100%        1.0 → 1.0
  复杂题                              8%          100%        1.0 → 1.5
```

Reading (aligned with Exp. 3-8): **easy questions ~tied at 100%**; **hard/poorly phrased: 8% → 100%**. Metric is pure retrieval **evidence recall** (upper bound on answer quality). Gold statutes are confirmed present in `laws/`.

> Offline mode uses pre-labeled `subqueries` for “agent decomposed search” to isolate **retrieval strategy**; real systems generate subqueries in the ReAct loop. End-to-end answer quality: `evaluation/evaluate.py` (needs API key).

Full agent on offline KB (retrieval offline; **answer generation** needs API):

```bash
python main.py --kb-type offline --query "醉酒过失致人重伤且有盗窃前科如何量刑"
python main.py --kb-type offline --query "故意杀人罪判几年" --mode compare
```

#### 1. Start retrieval pipeline (for local KB)

```bash
cd ../retrieval-pipeline
python main.py
# http://localhost:4242
```

#### 2. Index documents

```bash
python index_local_laws.py
python index_local_laws.py --categories 宪法 民法典
python index_local_laws.py --max-docs 10

python main.py --index path/to/document.txt
python main.py --index path/to/documents/
python main.py --index documents/ --chunk-size 2048
```

#### 3. Run Agentic RAG

```bash
python main.py
python main.py --mode non-agentic
python main.py --verbose
python main.py --no-verbose

# Single query
python main.py --query "宪法第一条是什么？" --mode agentic
python main.py --query "盗窃罪的立案标准是什么？" --mode non-agentic
python main.py --query "故意杀人罪判几年？" --mode compare

# Batch
python main.py --batch queries.txt --output results.json
python main.py --batch queries.txt --mode non-agentic

# Providers
python main.py --provider openai --model gpt-5.6-luna
python main.py --provider doubao --model doubao-seed-1-6-thinking-250715
python main.py --provider siliconflow --query "你好"
python main.py --provider dashscope --model qwen3.7-plus --query "你好"
```

Interactive: type questions; `quit`/`exit`; `clear` history; `mode` switch agentic/non-agentic.

#### 4. Evaluation

```bash
cd evaluation
python dataset_builder.py
python evaluate.py
python evaluate.py --provider kimi --kb-type local --output custom_results
```

### Project structure

```
agentic-rag/
├── config.py, agent.py, tools.py
├── offline_retriever.py, compare_offline.py
├── chunking.py, main.py, index_local_laws.py
├── quickstart.py, test_simple.py, requirements.txt
├── laws/   # Chinese law tree (宪法…程序法)
└── evaluation/
    ├── dataset_builder.py, offline_qa.json, evaluate.py
```

### How it works

**Agentic:** reason → `knowledge_base_search` → iterate → optional `get_document` → synthesize with citations → memory for follow-ups.

**Non-agentic:** one search with raw query → top-K in prompt → one LLM answer.

### Config knobs

`local_top_k`, `--verbose` / `--no-verbose`, `temperature` in `config.py`.

### Evaluation results

**Retrieval layer (offline, reproducible):** table in §0 — hard questions **8% → 100%** evidence recall.

**Generation layer (needs API):** `evaluation/evaluate.py` — success/key-concept recall, latency, citation coverage. Agentic: better multi-facet coverage and citations; slower. Non-agentic: faster; weaker on ambiguous queries.

### Troubleshooting

```bash
curl http://localhost:4242/health
cd ../retrieval-pipeline && python main.py

python index_local_laws.py
ls -la document_store.json
curl http://localhost:4242/stats
```

API keys: check env / `.env`. Indexing needs pipeline up and UTF-8 files when using local mode.

### License

Educational project.

---
