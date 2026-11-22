# 用 Mem0 和 Kimi 观察跨会话记忆 / Exploring cross-session memory with Mem0 and Kimi

引入记忆框架后，应用可以把信息提取与检索交给专门组件，但仍需理解框架实际保存了什么。本实验用 Mem0 连接对话与长期存储，观察一条信息怎样进入后续回答。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

记忆操作包含提取、写入、搜索和使用。应用还需要提供用户标识，把不同用户的数据隔离开来。框架返回的片段应经过语境核对，不能因为它被称为“记忆”就默认始终正确。

### 概述

同一个用户先说住在北京，后来搬到上海。下一次问起住址时，Agent 能找回哪些记录？回答又采用了哪一条？本实验让同一用户和 Agent 跨会话使用 Mem0，分别检查事实写入、候选记忆和最终回答。课堂练习借用了 LoCoMo 的长程对话问题。原始 LoCoMo 提供已有的对话、问题和标注；这里的对话由本地脚本生成。[LoCoMo 数据集与任务说明](https://snap-research.github.io/locomo/)

### 一轮对话怎样使用记忆

`experiment.py` 会轮换协作规划、信息共享、多步解题、谈判、教学五类场景，在每个场景中生成多次会话，随机选择回答的 Agent。同一场景内用户标识固定；检索同时按用户和 Agent 标识过滤，同一 Agent 能跨会话读到自己的记录。每一轮先取最多五条相关记忆，将其与最近的对话放入模型输入，收到回答后，再把本轮问答交给 Mem0 提取事实。

本地模式使用 Mem0 OSS 的 v3 记忆管线（Python 依赖为 `mem0ai[nlp]>=2.0,<3`），由 SDK 执行仅追加的事实提取与混合检索。抽取和答题按配置使用语言模型，嵌入使用独立的 OpenAI 配置。也可以切换到 Mem0 Cloud，由服务端处理记忆。默认答题模型为 Moonshot 的 `kimi-k3`；使用下文的 OpenRouter 回退时，应在结果的 `config.kimi.model_name` 中核对实际配置。

### 运行本地场景

先用 `python experiment.py --scenarios 1 --output results/` 跑通一类场景。如果要轮换五类各两次，再运行：

```bash
python experiment.py --scenarios 10 --output results/
```

在输出目录打开 `locomo_results_*.json`，先读 `scenarios` 中一轮实际的提问与回答，再看汇总字段。文件名沿用旧名。脚本没有加载 LoCoMo 的对话、参考答案或官方评分器，输出不可用于复现论文分数。

- **一致性和连贯性**是教学用的近似指标。前者检查英文回答中是否出现 `however`、`I was wrong` 等转折或纠正用语；后者按空格切词，计算提问中的词在回答里出现的比例。诚实纠错可能降低前一项，简单复述提问也可能抬高后一项。要判断是否记对事实，需要回查具体对话。
- **生成耗时**（`avg_response_time`）只覆盖答题模型的生成调用；检索在计时前，写入在计时后。回答长度按字符计。
- **记忆数量**（`memory_utilization`）是查询该场景用户时返回的条数，上限为 100。它可以帮助检查是否写入了记录。要测事实召回率，应另列应答事实，并逐条核对回答。

### 架构与后端

- `agent.py` / `config.py` / `experiment.py`  
- 本地 Chroma 或 Mem0 Cloud（配置见 English 节代码块）

<a id="learning-1"></a>

## 准备环境与输入

下面会用到模型服务。先按配置说明选择一个提供商，准备对应的模型名称、服务地址和 API Key，再运行小规模例子。一次完整运行的费用取决于模型、输入长度和调用次数。

### 安装

Python 3.12 与根目录 `ch3` extra（包含实体 / BM25 信号所需的 Mem0 NLP 支持）、Kimi API Key；可选 Mem0 云端 Key。

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

cd chapter3/mem0

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
# 编辑 .env 填入 API Key
```

环境变量：

- `KIMI_API_KEY`  
- `MODEL_NAME`（默认 `kimi-k3`）——**原始 Moonshot 模型 id**，不要用 `provider/model` 斜杠形式  
- `MEMORY_BACKEND`：`local` / `cloud`  
- `MAX_TOKENS`（默认 128000，作为聊天请求的生成上限）
- `OPENAI_API_KEY`（本地后端的默认嵌入模型使用）

<a id="learning-2"></a>

## 按照步骤完成实验

按下文准备依赖、存储和模型凭据后，运行单用户演示。先输入一条清晰事实，再换一种问法查询；随后加入修正信息，观察存储与检索结果怎样变化。

### 用一次写入和一次追问检查记忆

先输入一条容易核对、且不涉及真实隐私的偏好，例如“演示用户希望回答附带单位”。完成写入后，查看实际保存的记录，再用一个确实需要单位的问题追问。最后提出一个与该偏好无关的问题，检查系统是否错误地到处套用它。这样能依次检查保存、检索和使用三个环节。

### 快速开始

```bash
python quickstart.py
```

#### 记忆管线演示（仅追加提取 + 混合检索）

```bash
python main.py --mode demo --user-id demo_user
```

书中示例：先说住在北京，后来说搬到上海。检查存储中是否同时出现两次陈述，再看检索顺序和回答。若回答仍是北京，先查上海这条事实是否已写入、是否被检索到，再看模型如何判断先后。

#### 直接记忆操作 CLI

```bash
python main.py --help

python main.py --mode memory --op add   --text "我住在北京，是一名后端工程师" --user-id u1
python main.py --mode memory --op search --query "这个用户住在哪里？" --user-id u1
python main.py --mode memory --op get-all --user-id u1 --output mem.json
python main.py --mode memory --op history --memory-id <id>
python main.py --mode memory --op delete --memory-id <id>
```

无 Key 时 CLI 会解析参数后明确报错，**不会伪造**记忆输出。

#### 交互 / 批处理

```bash
python main.py --mode interactive
python main.py --mode batch --input conversations.json --output results.json
```

<a id="learning-3"></a>

## 分析结果与形成判断

检查新增内容是否来自对话，检索是否命中了正确用户，以及旧事实是否仍影响回答。若要与第三章介绍的标准基准比较，还需单独接入相同数据、问题与评分方法。

### 检查自己的解释

如果事实已经成功写入，但问答仍然失败，你会先检查检索条件还是模型上下文？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — Mem0 memory framework + Kimi for long-context multi-session memory (Experiment 3-2 comparison track).  
> 配套《深入理解 AI Agent》第 3 章——Mem0 记忆框架 + Kimi，长上下文多会话记忆（实验 3-2 的延伸练习）。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 项目结构

```
mem0/
├── agent.py, config.py, experiment.py, main.py, quickstart.py
├── requirements.txt, env.example, README.md
```

<a id="learning-5"></a>

## 排查问题与查阅资料

### 故障排查

检查 `KIMI_API_KEY`、`./data/` 写权限、`MEM0_API_KEY`；`LOG_LEVEL=DEBUG`。

### 局限与许可

需联网调用 API；记忆随使用增长；实验中上下文有上限。教学材料许可。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

- Primary provider keys unchanged if set.  
- Else `OPENROUTER_API_KEY` routes chat LLM via `https://openrouter.ai/api/v1` with automatic model id mapping; `OPENROUTER_MODEL` forces a specific id.  
- **Note:** Mem0’s embedder still uses OpenAI embeddings (OpenRouter has no embeddings endpoint), so `OPENAI_API_KEY` is still required for store/retrieve. OpenRouter only covers the chat LLM (ADD-only fact extraction and answering).

Add `OPENROUTER_API_KEY=...` to `.env` (see `env.example`).

## English

### Overview

An agent that combines the **Mem0** memory framework with the **Kimi** language model for LOCOMO-style long-context multi-agent / multi-session tasks:

- **Persistent memory** via Mem0 across sessions  
- **Kimi** integration (experiment caps context budget below the model’s full window)  
- locally generated multi-session scenarios
- Multi-session and multi-agent collaboration with shared memory  

### Features

**Core:** Mem0 v3 ADD-only extraction and hybrid retrieval; context preservation; metrics (consistency, coherence, latency, memory use); local or cloud memory backend.

**Local scenarios:** collaborative planning; information sharing; multi-step problem solving; negotiation; teaching & learning.

### Installation

Prerequisites: Python 3.12 with the root `ch3` extra (including Mem0's NLP support for entity/BM25 signals), Kimi API key; optional Mem0 cloud key.

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

cd chapter3/mem0

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# Edit .env with API keys
```

Required env:

- `KIMI_API_KEY`  
- `MODEL_NAME` (default `kimi-k3`) — **raw Moonshot model id** (e.g. `kimi-k3`, `kimi-k2.5`); do **not** use `provider/model` slash form; Mem0 uses OpenAI-compatible provider pointed at Moonshot `base_url` and forwards the string verbatim (`kimi/k3` → “Not found the model”)  
- `MEMORY_BACKEND`: `local` / `cloud`  
- `MAX_TOKENS` (default 128000)  

### Quick start

```bash
python quickstart.py
```

Shows basic chat with memory, multi-session persistence, multi-agent collaboration.

#### Memory pipeline demo (ADD-only extraction + hybrid retrieval)

Demonstrates Mem0 v3's append-only history and cross-session recall:

```bash
python main.py --mode demo --user-id demo_user
```

Book example: a user lives in Beijing and later moves to Shanghai. Mem0 preserves both dated facts, while hybrid, time-aware retrieval ranks the current one. Same routine: `memory_pipeline_example()` in `quickstart.py`.

#### Direct memory operations CLI

```bash
python main.py --help   # Chinese descriptions

python main.py --mode memory --op add   --text "我住在北京，是一名后端工程师" --user-id u1
python main.py --mode memory --op search --query "这个用户住在哪里？" --user-id u1
python main.py --mode memory --op get-all --user-id u1 --output mem.json
python main.py --mode memory --op history --memory-id <id>
python main.py --mode memory --op delete --memory-id <id>
```

Flags: `--op {add,search,get-all,history,delete}`, `--text`, `--query`, `--memory-id`, `--user-id`, `--agent-id`, `--model`, `--output`. `--text` may be a raw string or path to a JSON message list.

> Demo, memory ops, and chat modes need a working LLM key (`KIMI_API_KEY`) and vector store. Without a key the CLI parses args then reports the missing key—no fabricated memory output.

#### Interactive / batch

```bash
python main.py --mode interactive
# commands: help, memories, metrics, save, load, new, exit

python main.py --mode batch --input conversations.json --output results.json
```

Batch input format:

```json
[
  {
    "session_id": "session_001",
    "user_id": "user_001",
    "agent_id": "agent_001",
    "turns": ["First user message", "Second user message"]
  }
]
```

### Local multi-session exercise

```bash
python experiment.py --scenarios 10 --output results/
```

The runner uses local prompts and heuristic scores. It does not load or score the official LoCoMo dataset. Results under `results/` include per-scenario and overall metrics.

### Architecture

- `agent.py`: `Mem0Agent`, `KimiK3Client`, `AgentContext`  
- `config.py`: Kimi / Mem0 / LOCOMO config  
- `experiment.py`: `LOCOMOBenchmark`  

Mem0 provides append-only extraction, hybrid retrieval, and multi-level (user/agent/session) organization.

### Memory backends

```python
# Local Chroma
config.mem0.backend = "local"
config.mem0.vector_store_config = {
    "provider": "chroma",
    "config": {"collection_name": "my_collection", "path": "./data/chroma_db"}
}

# Cloud
config.mem0.backend = "cloud"
config.mem0.api_key = "your_mem0_api_key"
```

### Troubleshooting

1. API key: set valid `KIMI_API_KEY` in `.env`  
2. Local backend: write permission under `./data/`  
3. Cloud: valid `MEM0_API_KEY`  
4. Debug: `export LOG_LEVEL=DEBUG`  

### Project structure

```
mem0/
├── agent.py, config.py, experiment.py, main.py, quickstart.py
├── requirements.txt, env.example, README.md
```

### Limitations

Needs network for APIs; memory grows with use; context capped in experiment config; quality depends on model availability.

### License / acknowledgments

Part of AI Agent Book materials. Mem0 by Mem0 AI; Kimi by Moonshot AI.

---
