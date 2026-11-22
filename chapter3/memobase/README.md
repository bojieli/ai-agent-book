# Memobase Agent / Memobase Agent（Profile + Event 与手写记忆对照）

“用户偏好简短回答”和“用户昨天改了会议时间”都是记忆，却有不同的时间特征。本实验围绕画像与事件两类信息，解释记忆系统为什么需要多种表示。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

画像总结相对稳定的属性，事件保留发生时间和具体经过。本目录既包含连接真实 Memobase 服务的演示，也包含手写的教学实现。它们可以帮助理解相似概念，但不能把手写实现的结果当作框架本身的性能。

### 本目录两条线——不要搞混

1. **真实 Memobase 框架演示**（`profile_demo.py`）——官方开源 SDK（`memobase>=0.0.27`）对接**正在运行的 Memobase 服务**，展示书中的 *Profile*（结构化用户属性）+ *Event Memory*（时间线）。见下文 Profile + Event 演示。  
2. **手写记忆 Agent**（`agent.py` / `main.py`）——自包含、受 Memobase 启发的 `MemoryStore`（情景 / 语义 / 程序 / 工作记忆，pickle 持久化），直接调 Kimi。**不需要 Memobase 服务**，只要 `KIMI_API_KEY`。`--mode`（interactive / benchmark / demo / task）驱动的是这条线。

### 手写 Agent 功能

**记忆类型：** 情景、语义、程序、工作记忆。  
**操作：** 超阈值压缩、巩固、重要性衰减、聚类、相关度/近因检索。  
**模型：** Kimi K3。  
**评测类别：** 多轮推理、长上下文问答、任务规划、知识整合、工具使用。

### 架构（手写）

- **MemoryStore** / **MemobaseAgent**（`agent.py`）  
- **LOCOMOBenchmark**（`locomo_benchmark.py`）  

压缩 / 巩固 / 检索策略与 English 节相同。

<a id="learning-1"></a>

## 准备环境与输入

下面会用到模型服务。先按配置说明选择一个提供商，准备对应的模型名称、服务地址和 API Key，再运行小规模例子。一次完整运行的费用取决于模型、输入长度和调用次数。

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

cd chapter3/memobase

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
# 手写 Agent 可填写 KIMI_API_KEY；也可用 LLM_PROVIDER=dashscope 与 DASHSCOPE_API_KEY
```

在 `config.py` 中调整模型、记忆阈值、基准与日志。

<a id="learning-2"></a>

## 按照步骤完成实验

先用手写演示追踪一条信息的保存与查询。随后按下文启动 Memobase 服务，阅读并运行 `profile_demo.py`，比较框架返回的画像与事件。每次比较都应记录实际采用了哪条实现路径。

### 用一次写入和一次追问检查记忆

先输入一条容易核对、且不涉及真实隐私的偏好，例如“演示用户希望回答附带单位”。完成写入后，查看实际保存的记录，再用一个确实需要单位的问题追问。最后提出一个与该偏好无关的问题，检查系统是否错误地到处套用它。这样能依次检查保存、检索和使用三个环节。

### 用法（手写 Agent）

```bash
python main.py --mode interactive
# /help /memory /clear /reset /learn /exit

python main.py --mode benchmark
python main.py --mode benchmark --category multi_turn_reasoning
python main.py --mode benchmark --num-tasks 5

python main.py --mode demo
python main.py --mode task --task "Plan a 7-day trip to Japan with a $3000 budget"
```

额外：`--api-key`、`--no-memory`、`--verbose`。

### Memobase Profile + Event 演示（真实 SDK）

`profile_demo.py` 展示 **Profile**（topic → sub-topic → content）与 **Event Memory**（时间线）。流水线：`insert` → `flush` → `profile` / `event` / `context`。

#### 前置

抽取在**服务端**完成，需要可访问的 Memobase：

- **自托管**：[memodb-io/memobase](https://github.com/memodb-io/memobase)（docker compose）。默认 `http://localhost:8019`，token `secret`。抽取模型在**服务端**配置。  
- **云端**：https://www.memobase.ai 的 `project_url` + `api_key`  

客户端：`--project-url` / `--api-key` 或 `MEMOBASE_PROJECT_URL` / `MEMOBASE_API_KEY`。

#### 运行

```bash
# 在上方安装并激活统一 `ch3` 环境后，从仓库根目录进入本项目：
cd chapter3/memobase

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

python profile_demo.py
python profile_demo.py --dry-run
python profile_demo.py --op profile
python profile_demo.py --op event
python profile_demo.py --op context
python profile_demo.py --input chat.json --output result.json
```

连不上服务时会给出可操作提示（`--dry-run` 或配置 URL），**不会捏造**记忆结果。

<a id="learning-3"></a>

## 分析结果与形成判断

观察临时事件有没有被错误概括为稳定属性，时间更新是否保留，以及回答是否使用了恰当的记忆类别。不要仅凭字段名称一致就认定两套实现行为相同。

### 结果与排错

结果目录 `benchmark_results/`。常见问题：API Key、记忆溢出（调阈值/压缩）、性能（降 `MODEL_MAX_TOKENS`）。

### 检查自己的解释

