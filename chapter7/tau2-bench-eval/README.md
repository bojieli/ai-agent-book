# 在交互环境中评价客服 Agent

用户打电话说手机上不了网。客服请他关闭省流量模式，他照做了。现在可以在工单上写“已解决”吗？先想一想，要给这次服务打分，你会核对哪条线路、谁做了什么，以及用户的手机最后能不能上网。

[English](#english)

<a id="learning-0"></a>

## 理解问题与方法

τ²-bench 的电信环境让两方都能动手。客服可以查询账户、给指定线路补充流量；用户模拟器可以操作自己的设备。评估程序既能回看双方的工具调用，也能在通话结束后读取环境状态。一次配合成功可能只是解决问题的第一步，能得多少分还要看这道题选了哪些判据。

### 在共享环境中观察双方怎样解决问题

实验 7-1 选取五个 telecom 任务，每题运行一次，客服 Agent 与用户模拟器采用同一模型。双方都能影响环境，因此不能只读客服的语言回答：还要检查用户是否完成了被要求的操作，以及客服是否修改了正确的业务状态。

<a id="learning-1"></a>

## 准备环境与输入

第一次做实验，可以先读仓库附的[五题轨迹](validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/trajectories.json)，按下文的 Python 练习复核分数。如果要让客服与模拟用户重新对话，再安装下面指定版本的框架。

### 准备固定版本的外部环境

本目录保留实验包装与结果，上游源码需要另外获取。下面从仓库根目录克隆并固定提交，然后创建 Python 3.12 环境：

```bash
git clone https://github.com/sierra-research/tau2-bench.git chapter7/tau2-bench
git -C chapter7/tau2-bench checkout --detach 8d005b0e5b9e4af0bc055886fa7f95fc86d1710e
cd chapter7/tau2-bench
uv venv --python 3.12
uv pip install -e .
```

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读一条电信任务的目标和工具轨迹，再按下文取得固定版本的外部框架。配置模型后从单个任务、单次试验开始，逐步核对每次动作如何改变状态，最后才扩展到任务集合。

### 从一个任务扩展到五个任务

配置 `OPENROUTER_API_KEY` 后，先把下面的 `--num-tasks` 设为 1，读懂一条轨迹，再恢复为 5。保留 `--num-trials 1`，便于把一次结果对应到具体任务。已有运行使用同一个 `gpt-4.1-mini` 作为双方模型，并发数为 3；两侧温度为 0，记录的随机种子为 300。

```bash
.venv/bin/tau2 run \
  --domain telecom \
  --agent-llm openrouter/openai/gpt-4.1-mini \
  --user-llm openrouter/openai/gpt-4.1-mini \
  --num-trials 1 \
  --num-tasks 5 \
  --max-concurrency 3 \
  --save-to exp7-1-openrouter-gpt41mini-telecom-5tasks-20260802-v1 \
  --log-level INFO
```

<a id="learning-3"></a>

## 分析结果与形成判断

本目录保留的是复现配置与记录，运行主体在外部框架中。少量任务的一次成功率不代表整个基准成绩；应同时记录任务选择、模型与试验次数。

### 为什么 4/5 不足以解释系统表现

已有记录中，五题均以 `user_stop` 正常结束，没有提供商错误；平均奖励和 Pass@1 为 0.80。提供商报告的总费用约为 $0.151312，其中客服 $0.112672，用户模拟器 $0.0386396。费用和分数属于这次运行条件。

先用归档核对 0.80 的分母。在本实验目录运行下面的命令，只读已有轨迹，无需模型账号。每行依次打印试验编号、奖励和任务编号；对照最后一列，看这五次运行是否回答了同一道题。

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path

run = Path("validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1")
records = json.loads((run / "trajectories.json").read_text())["simulations"]
for record in records:
    print(record["trial"], record["reward_info"]["reward"], record["task_id"])
PYTHON
```

你会看到五个不同的任务编号，奖励四个为 1，一个为 0。如果要回答“同一题连做两次，能否两次都成功”，应保留同一组任务，从相同初始状态分别重跑。把不同任务的两条记录拼在一起，衡量的是另一件事。

更值得细读的是失败题。用户给出的号码是 `555-123-2002`，Agent 却选择了 `L1001`；工具随后明确显示该线路对应 `555-123-2001`，它仍使用了这条线路的 3.2/5 GB 用量。虽然用户侧成功关闭了 Data Saver，Agent 没有检查正确的 `L1002`，也未补充要求的 2 GB 流量。71 条消息的轨迹最后转交人工，`refuel_data` 与后续三项环境断言失败。另一个过程问题是，它在一轮中发起了两个客户查询，而策略规定一次只能调用一个工具。

为什么关掉省流量模式仍得 0 分？在同一份轨迹里，`action_checks` 记录指定动作有没有出现，`env_assertions` 记录结束时的状态是否符合期望。用下面的命令并排读这两份结果：

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path

run = Path("validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1")
records = json.loads((run / "trajectories.json").read_text())["simulations"]
failed = next(record for record in records if record["reward_info"]["reward"] == 0)
score = failed["reward_info"]
for check in score["action_checks"]:
    print("动作", check["action"]["name"], check["action_match"])
for check in score["env_assertions"]:
    print("状态", check["env_assertion"]["func_name"], check["met"])
print("计分依据", score["reward_breakdown"])
PYTHON
```

两个指定动作匹配了一个。三个状态检查分别核对移动数据状态、网络速度和指定线路的补充流量，结果全部为假。`reward_basis` 在这五题里都只列出 `ENV_ASSERTION`。所以不能把匹配的一个动作算成半分；它的价值在于告诉你用户已经配合，下一步应沿客服选线路的过程查错。同样，一轮发起两次查询是另一个值得修的过程问题，但这次分数没有单独为它扣分。

上游对记录格式和试验次数的检查通过，完整任务覆盖检查未通过：排行榜要求覆盖整个 telecom 集合。要复核本次五题的费用与覆盖范围，可读[运行汇总](validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/evidence.json)和[文件清单](validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/manifest.json)。

### 检查自己的解释

Agent 得到了正确最终状态，却违反中间业务规则，应怎样评价这次运行？

## English

# Experiment 7-1: τ²-bench telecom evaluation

This directory retains the bounded τ²-bench campaign requested by the
manuscript: five telecom tasks, one trial per task, with the same model acting
as the customer-service Agent and user simulator.

## Code map

- **Run first:** follow the pinned external checkout command below and run one task with num-trials 1.
- **Start here:** the τ²-bench CLI is the runner; this directory is the reproducibility and evidence wrapper.
- **Core behavior:** the external telecom environment executes the Agent/user turns; this project records the resulting trajectory.
- **State / protocol:** saved raw trajectory, task seed, model IDs and run manifest under validation/runs/.
- **Verifier:** task reward plus the chapter acceptance checks; inspect the failed task record, not only the 4/5 aggregate.
- **Experiment variable:** fixed task set, model pair, concurrency and seed.
- **Skip on first pass:** upstream framework internals and cost-report formatting.

## Reproduction

The external checkout is deliberately not vendored. Clone and pin the
authoritative source first:

```bash
git clone https://github.com/sierra-research/tau2-bench.git chapter7/tau2-bench
git -C chapter7/tau2-bench checkout --detach 8d005b0e5b9e4af0bc055886fa7f95fc86d1710e
cd chapter7/tau2-bench
uv venv --python 3.12
uv pip install -e .
```

With `OPENROUTER_API_KEY` configured, the saved campaign used:

```bash
.venv/bin/tau2 run \
  --domain telecom \
  --agent-llm openrouter/openai/gpt-4.1-mini \
  --user-llm openrouter/openai/gpt-4.1-mini \
  --num-trials 1 \
  --num-tasks 5 \
  --max-concurrency 3 \
  --save-to exp7-1-openrouter-gpt41mini-telecom-5tasks-20260802-v1 \
  --log-level INFO
```

Both model temperatures were `0`; τ²-bench recorded seed `300`. The retained
raw trajectory is under
[`validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/`](validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/).

## Result

The Agent passed 4/5 tasks, for average reward and Pass@1 of **0.80**. All five
simulations ended normally with `user_stop`; there were no provider errors.
The retained provider-reported costs total about **$0.151312**: $0.112672 for
the Agent and $0.0386396 for the user simulator.

The failed task was
`[mobile_data_issue]data_saver_mode_on|data_usage_exceeded[PERSONA:Easy]`.
The customer supplied phone `555-123-2002`, but the Agent selected line
`L1001`. A later `get_details_by_id(L1001)` result explicitly associated that
line with phone `555-123-2001`; nevertheless, the Agent continued using its
3.2/5 GB usage reading. It correctly had the user disable Data Saver, but did
not inspect the matching `L1002` line or perform the required 2 GB data refuel.
It spent the remainder of a 71-message trajectory on unrelated diagnostics and
ultimately transferred to a human. Consequently, `refuel_data` and all three
downstream environment assertions failed. The trajectory also exposes an
earlier policy violation where the Agent emitted two customer-lookup tool calls
in one turn even though the telecom policy permits only one at a time.

This is a useful dual-control failure: the user-side Data Saver action occurred
and was verified in the shared environment, while the Agent-side line-selection
mistake prevented the second state mutation and final recovery.

## Verification boundary

The upstream public verifier reports:

- format validation: passed;
- trial-count validation: passed;
- task validation: failed because a public leaderboard submission must cover
  the full telecom task set.

That coverage failure is expected for the five-task command specified by this
book experiment. This evidence therefore establishes the bounded Experiment
7-1 campaign, not a full-domain τ²-bench leaderboard result. See
[`evidence.json`](validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/evidence.json)
for machine-readable outcomes and [`manifest.json`](validation/runs/exp7-1-openrouter-gpt41mini-telecom-20260802-v1/manifest.json)
for content hashes.

### 任务与计分复核（2026-10-07）

五条任务、运行轨迹及奖励重新对照，合计四题通过；当前 trajectories 与 evidence 两项文件均存在，但哈希与 manifest 记录不符。当前内容可用于逐条核对，归档一致性仍待确认；历史文件与哈希保持原样。正文的法国漫游案例保留两侧初始化、号码与线路映射、用户工具调用、275 Mbps 测速及最终两条断言。`reward_basis` 仅选择 `ENV_ASSERTION`，动作检查仍单独出现在结果中；过程规则未纳入总分由任务计分配置决定，二元奖励也可以组合过程条件。正文改用字段表解释任务，完整定义和消息编号留在归档中。
