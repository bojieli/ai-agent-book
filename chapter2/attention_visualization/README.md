# Attention Visualization / 注意力机制可视化

当模型处理一句话时，不同位置会以不同权重读取已有位置的信息。注意力热力图把这些权重画出来，帮助你把抽象的矩阵计算与具体词元联系起来。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

图中的行通常对应正在计算的位置，列对应被读取的位置。层和注意力头不同，图案也会不同。因果模型不能读取未来位置，因此图中的遮挡区域首先反映模型结构，而不是某个词“没有意义”。

### 概述

用于探索语言模型注意力机制的交互式工具。每次 Agent 运行可生成一条轨迹供前端查看与对比；也可用独立 CLI 直接导出热力图 PNG。

每次运行可记录：

- 输入查询与模型回复
- 逐 token 注意力权重
- 各层/各头的注意力模式
- 注意力分布的统计分析

### 架构

1. **Agent 生成轨迹**：运行 `agent.py` 或 `main.py`
2. **JSON 存储**：写入 `frontend/public/trajectories/` 下的唯一文件
3. **前端可视化**：React 应用通过标签页加载并展示全部轨迹

### 工作原理

#### 轨迹生成

**`agent.py`：** 多种查询类型的基础注意力跟踪；单步回复；适合理解基础模式。

**`main.py`：** 带工具的 ReAct Agent；多步推理；观察使用工具时注意力如何变化。

两者均生成带时间戳的轨迹、写入 `frontend/public/trajectories/`，并更新 manifest。

#### 数据格式

```json
{
  "id": "20250914_123456",
  "timestamp": "2025-09-14 12:34:56",
  "test_case": {
    "category": "Math",
    "query": "What is 25 * 37?",
    "description": "Agent trajectory from..."
  },
  "response": "The answer is...",
  "tokens": ["What", "is", "25", ...],
  "attention_data": {
    "tokens": [...],
    "attention_matrix": [[...]],
    "num_layers": 1,
    "num_heads": 16
  },
  "metadata": {}
}
```

#### 前端

从 manifest 加载全部轨迹；标签切换；展示热力图、token 分析与统计；有新轨迹时自动更新。

### 功能

- 多次运行各自独立轨迹
- 标签导航
- 交互式 token-to-token 热力图
- Token 级分析
- 统计：平均/最大注意力、熵
- 分类：Math、Knowledge、Reasoning、Code、Creative
- 持久化存储

### 提示

- 首次运行下载约 1–2 GB 模型；推荐 GPU/MPS
- 同时跑 `agent.py` 与 `main.py` 对比有/无工具时的注意力
- 用标签对比相似查询
- 观察数学 / 知识 / 推理 / 代码 / 创作等模式差异

### 说明

- 轨迹带时间戳保证唯一
- manifest 保留最近 50 条轨迹
- 轨迹跨会话持久存在

---

<a id="learning-1"></a>

## 准备环境与输入

生成新的热力图要在本机加载模型和分词器。首次加载可能需要下载权重；如果只想学读图，可以先打开仓库里保存的[北京天气热力图](runs/exp2-2-qwen3-0.6b-20260730-v3/beijing_attention_layers.png)，比较同一句话在浅层和深层的注意力分布。

### 依赖与安装

**Python：** 3.12、PyTorch、Transformers，由根目录 `ch2` extra 安装。
**前端：** Node.js 14+、npm/yarn，见 `frontend/package.json`。

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

cd chapter2/attention_visualization

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
# 编辑 .env 配置模型、设备与可视化选项
cd frontend && npm install
```

<a id="learning-2"></a>

## 按照步骤完成实验

先准备下文中的本地模型依赖，运行默认命令得到一张热力图。确认横纵轴与词元的对应关系，再只改变一个变量：提示词、层或注意力头。先比较一对图，最后再查看跨层视图。

### 快速开始（独立 CLI）

复现第 2 章注意力模式（实验 2-2）最快的方式是 `attention_cli.py`：真实跑模型、捕获自注意力、直接写出热力图 PNG——无需前端。

```bash
# 默认提示词热力图（最后一层、头平均）
python attention_cli.py

