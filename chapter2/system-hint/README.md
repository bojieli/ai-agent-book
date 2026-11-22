# System-Hint Enhanced AI Agent / Agent 状态栏（System Hint）实验

长任务中，Agent 可能忘记还剩多少预算、已经处理了哪些文件，或正在等待什么结果。本实验把这些运行状态整理成短提示，观察它们怎样帮助模型选择下一步。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

假设 Agent 正在访问一项暂时不可用的服务。它刚试过几次？是再试一次，还是改用备用服务？程序可以数清工具调用次数，把计数附在工具回执里，供模型决定下一步。计数是否真的减少了重复尝试，可以从调用记录里查出来。

### 提示在什么时候进入上下文

最初的系统提示交代长期规则；任务进行到哪一步、还有哪些事没做，则要随运行更新。本目录对应书中的**实验 2-9：几种好用的 Agent 状态栏技术**。交互演示可以把动态摘要放在上下文末尾，以 `role=user` 传给模型；正式对照中，工具计数也会随工具回执送达。先用离线预览看看程序生成了什么提醒，再读下方的逐次调用记录，看模型接到提醒后采取了什么行动。

### 核心功能

#### 1. 时间戳跟踪
- 为用户消息与工具结果添加时间戳
- 帮助 Agent 理解时间上下文
- 可模拟时间流逝以演示多日场景

#### 2. 工具调用计数器
- 统计每个工具被调用次数
- 抑制无限循环与重复行为
- 在工具响应中展示调用序号（如 `Tool call #3 for 'read_file'`）

#### 3. TODO 列表管理
- 系统提示中带任务管理规则
- 四态：pending、in_progress、completed、cancelled
- 对话中可重写与更新
- 复杂任务（3 步以上）自动建 TODO

#### 4. 详细错误信息
- 错误类型、参数、堆栈（verbose）
- 修复建议
- 帮助 Agent 从失败中调整策略

#### 5. 系统状态感知
- 当前目录、Shell、系统信息
- 随文件系统导航动态更新
- 为命令执行提供上下文

#### 6. 自动轨迹保存
- 每轮将完整对话与状态写入 `trajectory.json`
- 执行失败也能保留调试信息
- 含历史、工具调用、TODO、配置
- 用 `view_trajectory.py` 分析

### System Hint 如何工作

System hint 是在发给 LLM **之前**以临时 **user 消息**注入的上下文信息，**不**写入对话历史，避免永久污染上下文，同时提供关键状态。

示例见英文节。系统提示中还包含 TODO 管理、错误处理与工具使用规则：复杂任务自动建 TODO、同时只有一个 `in_progress`、关注工具调用次数、错误恢复策略等。

### 说明

- System hint 以临时 user 消息注入，不写入历史
- 轨迹文件保留完整执行状态便于调试
- TODO 帮助多步任务保持焦点
- 工具计数器自动抑制无限循环
- 带建议的详细错误帮助自我纠正

---

<a id="learning-1"></a>

## 准备环境与输入

先用 `view_trajectory.py` 打开已有的 `trajectory.json`，找出工具调用后的状态提示；这个查看过程不发模型请求。要观察自己的任务怎样更新状态，再为 Agent 配置模型服务。

### 先跑离线预览（无需 API Key）

想在不配置任何 API Key 的情况下直观看到状态栏如何改变模型看到的上下文：

```bash
python main.py --mode preview
```

该命令在本地渲染书中五种状态栏技术（时间戳、工具调用计数器、TODO 列表、详细错误信息、系统状态感知），对每一项做一次 **「无状态栏 vs 有状态栏」** 的前后对比，并打印最终追加到上下文末尾的完整状态栏消息。配合 `--no-timestamps` / `--no-counter` / `--no-todo` / `--no-errors` / `--no-state` 可分别关闭某一类。整个过程不发起任何 LLM 调用。

### 配置项（`SystemHintConfig`）

| 参数 | 默认 | 说明 |
|------|------|------|
| `enable_timestamps` | `True` | 为消息添加时间戳 |
| `enable_tool_counter` | `True` | 跟踪工具调用次数 |
| `enable_todo_list` | `True` | 启用 TODO 管理 |
| `enable_detailed_errors` | `True` | 提供详细错误信息 |
| `enable_system_state` | `True` | 跟踪系统状态 |
| `timestamp_format` | `"%Y-%m-%d %H:%M:%S"` | 时间戳格式 |
| `simulate_time_delay` | `False` | 模拟时间流逝（演示） |
| `save_trajectory` | `True` | 保存轨迹到文件 |
| `trajectory_file` | `"trajectory.json"` | 轨迹输出路径 |

