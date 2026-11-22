# 比较固定的快慢角色协作

语音交互要求及时响应，复杂任务又需要较长规划。固定快慢角色的设计试图让快速交互与较慢处理同时进行。本项目用对照任务研究这种分工。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

固定拓扑预先定义角色与消息路径，减少临时协调工作，但可能限制任务中的灵活分工。与单模型比较时，需要保持任务、用户行为与成功条件一致。

### 固定分工与自主编排比较什么

这是实验 10-3 的固定拓扑基线，对应的自主路线在同章 `autonomous-phone-registration`。TalkAct 的 duplex 组同时使用快速与慢速 Agent，strawman 组只使用慢速模型。四个隔离任务在两种条件下各重复两次，共 16 条轨迹；比较的是响应延迟、任务结果与成本之间的关系。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 保持任务和调用者配置一致

已有实验使用上游 `19PINE-AI/TalkAct` 的提交 `7d70007f72d45ddfc1a14e8e229b6d444e4919a2`、Python 3.12.11、Chromium 149 与隔离 Flask 任务服务。快速层为 `claude-haiku-4-5`，慢速层为 `claude-opus-4-8`；单模型组只保留慢速层。

默认 Gemini 调用者凭据在当时返回 `400 API_KEY_INVALID`，因此改用上游支持的 `CUV_USER_MODEL=claude-sonnet-4-5-20250929`。这保留了拓扑与任务，但双方同属一个模型系列可能影响结果；不要把这组数据与默认 Gemini 调用者的上游结果混在一起。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读一条任务中的用户话语和系统响应时间线，辨认哪个角色在沟通、哪个在处理任务。按下文准备外部 TalkAct 环境，在本地受控任务上比较双角色与单模型路径。

### 运行对照并核对完整轨迹

第一个命令在准备好的上游源码环境中执行四个任务；第二个命令从本书仓库根目录核对已有记录。注意上游 `--seeds` 在这个固定版本中只是给重复试验加标签，没有向运行器或提供商注入确定性随机种子。

```bash
CUV_USER_MODEL=claude-sonnet-4-5-20250929 python bench/run_bench.py \
  --tasks forms-insurance booking-flight webmail-report meeting-helper \
  --conditions duplex strawman \
  --seeds 2
```

```bash
python chapter10/talkact-reproduction/validate_campaign.py \
  chapter10/talkact-reproduction/validation/runs/exp10-3-talkact-anthropic-caller-20260803-v2
```

<a id="learning-3"></a>

## 分析结果与形成判断

响应更早不等于任务完成更早。应检查早期回复是否有用、信息是否同步，以及慢角色结果到达后是否纠正了临时判断。

### 延迟优势不等于所有维度都更好

| 指标 | Duplex | Strawman |
| --- | ---: | ---: |
| 轨迹数 | 8 | 8 |
| 任务成功率 / 部分得分 | 1.000 / 1.000 | 1.000 / 1.000 |
| 探针正确率 | 0.833 | 0.917 |
| 语音延迟 p50 / p90 | 2.32 / 2.85 秒 | 12.52 / 21.14 秒 |
| 最大语音延迟 | 4.03 秒 | 37.29 秒 |
| 平均整段任务耗时 | 207.2 秒 | 178.0 秒 |
| 语音延迟样本数 | 47 | 44 |

中位语音延迟改善约为 `12.52 / 2.32 = 5.40` 倍，但任务成功率持平，单模型组的探针正确率和平均总耗时反而更好。12 条有动作得分的轨迹全部成功，另外四条 meeting-helper 使用探针评分，不能把它们的评分字段当作相同测量。

原始记录还保留了 39 次快到慢转交、33 次慢到快事件、91 个延迟样本，以及各层 token、缓存与步骤统计。它没有逐请求提供商 response ID，也没有模拟调用者 token，因此不能用这些记录推断未保存的成本。完整英文数据、23 个文件的 manifest 和认证失败历史均留在本文。

### 检查自己的解释

快速角色为了减少等待先作了承诺，慢角色随后发现不可行，系统应怎样处理？

## English

# Experiment 10-3 · Fixed-topology TalkAct baseline

This is the fixed-topology comparison arm of Chapter Experiment 10-3. Its
validation artifacts use the current `10-3` identifier; the autonomous arm is
implemented in [`autonomous-phone-registration`](../autonomous-phone-registration/).

This record covers the pinned external TalkAct reproduction used by current
Experiment 10-3. The comparison runs concurrent fast/slow agents (`duplex`) against a
single-model control (`strawman`) over four hermetic tasks and two labeled
repetitions per task and condition.

