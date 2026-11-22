# 在固定工具环境中比较模型行动方式

有的模型先大量阅读，有的模型很快开始改代码。要判断这种倾向是否来自模型，就需要把工具、任务和提示词尽量保持一致。本实验围绕这个控制变量问题展开。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

相同 Harness 向不同模型提供相同仓库与动作接口，再观察首次修改之前的探索过程。探索次数、修改时机与最终正确性分别反映不同侧面，不应把“更快动手”直接当成更高能力。

### 固定脚手架，才能比较模型的行动倾向

实验 7-8 为不同模型提供相同的系统提示、用户任务、仓库、工具名称、JSON schema、工具结果、轮数上限与独立测试命令。默认还使用同一个 OpenRouter 兼容端点，减少提供商适配器的差别。中性提示不要求先读多少文件、先写计划或尽早编辑，因此可以观察模型自行选择的顺序。

三个小型仓库分别涉及局部 bug、跨文件身份信息修改和影响公共契约的缓存修复。每个用例初始测试都会失败，每次运行使用新的临时副本，结束后再独立运行测试。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读固定任务与工具定义，列出两条合理但不同的工作路径。按下文配置模型，运行相同条件的多次试验；比较读文件、执行检查和开始修改的时刻。

### 先运行中性条件，再单独做提示消融

从仓库根目录准备环境并运行以下命令。运行器在重复试验之间交替模型顺序，并在每个“模型 × 任务 × 试验”单元后保存进度；使用相同输出目录重跑时，只补齐缺失单元。

```bash
uv sync --locked --extra ch6
export OPENROUTER_API_KEY=...
uv run python chapter7/model-action-threshold/experiment.py \
  --models openai/gpt-5.6-sol anthropic/claude-sonnet-5 \
  --trials 3 \
  --policy neutral \
  --output chapter7/model-action-threshold/results/my-run
```

下面另建一个输出目录，加入明确的 explore-first 指令。中性组比较固定脚手架下的模型差异；两组之间的比较则考察脚手架指令能改变多少行为。不要把它们混成同一组模型成绩。

```bash
uv run python chapter7/model-action-threshold/experiment.py \
  --models openai/gpt-5.6-sol anthropic/claude-sonnet-5 \
  --trials 3 --policy explore-first \
  --output chapter7/model-action-threshold/results/explore-first
```

<a id="learning-3"></a>

## 分析结果与形成判断

如果某模型探索更多但更少返工，额外步骤可能有价值。反过来，大量阅读也可能没有收集到必要信息。分析应结合独立测试结果与总成本。

### 把第一次编辑放回完整轨迹中

同时记录首次编辑前的工具调用、耗时、读取/搜索次数和独立文件数；再看模型首次触发的测试是否通过、测试后的返工、总编辑次数、改动文件数、最终成功率、延迟与 token。更早编辑并不等于更高质量，更晚编辑也未必是必要探索。

`config.json` 保存系统提示与工具 schema 的哈希，`observations.jsonl` 保留逐条轨迹，`summary.json` 汇总指标，`manifest.json` 核对这三个文件。完整记录应包含所有要求的单元且没有 API 错误；任务失败仍是有效观察，不能因结果不好而删除。

### 检查自己的解释

怎样区分模型主动选择的策略，与提示词无意中鼓励的策略？

<a id="learning-5"></a>

## 排查问题与查阅资料

### 检查测量实现

以下离线测试检查路径范围、事件边界计数、返工测量、汇总，以及样例初始状态是否确实失败：

```bash
python -m unittest discover -s chapter7/model-action-threshold/tests -v
```

## English

# Experiment 7-8: Model action thresholds in a fixed coding harness

This experiment tests whether an explore-first or implement-first tendency
follows the **model** when the coding harness is held fixed. Both model
families receive the same system prompt, user task, repository, tool names,
JSON schemas, tool results, turn limit, and independent test command. By
default both are also routed through the same OpenRouter OpenAI-compatible
endpoint, reducing provider-adapter differences.

The neutral prompt does not require the model to read any number of files,
produce a plan, edit early, or run tests. The experiment records what the
model chooses to do.

## Tasks and metrics

Three miniature repositories cover a localized bug, a cross-cutting identity
change, and a public-contract-sensitive cache fix. Every fixture starts with
failing tests. Each run is performed in a fresh temporary copy and is
independently tested at the end.

Primary process metrics:

- tool calls and elapsed time before the first edit;
- read/search calls and unique files read before the first edit;
- whether the first model-triggered test run passes;
- edits after the first test, total edits, and files changed;
- final test success, latency, and token usage.

Time to first edit is not a quality score. Interpret it together with
first-patch acceptance, rework, final success, and total cost.

## Install and run

From the repository root:

```bash
uv sync --locked --extra ch6
export OPENROUTER_API_KEY=...
uv run python chapter7/model-action-threshold/experiment.py \
  --models openai/gpt-5.6-sol anthropic/claude-sonnet-5 \
  --trials 3 \
  --policy neutral \
  --output chapter7/model-action-threshold/results/my-run
```

The runner alternates model order between trials and checkpoints the campaign
after every cell. Re-running the same command and output directory resumes
only the missing model × task × trial cells. `config.json` hashes the system prompt and tool schema;
`observations.jsonl` retains every trajectory; `summary.json` aggregates the
metrics; and `manifest.json` hashes those three artifacts.

Run the optional harness ablation separately:

```bash
uv run python chapter7/model-action-threshold/experiment.py \
  --models openai/gpt-5.6-sol anthropic/claude-sonnet-5 \
  --trials 3 --policy explore-first \
  --output chapter7/model-action-threshold/results/explore-first
```

Do not merge neutral and explore-first observations into one model comparison.
The first run estimates the model effect under a neutral harness; comparing
the two campaigns estimates how much an explicit harness instruction modifies
that behavior.

## Validate the implementation

The offline tests verify path confinement, event-boundary accounting, rework
measurement, aggregation, and that every fixture starts in the intended
failing state:

```bash
python -m unittest discover -s chapter7/model-action-threshold/tests -v
```

The saved validation campaign in `results/` is considered complete only when
its manifest contains every requested model × task × trial observation and no
API errors. Model task failures remain valid experimental outcomes and are not
silently discarded.