<a id="learning-2"></a>

## 按照步骤完成实验

先运行预览模式，看一条状态提示包含哪些字段。随后阅读它们从哪里取得数值，再配置模型运行一个示例任务。对照每轮提示与工具记录，确认提示中的进度确实来自已经发生的动作。

### 快速开始

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

cd chapter2/system-hint

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
# 编辑 .env，填入 KIMI_API_KEY
export KIMI_API_KEY='your-api-key-here'
```

> **通用回退（OpenRouter）**：未设置 `KIMI_API_KEY` 时，只要配置了 `OPENROUTER_API_KEY`，实验会自动改走 OpenRouter（`kimi-*` 会映射为 `moonshotai/kimi-k2`）。设置了 `KIMI_API_KEY` 时行为完全不变。

#### 基本用法

```bash
python main.py --mode preview
python main.py
python main.py --mode sample
python main.py --mode single --task "Create a hello world Python script"
python main.py --mode single --task "..." --provider kimi --model kimi-k3 --output run1.json
python main.py --mode demo --demo basic
python main.py --mode demo --demo loop
python main.py --mode demo --demo comparison
python main.py --mode single --no-todo --no-timestamps --task "Simple task"
python main.py --mode preview --no-todo --no-timestamps
python quickstart.py
python view_trajectory.py
python view_trajectory.py path/to/trajectory.json
```

#### 编程方式

```python
from agent import SystemHintAgent, SystemHintConfig

config = SystemHintConfig(
    enable_timestamps=True,
    enable_tool_counter=True,
    enable_todo_list=True,
    enable_detailed_errors=True,
    enable_system_state=True,
    save_trajectory=True,
    trajectory_file="my_trajectory.json"
)

agent = SystemHintAgent(
    api_key="your-api-key",
    provider="kimi",
    config=config,
    verbose=False
)

task = "Create a Python script that analyzes CSV files"
result = agent.execute_task(task, max_iterations=20)

print(f"Success: {result['success']}")
print(f"Final answer: {result['final_answer']}")
print(f"Trajectory saved to: {result['trajectory_file']}")
```

### 演示

```bash
python main.py --mode preview
python main.py --mode demo --demo basic
python main.py --mode demo --demo loop
python main.py --mode demo --demo comparison
```

### 示例任务

1. 项目分析（week1/week2 风格）
2. 文件操作
3. 代码生成
4. 系统命令

### 测试

```bash
python test_basic.py
```

<a id="learning-3"></a>

## 分析结果与形成判断

### 计数器有没有减少重试？

在正式对照中，Agent 需要在主服务不可用时找到可用的备用服务。评分程序检查三个条件：成功读取备用服务、提交正确的备用服务名、尝试主服务不超过三次。要回答“开启计数器后，Agent 是否更早改用备用服务”，还要数一数每组实际访问主服务的次数。

进入本实验目录，重读 Kimi K3 的五对轨迹。归档名沿用了旧编号 `exp2-8`，对应当前书中的实验 2-9。这段命令只读取本地文件。

```bash
python - <<'PYTHON'
import json
from pathlib import Path

cases = Path("runs/exp2-8-kimi-k3-20260730-v1/cases")
for path in sorted(cases.glob("tool_counter__*.json")):
    record = json.loads(path.read_text())
    probes = [event["arguments"]["name"] for event in record["tool_events"]
              if event["name"] == "probe_resource"]
    print(record["case_id"], record["condition"], " → ".join(probes), record["objective_pass"])