# 自定义提示词、指定层/头与输出路径
python attention_cli.py --prompt "北京 的 天气 怎么样" \
    --layer 0 --head 3 --output layer0_head3.png

# 先生成一段续写，再可视化整段序列
python attention_cli.py --prompt "Explain attention in one sentence." \
    --max-new-tokens 40

# 并排对比多层上的 attention sink
python attention_cli.py --compare-layers 0 13 -1 --output layer_compare.png
```

完整参数见 `python attention_cli.py --help`。主要参数：

| 参数 | 含义 | 默认 |
| --- | --- | --- |
| `-p, --prompt` | 待可视化文本 | `北京 的 天气 怎么样` |
| `-o, --output` | 输出 PNG 路径 | `attention_heatmap.png` |
| `-m, --model` | HF 模型名或本地路径 | `Qwen/Qwen3-0.6B` |
| `--device` | `cuda` / `mps` / `cpu` | 自动检测 |
| `-l, --layer` | 层索引（`-1` = 最后一层） | `-1` |
| `--head` | 头索引（`-1` = 对头平均） | `-1` |
| `--compare-layers` | 并排绘制多层 | 关 |
| `--max-new-tokens` | 捕获注意力前先生成 N 个 token | `0` |
| `--no-chat-template` | 直接喂原始提示词（不加 `<|im_start|>`） | 关 |
| `--cmap` | Matplotlib 色图 | `viridis` |

**怎样认轴。** 行对应读取信息的位置（Query），列对应被读取的位置（Key）。沿着同一行从左向右看，就能比较这个位置在各个已有位置上分配了多少注意力。主对角线右上方代表未来位置，因果模型会屏蔽这一区域。

> 首次运行会下载模型权重（约 1–2 GB）。推荐 GPU/MPS；短提示词用 CPU 也可。

### 交互式前端流程

#### 步骤 1：生成轨迹

```bash
# 方案 A：基础注意力跟踪演示
python agent.py

# 方案 B：带工具调用的 ReAct Agent（多步推理）
python main.py
```

每次运行会在 `frontend/public/trajectories/` 下写入带时间戳的轨迹文件。

#### 步骤 2：启动前端

```bash
cd frontend
npm install  # 仅首次
npm run dev
```

#### 步骤 3：查看

浏览器打开 http://localhost:3000。可保持前端运行，在另一终端继续生成新轨迹——界面会自动出现。

<a id="learning-3"></a>

## 分析结果与形成判断

### 从一个格子读到一列

打开前面的北京天气热力图。提示词分成 9 个 token，第一个是“北京”，最后一个是“样”。先找左下角：第 8 行、第 0 列（从 0 编号）表示模型处理“样”这个位置时，分给“北京”的注意力权重。三幅图使用同一套对数色标，颜色越亮，权重越大。对照最左和最右两幅图，这个格子在第 27 层明显更亮。

图里的数值已经对该层的 16 个注意力头取过平均。在本实验目录运行下面的命令，可以直接从保存的矩阵核对这个格子，再看首列的平均权重。只需安装 NumPy，无需下载模型。

```bash
python - <<'PYTHON'
import numpy as np

path = "runs/exp2-2-qwen3-0.6b-20260730-v3/attention_matrices.npz"
with np.load(path) as matrices:
    for layer in (0, 13, 27):
        weights = matrices[f"simple_layer_{layer}"]
        print(f"第 {layer} 层：末行首列 {weights[-1, 0]:.1%}，首列均值 {weights[:, 0].mean():.1%}")
