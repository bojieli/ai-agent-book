# 对照记忆系统的完整处理链

用户请助理查一笔租车预订。助理报对了预订确认号，却告诉用户，之前的对话没提到公司折扣码。实验记录里，检索明明命中了相关材料。这两个结果怎么会同时出现？

沿着一条回答往回查，先看系统存下了什么，再看它取回了哪些片段，最后看助理怎样使用这些材料。本目录有两项实验，共用第三章的 60 个用例。

| 想回答的问题 | 正文 | 运行时使用的参数 |
| --- | --- | --- |
| 把记忆整理成卡片、按需检索原对话，或把两者结合，哪条路径更适合任务？ | 实验 7-4 | `7-4` |
| 固定任务后，更换嵌入模型、重排器或回答模型会有什么影响？ | 实验 7-12 | `7-11`（程序及历史文件沿用旧编号） |

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

JSON 卡片、RAG 和混合路径使用不同表示与检索方式。每个用例应独立建立状态，避免上一题的信息泄漏到下一题。模型裁判还需要校准，才能知道分数与人工判断是否一致。

每次运行都记录任务是否成功、步数、工具调用、延迟、token 用量和成本，并保留检索排名与模型裁判的逐项评分。实验 7-3 的[共用评分框架](../../chapter3/user-memory-evaluation/)给事实正确性、完整性、关系判断和主动性各评一个档次，另外检查回答是否编造事实。前两项在文件里叫 `precision` 和 `recall`，应与检索阶段按相关片段数计算的指标分开阅读。

### 先比较记忆系统，再比较系统组件

实验 7-4 对相同的 60 个用例分别构建三种系统。Advanced JSON Cards 用模型抽取来源、人物关系、精确事实、时间状态和歧义，所有卡片直接进入回答上下文；RAG 将原始对话按完整轮次切分，强制调用 `search_memory`，可重排后用 top-5 片段回答；Hybrid 只常驻明确标成 `memory_tier: core` 的卡片，其他事实保留在原对话中，由 Agent 决定是否检索。

实验 7-12 再组合嵌入、重排器与主模型。固定问题基准的 `fixed_query_*` 指标用于减少主模型改写查询造成的干扰；真实 Agent 轨迹另行测量，允许初次检索后最多三次追问，因此工具次数和步数确实反映运行差别。

<a id="learning-1"></a>

## 准备环境与输入

如果只想检查一条检索轨迹，可先读上面的归档。若要生成自己的报告，`live_config.yaml` 可先试少量配置；检验更换嵌入、重排与主模型的影响时，再按下面的完整矩阵准备后端。

### 配置完整矩阵与小规模子集

`default_config.yaml` 描述完整矩阵，`live_config.yaml` 是已验证账号可用的开发子集。不要用子集结果代替完整矩阵。先安装依赖、复制配置并设置环境变量；报告中只保存脱敏状态，不保存 Key。

```bash
cd chapter7/user-memory-system-evaluation
python -m pip install -r requirements.txt
cp env.example .env
```

2026-07-31 的完整运行记录了四项替换：余额不足的 SiliconFlow BGE-M3 改由 OpenRouter 提供同一模型；无额度的 OpenAI embedding 同样改走 OpenRouter；Ark 的 Doubao embedding 端点不可用，改为 `qwen/qwen3-embedding-8b`；不可访问的 BGE cross-encoder 改为 `doubao-semantic` LLM 重排。

最后一项改变了重排器类型，因此结果实际比较的是无重排、豆包 LLM 重排和 Kimi LLM 重排，不能声称完成了 cross-encoder 对照。

运行前可只检查完整配置的端点。这会真实调用聊天、嵌入和重排路径，并记录脱敏错误：

```bash
python probe_backends.py --config default_config.yaml \
  --output results/full_matrix_backend_readiness.json
```

<a id="learning-2"></a>

## 按照步骤完成实验

先选一条案例，阅读对话、问题与评分依据。配置后运行单题路径，检查实际建立的记忆和回答时取出的内容。理解后再比较多种配置，最后汇总不同层次案例的成绩。

### 用单个用例检查流程，再运行全量

先用带 `--test-id` 的命令观察一条用例：原始记忆如何写入、如何检索、怎样回答，以及评分证据来自哪里。这些结果标记为 `smoke`。

```bash
python experiment.py 7-4 --config live_config.yaml \
  --test-id layer1_01_bank_account \
  --output results/live_7_4_layer1.json

python experiment.py 7-11 --config live_config.yaml \
  --test-id layer1_01_bank_account \
  --output results/live_7_11_matrix_layer1.json
```