PYTHON
```

前四对轨迹中，两组都只试了一次主服务。差别出现在 `ctr-05`：关闭计数器时，Agent 访问 `gateway-e` 失败后就改用 `mirror-e`；开启计数器时，它又试了一次 `gateway-e`，随后才改用备用服务。两组都是五题全部通过，主服务的访问次数却分别为五次和六次。这五对记录足以说明这次实验里差异出在哪一题；计数提醒在其他任务上能否减少重试，仍需用那些任务来检验。

其余六项对照及各组的轮数、用量和评分都可在[完整报告](runs/exp2-8-kimi-k3-20260730-v1/comparison.json)中查阅。两种时间戳提示共用同一组无提示记录，七项对照合计有 65 次独立保存的运行。

### 查看自己的交互轨迹

```bash
python view_trajectory.py
# 迭代次数、工具统计、TODO 进度、对话亮点、配置
```

跟踪指标：迭代数、工具成功/失败、TODO 完成情况、耗时（若启用时间戳）、最终成败。

### 检查自己的解释

哪些状态应由程序计算，哪些判断适合留给模型？“任务已完成”应该由谁来确认？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 2 — **Experiment 2-9 ★★: Useful Agent status-bar techniques**.
> 配套《深入理解 AI Agent》第 2 章 **实验 2-9 ★★：几种好用的 Agent 状态栏技术**。

← [Chapter 2 index / 返回第 2 章目录](../README.md)

---

### 项目结构

```
system-hint/
├── agent.py          # 带 system hint 的 Agent 实现
├── main.py           # 多模式 CLI
├── config.py         # 配置管理
├── quickstart.py     # 快速演示
├── test_basic.py
├── test_hint_behavior.py
├── view_trajectory.py
├── requirements.txt
├── env.example
├── trajectory.json   # 运行时生成
├── CHANGELOG.md
├── NOTES.md
└── README.md
```

<a id="learning-5"></a>

## 排查问题与查阅资料

### 故障排除

1. **未设置 API Key：** `export KIMI_API_KEY='your-api-key-here'`
2. **工具调用循环：** 启用 `enable_tool_counter=True`
3. **上下文丢失：** 启用时间戳与系统状态
4. **任务管理混乱：** 启用 TODO 列表

## Notes / 说明

- “System hint” and “Agent status bar” refer to the same mechanism in this lab.  
- 本实验中「System hint」与「Agent 状态栏」指同一机制。

## English

### Canonical matched campaign

The preview and interactive demo below illustrate the mechanism, but the
manuscript-grade Experiment 2-9 evidence comes from the frozen matched campaign:

```bash
python run_experiment_2_8.py \
  --output runs/exp2-8-kimi-k3-$(date +%Y%m%d-%H%M%S)
```

It runs five real Moonshot `kimi-k3` cases for every preregistered contrast:
disabled vs raw timestamps, guided timestamps, tool counter, TODO list,
detailed errors, system state, and all features combined. Arms alternate order
within each case. Every run uses an isolated local sandbox and is scored from
tool actions and filesystem state, not from the model's self-report. The runner
checkpoints after each accepted response and tool event, resumes without
regenerating completed cases, retains response IDs/usage/raw protocol, prices
usage in native CNY, hashes all evidence, and scans it for credentials. See
`experiment_protocol.json` for the frozen cases and claim policy; the historical
15-vs-21, 60%-vs-95%, and six-model time-sense figures are not relabeled as
results from this smaller suite.

### Overview

Corresponds to the book’s **Agent Status Bar** section. This directory is the `agent-status-bar` experiment framework—**system hint** and **Agent status bar** are two names for the same idea: inject a dynamic state summary as a temporary `role=user` message at the end of the context.

An advanced Agent that uses system hints to improve trajectories and reduce infinite loops, poor context awareness, and weak task management, with automatic trajectory saving for debugging.

### Offline preview first (no API key)

To see how the status bar changes the context the model would see, without any API key:

```bash
python main.py --mode preview
```

Renders five techniques (timestamps, tool-call counter, TODO list, detailed errors, system-state awareness), each as **without vs with** status bar, and prints the full status message appended at the end of context. Use `--no-timestamps` / `--no-counter` / `--no-todo` / `--no-errors` / `--no-state` to turn categories off. No LLM calls.

### Key features

#### 1. Timestamp tracking
- Timestamps on user messages and tool results
- Temporal context for multi-day style scenarios
- Optional simulated delays

#### 2. Tool call counter
- Counts calls per tool
- Helps prevent infinite loops / repetition
- Surfaces call number in tool responses (e.g. `Tool call #3 for 'read_file'`)

#### 3. TODO list management
- Task tracking with rules in the system prompt
- States: pending, in_progress, completed, cancelled
- Persistent rewrite/update across the conversation
- Agent auto-creates TODOs for complex (3+ step) tasks

#### 4. Detailed error messages
- Error type, arguments, traceback (verbose mode)
- Fix suggestions
- Helps the Agent adapt after failures

#### 5. System state awareness
- Current directory, shell, system info
- Updates as the Agent navigates
- Context for command execution

#### 6. Automatic trajectory saving
- Full history/state to `trajectory.json` each iteration
- Survives failed runs
- Includes history, tool calls, TODOs, config
- Analyze with `view_trajectory.py`

### Quick start

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

cd chapter2/system-hint

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# Edit .env with your provider key (Kimi or DashScope/Bailian)
export KIMI_API_KEY='your-api-key-here'

# Alibaba Cloud Model Studio / Bailian (Qwen):
# export LLM_PROVIDER=dashscope
# export DASHSCOPE_API_KEY='your-dashscope-api-key-here'
```

> **OpenRouter fallback:** If `KIMI_API_KEY` is unset but `OPENROUTER_API_KEY` is set, the experiment uses OpenRouter (`kimi-*` → `moonshotai/kimi-k2`). With `KIMI_API_KEY` set, behavior is unchanged.

#### Basic usage

```bash
# Offline status-bar preview (no API key)
python main.py --mode preview

