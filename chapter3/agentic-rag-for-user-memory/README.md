# Agentic RAG for User Memory / 面向用户记忆的 Agentic RAG

## 实验 3-9：用户说“我的车”时，助手应该查几次？

一位用户问：“我已经预约了哪些车辆保养服务？”助手准确答出本田雅阁的保养时间、地点，甚至价格。这份答案还遗漏了什么？先打开[逐题记录](validation/runs/20260729T214519Z-3_9-1bbf4623/evidence.json)，搜索 `layer2_01_multiple_vehicles`。沿着下面三处阅读，判断问题出在检索、回答还是验收。

1. 看 `agent_search_queries`。模型只搜了一次 `scheduled car services`。普通检索把八轮对话切成一块，相邻块重叠两轮，保留时间与会话元数据。每次取回四块，模型最多可以搜三次。
2. 看 `search_trajectory`。排名第一的片段提到特斯拉，以及两辆车的保险与道路救援服务。这是存在第二辆车的线索；要断言它也有预约，还需要找到能说明预约状态的记录。再翻到 `arms.plain.answer`：助手引用了两块与本田保养有关的对话，随即停止搜索。它既没有查清特斯拉的情况，也没有向用户说明这个缺口。
3. 看 `arms.plain.judge`。裁判在评语中指出遗漏了特斯拉，仍给出 `passed: true`，总奖励为 0.6875。由此可见，即使一道题通过，读者仍要核对委托中有没有一部分被落下。若要判断追加一次查询是否能补齐，可以保留原始四块及回答，再针对第二辆车搜索，用同一要求比较两份回答。

实验 3-9 和 3-11 共用这次受控运行及 60 道题。普通组通过 47 题，三层通过数分别为 19、15、13；其中 18 题只搜一次，6 题搜两次，36 题用满三次。能否找到足够证据比用没用完预算更值得检查。下文的 `offline_demo` 展示预设的多步查询，可与这条真实模型轨迹对照。[运行索引](validation/latest.json) · [结果与请求记录](validation/runs/20260729T214519Z-3_9-1bbf4623/)

