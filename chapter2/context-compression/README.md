# Context Compression Strategies / 上下文压缩策略对比

随着搜索和工具调用增加，对话历史可能比当前任务需要的信息多得多。本实验比较几种压缩方法，学习怎样减少输入长度，同时保留继续完成任务所需的证据。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

压缩可以针对单条工具结果，也可以面向整段历史；有的方法还会根据当前目标决定保留什么。摘要更短并不自动更好：若丢掉来源、约束或尚未解决的问题，后续推理可能失去依据。

### 压缩的是输入，检验的是任务信息

假设较早的一轮已经确定了一个文件路径，后面的任务仍需要它。压缩后的上下文即使更短、更流畅，只要丢失了这个路径，就可能让后续动作失败。阅读各压缩策略时，分别标出它保留的原始内容、生成的摘要和直接删除的部分。随后用相同任务检验这些处理是否保留了继续执行所必需的事实。

### 概述

演示并对比 LLM Agent 的多种上下文压缩策略，测试任务为调研 OpenAI 联合创始人当前职业归属。

上下文窗口越来越大（128K+）时，高效管理上下文关乎：

- **成本** — 减少 token
- **性能** — 更低延迟
- **可靠性** — 减少溢出错误
- **相关性** — 保留关键信息

本实验实现并对比 **6** 种策略及其取舍。

### 压缩策略

#### 1. 无压缩
- 网页原文直接进入上下文
- 观察原文逐轮累积时，哪一次请求最接近预算，以及程序何时停止
- 目的：展示基线问题

#### 2. 非任务感知：逐页摘要
- 每页单独 LLM 摘要再拼接
- 保留页内细节，可能丢跨页关系
- 多次 LLM 调用；适合来源彼此独立

#### 3. 非任务感知：合并摘要
- 先拼接全部网页再做一次总摘要
- 更利把握全局，可能丢页级归属
- 单次 LLM 调用；页多时可能撞限

#### 4. 上下文感知摘要
- 结合查询对全部搜索结果做聚焦摘要
- 相关性更好；多一次 LLM 调用

#### 5. 带引用的上下文感知摘要
- 在 #4 基础上加引用与来源链接
- 利于追问；上下文略大

#### 6. 窗口化上下文
- 最近一次工具调用保留全文，更早历史压缩
- 细节与效率折中
- 只压缩尚未标记 `[COMPRESSED]` 的消息

### 脚本一览

| 脚本 | 作用 | 输出 |
|------|------|------|
| `main.py` | 交互演示 / 单策略 | 控制台 |
| `experiment.py` | 自动对比（token / 压缩 / 成功表） | `results/` |
| `run_all_strategies.py` | 带逐轮详细日志 | `logs/` |
| `quickstart.py` | 菜单封装（检查环境并启动） | 控制台 |

如果想先比较两种方法，用 `experiment.py -s individual combined`。这个入口和 `run_all_strategies.py` 都支持用 `-s` 选择多个策略、用 `-n` 限制迭代轮数；`main.py` 每次演示一个策略，`quickstart.py` 则通过菜单选择入口。三个命令行入口都支持 `-m/--model`。策略别名为 `no_compression`、`individual`、`combined`、`context_aware`、`citations` 和 `windowed`。

### 先想好怎样比较

假设一条网页记录了某人加入一家公司的日期，另一条记录了离任日期。逐页摘要能否保留两个日期？合并摘要后还能分清哪个日期来自哪一页吗？带引用的摘要应当可以回查原文。试窗口化策略时，则可以观察同一条工具结果在刚读到和几轮之后分别保留了什么。比较时把这些问题与运行时间、输入长度一起记录。

<a id="learning-1"></a>

## 准备环境与输入

想先比较六种压缩策略，可以直接读[已保存的运行结果](results/kimi_k3_real_20260718.json)，无需准备 API Key。重新运行时要配置模型服务；即使选用内置的模拟搜索结果，负责决策和生成回答的模型仍需调用。

### 安装

```bash
# 在仓库根目录使用统一的第 2 章环境
uv sync --locked --python 3.12 --extra ch2

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch2]"

cd chapter2/context-compression

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
# 编辑 .env 填入 API Key
```

**所需 Key：**