PYTHON
```

从第 0、13 到 27 层，“样”分给“北京”的权重依次为 1.0%、48.3% 和 80.2%。图标题里的 `sink` 则取首列九个位置的平均值，依次为 14.7%、73.9% 和 83.2%。第一行的第一个 token 只能读到自己，首列权重必为 1，也计入这个平均值。这样读图，就能分清一个位置的权重和整列的统计量。

这张图只记录模型读取提示词的过程；“样”仍是用户输入的一部分。要判断模型的回答是否依赖“北京”，还得观察生成的答案，例如换一个城市重新提问，再比较答案怎样变化。

<a id="status-bar-comparison"></a>

### 实验 2-8：已打过三次电话，模型会怎么回答？

用户请 Agent 再给 Xfinity 打一次电话催退款，任务规定最多打三次。历史里已经有了三次通话，中间还夹着几次搜索。两组模型读到相同的办事经过；其中一组在上下文末尾额外看到状态栏，明确写着通话次数已达上限（3/3）。

先读[两组回答](runs/exp2-7-qwen3-0.6b-20260730-v2/comparison.json)。在 `arms` 下，每组的 `trials` 保存了三次回答的原文（`output_text`）和分类（`behavior`）。没有状态栏时，两次回答明确拒绝再打，一次归入“其他”；加上状态栏后，三次都明确拒绝。两组都没有被判为再次拨号。读第二次回答尤其有用：少一次明确拒绝，能不能就算多打了一通电话？

再看[两组最后一层的注意力图](runs/exp2-7-qwen3-0.6b-20260730-v2/status_bar_attention.png)。图只取每组第一次生成，按注意力头求平均；两组的这次回答都明确拒绝再打。把图和回答放在一起，可以观察同样作出拒绝时模型怎样读取历史和状态栏。若要判断加状态栏是否能稳定减少违规，还需要更多会出现违规的对照样本。归档沿用旧目录名 `exp2-7`。

### 检查自己的解释

若同一个词在不同层获得不同权重，能否用一张热力图概括模型对它的全部处理？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 2 — **Experiment 2-2 ★: Attention mechanism visualization**.  
> 配套《深入理解 AI Agent》第 2 章 **实验 2-2 ★：注意力机制可视化**。

← [Chapter 2 index / 返回第 2 章目录](../README.md)

---

### 项目结构

```
attention_visualization/
├── attention_cli.py      # 独立 CLI：提示词 -> 注意力热力图 PNG
├── agent.py               # 核心注意力跟踪 Agent
├── main.py               # 带工具调用的 ReAct Agent
├── tools.py              # 工具实现
├── visualization.py      # 可视化工具（热力图 / 对比）
├── config.py            # 配置
├── requirements.txt     # Python 依赖
├── env.example          # 环境变量模板
├── frontend/            # Next.js 前端
│   ├── pages/
│   ├── components/
│   └── public/
│       └── trajectories/  # 轨迹 JSON
│           ├── trajectory_YYYYMMDD_HHMMSS.json
│           └── manifest.json
└── attention_data/      # 额外轨迹存储
```

### 自定义轨迹

在 `agent.py` 的 `demonstrate_attention_tracking()` 中编辑：

```python
test_prompts = [
    ("Your custom query here", "Category"),
]
```

或在 `main.py` 的 `demonstrate_react_agent()` 中修改。也可编程调用：

```python
from agent import AttentionVisualizationAgent

agent = AttentionVisualizationAgent()
result = agent.generate_with_attention(
    "Your query here",
    max_new_tokens=100,
    temperature=0.3,
    save_trajectory=True,
    category="Custom"
)
```

<a id="learning-5"></a>

## 排查问题与查阅资料

### 故障排除

**前端无轨迹：** 至少运行一次 `agent.py` 或 `main.py`；检查 `frontend/public/trajectories/` 与 `manifest.json`。

**前端无法启动：** 确认 Node 14+；在 `frontend` 中 `npm install`；检查 3000 端口占用。

**生成很慢：** 首次下载模型；尽量用 GPU/MPS；减小 `max_new_tokens`。

## Notes / 说明

- Commands, paths, model names, and defaults are identical in both language sections.  
- 命令、路径、模型名与默认值在中英文两节中保持一致。

## English

### Overview

Interactive tools for exploring attention in language models. Each agent run can create a trajectory viewable in a frontend; a standalone CLI also writes heatmaps directly.

Each run can capture:

- Input query and model response
- Token-by-token attention weights
- Attention patterns across layers and heads
- Statistical analysis of attention distribution

### Architecture

1. **Agent generates trajectories**: Run `agent.py` or `main.py`
2. **JSON storage**: Unique files under `frontend/public/trajectories/`
3. **Frontend visualization**: React app loads trajectories with tab navigation

### Quick start (standalone CLI)

Fastest way to reproduce Chapter 2 attention patterns (实验 2-2): `attention_cli.py` runs a real model, captures self-attention, and writes a heatmap PNG—no frontend.

```bash
# Single heatmap for the default prompt (last layer, heads averaged)
python attention_cli.py

