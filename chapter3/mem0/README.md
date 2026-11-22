# Mem0 Agent with Kimi K3 for LOCOMO Benchmark / Mem0 Agent 与 LOCOMO 评测

引入记忆框架后，应用可以把信息提取与检索交给专门组件，但仍需理解框架实际保存了什么。本实验用 Mem0 连接对话与长期存储，观察一条信息怎样进入后续回答。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

记忆操作包含提取、写入、搜索和使用。应用还需要提供用户标识，把不同用户的数据隔离开来。框架返回的片段应经过语境核对，不能因为它被称为“记忆”就默认始终正确。

### 概述

将 **Mem0** 记忆框架与 **Kimi** 语言模型结合，面向 LOCOMO 风格长上下文、多会话 / 多 Agent 任务：

- 跨会话**持久记忆**  
- Kimi 集成（实验中会限制上下文预算）  
- LOCOMO 场景评测  
- 多会话、多 Agent 共享记忆协作

### 功能

**核心：** Mem0 v3 的 ADD-only 抽取与混合检索；跨会话上下文保持；一致性、连贯性、时延、记忆利用率等指标；本地或云端记忆后端。

**LOCOMO 场景：** 协作规划、信息共享、多步解题、谈判、教与学。

### LOCOMO 基准

```bash
python experiment.py --scenarios 10 --output results/
```

指标：一致性、连贯性、记忆保持、响应时间、上下文利用等。

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
- `MAX_TOKENS`（默认 128000）

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

书中示例：先说住在北京，后来说搬到上海。Mem0 保留两条带时间的事实，由混合、时间感知检索优先返回当前事实。

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

检查新增内容是否来自对话，检索是否命中了正确用户，以及旧事实是否仍影响回答。运行标准数据集时，还要区分记忆机制的效果和回答模型本身的能力。

### 检查自己的解释

如果事实已经成功写入，但问答仍然失败，你会先检查检索条件还是模型上下文？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — Mem0 memory framework + Kimi for long-context multi-session memory (Experiment 3-2 comparison track).  
> 配套《深入理解 AI Agent》第 3 章——Mem0 记忆框架 + Kimi，长上下文多会话记忆（实验 3-2 对照实现之一）。

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
- **LOCOMO benchmark** scenarios  
- Multi-session and multi-agent collaboration with shared memory  

### Features

**Core:** Mem0 v3 ADD-only extraction and hybrid retrieval; context preservation; metrics (consistency, coherence, latency, memory use); local or cloud memory backend.

**LOCOMO scenarios:** collaborative planning; information sharing; multi-step problem solving; negotiation; teaching & learning.

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

### LOCOMO benchmark

```bash
python experiment.py --scenarios 10 --output results/
```

Metrics: consistency, coherence, memory retention, response time, context utilization. Results JSON under `results/` with per-scenario and overall metrics.

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