- `LLM_PROVIDER`：`kimi`（默认）、`dashscope`/`qwen`/`bailian` 或 `openrouter`。
- `DASHSCOPE_API_KEY`：使用阿里云百炼 / Model Studio 时的 Key，默认模型 `qwen3.7-plus`（国际区 Key 可设置 `DASHSCOPE_BASE_URL`）。
- `MOONSHOT_API_KEY`：Kimi/Moonshot（在线跑必需）。书中实验 2-10 使用 Kimi K3（真实窗口约 1M）；演示通过 `CONTEXT_WINDOW_SIZE`（默认 128K）**故意收紧**溢出/压缩预算以便观察。可用 `MODEL_NAME` 或 `-m/--model` 覆盖（如 `kimi-k2.5`、`kimi-k3`、`moonshot-v1-128k`）。
- `OPENROUTER_API_KEY`：未设置 Moonshot key 时的通用回退（`kimi-*` → `moonshotai/kimi-k2`）。设了 `MOONSHOT_API_KEY` 时行为不变。
- `SERPER_API_KEY`：联网搜索（可选；缺失则用 mock 数据）

获取：[Moonshot](https://platform.moonshot.cn/)、[Serper 免费档](https://serper.dev/)

### 配置

`.env` 或 `config.py`：

- `MODEL_NAME`（默认 kimi-k3）
- `MODEL_TEMPERATURE`（默认 0.3）
- `MAX_ITERATIONS`（默认 50）
- `MAX_WEBPAGE_LENGTH`（默认 50000）
- `SUMMARY_MAX_TOKENS`（默认 500）
- `CONTEXT_WINDOW_SIZE`（默认 128000；相对 K3 真实 ~1M 的故意收紧）

<a id="learning-2"></a>

## 按照步骤完成实验

先运行策略列表命令，阅读每种方法的输入和输出，再配置模型运行单个策略。选择同一个研究问题做对照，保存压缩前后的消息，检查每次压缩发生的时机。最后才扩展到多策略批量比较。

### 用法

#### 完整实验（对比表 + JSON）

```bash
python experiment.py                          # 运行全部 6 种策略并生成对比表
python experiment.py -s context_aware         # 只运行「上下文感知压缩」
python experiment.py -s individual combined   # 只对比两种非任务感知策略
python experiment.py -m moonshot-v1-128k -o results/run.json
python experiment.py --list-strategies
```

依次测试所选策略、调研联合创始人归属、打印 Success / Time / **Tokens** / Compression / Overflows，保存到 `results/experiment_TIMESTAMP.json`（或 `-o`）。

主要参数：`-s/--strategy`、`-m/--model`、`-o/--output`、`-n/--max-iterations`、`--streaming`、`--list-strategies`。

#### 带日志跑全部策略

```bash
python run_all_strategies.py
python run_all_strategies.py -s windowed
python run_all_strategies.py --log-dir logs/k2 -m kimi-k2.5
```

- 顺序跑所选策略
- 压缩摘要写入日志
- 默认流式
- 日志：`<log-dir>/strategy_run_TIMESTAMP.log`
- JSON：`<log-dir>/strategy_results_TIMESTAMP.json`
- 末尾对比摘要

参数：`-s/--strategy`、`-m/--model`、`--log-dir`、`-n/--max-iterations`、`--list-strategies`。

#### 交互演示

```bash
python main.py                    # 提示选择策略
python main.py -s citations
python main.py -s windowed --no-streaming
```

默认开启流式；引用策略适合追问。

#### 编程调用

```python
from agent import ResearchAgent
from compression_strategies import CompressionStrategy

agent = ResearchAgent(
    api_key="your_api_key",
    compression_strategy=CompressionStrategy.CONTEXT_AWARE_CITATIONS,
    enable_streaming=True
)

result = agent.execute_research()

if result['success']:
    print(result['final_answer'])
    print(f"Tool calls: {len(result['trajectory'].tool_calls)}")
```

<a id="learning-3"></a>

## 分析结果与形成判断

同时观察上下文长度、压缩本身的开销和最终答案的证据完整性。如果答案漏掉用户约束，沿轨迹找到约束最后一次出现的位置。一次低成本运行也可能只是提前结束任务，应结合完成质量解释结果。

### 采集指标

成功率、执行时间、压缩比（压缩后/原始）、上下文溢出次数、工具调用次数、最终答案长度。

### 从六组历史结果复算表格

在本实验目录运行下面的代码即可读[原始结果](results/kimi_k3_real_20260718.json)。每组保存了统计字段、最终回答和时间戳。先读带引用的策略：原材料共 1,295,044 个字符，处理后有 52,891 个字符。下面的比值告诉你每 100 个原文字符留下了多少；要看引用能否支撑一条结论，还得读同一条记录里的 `final_answer`，找到具体说法再回查来源。

```python
import json
from pathlib import Path

runs = json.loads(Path("results/kimi_k3_real_20260718.json").read_text())
for run in runs:
    m = run["metrics"]
    ratio = m["total_compressed_size"] / m["total_original_size"]
    print(m["strategy"], m["iterations"], m["total_tokens"], f"{ratio:.1%}")
```

- **模型：** `kimi-k3`（该运行记录的模型名；演示预算 `CONTEXT_WINDOW_SIZE = 128000`）
- **搜索：** 真实 Serper + 页面抓取
- **任务：** 识别并追踪约 11 位 OpenAI 联合创始人的职业状态
- **日期：** 2026-07-18 · `MAX_ITERATIONS=15` · 原始 JSON：`results/kimi_k3_real_20260718.json`

| # | Strategy | Success | Iterations | Tokens | Compress | Overflows | Time |
|---|----------|---------|-----------|--------|----------|-----------|------|
| 1 | `no_compression` | ❌ (overflow at 165,227 tok > 128K) | 5 | 166,043 | 102.1% | 1 | 107s |
| 2 | `non_context_aware_individual_summary` | ✅ | 12 | 276,608 | 10.9% | 4 | 2980s |
| 3 | `non_context_aware_combined_summary` | ✅ | 10 | 93,449 | 4.3% | 0 | 1189s |
| 4 | `context_aware_summary` | ✅ | 7 | 40,157 | 3.0% | 0 | 967s |
| 5 | `context_aware_with_citations` | ✅ | 10 | 222,992 | 4.1% | 3 | 1235s |
| 6 | `windowed_context` | ✅ | 7 | 174,601 | 102.4% | 4 | 867s |

说明：

- **无压缩**在第五轮停止。旧代码把多轮累计输入 165,227 与应用预算 128,000 比较。单轮请求是否达到预算，需要查看该轮输入。
- **上下文感知摘要（#4）** token 最省（40,157 tokens，字符压缩 3.0%）。
- **逐页摘要（#2）**最慢（约 50 分钟）：推理模型对每页单独摘要。
- **窗口化（#6）**仅在用量跨过约 80% 预算时批量压缩未压缩工具消息；汇总表中的总时间为生成最终回复的五组中最短。
- `Success` 表示生成了最终回复，最终内容的完整性和准确性需另行评估。
- 当前代码的 `Compress` 汇总工具调用对象中的字符长度；窗口化随后改写消息历史，未同步回写这些对象。因此该列不能直接解释为最终窗口的长度比。例如窗口化组的两个计数是 1,128,824 与 1,102,382，相除确为 102.4%。
- 策略选择需综合任务质量、摘要调用成本和后续模型用量；重复运行后再比较稳定性。

### 同一个人的职业状态，两份回答一致吗？

沿用上面读入的 `runs`，逐份检查交给用户的答案。先找 Pamela Vagata 在汇总表中的那一行，再查读者能否从回答中打开来源网页。

```python
import re

for run in runs:
    answer = run["final_answer"] or ""
    if not answer:
        continue
    row = next(line for line in answer.splitlines()
               if line.startswith("|") and "Pamela Vagata" in line)
    print(run["metrics"]["strategy"], row)
    print("正文中带 http(s) 的网址数：", len(re.findall(r"https?://", answer)))
```

五份回答都列出了她，四份的表格写着 Pebblebed，窗口化组写着 Stripe。五份最终回答里都没有以 `http://` 或 `https://` 开头的网址。带引用组虽然提到 Pebblebed 的网站，读者仍需自行定位页面。要评职业状态这一项，可以先找有日期的任职材料，再检查回答有没有把过去的工作写成现职。若还要判断差异是否由压缩造成，就要固定同一批网页，逐一对照原文、摘要和最终回答；这里各组的搜索过程也会变化。

### 检查自己的解释

哪些信息适合被概括，哪些信息应该原样保留，例如精确数值、文件路径或工具调用标识？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 2 — **Experiment 2-10 ★★★: Comparison of context compression strategies**.
> 配套《深入理解 AI Agent》第 2 章 **实验 2-10 ★★★：上下文压缩策略对比**。

← [Chapter 2 index / 返回第 2 章目录](../README.md)

---

### 项目结构

```
context-compression/
├── config.py
├── web_tools.py
├── compression_strategies.py
├── agent.py
├── experiment.py
├── run_all_strategies.py
├── main.py
├── quickstart.py
├── requirements.txt
├── env.example
├── logs/
└── results/
```

### 关键组件

- **web_tools.py：** `search_web`（Serper + 抓取）、`fetch_webpage`、无 Key 时 mock
- **compression_strategies.py：** `ContextCompressor`、`CompressedContent`、动态压缩
- **agent.py：** 流式、工具、历史、窗口化压缩
- **experiment.py：** 自动跑、指标、对比表、JSON

### 研究任务

> 「查找所有 OpenAI 联合创始人的当前职业归属」

适合原因：需多次搜索、内容量大、考验上下文累积管理，结果可核对。

### 扩展

新策略：枚举 → `ContextCompressor` → `compress_search_results()` → 实验 runner。
新任务：改 `agent.py` 系统提示、`web_tools.py` mock、工具描述。

---

### 代码阅读顺序

- **Run first:** python experiment.py -s context_aware (or python quickstart.py for the menu).
- **Start here:** experiment.py::ExperimentRunner controls one strategy comparison.
- **Core behavior:** agent.py::ResearchAgent records the tool trajectory; compression_strategies.py::ContextCompressor applies the policy.
- **State / protocol:** AgentTrajectory, ToolCall and CompressionStrategy.
- **Verifier:** results/ JSON plus token/overflow counters; tests cover malformed tool results.
- **Experiment variable:** six compression strategies and the context-window budget.
- **Skip on first pass:** web search provider, streaming UI and plotting helpers.

<a id="learning-5"></a>

## 排查问题与查阅资料

### 故障排除

- **无 Serper Key：** mock 仍可验证压缩逻辑
- **非基线策略仍溢出：** 降低 `MAX_WEBPAGE_LENGTH` / `SUMMARY_MAX_TOKENS` / 搜索 `num_results`
- **偏慢：** `--no-streaming`、减小 `-n/--max-iterations`、改用 mock 搜索

## Notes / 说明

- The 128K budget is intentional so compression/overflow behavior is visible even on models with larger real windows.
- 128K 预算是故意收紧的，以便在真实窗口更大的模型上仍能观察到压缩与溢出行为。

## English

### Overview

Demonstrates and compares context compression strategies for LLM agents, using research on OpenAI co-founders’ current affiliations as the test task.

As context windows grow (128K+), efficient context management matters for:

- **Cost** — fewer tokens
- **Performance** — lower latency
- **Reliability** — fewer overflow errors
- **Relevance** — keep what matters

This lab implements and compares **6** strategies and their trade-offs.

### Compression strategies

#### 1. No compression
- Full webpage content into context
- Expected: fails after a few tool calls (overflow)
- Purpose: baseline problem

#### 2. Non-context-aware: individual summaries
- Summarize each page with LLM, then concatenate
- Preserves page-specific detail; may lose cross-page links
- Multiple LLM calls; good when sources are independent

#### 3. Non-context-aware: combined summary
- Concatenate all pages, then one summary
- Better overall picture; may lose per-page attribution
- One LLM call; may hit limits with many pages

#### 4. Context-aware summarization
- Query-focused summary over all search results
- Better relevance; extra LLM call

#### 5. Context-aware with citations
- Like #4 plus citations / source links
- Better for follow-ups; slightly larger

#### 6. Windowed context
- Full content for latest tool call; compress older history
- Balance detail vs efficiency
- Only compresses messages not already marked `[COMPRESSED]`

### Installation

```bash
# From the repository root: use the shared Chapter 2 environment
uv sync --locked --python 3.12 --extra ch2

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch2]"

cd chapter2/context-compression

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# Edit .env with your API keys
```

**API keys:**

- `LLM_PROVIDER` — `kimi` (default), `dashscope`/`qwen`/`bailian`, or `openrouter`.
- `DASHSCOPE_API_KEY` — Alibaba Cloud Model Studio / Bailian key when using DashScope; default model is `qwen3.7-plus` (set `DASHSCOPE_BASE_URL` for international keys).
- `MOONSHOT_API_KEY` — Kimi/Moonshot for live runs. Book 实验 2-10 uses Kimi K3 (~1M real window); the demo **caps** the compression/overflow budget at `CONTEXT_WINDOW_SIZE` (default 128K) so overflow/compression is observable. Override model via `MODEL_NAME` or `-m/--model` (e.g. `kimi-k2.5`, `kimi-k3`, `moonshot-v1-128k`).
- `OPENROUTER_API_KEY` — fallback if Moonshot key unset (`kimi-*` → `moonshotai/kimi-k2`). Unchanged if `MOONSHOT_API_KEY` is set.
- `SERPER_API_KEY` — web search (optional; mock data if missing)

Keys: [Moonshot](https://platform.moonshot.cn/), [Serper free tier](https://serper.dev/)

### Scripts overview

| Script | Purpose | Output |
|--------|---------|--------|
| `main.py` | Interactive demo / single strategy | Console |
| `experiment.py` | Automated comparison (token / compression / success table) | `results/` |
| `run_all_strategies.py` | Strategies with detailed per-round logs | `logs/` |
| `quickstart.py` | Menu wrapper (env check + launcher) | Console |

CLIs use Chinese `--help`. Shared useful flags:

- `-s/--strategy` — one or more strategies (default all 6); see list or `--list-strategies`
- `-m/--model` — override `MODEL_NAME`
- `-n/--max-iterations` — max tool-call rounds per strategy

Strategy aliases: `no_compression`, `individual`, `combined`, `context_aware`, `citations`, `windowed`.

### Usage

#### Full experiment (comparison table + JSON)

```bash
python experiment.py                          # all 6 strategies + comparison table
python experiment.py -s context_aware         # one strategy
python experiment.py -s individual combined   # two non-task-aware strategies
python experiment.py -m moonshot-v1-128k -o results/run.json
python experiment.py --list-strategies
```

Runs selected strategies sequentially, researches co-founder affiliations, prints Success / Time / **Tokens** / Compression / Overflows, saves `results/experiment_TIMESTAMP.json` (or `-o`).

Key flags: `-s/--strategy`, `-m/--model`, `-o/--output`, `-n/--max-iterations`, `--streaming`, `--list-strategies`.

#### All strategies with logging

```bash
python run_all_strategies.py
python run_all_strategies.py -s windowed
python run_all_strategies.py --log-dir logs/k2 -m kimi-k2.5
```

- Sequential strategies
- Compression summaries to log file
- Streaming by default
- Logs: `<log-dir>/strategy_run_TIMESTAMP.log`
- JSON: `<log-dir>/strategy_results_TIMESTAMP.json`
- End comparison summary

Flags: `-s/--strategy`, `-m/--model`, `--log-dir`, `-n/--max-iterations`, `--list-strategies`.

#### Interactive demo

```bash
python main.py                    # choose strategy at prompt
python main.py -s citations
python main.py -s windowed --no-streaming
```

Streaming on by default; follow-ups useful for citation strategy.

#### Custom usage

```python
from agent import ResearchAgent
from compression_strategies import CompressionStrategy

agent = ResearchAgent(
    api_key="your_api_key",
    compression_strategy=CompressionStrategy.CONTEXT_AWARE_CITATIONS,
    enable_streaming=True
)

result = agent.execute_research()

if result['success']:
    print(result['final_answer'])
    print(f"Tool calls: {len(result['trajectory'].tool_calls)}")
```

### Project structure

```
context-compression/
├── config.py
├── web_tools.py
├── compression_strategies.py
├── agent.py
├── experiment.py
├── run_all_strategies.py
├── main.py
├── quickstart.py
├── requirements.txt
├── env.example
├── logs/                    # from run_all_strategies.py
└── results/                 # experiment JSON
```

### Key components

- **web_tools.py:** `search_web` (Serper + crawl), `fetch_webpage`, mock data without key
- **compression_strategies.py:** `ContextCompressor`, `CompressedContent`, dynamic compression
- **agent.py:** streaming, tools, history, windowed compression
- **experiment.py:** automated runs, metrics, comparison table, JSON

### Metrics

Success rate, execution time, compression ratio (compressed/original size), context overflows, tool calls, final answer length.

### Expected results (qualitative)

1. No compression → overflow fail
2. Non-context-aware → may complete, miss detail
3. Context-aware → good size/relevance balance
4. With citations → best for follow-ups
5. Windowed → efficient for long multi-turn

### Historical run summary

The original README attributes these results to a live Serper + Moonshot run. The [archived run results](results/kimi_k3_real_20260718.json) contain metrics, final answers and timestamps for all six strategies.

- **Model:** `kimi-k3` (model name recorded in the summary; demo budget `CONTEXT_WINDOW_SIZE = 128000`)
- **Search:** real Serper + page crawl
- **Task:** track current affiliations of ~11 OpenAI co-founders
- **Date:** 2026-07-18 · `MAX_ITERATIONS=15` · raw: `results/kimi_k3_real_20260718.json`

| # | Strategy | Success | Iterations | Tokens | Compress | Overflows | Time |
|---|----------|---------|-----------|--------|----------|-----------|------|
| 1 | `no_compression` | ❌ (overflow at 165,227 tok > 128K) | 5 | 166,043 | 102.1% | 1 | 107s |
| 2 | `non_context_aware_individual_summary` | ✅ | 12 | 276,608 | 10.9% | 4 | 2980s |
| 3 | `non_context_aware_combined_summary` | ✅ | 10 | 93,449 | 4.3% | 0 | 1189s |
| 4 | `context_aware_summary` | ✅ | 7 | 40,157 | 3.0% | 0 | 967s |
| 5 | `context_aware_with_citations` | ✅ | 10 | 222,992 | 4.1% | 3 | 1235s |
| 6 | `windowed_context` | ✅ | 7 | 174,601 | 102.4% | 4 | 867s |

Notes:

- **No compression** stopped in the fifth iteration when the historical guard compared cumulative input with the application budget.
- **Context-aware summary (#4)** most token-efficient success (40,157 tokens, 3.0% char compression).
- **Individual summaries (#2)** slowest (~50 min): per-page summaries on a reasoning model.
- **Windowed (#6)** compresses only when usage crosses ~80% of budget; has the shortest reported runtime among the five arms that generated a final response.
- `Success` means a final response was generated; assess completeness and factual accuracy separately.
- The current `Compress` calculation aggregates character lengths on tool-call objects. Windowed compression later rewrites message history without updating those objects, so this column does not measure the final window size ratio. The archived windowed counts give 1,128,824 / 1,102,382, or 102.4%.
- Compare task quality, summarization cost and subsequent model usage across repeated runs.

### Configuration

`.env` or `config.py`:

- `MODEL_NAME` (default kimi-k3)
- `MODEL_TEMPERATURE` (default 0.3)
- `MAX_ITERATIONS` (default 50)
- `MAX_WEBPAGE_LENGTH` (default 50000)
- `SUMMARY_MAX_TOKENS` (default 500)
- `CONTEXT_WINDOW_SIZE` (default 128000; intentional cap vs K3’s real ~1M window)

### Troubleshooting

- **No Serper key:** mock data still exercises compression logic
- **Overflow on non-baseline strategies:** lower `MAX_WEBPAGE_LENGTH` / `SUMMARY_MAX_TOKENS` / search `num_results`
- **Slow:** `--no-streaming`, lower `-n/--max-iterations`, mock search

### Research task

> “Find the current affiliations of all OpenAI co-founders”

Good because it needs many searches, accumulates text, stresses context management, and has checkable outcomes.

### Extending

New strategy: enum → `ContextCompressor` → `compress_search_results()` → experiment runner.
New task: system prompt in `agent.py`, mock data in `web_tools.py`, tool descriptions as needed.

---