# Interactive mode (default)
python main.py

# Sample task (analyze week1/week2 projects)
python main.py --mode sample

# Single task from CLI
python main.py --mode single --task "Create a hello world Python script"

# Provider / model / trajectory path
python main.py --mode single --task "..." --provider kimi --model kimi-k3 --output run1.json

# Demos
python main.py --mode demo --demo basic
python main.py --mode demo --demo loop
python main.py --mode demo --demo comparison

# Disable features (preview or live)
python main.py --mode single --no-todo --no-timestamps --task "Simple task"
python main.py --mode preview --no-todo --no-timestamps

python quickstart.py
python view_trajectory.py
python view_trajectory.py path/to/trajectory.json
```

#### Programmatic usage

```python
from agent import SystemHintAgent, SystemHintConfig

config = SystemHintConfig(
    enable_timestamps=True,
    enable_tool_counter=True,
    enable_todo_list=True,
    enable_detailed_errors=True,
    enable_system_state=True,
    save_trajectory=True,
    trajectory_file="my_trajectory.json"
)

agent = SystemHintAgent(
    api_key="your-api-key",
    provider="kimi",
    config=config,
    verbose=False
)

task = "Create a Python script that analyzes CSV files"
result = agent.execute_task(task, max_iterations=20)

print(f"Success: {result['success']}")
print(f"Final answer: {result['final_answer']}")
print(f"Trajectory saved to: {result['trajectory_file']}")
```

### Project structure

```
system-hint/
├── agent.py          # Agent with system hints
├── main.py           # CLI (multiple modes)
├── config.py         # Configuration
├── quickstart.py     # Quick demo
├── test_basic.py
├── test_hint_behavior.py
├── view_trajectory.py
├── requirements.txt
├── env.example
├── trajectory.json   # Created at runtime
├── CHANGELOG.md
├── NOTES.md
└── README.md
```

### How system hints work

Hints are **temporary user messages** added before each LLM call. They are **not** stored in conversation history, so they avoid permanent context pollution while still supplying state.

Example:

```python
# System hint example (added as user message before LLM call):
=== SYSTEM STATE ===
Current Time: 2024-12-13 10:30:45
Current Directory: /home/user/projects
System: Linux (5.15.0)
Shell Environment: Linux Shell (bash)
Python Version: 3.10.0

=== CURRENT TASKS ===
TODO List:
  [1] 🔄 Read configuration file (in_progress)
  [2] ⏳ Process data (pending)
  [3] ✅ Initialize environment (completed)
```

The system prompt also includes management rules: auto TODO for complex tasks, only one `in_progress` at a time, tool-call awareness, error recovery patterns.

### Configuration (`SystemHintConfig`)

| Parameter | Default | Description |
|-----------|---------|-------------|
| `enable_timestamps` | `True` | Add timestamps to messages |
| `enable_tool_counter` | `True` | Track tool call counts |
| `enable_todo_list` | `True` | TODO list management |
| `enable_detailed_errors` | `True` | Detailed error info |
| `enable_system_state` | `True` | System state tracking |
| `timestamp_format` | `"%Y-%m-%d %H:%M:%S"` | Timestamp format |
| `simulate_time_delay` | `False` | Simulate time passing (demo) |
| `save_trajectory` | `True` | Save trajectory to file |
| `trajectory_file` | `"trajectory.json"` | Trajectory output path |

### Demonstrations

```bash
python main.py --mode preview                          # offline before/after
python main.py --mode demo --demo basic                # all hints together
python main.py --mode demo --demo loop                 # loop prevention via counter
python main.py --mode demo --demo comparison           # with vs without hints
```

### Sample tasks

1. Project analysis (week1/week2 style)
2. File operations
3. Code generation
4. System commands

### Analyzing results

```bash
python view_trajectory.py
# iterations, tool stats, TODO progress, highlights, config
```

Metrics: iterations, tool success/fail, TODO completion, time (if timestamps), final success.

### Testing

```bash
python test_basic.py
```

### Troubleshooting

1. **API key not set:** `export KIMI_API_KEY='your-api-key-here'`
2. **Tool loops:** enable `enable_tool_counter=True`
3. **Lost context:** enable timestamps + system state
4. **Task management:** enable TODO list

### Notes

- Hints are temporary user messages, not stored in history
- Trajectories capture full execution for debugging
- TODOs keep multi-step focus
- Counters reduce infinite loops
- Detailed errors help self-correction

---
