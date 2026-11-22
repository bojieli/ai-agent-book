# Agent End-to-End Cost Analysis / Agent 任务端到端成本分析（实验 7-10）

用户只提了一次退款申请，客服助理却要查订单、看物流、核对政策，再组织答复。为什么用户只问了一次，账上却有八次模型调用？翻开一轮的用量明细，先算清缓存命中怎样计价，再看八轮加起来能省多少。

[English](#english)

<a id="learning-0"></a>

## 理解问题与方法

每轮请求都会把一部分历史再次送给模型。提供商返回的 `prompt_tokens` 包括命中缓存的输入，所以先从中减去 `cached_tokens`，余数按普通输入价计算。回复另按输出价计。工具返回的文字进入后续提示时已经算在输入中；统计它占了多少，是为了查明费用来源，再加一次就重复计费了。

<a id="learning-1"></a>

## 准备环境与输入

仓库里的[退款任务轨迹](sample_trace.json)保存了四种设置各八轮的用量。初次学习可以用 Python 标准库复算，无需模型账号。四组用的是同一套预设订单、物流和政策资料，模型的输出长度和缓存命中量则可以不同。

<a id="learning-2"></a>

## 按照步骤完成实验

在本实验目录运行下面的代码。取同时启用稳定前缀和压缩的 `both` 组，从第一轮查订单开始核对：

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path

trace = json.loads(Path("sample_trace.json").read_text())
group = next(row for row in trace["scenarios"] if row["key"] == "both")
price = trace["pricing"]
def call_cost(span):
    cached = span["cached_tokens"]
    ordinary = span["prompt_tokens"] - cached
    return (ordinary * price["input"] + cached * price["cached"]
            + span["completion_tokens"] * price["output"]) / 1_000_000

print("第一轮费用：", format(call_cost(group["spans"][0]), ".8f"))
print("八轮合计：", format(sum(call_cost(span) for span in group["spans"]), ".8f"))
PYTHON
```

第一轮输入 1,056 个 token，其中 1,024 个命中缓存，只剩 32 个按普通输入计价；输出 139 个。代入归档单价（每百万 token 分别为 0.15、0.075、0.60 美元），这一轮是 0.00016500 美元。八轮相加才是这组的一次任务费用。下文按步骤列出哪一轮最贵，并用 p50、p95、p99 描述单步成本的分布。

离线命令可以改价格、重算成本构成；在线命令用 OpenAI 兼容接口重新生成答复。运行器默认模型是 `gpt-5.6-luna`，而下面的归档样例使用 `gpt-4o-mini`。为了复算表中的数值，离线命令显式选用样例的模型预设。

#### 文件

| 文件 | 说明 |
|------|------|
| `config.py` | 模型与价格：`Pricing` 单价对象 + 常见 OpenAI 模型单价预设，token→成本换算 |
| `tracer.py` | 自建轻量 tracing：包裹每次 LLM 调用记录 token/缓存/时延/成本；成本构成拆解、单步成本分布、按步骤拆解表；支持从录制用量离线复算（`from_records`）|
| `agent.py` | 多轮客服退款 Agent 任务；`run_scenario(kv_cache, compress)` 把两个开关正交组合成 2×2 场景，并用 tiktoken 估算「工具返回注入」token |
| `demo.py` | 命令行入口（argparse）：在线跑真实模型 / 离线复算；选择 A/B 场景、模型单价、输出文件 |
| `sample_trace.json` | 一次真实运行录下的四个场景逐步 token 用量（离线模式的输入，成本按当前单价重算）|
| `tests/` | 离线 pytest 回归测试：trace 解析与 usage 计费容错 |
| `requirements.txt` / `env.example` | 依赖与环境变量示例 |

#### 运行

```bash
# 从仓库根目录进入实验目录
cd chapter7/agent-cost-analysis
python3 -m venv .venv
source .venv/bin/activate
# Windows PowerShell：.\.venv\Scripts\Activate.ps1；cmd：.venv\Scripts\activate.bat
python -m pip install -r requirements.txt

# 离线复算四组历史结果
python demo.py --offline --scenario all --model gpt-4o-mini

# 重新调用模型时，先配置 OPENAI_API_KEY 或 OPENROUTER_API_KEY
python demo.py --live
```

在线默认运行朴素组和同时启用两项优化的组；选 `--scenario all` 会运行全部四组，启用预热时另有预热调用。

#### 测试

自动化测试均为离线回归测试，不需要 API Key。

```bash
# 在已激活的实验环境中
python -m pip install pytest
python -m pytest tests
```

##### 命令行参数（`python demo.py --help`）

| 参数 | 说明 |
|------|------|
| `--live` / `--offline` | 在线真实调用（默认）/ 离线从 trace 文件复算（无需 key）|
| `--scenario NAME` | `ab`(默认=naive+both) / `all`(2×2 四组) / 逗号分隔子集 `naive,kv,compress,both` |
| `--trace FILE` | 离线读取的 canned trace，默认 `sample_trace.json` |
| `--save-trace FILE` | 在线跑时把真实 token 用量落盘，供之后 `--offline` 复算 |
| `--model NAME` | 模型名（决定默认单价预设：`gpt-4o-mini`/`gpt-4o`/`gpt-4.1-mini`/`gpt-4.1`）|
| `--price-input/-cached/-output` | 覆盖三档单价（每百万 token 美元）|
| `--no-warmup` | 关闭 KV-cache 组的前缀预热（默认预热以稳定命中缓存）|
| `--output FILE` | 把成本拆解结果（含成本构成/分布/逐步用量）写成 JSON |

> **不改任何参数直接 `python demo.py`，行为与之前一致**：在线跑 A(朴素) 与 B(优化) 两组并打印拆解 + A/B 对比表。

#### A/B 四种策略（完整 2×2）

同一个 8 轮客服退款任务（查订单 → 查物流 → 查退款政策 → 查知识库 → 风控 → 发起退款 → 通知 → 关单），四组做的是**同样的逻辑工作**，只在上下文构造上不同——因此成本差异纯粹来自「是否 KV-cache 友好」与「是否压缩上下文」两个正交开关：

| 场景 | KV-cache | 压缩 | 上下文构造 |
|------|:--:|:--:|------|
| `naive` A 朴素 | ✗ | ✗ | 每轮 system 前塞随机 session 头（破坏前缀）+ 历史工具返回原样带全 |
| `kv` 仅缓存 | ✓ | ✗ | 稳定长前缀（system 逐字节不变）+ 历史不压缩 |
| `compress` 仅压缩 | ✗ | ✓ | 前缀不稳定 + 仅最近 2 轮保留完整工具返回、更早压成一句话摘要 |
| `both` B 优化 | ✓ | ✓ | 稳定长前缀 + 上下文压缩（两个杠杆叠加）|

> 为聚焦「输入侧」两个杠杆，四组都用 `temperature=0` 且限制输出长度（`max_tokens=160`），让输出 token 成本近似为四组相等的固定项，避免模型生成长度的随机波动干扰对比。
>
> 工具环境是「受控」的（工具返回内容预设，真实系统里来自订单/物流/知识库后端），模型调用提供了逐轮 token 用量。表中的美元金额由这些用量和实验单价算出，便于读者更换假设重算。

#### 真实运行输出（gpt-4o-mini）

以下为一次真实运行（`python demo.py --scenario all`）的输出，`sample_trace.json` 即由该次运行落盘、供 `--offline` 复现。

##### (a) 单次任务成本拆解：按步骤 + 按成本构成 + 分布

```
===== 成本拆解: A 朴素(无缓存/无压缩)（单次任务全链路拆解） =====
步骤       工具/动作                   输入tok    缓存tok    工具tok    输出tok    时延(s)        成本($)
---------------------------------------------------------------------------------------
turn-1   query_order              1113        0      276      104     3.15     0.000229
turn-2   query_logistics          1807        0      829       99     2.09     0.000330
turn-3   check_refund_policy      2154        0     1046      139     2.69     0.000406
turn-4   query_knowledge_base     2564        0     1287      160     2.92     0.000481
turn-5   query_user_history       2863        0     1389      136     2.69     0.000511
turn-6   issue_refund             3123        0     1490      160     3.07     0.000564
turn-7   send_notification        3408        0     1579      160     3.09     0.000607
turn-8   close_ticket             3668        0     1648      160     2.50     0.000646
---------------------------------------------------------------------------------------
合计                               20700        0     9544     1118    22.20     0.003776

最贵的一步 → turn-8 / close_ticket: $0.000646（占总成本 17.1%）
成本构成:
  未缓存输入     20700 tok  $0.003105  (82.2%)
  缓存输入           0 tok  $0.000000  (0.0%)
  输出            1118 tok  $0.000671  (17.8%)
  其中「工具返回注入」累计输入 9544 tok （同一份工具返回在后续每轮被反复计费）
单步成本分布(n=8): 均值 $0.000472  p50 $0.000481  p95 $0.000646  p99 $0.000646

===== 成本拆解: B 优化(KV缓存+压缩)（单次任务全链路拆解） =====
步骤       工具/动作                   输入tok    缓存tok    工具tok    输出tok    时延(s)        成本($)
---------------------------------------------------------------------------------------
turn-1   query_order              1056     1024      276      139     2.41     0.000165
turn-2   query_logistics          1781        0      829      112     2.18     0.000334
turn-3   check_refund_policy      2143     1024     1046      151     2.56     0.000335
turn-4   query_knowledge_base     2310        0     1052      160     3.03     0.000442
turn-5   query_user_history       2060     1024      635      160     2.48     0.000328
turn-6   issue_refund             2143     1024      551      160     2.71     0.000341
turn-7   send_notification        2188     1024      430      160     2.79     0.000347
turn-8   close_ticket             2354     1024      429      122     2.38     0.000349
---------------------------------------------------------------------------------------
合计                               16035     6144     5248     1164    20.54     0.002643

最贵的一步 → turn-4 / query_knowledge_base: $0.000442（占总成本 16.7%）
成本构成:
  未缓存输入      9891 tok  $0.001484  (56.1%)
  缓存输入        6144 tok  $0.000461  (17.4%)
  输出            1164 tok  $0.000698  (26.4%)
  其中「工具返回注入」累计输入 5248 tok （同一份工具返回在后续每轮被反复计费）
单步成本分布(n=8): 均值 $0.000330  p50 $0.000335  p95 $0.000442  p99 $0.000442
```

可以看到：朴素组 A 的输入 token 随轮次从 1113 一路涨到 3668（上下文累积效应，最后一步最贵），「工具返回注入」累计吃掉 9544 输入 token；优化组 B 的输入 token 被压缩策略压住（末轮 2354 而非 3668，工具注入累计降到 5248），且多数轮次持续命中 1024 缓存 token，缓存输入把整块费用打了 5 折。

##### (b) 完整 2×2 A/B 对比

```
===== A/B 成本对比（同一个 8 轮客服退款任务）=====
方案                             总输入tok      缓存tok      缓存率    输出tok       总成本($)       vs基线
------------------------------------------------------------------------------------------
A 朴素(无缓存/无压缩)                   20700          0     0.0%     1118     0.003776         基线
KV 仅缓存(稳定前缀/不压缩)                20386      13568    66.6%     1112     0.002707     -28.3%
仅压缩(前缀不稳定/摘要)                   16177          0     0.0%     1147     0.003115     -17.5%
B 优化(KV缓存+压缩)                   16035       6144    38.3%     1164     0.002643     -30.0%
------------------------------------------------------------------------------------------

重点对比：A 朴素(无缓存/无压缩)  →  B 优化(KV缓存+压缩)
  总 token:   A=21818  →  B=17199   减少 4619 (21.2%)
  缓存 token: A=0  →  B=6144   （B 靠稳定前缀命中缓存）
  总成本:     A=$0.003776  →  B=$0.002643   降低 $0.001133 (30.0%)
  成本倍率:   A 是 B 的 1.43 倍
```

结论（读出两个杠杆各自与叠加的贡献）：
- **仅 KV-cache**：不改上下文长度，只靠稳定前缀让重复的系统提示/工具定义/历史轮次按缓存价计费，缓存率冲到 66.6%，端到端成本就降了 **28.3%**——本例中它是单个最有效的杠杆。
- **仅压缩**：把旧轮次工具返回压成摘要，总输入 token 从 20700 降到 16177（约 −22%），端到端成本降 **17.5%**；但因为前缀不稳定，缓存率为 0。
- **两者叠加（B 优化）**：输入 token 最少、又能命中缓存，端到端总成本降 **30.0%**（A 是 B 的 1.43 倍）。单看输入侧成本，降幅落在书中「KV Cache 可降低 30%-60% 输入 token 成本」的经验区间内。

> 注意 KV 与压缩并非简单相加：压缩缩短了历史，可被缓存的「历史轮次」也随之变少，所以 B 的缓存 token（6144）反而少于「仅 KV」（13568）。这正是评估的价值——两个优化叠加时要实测协同效应，而不是把各自的收益直接相加。

#### 离线复算（无需 API key）

`sample_trace.json` 存的是上面这次真实运行的**逐步 token 用量（实测值）**；离线模式只做「按单价重算成本」这一步纯离线数学，因此无需 key 即可复现全部表格，还能一键换算到其它模型定价：

```bash
python demo.py --offline --scenario all --model gpt-4o-mini  # 用样例单价复算
python demo.py --offline --scenario all --model gpt-4o  # 同一份 token 用量，换 gpt-4o 单价重算
python demo.py --offline --price-input 0.20 --price-cached 0.10 --price-output 0.80
```

为什么换成表里的 `gpt-4o` 预设后仍然节省 30.0%？这两个预设恰好把三档价格按同一倍数放大，A 从 0.003776 美元变为 0.062930 美元，B 从 0.002643 美元变为 0.044047 美元，比例自然不变。试着只改一档：让缓存输入也按每百万 0.15 美元计价，普通输入与输出价格保持原值。用同一份轨迹重算，A 仍是 0.00377580 美元，B 变为 0.00310365 美元，节省比例降到 17.8%。这才看得出缓存折扣对这项选择有多大影响。

#### 注意事项

- 具体数字每次在线运行会有小幅波动：OpenAI 的 prompt cache 是**尽力而为**的（按约 128 token 的块缓存、约 5–10 分钟过期、偶尔未命中），因此某些轮次可能出现 `cached_tokens=0`（如上面 B 组的 turn-2/turn-4）。`demo.py` 在正式计量前会先对 KV-cache 组跑一次「预热」把稳定前缀写入缓存，让命中更稳定；`--no-warmup` 可关闭。
- 单价预设见 `config.py` 的 `PRICING_PRESETS`。这里的历史样例按每百万 token 输入 0.15、缓存输入 0.075、输出 0.60 美元计算。用 `--model` 可选择预设，用 `--price-input`、`--price-cached`、`--price-output` 可分别指定三档价格。
- 「工具返回注入」token 用 tiktoken 按当前模型的编码器离线估算（统计每轮输入里工具返回文本占多少 token），用于回答书中「一次工具返回可能占 2000-5000 token，且在后续每轮被反复计费」这一放大因素。
- 凭据选择由 `config.make_client_and_model` 决定：请求 `gpt-5` 开头的模型且配置了 OpenRouter 时优先走 OpenRouter；其余情况优先用 OpenAI，只有 OpenRouter 凭据时则走其兼容端点。离线复算不需要凭据。

<a id="learning-3"></a>

## 分析结果与形成判断

换一份轨迹，组合起来最省钱的办法会变吗？打开 [Kimi K2.5 的逐轮记录](runs/exp7-9-kimi25-20260730-v2/report.json)，只比较稳定前缀的两组。下面按该次运行保存的三档单价复算，金额单位为美元。

| 八轮合计 | 普通输入 token | 缓存输入 token | 输出 token | 模型费用 |
|---|---:|---:|---:|---:|
| 只稳定前缀（`kv`） | 4,729 | 14,779 | 1,266 | 0.008254 |
| 稳定前缀并压缩历史（`both`） | 7,180 | 8,123 | 1,280 | 0.009058 |

可以把两行相减来解释结果。缓存输入少了 6,656 个，普通输入却多了 2,451 个，输出也多了 14 个。用归档里 `pricing` 的三档单价分别乘这三项差额，合计多花约 0.000804 美元。总输入确实缩短了 4,205 个 token，只看总输入长度会漏掉两档输入的价差。

正式表格只统计每组记录下来的八轮。在线脚本默认给启用缓存的组先跑一次完整预热，预热用量没有写入这八轮。若要回答“为了完成一笔退款，服务总共花了多少钱”，还要计入预热、失败尝试和重试的开销，并用实际办成的退款笔数作分母。本例用预设工具返回演示成本拆解，没有验证银行或商家实际退款。

### 检查自己的解释

如果减少一次调用却使任务失败率上升，平均每个成功任务的成本会怎样变化？

## English

This project performs a full cost decomposition for a multi-turn agent workflow (refund handling), including input/cache/output tokens, latency, and cost distribution. It enables practical measurement of where costs come from and how optimization strategies affect total spend.

### What it does

The benchmark runs a fixed 8-turn customer refund scenario and records every LLM call with a lightweight tracing layer:
- token usage (prompt, cached prompt, output)
- latency
- model cost by pricing table

It then reports:
- per-step cost breakdown
- cost component breakdown (non-cached input / cached input / output)
- p50/p95/p99 for per-step cost
- full 2×2 A/B comparison between optimization levers

The two levers are:
- **KV-cache friendliness**: keep a stable prefix to maximize cache hits
- **Context compression**: summarize long tool outputs for earlier turns

### Default model and API behavior

- Default model: `gpt-5.6-luna`.
- Preferred credentials: `OPENAI_API_KEY`, fallback to `OPENROUTER_API_KEY` (`gpt-*` remapped to `openai/*`).
- If OpenRouter keys exist for `gpt-5.x`, it is preferred due to authentication requirements.
- Offline mode is supported via `sample_trace.json` so all tables can be recomputed without API calls.

### Files

| File | Purpose |
|---|---|
| `config.py` | pricing model definitions and pricing presets |
| `tracer.py` | tracing helper and cost decomposition/aggregation |
| `agent.py` | 8-turn refund agent with `run_scenario(kv_cache, compress)` |
| `demo.py` | CLI entry for online/offline runs |
| `sample_trace.json` | captured 2×2 scenario token records for offline recomputation |
| `tests/` | offline pytest regressions for trace parsing and usage accounting |
| `requirements.txt` / `env.example` | dependencies and environment templates |

### Run

```bash
# From the repository root: use the shared Chapter 6 environment
uv sync --locked --python 3.12 --extra ch6

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch6]"

cd chapter7/agent-cost-analysis

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

export OPENAI_API_KEY=your-openai-api-key   # or OPENROUTER_API_KEY=your-openrouter-api-key
python demo.py
python demo.py --offline --scenario all
```

### Tests

Automated tests are offline and do not require API keys.

```bash
# From the repository root, include the dev extra for pytest:
uv sync --locked --python 3.12 --extra ch6 --extra dev

# pip testing fallback:
# python -m pip install -e ".[ch6,dev]"

cd chapter7/agent-cost-analysis
python -m pytest tests
```

### CLI options

| Argument | Meaning |
|---|---|
| `--live` / `--offline` | call real model (default) / recompute from trace |
| `--scenario` | `ab` (naive+both), `all` (four scenarios), or subset list |
| `--trace` | trace file for offline mode |
| `--save-trace` | persist observed token usage from online runs |
| `--model` | model name for price preset |
| `--price-input` / `--price-cached` / `--price-output` | override per-million-token prices |
| `--no-warmup` | disable prefix warmup for KV-cache scenario |
| `--output` | export full result JSON |

### A/B scenarios (2×2)

| Scenario | KV-cache | Compression | Context design |
|---|---|---|---|
| `naive` | no | no | random session header + full tool returns |
| `kv` | yes | no | stable long prefix |
| `compress` | no | yes | only keep last 2 turns full; older turns summarized |
| `both` | yes | yes | stable prefix + compressed history |

The task logic is identical across scenarios so differences isolate optimization effects.

### Interpretation

Empirical results show:
- KV-cache can produce large improvements when prefixes are stable.
- Compression lowers prompt growth while keeping functional behavior.
- Joint optimization usually gives best total cost, though cache gains and compression gains are not simply additive.

### Offline recomputation

Offline mode reads `sample_trace.json` and re-runs only cost arithmetic, enabling:
- quick replication without keys
- quick “what-if” with different model prices

### Notes

- Observed numbers can vary due to real API behavior and cache timing.
- Prompt cache is best-effort and may miss in some turns.
- Tool-return token estimate uses tokenizer counts against current model encoder.
- Key precedence: prefer `OPENAI_API_KEY`; fallback is automatic via OpenRouter for supported paths.

---