[English](#english)

[从一个问题追查多段记忆](#learning-0) · [选择演示或检索后端](#learning-1) · [跟踪模型怎样追加查询](#learning-2) · [检查遗漏的车辆记录](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 从一个问题追查多段记忆

检索一次得到的信息可能只是线索，例如某次旅行的时间。Agent 需要利用线索继续寻找预算、同行者或后续修改。原始对话提供出处，不能把一次检索到的旧偏好直接当成当前事实。

### 学习目标

1. 长对话分块索引  
2. 对接外部混合检索流水线  
3. 工具调用 + ReAct 的 Agentic RAG  
4. LLM 自动打分评测记忆  
5. 面向对话查询的检索优化  
6. 跨项目评估框架集成

### 架构

项目默认把 20 轮对话切成一块，相邻块重叠两轮；本页引用的受控实验将窗口设为八轮。块中保存会话编号、时间和原文，方便从搜索结果追溯出处。助手通过记忆工具查询外部检索服务（4242 端口）或本地 BM25 索引，读完返回的片段后决定继续找还是作答，评审模型最后按题目要求检查回答。

### 关键概念

分块、混合检索、Agentic ReAct、自动 LLM 评测、上下文增强——与 English 节一致。

<a id="learning-1"></a>

## 选择演示或检索后端

`offline_demo.py` 提供一条可在本机阅读的搜索路径。要看模型在车辆题上实际搜了几次，打开本页开头链接的逐题记录，把查询词与每次命中的对话放在一起读。

### 前置条件

Python 3.12 与根目录 `ch3` extra。**4242 流水线可选**；默认 `auto` 回退本地 BM25。仅 LLM 模式需 API Key。**`offline-demo` 无需 Key 与 4242。**

### 安装与后端

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

cd chapter3/agentic-rag-for-user-memory

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env

# 可选
cd ../retrieval-pipeline && python api_server.py
```

| 值 | 行为 |
|----|------|
| `auto` | 默认可达则用流水线，否则本地 BM25 |
| `local` | 始终离线 BM25 |
| `pipeline` | 始终 4242 |

### 配置、用例层级、组件

`config.py` 分块/索引/Agent 参数；L1/L2/L3 用例；`chunker` / `indexer` / `tools` / `agent` / `evaluator`。

<a id="learning-2"></a>

## 跟踪模型怎样追加查询

先运行离线示例，比较多步路径与简单召回。对每个返回片段标记它回答了问题的哪一部分。再按下文接入模型和检索后端，用同一用户的多轮记录观察查询怎样变化。

### 运行

```bash
python main.py --mode offline-demo
python offline_demo.py
python offline_demo.py --output results/offline_demo.json

python test_pipeline.py
python main.py
python main.py --mode demo
python main.py --mode batch --category layer1 --backend local
```

CLI 标志见 English 节；`python main.py --help` 含中文说明。

<a id="learning-3"></a>

## 检查遗漏的车辆记录

检查是否找齐了必要片段、是否混入其他用户的内容，以及后来的修改有没有覆盖旧信息。离线示例展示检索结构，真实模型是否会提出同样的查询，需要另行观察。

### 第二辆车在哪一步消失了

先在车辆题的原始对话里标出两辆车，再看最后一次搜索到底取回了哪几段。如果特斯拉已经出现在命中片段里，重读回答，看看遗漏是在组织答案时发生的；如果片段里只提到一辆车，则回查查询词和分块位置。按这个顺序查，才知道下一次该改搜索还是改答题。

### 换了查询词，找回的记忆有什么变化？

保险变更题里有两个容易混淆的日期。用户在 9 月 15 日的通话中得知，新计划要到次年 1 月 1 日才生效。假如要回答“10 月份用哪份计划”，助手即使准确记得新计划的名称，也得把它说成即将发生的变更。检索结果排在前面，只说明片段与问题相关；要判断计划何时适用，还得读通知里的生效日期。

这道题实际用了三次搜索。在实验目录运行下面的代码，按片段编号数一数每次多读到了多少材料。

```python
import json
from pathlib import Path

record = Path("validation/runs/20260729T214519Z-3_9-1bbf4623/evidence.json")
rows = json.loads(record.read_text(encoding="utf-8"))["results"]
case = next(row for row in rows if row["test_id"] == "layer2_20_healthcare_coverage_changes")
seen = set()
for turn in case["search_trajectory"]:
    for call in turn["tool_calls"]:
        chunks = [hit["chunk_id"] for hit in call["results"]]
        print(call["query"], "返回", len(chunks), "新增", len(set(chunks) - seen))
        seen.update(chunks)
```

三次各返回四个片段，新增数依次是 4、3、0。最后一次把查询改成了 `HMO transition issues`，前四个结果连顺序都和上一次相同。若关心的是哪一天起换用新计划，可以回到第一次搜索已经找到的保险通知，核对原话。搜索次数增加到三次，并没有带来三份独立的证明。

### 离线演示结果

`layer2_01_multiple_vehicles` 上 naive 证据召回 **50%**、agentic **100%**（见 English 表）。

### 检查自己的解释

用户先说喜欢海边，后来取消旅行计划，系统应保留哪些记忆，又应怎样避免过时建议？

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — agentic multi-hop retrieval over conversation memory with offline demo and optional pipeline backend.  
> 配套《深入理解 AI Agent》第 3 章——对话记忆上的 Agentic 多跳检索；含离线演示与可选检索流水线。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

<a id="learning-5"></a>

## 排错与参考

### 故障排查

Top-k 需同时设 `top_k` 与 `rerank_top_k`；流水线不可达时用 `--backend auto/local`；LLM 评测需有效 Key 与 `evaluation_criteria`。

### 相关与许可

见同章 `user-memory`、`user-memory-evaluation`、`agentic-rag`、`contextual-retrieval`。教学用途。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

If primary keys are absent and `OPENROUTER_API_KEY` is set, chat LLM routes through OpenRouter with automatic model mapping. See `env.example`.

## English

### Canonical live campaign

`python campaign.py` launches the shared controlled Experiment 3-9/3-11
campaign over all 60 authoritative YAML cases. Experiment 3-9 uses fixed-round
windows and a live `search_user_memory` ReAct trajectory; raw retrieved chunks,
agent-generated searches, layer scores, and independent judge receipts are
retained. Canonical evidence is `validation/latest.json`.

### Learning objectives

1. Chunk long conversations for indexing  
2. Integrate external retrieval pipelines (hybrid search)  
3. Agentic RAG with tool-calling and ReAct  
4. Evaluate memory with automatic LLM scoring  
5. Optimize retrieval for conversation queries  
6. Integrate evaluation frameworks across projects  

### Architecture

```
User Memory Test Cases (60 cases, 3 layers)
        → Conversation Chunker (~20-round segments + overlap + enrichment)
        → External Retrieval Pipeline (port 4242) or local BM25
             Dense + Sparse hybrid
        → Agentic RAG Agent (ReAct; search_memory / get_conversation_context / get_full_conversation)
        → LLM Evaluation (reward 0–1, pass/fail, reasoning)
```

### Key concepts

1. **Conversation chunking** — ~20 rounds, searchable, contextual, efficient  
2. **Hybrid retrieval** (optional pipeline) — dense + BM25 + fusion; scalable  
3. **Agentic RAG** — Reason → Act → Observe → iterate  
4. **LLM evaluation** — integrates user-memory-evaluation style scoring (≥0.6 pass)  
5. **Contextual enrichment** — metadata, neighbors, tags  

### Prerequisites

- Python 3.12 with the root `ch3` extra
- **Port 4242 pipeline is OPTIONAL.** Default `retrieval_backend="auto"`: use pipeline if reachable, else **built-in local BM25** (offline).  
- API keys only for LLM modes (`batch` / `interactive` / `demo`).  
- **`--mode offline-demo` needs NO API key and NO port 4242.**  

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

cd chapter3/agentic-rag-for-user-memory

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# Edit API keys
```

### Retrieval backend

| value | behavior |
|-------|----------|
| `auto` | default — pipeline if up, else local BM25 |
| `local` | always offline BM25 |
| `pipeline` | always port 4242 |

Optional pipeline:

```bash
cd ../retrieval-pipeline
python api_server.py   # http://localhost:4242
```

### Running

```bash
# Offline multi-hop vs naive recall (no API, no 4242)
python main.py --mode offline-demo
python offline_demo.py
python offline_demo.py --output results/offline_demo.json

python test_pipeline.py
python main.py
python main.py --mode demo
python main.py --mode batch --category layer1 --backend local
```

CLI: `--mode {interactive,batch,demo,offline-demo}`, `--category`, `--test-id`, `--query`, `--provider`, `--model`, `--index-mode {dense,sparse,hybrid}`, `--backend {auto,local,pipeline}`, `--top-k`, `--rounds-per-chunk`, `--store-path`, `--test-cases-dir`, `--output`, `--config`. See `python main.py --help` (Chinese).

### Offline demo results (reproducible)

On `layer2_01_multiple_vehicles` (Honda + Tesla across sessions), real BM25:

| metric | naive single-query | agentic multi-hop |
|--------|:------------------:|:-----------------:|
| retrieval queries issued | 1 | 5 |
| memory chunks retrieved | 3 | 5 |
| decisive-evidence recall | **50%** | **100%** |
| can fully disambiguate & answer | no | yes |

Naive is dominated by “schedule service” keywords and misses Honda confirmation (`FS-447291`). Agentic discovers the second vehicle, issues focused follow-ups, recovers evidence. Numbers from actual retrieval, not hard-coded.

### Interactive options

Load / view test cases; configure chunking/index/agent; evaluate single or by category; generate reports.

### Example code

```python
from config import Config
from evaluator import UserMemoryEvaluator

config = Config.from_env()
evaluator = UserMemoryEvaluator(config)
test_cases = evaluator.load_test_cases(category="layer1")
result = evaluator.evaluate_test_case("layer1_01_bank_account")
report = evaluator.generate_report("results/evaluation_report.txt")
```

### Config highlights

```python
config.chunking.rounds_per_chunk = 20
config.chunking.overlap_rounds = 2
config.index.mode = "hybrid"
config.index.enable_contextual = True
config.agent.max_search_results = 5
config.evaluation.max_iterations = 10
```

### Test layers

- **L1** simple retrieval — “What is my checking account number?”  
- **L2** multi-conversation — “Which vehicle needs service first?”  
- **L3** complex reasoning — “What urgent issues before my trip?”  

### Components

`chunker.py`, `indexer.py`, `tools.py` (`search_memory`, `get_conversation_context`, `get_full_conversation` — full content), `agent.py` (ReAct), `evaluator.py`.

### Metrics / troubleshooting

Success rate, LLM reward, iterations, tool calls, latency, index time.  

**Top-k:** pipeline uses `top_k` (candidates) and `rerank_top_k` (final).  
**LLM eval missing:** need evaluator API + criteria.  
**Pipeline down:** not fatal with `--backend auto`; force offline with `--backend local`.

### Related

`user-memory`, `user-memory-evaluation`, `agentic-rag`, `contextual-retrieval` (chapter3 paths).

### License

Educational curriculum materials.

---