用户连续三次选择同一种酒店，何时可以把事件概括成偏好？这种概括还应保留什么证据？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — real Memobase SDK demo **and** a Memobase-inspired hand-rolled memory agent (Experiment 3-2 track).  
> 配套《深入理解 AI Agent》第 3 章——真实 Memobase SDK 演示 **与** Memobase 风格自研记忆 Agent（实验 3-2 对照）。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

<a id="learning-5"></a>

## 排查问题与查阅资料

### 许可

教学用途；致谢 Moonshot / Memobase / LOCOMO 相关设计。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

If primary keys are absent and `OPENROUTER_API_KEY` is set, chat LLM routes through OpenRouter with automatic model mapping; `OPENROUTER_MODEL` forces an id. See `env.example`.

## English

### Two tracks in this folder — don’t confuse them

1. **Real Memobase framework demo** (`profile_demo.py`) — uses the actual open-source Memobase SDK (`pip install memobase`, package `memobase>=0.0.27`) against a **running Memobase server**. Canonical demo of Memobase’s *Profile* (structured user attributes) + *Event Memory* (timeline). See [Memobase Profile + Event Demo](#memobase-profile--event-demo-real-sdk).  
2. **Hand-rolled memory agent** (`agent.py` / `main.py`) — self-contained *Memobase-inspired* `MemoryStore` (episodic / semantic / procedural / working, pickle-persisted) calling Kimi directly. **No Memobase server**—only `KIMI_API_KEY`. The `--mode` commands (interactive / benchmark / demo / task) drive this agent.

### Features (hand-rolled agent)

**Memory types:** episodic (task experiences), semantic (facts), procedural (patterns), working (short-term context).

**Operations:** compression when over threshold; consolidation; importance-based decay; clustering; relevance/recency retrieval.

**Model:** Kimi K3 integration (tool use, multi-step reasoning, long context).

**LOCOMO-style categories:** multi-turn reasoning, long-context Q&A, task planning, knowledge integration, tool usage.

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

cd chapter3/memobase

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# Set KIMI_API_KEY, or use LLM_PROVIDER=dashscope/qwen/bailian with DASHSCOPE_API_KEY
```

Edit `config.py` for model, memory thresholds, benchmark, logging.

### Usage (hand-rolled agent)

#### Interactive

```bash
python main.py --mode interactive
```

Commands: `/help`, `/memory`, `/clear`, `/reset`, `/learn`, `/exit`.

#### Benchmark

```bash
python main.py --mode benchmark
python main.py --mode benchmark --category multi_turn_reasoning
python main.py --mode benchmark --num-tasks 5
```

#### Demo / single task

```bash
python main.py --mode demo
python main.py --mode task --task "Plan a 7-day trip to Japan with a $3000 budget"
```

Extra: `--api-key KEY`, `--no-memory`, `--verbose`.

### Memobase Profile + Event Demo (real SDK)

`profile_demo.py` uses the **real** Memobase SDK: **Profile** (topic → sub-topic → content, e.g. `basic_info→城市`, `work→职位`) and **Event Memory** (timeline for “when did we discuss budget?”). Pipeline: `insert` → `flush` → `profile` / `event` / `context`.

#### Prerequisites

Memobase extracts **server-side**; you need a reachable service:

- **Self-hosted**: [memodb-io/memobase](https://github.com/memodb-io/memobase) (docker compose). Default `http://localhost:8019`, token `secret`. Extraction model is in the **server’s** `.env` / `config.yaml` (`--model` on the client is informational only).  
- **Cloud**: `project_url` + `api_key` from https://www.memobase.ai  

Client: `--project-url` / `--api-key` or `MEMOBASE_PROJECT_URL` / `MEMOBASE_API_KEY` (see `env.example`).

#### Running

```bash
# From the repository root, after installing and activating the shared `ch3` environment above:
cd chapter3/memobase

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

python profile_demo.py
python profile_demo.py --dry-run
python profile_demo.py --op profile
python profile_demo.py --op event
python profile_demo.py --op context
python profile_demo.py --input chat.json --output result.json
```

If no server is reachable, the demo exits with an actionable message (try `--dry-run` or set `--project-url`)—it does **not** invent memory output.

### Architecture (hand-rolled)

- **MemoryStore** (`agent.py`): pickle persistence, compression, clustering, decay, retrieval  
- **MemobaseAgent** (`agent.py`): message processing with memory context, learning, metrics  
- **LOCOMOBenchmark** (`locomo_benchmark.py`): tasks, scoring, persistence  

### Memory strategies

**Compression:** sort by importance/recency; keep important; cluster low-importance into summaries.  
**Consolidation:** decay; drop very low importance; extract patterns → procedural.  
**Retrieval:** content search + recent episodic + procedural → format into context.

### Results / development

Benchmark outputs under `benchmark_results/`. Extend tools / memory types in `config.py` / `locomo_benchmark.py` as needed.

### Troubleshooting

1. API key: `KIMI_API_KEY` in `.env`, or `DASHSCOPE_API_KEY` with `LLM_PROVIDER=dashscope`
2. Memory overflow: lower `MAX_MEMORY_ENTRIES`, more aggressive compression, manual consolidation  
3. Slow: reduce `MODEL_MAX_TOKENS`, enable cache, category-specific benchmarks  

### License / acknowledgments

MIT-style educational use. Kimi by Moonshot AI; Memobase concepts; LOCOMO-inspired design.

---
