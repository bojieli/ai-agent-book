# 观察记忆、计划与互动如何形成群体行为

多个角色在同一个虚拟世界中生活，会产生怎样的交流与计划变化？本项目以 Generative Agents 环境为例，学习个体记忆机制与群体行为之间的联系。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4)。

<a id="learning-0"></a>

## 理解问题与方法

角色根据观察形成记忆，通过检索与反思生成计划，再与环境和其他角色互动。看起来连贯的故事可能由这些局部机制产生，但不能只凭叙事合理就证明每个机制都有效。

### 在同一个社会初始状态上改变一个条件

实验 10-5 使用上游 Smallville 的 25 个角色与每步十秒的世界时钟。三组都从同一份加载历史后的零步状态分叉，控制 `agent_history_init_n25.csv` 中 248 条关系记忆及其生成表示。

baseline 保留 Isabella 的情人节聚会和 Sam 的市长选举目标；custom_goal 在同一时间、地点把聚会改为气候韧性工作坊；no_reflection 保留基线目标，关闭 `Persona.reflect()` 并提高重要性触发阈值，同时保留感知、检索、计划、执行和聊天记忆。每组都运行 17,280 步，即两个虚拟日。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 使用隔离环境与运行时适配层

上游 2023 年源码依赖旧的 `openai` 0.27 接口，因此采用独立 Python 3.11 环境。这里固定上游提交，通过运行时适配连接当前聊天与嵌入端点，不修改上游 checkout。

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
git clone https://github.com/joonspk-research/generative_agents.git /tmp/generative_agents
git -C /tmp/generative_agents checkout --detach fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4
```

已有配置使用 DashScope 国际端点的 `qwen3.7-flash` 和 `text-embedding-v4`，需要 `DASHSCOPE_API_KEY`；`GA_OPENAI_API_BASE`、`GA_CHAT_MODEL`、`GA_EMBEDDING_MODEL` 可显式覆盖，覆盖后属于另一组实验条件。适配器保留脱敏请求、响应、ID、用量、延迟和错误；嵌入向量保存在记忆状态中，响应记录只保存维度与内容哈希。

<a id="learning-2"></a>

## 按照步骤完成实验

先选择一个角色，按时间阅读它的观察、记忆和计划，再查看一次交互怎样改变后续行动。按下文准备外部世界与模型接口后，比较保留或移除某个机制时的差异。

### 先生成共同种子，再启动三组模拟

先执行 seed 命令一次，再启动或恢复三组。每 360 步（一个虚拟小时）保存一次；只有模拟状态和压缩响应记录都落盘后才原子更新状态文件。恢复时从该检查点继续，保留第一天和最终状态；更早的小时副本在下一次保存成功后删除。

```bash
.venv/bin/python run_campaign.py \
  --upstream /tmp/generative_agents \
  --output outputs/exp10-5 \
  --mode seed
```

```bash
.venv/bin/python launch_campaigns.py \
  --upstream /tmp/generative_agents \
  --output outputs/exp10-5 \
  --python .venv/bin/python