确认流程后，再运行默认的 60 个用例。以下分别对应系统比较和组件矩阵：

```bash
python experiment.py 7-4 --config default_config.yaml \
  --output results/experiment_7_4.json

python experiment.py 7-11 --config default_config.yaml \
  --output results/experiment_7_11.json
```

长任务可用 `run_full.py`。它先保存单用例检查点再计数，恢复有效检查点，并只合并直接运行记录；readiness 文件减少对已知不可用端点的重复调用，但对应矩阵单元仍以 `status: error` 保留。

```bash
python run_full.py 7-4 --config live_config.yaml --workers 4 \
  --output results/full_7_4_60_cases.json

python run_full.py 7-11 --config default_config.yaml --workers 4 \
  --readiness results/full_matrix_backend_readiness.json \
  --output results/full_7_11_60_case_matrix.json
```

<a id="learning-3"></a>

## 分析结果与形成判断

一套系统得分低，可能是提取丢失、检索失败或回答误用。沿完整轨迹定位，比直接更换回答模型更有依据。裁判不一致的案例应回到评分规则核对。

### 同时读任务分数、检索指标与成本覆盖

共享评分器看到权威原始材料，分别评价 precision、recall、reasoning、proactivity，并单独给出幻觉否决。成功要求前三项至少达到 good（3/4）且无幻觉否决，`reward` 仍保留部分得分。检索用 hit@5、recall@5 与 MRR 描述；`interaction_analysis` 再分析重排器在不同嵌入和主模型条件下是否有价值，以及主模型是否在检索不完整时仍答对。

提供商错误单独记为 `status: error`，不计作模型任务失败。只有 60 个独立用例和全部配置单元完成，`run_scope` 才是 `full`；筛选运行是 `smoke`，全量调用中仍有提供商错误则是 `incomplete-full-suite`。成本还应检查 `unpriced_tokens`，未知价格不等于零成本。

回到开头的租车题。打开[这道题的运行记录](results/checkpoints/7_11/default_config/layer1_07_car_rental.json)，找到嵌入模型为 `mistral`、重排器为 `none`、主模型为 `doubao` 的组合。它的 `retrieval_hit_at_5` 为 1，说明前五个片段里有相关材料。助理报出了确认号，却断言原对话没有折扣码。裁判对照原文找到了折扣码，完整性给了 2 分，还触发了幻觉否决。单凭一次检索命中，既不能断定两个号码都进了回答上下文，也不能断定助理会把它们用对。

实验 7-4 的历史汇总记载了 180 条轨迹（60 个用例，各跑三种系统），并报告所有调用均已计价。历史文件名为 `results/full_7_4_60_cases_costed.json`，当前仓库未收录这份完整报告；上面的 `run_full.py 7-4` 命令可生成自己的记录。`build_73_evidence.py` 可从已有轨迹派生实验 7-3 的评分证据。