# Custom prompt, inspect a specific layer/head, choose the output path
python attention_cli.py --prompt "北京 的 天气 怎么样" \
    --layer 0 --head 3 --output layer0_head3.png

# Generate a short continuation first, then visualize the whole sequence
python attention_cli.py --prompt "Explain attention in one sentence." \
    --max-new-tokens 40

# Compare how the attention sink emerges across layers, side by side
python attention_cli.py --compare-layers 0 13 -1 --output layer_compare.png
```

Run `python attention_cli.py --help` for the full flag list. Key flags:

| Flag | Meaning | Default |
| --- | --- | --- |
| `-p, --prompt` | Text to visualize | `北京 的 天气 怎么样` |
| `-o, --output` | Output PNG path | `attention_heatmap.png` |
| `-m, --model` | HF model name or local path | `Qwen/Qwen3-0.6B` |
| `--device` | `cuda` / `mps` / `cpu` | auto-detect |
| `-l, --layer` | Layer index (`-1` = last) | `-1` |
| `--head` | Head index (`-1` = average over heads) | `-1` |
| `--compare-layers` | Render several layers side by side | off |
| `--max-new-tokens` | Generate N tokens before capturing attention | `0` |
| `--no-chat-template` | Feed the raw prompt (no `<|im_start|>` markers) | off |
| `--cmap` | Matplotlib colormap | `viridis` |

**What the heatmap shows.** Rows are Query positions; columns are Key positions. The tool prints the **attention-sink share**—the fraction of each row’s attention on the first token. On `Qwen3-0.6B` the last-layer sink often absorbs ~75–85% of every row (Chapter 2 “Attention Sink”), while layer 0 is closer to a local diagonal. The masked upper triangle shows the causal triangle: each token attends only to itself and prior tokens.

> First run downloads model weights (~1–2 GB). GPU/MPS recommended; CPU works for short prompts.

### Canonical Experiment 2-2 evidence

The acceptance campaign captures more than a display-only heatmap: it pins the
real Qwen3-0.6B revision, retains lossless first/middle/last-layer matrices for
the exact `北京 的 天气 怎么样` prompt, generates a sequence with distinct
`<think>` and final-answer regions, verifies the causal upper triangle
numerically, and reports attention-sink plus beginning/middle/end position
measurements. Observed magnitudes are results, not favorable-result gates.

```bash
python run_attention_experiment.py \
  --output runs/exp2-2-qwen3-0.6b-$(date +%Y%m%d-%H%M%S)
```

The latest completed real run is summarized by `validation/latest.json`; its
manifest hashes the evidence JSON, lossless NPZ tensors, and both heatmaps.

### Interactive frontend workflow

#### Step 1: Generate trajectories

```bash
# Option A: basic attention tracking demo
python agent.py

# Option B: ReAct agent with tool calling (multi-step reasoning)
python main.py
```

Each run writes a timestamped trajectory under `frontend/public/trajectories/`.

#### Step 2: Start the frontend

```bash
cd frontend
npm install  # first time only
npm run dev
```

#### Step 3: View

Open http://localhost:3000. Keep the frontend running; new trajectories appear automatically.

### Experiment 2-8: status-bar comparison

The manuscript's Xfinity control is a separate matched campaign, not the older
tool-vs-no-tool demo. It runs the same complete trajectory in two arms, adds
the exact `<agent_status>` 3/3 block only to the intervention arm, samples
three real Qwen3-0.6B decisions per arm, and captures the final layer's true
eager-attention tensor for the first matched pair.

```bash
python run_status_bar_experiment.py \
  --output runs/exp2-7-qwen3-0.6b-$(date +%Y%m%d-%H%M%S)