```

```bash
python -m pytest tests
```

产物写入 `outputs/`。它们只有在完成并验证、明确选作保留记录后，才进入正式记录目录。

<a id="learning-3"></a>

## 分析结果与形成判断

模拟世界的步长、初始人物设定和模型都会影响结果。需要区分计划被写出与行动实际发生，并保留不连贯或未完成的案例。

### 社会行为的变化需要逐层解释

已有三组都到达 2023-02-15 00:00:00，各保留 25 个角色、17,280 行移动记录和 48 个持久检查点。记录包含 148,856 次带唯一 ID 的提供商调用、231 次有界地点修正、25 次独立 Anthropic 判读和 321 个 manifest 文件。

基线聚会传播到三名角色，工作坊只出现在 Isabella 自己的记忆中，没有向外扩散；两组分别产生 1,363 与 977 条关联证据的反思，关闭反思组为零。盲评在 25 个角色中对 17 个偏好基线、对 8 个偏好关闭反思组。基线在时间连贯、人格一致、记忆连续、社交响应四项均分上更高，具体数值与原始判读链接保留在下方英文记录。

这些是混合结果：反思可能改善某些行为，并不意味着替换目标必然引发社会传播。应从具体角色的记忆、行动和判读证据解释差异。

### 检查自己的解释

如果角色的计划很合理，却频繁没有执行，应该检查记忆检索、计划更新还是环境动作？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 为什么需要记录兼容性修正

临时连接失败、超时、限流和服务不可用会在同一次逻辑调用内最多重试五次，并保留 `transport_retries`；默认单次请求超时为 90 秒，可通过 `GA_PROVIDER_TIMEOUT_SECONDS` 修改。重试耗尽或非临时失败仍记为 `success: false`，对应检查点隔离为 `.failed-*`，从最后一个干净状态重放。

旧任务分解解析器可能在接受非空回复后，因缺少或错误的时长字段而崩溃。运行时补丁先尝试原输出；仅在解析形状错误时去掉说明文字，按原顺序保留格式化时长行，并受总时长约束。没有可解析行时仍按原五次预算重新请求，原始响应始终保留。

另一项修正处理 action-arena 输出的括号、引号和空白，并在空间记忆返回的可访问地点中做不区分大小写的精确匹配。无效输出只能留在可访问的当前位置，或使用上游顺序中的首个可访问地点，不能凭空创建地点。每次改动都写入兼容性记录。理解这些修正，才能区分 Agent 行为与旧软件接口的影响。

## English

# Experiment 10-5: Stanford Generative Agents reproduction

This project runs the manuscript's full Agent-society experiment against the
official `joonspk-research/generative_agents` source at commit
`fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4`. It preserves the upstream
25-persona Smallville environment and ten-second world step while replacing
the obsolete GPT-3 API surface with current OpenAI-compatible chat and
embedding endpoints at runtime. The upstream checkout is not modified.

Status: **complete**. The retained campaign has three equal 17,280-step
(two-virtual-day) arms, complete analysis, and an independently passing
[acceptance report](validation/runs/exp10-5-qwen37flash-20260804-v1/acceptance.json):

- `baseline`: the original Isabella Rodriguez Valentine's party and Sam Moore
  mayoral-election seeds;
- `custom_goal`: the same history seed, with Isabella's initial party goal
  replaced by a community climate-resilience workshop at the same place and
  time;
- `no_reflection`: the baseline goal with `Persona.reflect()` disabled and the
  importance trigger raised defensively, preserving perception, retrieval,
  planning, execution, and chat memory but preventing new reflection thoughts.

All three arms fork one shared history-loaded step-zero seed. This controls for
the 248 relationship memories in upstream `agent_history_init_n25.csv` and for
their generated thought/event-triple/poignancy/embedding representations.

## Retained results

Every arm reached exactly `February 15, 2023, 00:00:00` with 25 personas,
17,280 movement rows, and 48 durable checkpoints. The package retains 148,856
canonical provider calls with an equal number of unique response IDs, no
logical errors, positive usage on every response, 231 bounded action-arena
corrections, 25 independent Anthropic judgments, and 321 manifest-bound files.
All 14 acceptance gates pass, including the credential scan.

The findings are mixed, as allowed by the preregistered interpretation rule:

- the baseline Valentine's event reached three agents, while the custom
  climate-resilience workshop appeared only in Isabella Rodriguez's memory and
  did not diffuse beyond its originator;
- the baseline and custom arms created 1,363 and 977 evidence-linked reflection
  thoughts respectively; the reflection-disabled arm created exactly zero;
- the blind judge preferred baseline for 17 of 25 personas and preferred the
  reflection-disabled arm for eight. Baseline scored higher on temporal
  coherence (2.12 vs 1.56), personality consistency (3.20 vs 2.20), memory
  continuity (2.72 vs 1.52), and social responsiveness (3.44 vs 2.48).

The full deterministic analysis is retained in
[`deterministic_analysis.json`](validation/runs/exp10-5-qwen37flash-20260804-v1/analysis/deterministic_analysis.json),
and the raw blind-judge receipts and summary are under the same package's
`analysis/` directory. Failed and interrupted attempts remain separately named
and manifest-bound; they are not counted as canonical evidence.

## Environment

Use an isolated Python 3.11 environment because the 2023 source depends on the
legacy `openai` 0.27 API:

```bash
python3.11 -m venv .venv
.venv/bin/pip install -r requirements.txt
git clone https://github.com/joonspk-research/generative_agents.git /tmp/generative_agents
git -C /tmp/generative_agents checkout --detach fe05a71d3e4ed7d10bf68aa4eda6dd995ec070f4
```

Set `DASHSCOPE_API_KEY` in the environment. The default current models are
`qwen3.7-flash` and `text-embedding-v4` through DashScope's international
OpenAI-compatible endpoint. `GA_OPENAI_API_BASE`, `GA_CHAT_MODEL`, and
`GA_EMBEDDING_MODEL` are explicit overrides; changing them defines a different
experimental configuration.

The adapter never serializes the credential. It retains full chat
requests/responses, provider IDs, token usage, latency, and errors. Embedding
vectors remain in the simulation memory state; receipts retain their dimension
and content hash instead of duplicating every float.

Transient transport failures (`APIConnectionError`, timeout, rate limit, or
service unavailable) are retried up to five times inside the same logical
provider call with bounded exponential backoff. The successful logical receipt
retains every failed transport attempt in `transport_retries`; an exhausted or
non-transient failure remains `success: false`. Any checkpoint containing a
failed logical call is quarantined as `.failed-*` and replayed from the last
clean checkpoint instead of advancing canonical status. Each physical request
has a 90-second client timeout by default; `GA_PROVIDER_TIMEOUT_SECONDS` is an
explicit override.

The legacy task-decomposition helper intends to retry malformed model output
five times, but its validator accepts every nonempty response before cleanup;
an otherwise successful response can therefore crash the worker while parsing
a missing or nonnumeric duration field. For this prompt only, the runtime
overlay first keeps the raw output when upstream can parse it. On a parser-shape
failure (`IndexError`, `TypeError`, or `ValueError`), it removes commentary and
keeps formatted duration rows in response order, bounded by the requested total,
before passing them through the unchanged upstream cleanup. The raw provider
response remains in the receipt. Output with no parseable rows is requested
again up to the original five-attempt budget; exhaustion still raises, causing
the checkpoint and its receipt to be quarantined and replayed from the last
durable state.

The runtime overlay also contains one narrow compatibility correction for the
legacy action-arena prompt. Upstream asks for `{arena}` but removes only the
closing brace before looking up the arena. The overlay strips response-only
braces, quotes, and whitespace, then matches case-insensitively to an exact
arena returned by the persona's spatial memory. Invalid output stays in the
current arena when that arena is accessible in the selected sector, otherwise
it uses the first accessible arena in upstream order. It can never return an
arena outside that accessible list. Every changed output is retained in a
credential-free per-checkpoint JSONL compatibility receipt.

## Run and resume

Prepare the identical history seed once:

```bash
.venv/bin/python run_campaign.py \
  --upstream /tmp/generative_agents \
  --output outputs/exp10-5 \
  --mode seed
```

Launch or resume all three arms as detached processes:

```bash
.venv/bin/python launch_campaigns.py \
  --upstream /tmp/generative_agents \
  --output outputs/exp10-5 \
  --python .venv/bin/python
```

Each arm saves after 360 steps (one virtual hour). A status file is updated
atomically only after the simulation state and compressed provider receipt are
durable. Restarting the launcher resumes from that checkpoint. The day-one
checkpoint and final state are retained; superseded hourly storage copies are
removed after the next checkpoint succeeds.

Run offline tests with:

```bash
python -m pytest tests
```

Generated campaigns belong under `outputs/` and are ignored until a completed,
validated evidence package is deliberately selected for retention.