实验 7-12 的[完整矩阵](results/full_7_11_60_case_matrix.json)收录了 1,440 条轨迹（4 种嵌入配置 × 3 种重排配置 × 2 个主模型 × 60 道题）。运行前，9 项后端就绪检查全部通过；原计划的 BGE-M3、OpenAI 和豆包嵌入配置中，有的更换了服务商，有的替换了模型，实际使用的后端及替代理由见[配置说明](#backend-substitutions-2026-07-31)。在本目录运行 `python3 validation/verify_full_matrix_20260731.py`，可以离线核对每道题是否跑齐 24 种组合、有无提供商错误、是否还有用量未计价。

离线测试：

```bash
pytest -q ../../chapter3/user-memory-evaluation/test_structured_rubric.py test_experiment.py
```

### 检查自己的解释

两个系统答案相同，但一个读取了大量无关历史，评价中还应包含哪些成本指标？

## English

The historical identifier 7-11 below corresponds to Experiment 7-12 in the current Chinese chapter. The 7-4 costed report named below is referenced in the original run notes and is absent from this checkout.

# Experiments 7-4 and 7-11: end-to-end user-memory evaluation

This companion runs memory systems. It does not score canned response files.
It reuses the 60 cases in `chapter3/user-memory-evaluation/test_cases` and
records an API-backed trajectory for every `(case, configuration)` cell.

← [Chapter 7 index](../README.md) · [Book acceptance criteria](../../book/chapter7.md)

## What is implemented

### Experiment 7-4: Advanced JSON Cards vs RAG vs hybrid

For every one of the same 60 cases, the runner independently builds and runs:

| System | Ingestion and answering path | Steps/tools |
| --- | --- | --- |
| Advanced JSON Cards | An LLM extracts structured cards containing provenance, person/relationship, exact facts, temporal status, and ambiguity; all cards stay in the answer context. | One answer step, zero retrieval tools |
| RAG | Raw conversations are split on complete turns, embedded into a dense index, searched through an actual `search_memory` tool call, optionally reranked, then answered from top-5 chunks. | Forced retrieval plus answer |
| Hybrid | Only cards explicitly classified `memory_tier: core` stay resident; supporting/episodic facts remain in raw conversations while the main Agent decides whether to call `search_memory`. | One or two steps; tool use is observed, not hard-coded |

The JSON report records success/reward, rubric dimensions, hallucination veto,
steps, tool calls, latency, input/output tokens, cost and price-coverage gaps.
`success` requires at least `good` (3/4) on precision, recall and reasoning plus
no hallucination veto; `reward` still preserves partial credit.
`failure_boundaries` lists failed cases and per-dimension weaknesses for each
system/layer, plus a paired hybrid-synergy/regression analysis.

### Experiment 7-11: full component matrix

`default_config.yaml` sweeps all three selection points from the book:

- embeddings: BGE-M3, OpenAI, and an independently hosted Mistral control,
  plus a documented Qwen3 substitution for the unreachable Doubao embedding
  (see "Backend substitutions" below);
- rerankers: no-reranker baseline, a Doubao semantic reranker (documented
  substitution for the unreachable BGE cross-encoder), and the Kimi semantic
  reranker;
- main models: Kimi and Ark/Doubao under an identical retrieval contract.

### Backend substitutions (2026-07-31)

Acceptance is tied to equivalent providers/models, not to one vendor's
official API. Every substitution is recorded in `default_config.yaml` and in
the sanitized receipts `results/candidate_backend_probes_20260731.json` and
`results/full_matrix_backend_readiness_20260731.json`:

- SiliconFlow's key is valid but the account balance is 0 (HTTP 402), so
  `bge-m3` runs the identical `baai/bge-m3` model via OpenRouter.
- The direct OpenAI account has no credits (HTTP 429), so `openai-small`
  runs the identical `openai/text-embedding-3-small` via OpenRouter.
- Ark embeddings require a console-provisioned endpoint id and every public
  Doubao embedding model name returns 404 on this account, so the Doubao
  embedding slot is honestly replaced by `qwen/qwen3-embedding-8b` via
  OpenRouter (the closest Chinese-provider multilingual embedding).
- No cross-encoder reranker is reachable (SiliconFlow balance 0; DashScope
  gte-rerank returns 403 AccessDenied with this international key), so the
  BGE cross-encoder slot is honestly replaced by `doubao-semantic`, a second
  LLM reranker on the Doubao chat model. The matrix therefore compares
  none / Doubao-LLM / Kimi-LLM reranking; no cross-encoder is claimed.

A source-aware retrieval judge selects the relevant chunk IDs before the matrix
run. Each cell is then measured with hit@5, recall@5 and MRR, as well as task
success, rubric score, steps, tool calls, latency and cost. The report does not
rank components in isolation: `interaction_analysis` calculates reranker value
conditional on embedding and main model, flags observed reranker redundancy,
and measures whether stronger main models succeed despite incomplete retrieval.

Embedding/reranker quality is also measured with an identical fixed user-query
benchmark in every cell (`fixed_query_*`), avoiding main-model query wording as
a confound. The production Agent trajectory is measured separately: retrieval
is mandatory, but the main model may make up to three follow-up searches, so
steps/tool calls are real efficiency signals instead of constants.

Provider failures become explicit `status: error` matrix records and never count
as task failures. This prevents an unavailable account or endpoint from silently
changing a quality comparison.

The report has a machine-readable `run_scope`. A run is marked `full` only when
all 60 distinct case IDs and all configured cells completed. Filtered evidence
is always marked `smoke`; a 60-case invocation with provider errors is marked
`incomplete-full-suite`.

## Experiment 7-3 prerequisite

The shared judge in [`chapter3/user-memory-evaluation`](../../chapter3/user-memory-evaluation/)
is now the structured Experiment 7-3 judge. It sees the authoritative source and
returns four grades for precision, recall, reasoning, and proactivity, with
evidence and boundary cases. A separate hallucination result is a hard veto.
The runner here uses that judge for 7-4 and 7-11 task success.

The completed 7-4 campaign also provides the full execution evidence for 7-3:
all 60 distinct cases across three systems produced 180/180 real structured
judgments. [`results/full_7_3_structured_rubric_evidence.json`](results/full_7_3_structured_rubric_evidence.json)
validates every saved record against the four-dimension contract and independent
hallucination veto, and content-hashes the immutable source report. It is built
by `python build_73_evidence.py`; the derivation performs no model calls and
does not add or change any score.

## Install and configure

```bash
cd chapter7/user-memory-system-evaluation
python -m pip install -r requirements.txt
cp env.example .env
```

Credentials are read only from environment variables; reports never contain
keys. `default_config.yaml` is the full book matrix. All matrix components
carry dated list prices so `unpriced_tokens` stays zero; the report exposes
`unpriced_tokens` so incomplete cost accounting cannot look like a zero-cost
system.

## Run

The default is all 60 cases:

```bash
python experiment.py 7-4 --config default_config.yaml \
  --output results/experiment_7_4.json

python experiment.py 7-11 --config default_config.yaml \
  --output results/experiment_7_11.json
```

Use filters only for smoke tests:

```bash
python experiment.py 7-4 --config live_config.yaml \
  --test-id layer1_01_bank_account \
  --output results/live_7_4_layer1.json

python experiment.py 7-11 --config live_config.yaml \
  --test-id layer1_01_bank_account \
  --output results/live_7_11_matrix_layer1.json
```

Restart-safe complete campaigns:

```bash
python run_full.py 7-4 --config live_config.yaml --workers 4 \
  --output results/full_7_4_60_cases.json

python run_full.py 7-11 --config default_config.yaml --workers 4 \
  --readiness results/full_matrix_backend_readiness.json \
  --output results/full_7_11_60_case_matrix.json
```

`run_full.py` writes one case checkpoint before counting it, resumes valid
checkpoints, and merges only direct records. A readiness file avoids repeatedly
calling a provider already proven unavailable while still emitting every blocked
matrix cell as `status: error`.

`live_config.yaml` is a known-working development-account subset. It uses real
Mistral/Codestral embeddings, no-reranker and Kimi reranker, and Kimi/Doubao main
models. It does not replace the full BGE/OpenAI/Doubao matrix.

Probe the full configuration without running 60 cases:

```bash
python probe_backends.py --config default_config.yaml \
  --output results/full_matrix_backend_readiness.json
```

The probe calls the actual configured chat, embedding, and reranking paths and
stores sanitized status/error evidence. Keys are never written.

## Tests and checked-in live evidence

```bash
pytest -q ../../chapter3/user-memory-evaluation/test_structured_rubric.py test_experiment.py
```

- `results/live_7_4_core_hybrid_layer1.json`: three complete layer-1 7-4 trajectories
  using the exact core-card hybrid path.
- `results/full_7_4_60_cases_costed.json`: canonical completed Experiment 7-4
  campaign—60 distinct cases × three systems, 180/180 real trajectories, zero
  trajectory errors, `validation_scope: full`, and complete native-currency cost
  coverage. Its top-level and completion status are both `complete`.
- `results/live_7_11_matrix_layer1.json`: current-code live factorial 7-11 smoke
  (generated by the command above when present).
- `../../chapter3/user-memory-evaluation/results/live_7_3_layer1.json`: live Kimi structured-rubric result.
- `../../chapter3/user-memory-evaluation/results/live_7_3_hallucination_veto.json`:
  live Kimi proof that one unsupported number forces reward to zero.
- `results/full_matrix_backend_readiness.json`: sanitized full-matrix endpoint probe.
- `results/full_matrix_backend_readiness_20260731.json`: sanitized 9/9 readiness
  probe under the documented substitutions; `results/candidate_backend_probes_20260731.json`
  keeps the per-candidate rejection receipts (SiliconFlow 402 balance, OpenAI 429,
  Ark embedding 404s, DashScope rerank 403) that justify each substitution.

These evidence files contain synthetic benchmark answers, metrics and model
names, but no credentials or complete source conversations. Experiment 7-4 is
complete only through the canonical full report named above; the `live_*` files
remain smoke evidence and must not be substituted for it.

Experiment 7-11 is **complete**: the full 4×3×2×60 matrix campaign finished with
1,440/1,440 real trajectories, zero error records, and zero unpriced usage in
`results/full_7_11_60_case_matrix.json` (top-level and completion status both
`complete`), executed under the documented backend substitutions above
(`results/full_matrix_backend_readiness_20260731.json`).
`validation/verify_full_matrix_20260731.py` independently rechecks case/cell
coverage, trajectory cleanliness, metric finiteness, pricing coverage, and the
interaction analysis (ALL CHECKS PASSED).
None of the earlier blockers changed the completed 7-4 status.
