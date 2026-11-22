# 在交互环境中评价客服 Agent

客服回答看起来合理，后台状态却可能没有正确改变。τ²-bench 把用户交互、工具操作与任务结果放在同一环境中，适合学习怎样评价完整任务行为。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

模拟用户提供需求，Agent 使用工具，环境根据状态判断任务完成情况。一次评价因此不只是给文本打分，还涉及工具参数、操作顺序和业务约束。用户模拟器的行为也会影响任务难度。

### 在共享环境中观察双方怎样解决问题

实验 7-1 选取五个 telecom 任务，每题运行一次，客服 Agent 与用户模拟器采用同一模型。双方都能影响环境，因此不能只读客服的语言回答：还要检查用户是否完成了被要求的操作，以及客服是否修改了正确的业务状态。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

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

更值得细读的是失败题。用户给出的号码是 `555-123-2002`，Agent 却选择了 `L1001`；工具随后明确显示该线路对应 `555-123-2001`，它仍使用了这条线路的 3.2/5 GB 用量。虽然用户侧成功关闭了 Data Saver，Agent 没有检查正确的 `L1002`，也未补充要求的 2 GB 流量。71 条消息的轨迹最后转交人工，`refuel_data` 与后续三项环境断言失败。另一个过程问题是，它在一轮中发起了两个客户查询，而策略规定一次只能调用一个工具。

这个例子同时包含用户侧成功和客服侧失败。上游检查中的格式与试验次数通过，但完整任务覆盖检查失败，因为排行榜要求覆盖整个 telecom 集合。这里的五题观察可以用于学习局部机制，不能作为全域排行榜结果。完整轨迹、`evidence.json` 和 `manifest.json` 的原始链接保留在本文英文部分。

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