```

The output retains raw prompts, token IDs/text, behavior classifications,
region-level response attention, lossless matrices, a side-by-side heatmap,
model revision, hashes, and a completion receipt. The preregistered design is
`status_bar_protocol.json`; completion does not depend on a favorable result.

### Project structure

```
attention_visualization/
├── attention_cli.py      # Standalone CLI: prompt -> attention heatmap PNG
├── agent.py               # Core attention tracking agent
├── main.py               # ReAct agent with tool calling
├── tools.py              # Tool implementations
├── visualization.py      # Visualization utilities (heatmap / comparison)
├── config.py            # Configuration settings
├── requirements.txt     # Python dependencies
├── env.example          # Environment variable template
├── frontend/            # Next.js frontend
│   ├── pages/
│   ├── components/
│   └── public/
│       └── trajectories/  # Stored trajectory JSONs
│           ├── trajectory_YYYYMMDD_HHMMSS.json
│           └── manifest.json
└── attention_data/      # Additional trajectory storage
```

### How it works

#### Trajectory generation

**`agent.py`:** basic attention tracking on various query types; single-step responses; good for basic patterns.

**`main.py`:** ReAct agent with tools; multi-step reasoning; shows how attention shifts with tools.

Both scripts write unique timestamped trajectories, save under `frontend/public/trajectories/`, and update the manifest.

#### Data format

```json
{
  "id": "20250914_123456",
  "timestamp": "2025-09-14 12:34:56",
  "test_case": {
    "category": "Math",
    "query": "What is 25 * 37?",
    "description": "Agent trajectory from..."
  },
  "response": "The answer is...",
  "tokens": ["What", "is", "25", ...],
  "attention_data": {
    "tokens": [...],
    "attention_matrix": [[...]],
    "num_layers": 1,
    "num_heads": 16
  },
  "metadata": {}
}
```

#### Frontend

Loads trajectories from the manifest; tabs between runs; heatmaps, token analysis, stats; auto-updates when new trajectories appear.

### Features

- Multiple trajectories per agent run
- Tab navigation between runs
- Interactive attention heatmap
- Token-level analysis
- Stats: average / max attention, entropy
- Categories: Math, Knowledge, Reasoning, Code, Creative
- Persistent storage

### Custom trajectories

Edit `demonstrate_attention_tracking()` in `agent.py`:

```python
test_prompts = [
    ("Your custom query here", "Category"),
]
```

Or `demonstrate_react_agent()` in `main.py`. Programmatic:

```python
from agent import AttentionVisualizationAgent

agent = AttentionVisualizationAgent()
result = agent.generate_with_attention(
    "Your query here",
    max_new_tokens=100,
    temperature=0.3,
    save_trajectory=True,
    category="Custom"
)
```

### Requirements & installation

**Python:** 3.12, PyTorch, Transformers — installed by the root `ch2` extra.
**Frontend:** Node.js 14+, npm/yarn — see `frontend/package.json`.

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

cd chapter2/attention_visualization

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# edit .env for model, device, visualization settings
cd frontend && npm install
```

### Tips

- First run downloads ~1–2 GB model; prefer GPU/MPS
- Run both `agent.py` and `main.py` to compare tool vs no-tool attention
- Use tabs to compare similar queries
- Look at patterns across math / knowledge / reasoning / code / creative

### Troubleshooting

**No trajectories in frontend:** run `agent.py` or `main.py` once; check `frontend/public/trajectories/` and `manifest.json`.

**Frontend won’t start:** Node 14+; `npm install` in `frontend`; check port 3000.

**Slow generation:** first-run download; use GPU/MPS; smaller `max_new_tokens`.

### Notes

- Trajectories are timestamped for uniqueness
- Manifest keeps the last 50 trajectories
- Trajectories persist across sessions

---