Status: **complete for the retained Anthropic-caller configuration**. The
[canonical run](validation/runs/exp10-3-talkact-anthropic-caller-20260803-v2/)
contains all 16 episode logs, aggregate and per-episode analysis, the exact
protocol and environment, console logs, and a manifest. The independent
validator passes all 17 gates.

## Configuration and deviation

The campaign used the official `19PINE-AI/TalkAct` source at commit
`7d70007f72d45ddfc1a14e8e229b6d444e4919a2`, Python 3.12.11, Playwright
Chromium 149, and the hermetic Flask task server. The concurrent arm kept the
pinned source's fast `claude-haiku-4-5` and slow `claude-opus-4-8` agents; the
strawman arm kept the slow model alone.

TalkAct normally uses Gemini for its simulated caller, but the configured
Gemini credential returned `400 API_KEY_INVALID`. The campaign therefore used
the source-supported `CUV_USER_MODEL=claude-sonnet-4-5-20250929` override. This
preserves the task and agent topology but makes the caller Anthropic-based too,
which can introduce same-family bias. These results are a distinct
Anthropic-caller configuration and must not be silently pooled with upstream
results that use the default Gemini caller.

The exact campaign was:

```bash
CUV_USER_MODEL=claude-sonnet-4-5-20250929 python bench/run_bench.py \
  --tasks forms-insurance booking-flight webmail-report meeting-helper \
  --conditions duplex strawman \
  --seeds 2
```

## Results

| Metric | Duplex | Strawman |
| --- | ---: | ---: |
| Episodes | 8 | 8 |
| Task success | 1.000 | 1.000 |
| Partial credit | 1.000 | 1.000 |
| Probe correctness | 0.833 | 0.917 |
| Voice latency p50 | 2.32 s | 12.52 s |
| Voice latency p90 | 2.85 s | 21.14 s |
| Voice latency maximum | 4.03 s | 37.29 s |
| Mean episode wall time | 207.2 s | 178.0 s |
| Voice-latency samples | 47 | 44 |

All 12 action-scored episodes achieved full deterministic success and partial
credit. The four `meeting-helper` episodes intentionally have no action-success
field and instead earned perfect retained probe-answer scores. There were no
episode or provider errors.

The concurrent arm reduced median voice latency by about **5.40×**
(`12.52 / 2.32`), materially below the upstream roughly 15× result. It did not
improve task success: the arms tied. The control also had higher aggregate
probe correctness (0.917 versus 0.833) and lower mean wall time (178.0 seconds
versus 207.2 seconds). The retained run therefore supports a response-latency
advantage for duplex, not a blanket quality or total-runtime advantage.

## Evidence and validation

The 16 raw episodes retain 39 fast-to-slow relays, 33 slow-to-fast events, 91
voice-latency samples, deterministic task checks, probe grades, transcripts,
environment state, and aggregate provider usage. The duplex slow tier used
19,124 input and 26,105 output tokens across 166 steps; its fast tier used
98,945 input and 5,782 output tokens across 87 turns. The strawman slow tier
used 19,208 input and 28,966 output tokens across 177 steps. Cache-read and
cache-creation counts are retained in the episode records.

Run the validator from the repository root:

```bash
python chapter10/talkact-reproduction/validate_campaign.py \
  chapter10/talkact-reproduction/validation/runs/exp10-3-talkact-anthropic-caller-20260803-v2
```

The generated [acceptance report](validation/runs/exp10-3-talkact-anthropic-caller-20260803-v2/acceptance.json)
passes source-pin, campaign-shape, model, usage, error, concurrency, bridge,
latency, task-check, judge, aggregate, and credential-scan gates. The
[manifest](validation/runs/exp10-3-talkact-anthropic-caller-20260803-v2/manifest.json)
hashes the 23 inputs and outputs from which those generated files are derived.
The earlier [authentication preflight](validation/exp10-3-anthropic-auth-20260803-v1/preflight.json)
is retained as failure history, not as the final result.

## Limitations

- The pinned runner's `--seeds` option labels repetitions but does not inject a
  deterministic random seed into the episode runner or provider calls.
- The pinned source retains model labels and aggregate fast/slow token usage
  per episode, but not individual provider response IDs.
- Simulated-caller token usage is not retained by the pinned source.
- `meeting-helper` is evaluated through retained probe grades rather than the
  action-based success and partial-credit fields used by the other tasks.
- The Anthropic caller deviation preserves the benchmark topology but is not
  directly comparable to the upstream default-Gemini caller configuration.
