# 在固定工具环境中比较模型行动方式

两个编程助手接到同一道缓存修复题。一个多读了几份文件才改代码，另一个很快发出了写文件请求。如果这次请求被工具拒绝，应该从什么时候算它“开始动手”？本实验保留了逐步记录，可以分别找到第一次尝试、第一次写入成功和第一次测试。

[English](#english)

<a id="learning-0"></a>

## 理解问题与方法

要比较模型倾向于先探索还是先修改，先让它们面对相同的任务和工具。这里的“行动阈值”通过可以观察的行为来衡量：发出第一次编辑请求之前，模型做了几次查询，实际读过几份文件，花了多少时间。一次编辑能否解决问题，还得另外看测试。

实验 7-9 为不同模型提供相同的系统提示、用户任务、仓库、工具名称、JSON schema、工具返回结果的规则、轮数上限与独立测试命令。默认还使用同一个 OpenRouter 兼容端点，减少提供商适配器的差别。中性提示不要求先读多少文件、先写计划或尽早编辑，因此可以观察模型自行选择的顺序。

三个小型仓库分别涉及局部 bug、跨文件身份信息修改和影响公共契约的缓存修复。每个用例初始测试都会失败，每次运行使用新的临时副本，结束后再独立运行测试。

<a id="learning-1"></a>

## 准备环境与输入

先打开[缓存修复任务](tasks/cache_contract/task.json)，读清用户要求保留的公共接口。仓库附有两种模型各做三道题、每题三次的[中性提示运行记录](results/exp7-8-action-threshold-20260731-v1/observations.jsonl)。先用下文的 Python 标准库命令读这 18 条轨迹，只有重新调用模型时才需要 API 凭据。

<a id="learning-2"></a>

## 按照步骤完成实验

在本实验目录执行下面的命令，取出 Claude Sonnet 5 第二次做缓存题的记录。每行开头的数字是轨迹中的事件序号，中间还穿插着模型回复，因此工具事件的序号可以不连续。

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path

run = Path("results/exp7-8-action-threshold-20260731-v1")
rows = [json.loads(line) for line in (run / "observations.jsonl").read_text().splitlines()]
case = next(row for row in rows if row["model"] == "anthropic/claude-sonnet-5"
            and row["task_id"] == "cache_contract" and row["trial"] == 2)
for event in case["events"]:
    if event["type"] == "tool":
        print(event["sequence"], event["tool"], event["result"].get("error", ""))
print("首个受测补丁通过：", case["first_patch_test_passed"])
print("首次补丁测试后成功编辑的次数：", case["edits_after_first_test"])
PYTHON
```

第 7 个事件是 `write_file`。这个工具只创建新文件，目标已经存在，于是返回 `file already exists`。到第 9 个事件，模型改用 `replace_text` 才真正写入；第 11 个事件的测试通过。按“开始尝试”来算，前面有一次搜索、两次读文件，共三次工具调用。按“开始改动仓库”来算，还要把失败的写入算在前面。这条记录的返工数为零。读这个字段时要注意，只有首次受测补丁之后返回成功的编辑才计数。若要查模型后来是否还尝试过编辑、工具是否拒绝了它，得看逐条事件。

### 先运行中性条件，再单独做提示消融

从仓库根目录准备环境并运行以下命令。运行器在重复试验之间交替模型顺序，并在每个“模型 × 任务 × 试验”单元后保存进度；使用相同输出目录重跑时，只补齐缺失单元。

```bash
# 先在当前终端配置 OPENROUTER_API_KEY
uv run --no-project --with openai python chapter7/model-action-threshold/experiment.py \
  --models openai/gpt-5.6-sol anthropic/claude-sonnet-5 \
  --trials 3 \
  --policy neutral \
  --output chapter7/model-action-threshold/results/my-run
```

下面另建一个输出目录，加入明确的 explore-first 指令。中性组比较固定脚手架下的模型差异；两组之间的比较则考察脚手架指令能改变多少行为。不要把它们混成同一组模型成绩。

```bash
uv run --no-project --with openai python chapter7/model-action-threshold/experiment.py \
  --models openai/gpt-5.6-sol anthropic/claude-sonnet-5 \
  --trials 3 --policy explore-first \
  --output chapter7/model-action-threshold/results/explore-first
```

<a id="learning-3"></a>

## 分析结果与形成判断

先只比较同一道缓存题。GPT-5.6-sol 在三次试验中，每次都先调用了六次工具，读过四份不同的文件才尝试编辑。Claude Sonnet 5 每次都是三次调用、两份文件。两者的首个受测补丁和最终独立测试都通过了。多读的两份文件有没有帮助？这六条轨迹能说明模型采取了不同做法；要判断那两份文件值不值得读，还得找出其中哪条信息可能改变补丁，并用能区分两种做法的任务复测。

### 把第一次编辑放回完整轨迹中

运行器在工具返回结果时给事件打时间戳，所以 `seconds_to_first_edit` 一直量到第一次编辑工具返回，包含这次调用的处理时间。若要单独分析模型迟迟没有发出请求的原因，还需记录派发时刻。再对照此前的读取与搜索次数、读过多少不同文件、首个受测补丁是否通过、此后成功编辑了几次、改动的文件数，以及最终独立测试、总耗时和 token 用量。更早编辑并不等于更高质量，更晚编辑也未必是必要探索。

`config.json` 保存系统提示与工具 schema 的哈希，`observations.jsonl` 保留逐条轨迹，`summary.json` 汇总指标，`manifest.json` 核对这三个文件。完整记录应包含所有要求的单元且没有 API 错误；任务失败仍是有效观察，不能因结果不好而删除。

### 检查自己的解释

怎样区分模型主动选择的策略，与提示词无意中鼓励的策略？

<a id="learning-5"></a>

## 排查问题与查阅资料

### 检查测量实现

以下离线测试检查路径范围、事件边界计数、返工测量、汇总，以及样例初始状态是否确实失败：

```bash
python3 -m unittest discover -s chapter7/model-action-threshold/tests -v
```

## English

# Experiment 7-9: Model action thresholds in a fixed coding harness

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
- successful edits after the first tested patch, edit attempts and successes, and files changed;
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
