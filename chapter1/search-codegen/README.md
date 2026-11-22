# 把搜索得到的信息交给代码计算

“两个城市相距多远”同时包含事实查询和数值计算。只让模型凭记忆作答，难以核对数据来源；只运行程序，又缺少输入数据。本实验把搜索与代码执行串起来，观察 Agent 怎样完成这类复合任务。

[English](#english)

[搜索材料怎样进入计算](#learning-0) · [检查请求与托管工具配置](#learning-1) · [对照直接计算与先澄清的任务](#learning-2) · [从服务端回执核对调用](#learning-3)

<a id="learning-0"></a>

## 搜索材料怎样进入计算

模型先决定需要哪些信息，再调用托管搜索和代码执行工具。搜索结果提供可追溯的数据，代码把数据转成可检查的计算。回答中的引用与计算过程应能对应起来，才能判断结论是怎样得到的。

从同一份[服务端回执](validation/runs/real_20260731T170529Z/receipts.json)读两道题。第一道给定十个东盟国家的首都，要求找出相距最近的一对；第二道要求分析比特币走势，起初没有指定数据源和指标。哪一道可以立即动手？在本实验目录运行下面的代码，只读归档，便能看到当时的区别。

```python
import json
from pathlib import Path

path = Path("validation/runs/real_20260731T170529Z/receipts.json")
record = json.loads(path.read_text())
run = next(run for run in record["turns"] if run["backend"] == "dashscope")
for n, turn in enumerate(run["api_turns"], start=1):
    calls = [item["type"] for item in turn["response"]["output"]
             if item["type"] in {"web_search_call", "code_interpreter_call"}
             and item.get("status") == "completed"]
    print(n, calls)
```

第一行各有一次搜索和代码执行。十座首都共有 45 种配对，托管 Python 算出吉隆坡与新加坡相距约 316.35 公里，与本地大圆距离计算一致。第二行是空列表：模型先向用户澄清比特币数据源和指标。打开该轮的最终消息，就能读到模型请用户补充的条件。第三行才是接续澄清后的三次搜索和四次代码执行，涉及 MA7、MA20、RSI14、MACD、区间收益、最大回撤和走势图。可对照该次请求的 `previous_response_id` 检查它接续了哪次响应。

这些回执来自 2026 年 7 月 31 日百炼 `qwen3.7-plus` 的 Responses API。官方 OpenAI 路线的 `gpt-5.6-sol` 请求当时返回 `credit_balance_exhausted`，相应配置与记录也保留下来。OpenRouter 在本实验中用于诊断。阅读自己的新运行时，先按后端和任务找对回执，再核对服务端完成的工具项及其 URL 引用。

### 搜索与计算分别提供什么证据

实验 1-3 使用 Responses API 的托管 `web_search` 与 `code_interpreter`。搜索负责取得带来源的信息，代码解释器负责执行计算；验证时需要看到提供商返回的已完成工具项与 URL 引用，不能只根据最终文字判断工具是否执行。

原文中的两个 JSON 请求保留了不同后端的具体形状。OpenAI 路线传入推理与文本详细程度设置；DashScope 路线使用流式响应，并保存最终 `response.completed` 对象。已有记录中，后者长时间不返回内容的非流式请求会被网关中断，因此“流式接收”和“结果是否完成”需要分别处理。

<a id="learning-1"></a>

## 检查请求与托管工具配置

可以先读下方归档，再用 `--dry-run` 查看客户端打算发送哪些工具定义。要取得新的执行结果，选择支持这两种托管工具的后端，并按下面的示例配置凭据。

### 先检查请求，再选择一个后端

下面保留完整配置和 CLI 示例。共享仓库环境应遵循根目录的 Python 3.11–3.13 约束；原文中 Python 3.9+ 指的是本目录早期单项目要求。先运行 `--dry-run` 核对请求内容，再使用自己有额度的后端完成首都距离任务。`--backend openrouter` 在这里是诊断路径，不会自动替代托管工具实验。

```bash
# From the repository root: use the shared Chapter 1 environment
uv sync --locked --extra ch1

# Activate it before changing directories:
source .venv/bin/activate

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch1]"

cd chapter1/search-codegen

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

export OPENAI_API_KEY=your-openai-api-key

# Exact official path
python main.py --backend openai --mode single \
  --request "东盟 10 国首都之间最近的一对是哪两个？请搜索并用 Python 计算" \
  --reasoning high --verbosity high --output result.json

# Equivalent-provider path (eligible for acceptance): Alibaba Model Studio
export DASHSCOPE_API_KEY=your-dashscope-api-key
python main.py --backend dashscope --mode single \
  --request "东盟 10 国首都之间最近的一对是哪两个？请搜索并用 Python 计算" \
  --output result.json

# Inspect the exact request without an API call
python main.py --backend openai --dry-run \
  --request "东盟 10 国首都之间最近的一对？" \
  --reasoning max --verbosity high

# Proxy diagnostic only; not canonical acceptance
export OPENROUTER_API_KEY=your-openrouter-api-key
python main.py --backend openrouter --mode single --request "Search current news"
```

<a id="learning-2"></a>

## 对照直接计算与先澄清的任务

先读 `example_request.py` 和下文中的请求示例，识别模型、工具、用户需求三个部分。再选一个支持相应托管工具的后端，完成凭据配置，运行单次查询。不要把“请求里写了工具名”当作工具确实执行过。

### 从明确问题到需要澄清的问题

首都距离任务需要先取得十个首都的坐标，再计算 45 对大圆距离，并说明最近的一对。先检查坐标来源，再核对计算输出，最后比较独立参考结果。

第二个任务故意没有指定比特币数据源与技术指标。第一次回复应先澄清这些偏好；用户补充后，再通过 `previous_response_id` 继续同一任务。这样可以观察“提出澄清问题”是否真的发生在工具调用之前。完整对照与离线检查命令如下：

```bash
cd chapter1/search-codegen
python run_experiment_1_3.py --backends openai dashscope --reasoning high
```

```bash
python -m pytest -q test_responses_agent.py
python -m py_compile agent.py config.py main.py run_experiment_1_3.py
```

<a id="learning-3"></a>

## 从服务端回执核对调用

在轨迹中寻找搜索、代码执行和最终答案三个环节。若使用城市距离问题，还应检查坐标来源、距离公式和参与比较的城市集合。一个格式漂亮的表格不足以证明计算正确；缺少的国家或错误坐标都会改变最近的一对。

### 连同提供商限制阅读已有结果

2026-07-31 的记录由 DashScope `qwen3.7-plus` 完成：首都任务通过一次托管搜索批量取得十组坐标，再用托管 Python 枚举 45 对，得到吉隆坡—新加坡 316.35 km；比特币任务先澄清，再执行 3 轮搜索、4 次代码调用，计算 MA7/MA20、RSI14、MACD(12,26,9)、区间收益与最大回撤。

同次记录中的 OpenAI 路线在工具执行前收到 `credit_balance_exhausted`，属于额度失败。这次运行中，直接请求行情接口连续超时，模型随后把一组价格直接写入代码，并在报告中称数据整理自搜索材料。复核数据时，应将每个日期和价格逐项对回来源，检查是否符合用户指定的 CoinGecko 日线口径；调用完成与数据核验分别记录。图像文件留在沙箱内，接口只返回执行日志。先澄清的行为由显式系统规则引导。

### 检查自己的解释

用户只说“做一份城市距离分析”时，哪些条件应该先澄清，哪些可以在回答中说明假设？

## English

# GPT-5.6 Sol Deep Research / GPT-5.6 Sol 深度研究

> Responses API companion for Chapter 1, Experiment 1-3: hosted
> `web_search` + hosted `code_interpreter`, typed tool traces, citations, and an
> intent-clarification continuation. The canonical path is OpenAI GPT-5.6 Sol;
> acceptance is multi-provider and may be closed by any provider whose
> Responses API genuinely closes the search/code loop server-side — currently
> Alibaba Model Studio (DashScope) `qwen3.7-plus`.

← [Chapter 1 index / 返回第 1 章目录](../README.md) ·
📖 [Book experiment / 正文实验](../../book/chapter1.md)

## What this companion implements

The canonical path is the OpenAI **Responses API**, not a Chat Completions
request that merely contains similarly named tool objects. The active agent in
`agent.py` sends:

```json
{
  "model": "gpt-5.6-sol",
  "tools": [
    {"type": "web_search", "search_context_size": "medium"},
    {
      "type": "code_interpreter",
      "container": {"type": "auto", "memory_limit": "4g"}
    }
  ],
  "reasoning": {"effort": "high"},
  "text": {"verbosity": "high"}
}
```

The DashScope backend speaks the same `/responses` protocol against
`{DASHSCOPE_BASE_URL}/responses` with the provider's hosted-tool shapes:

```json
{
  "model": "qwen3.7-plus",
  "tools": [{"type": "web_search"}, {"type": "code_interpreter"}],
  "stream": true
}
```

DashScope runs thinking natively (no `reasoning.effort`/`text.verbosity`
knobs) and its gateway drops non-streaming requests that stay silent for
about 60 seconds, so the backend always streams and keeps the final
`response.completed` object, which has the same shape as a non-streaming
response.

Acceptance is based on provider output items. A successful ASEAN-capitals run
must contain completed `web_search_call` and `code_interpreter_call` items,
clickable URL citations, and the computed closest pair. A text answer that says
it used Python does not pass without the provider tool receipt.

The second scenario sends the deliberately ambiguous Bitcoin request used in
the chapter, requires the first response to clarify material preferences before
using tools, then continues with `previous_response_id` after the user supplies
the data source and indicators.

## Current evidence status

Run the complete validator with:

```bash
cd chapter1/search-codegen
python run_experiment_1_3.py --backends openai dashscope --reasoning high
```

The latest evidence is [validation/latest.json](validation/latest.json); raw
credential-free receipts, a manifest, and SHA-256 sidecars live in
`validation/runs/real_20260731T170529Z/`.

Result of the 2026-07-31 multi-provider acceptance run: **passed**, with
`dashscope` (`qwen3.7-plus`) as the acceptance backend.

- ASEAN capitals: one hosted `web_search_call` batching ten model-issued
  coordinate queries, then a hosted `code_interpreter_call` that enumerated all
  45 haversine pairs and found Kuala Lumpur–Singapore at 316.35 km — the same
  pair as the independent local reference computed from standard coordinates.
- Bitcoin technical analysis: the first turn asked which data source and which
  indicators to use **without calling any tool**; the continuation via
  `previous_response_id` ran 3 model-directed search rounds and 4 hosted
  `code_interpreter_call`s computing MA7/MA20, RSI14, MACD(12,26,9), period
  return and max drawdown, and plotted a close-price chart in the sandbox.
- The official OpenAI `gpt-5.6-sol` path is still intact but remains
  quota-blocked: both calls returned `credit_balance_exhausted` before any
  hosted tool ran, which is recorded in the same evidence file.
- Honest qualifications: the DashScope sandbox has no outbound network, so the
  daily closes were extracted through web search (the model disclosed this in
  its report); the chart PNG stays inside the sandbox because this Responses
  API returns execution logs only; and `qwen3.7-plus` only asks before acting
  when the system prompt carries an explicit clarify-first rule — the shipped
  prompt encodes it.
- The OpenRouter route is retained strictly as a diagnostic and is never
  accepted. No fallback model, local Python replacement, fabricated tool
  trace, or Chat-Completions approximation is counted as fulfillment.

Earlier blocked attempts are kept under `validation/real_20260729T155459Z/`
and `validation/real_20260730T033800Z/`.

## Setup and CLI

Python 3.9+ is required.

```bash
# From the repository root: use the shared Chapter 1 environment
uv sync --locked --extra ch1

# Activate it before changing directories:
source .venv/bin/activate

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch1]"

cd chapter1/search-codegen

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

export OPENAI_API_KEY=your-openai-api-key

# Exact official path
python main.py --backend openai --mode single \
  --request "东盟 10 国首都之间最近的一对是哪两个？请搜索并用 Python 计算" \
  --reasoning high --verbosity high --output result.json

# Equivalent-provider path (eligible for acceptance): Alibaba Model Studio
export DASHSCOPE_API_KEY=your-dashscope-api-key
python main.py --backend dashscope --mode single \
  --request "东盟 10 国首都之间最近的一对是哪两个？请搜索并用 Python 计算" \
  --output result.json

# Inspect the exact request without an API call
python main.py --backend openai --dry-run \
  --request "东盟 10 国首都之间最近的一对？" \
  --reasoning max --verbosity high

# Proxy diagnostic only; not canonical acceptance
export OPENROUTER_API_KEY=your-openrouter-api-key
python main.py --backend openrouter --mode single --request "Search current news"
```

Important options:

| Option | Meaning |
|---|---|
| `--backend openai` | Canonical `https://api.openai.com/v1/responses` path |
| `--backend dashscope` | Equivalent-provider path: DashScope Responses API, hosted `web_search` + `code_interpreter`, eligible for acceptance |
| `--backend openrouter` | Explicit proxy diagnostic; never silently substituted |
| `--reasoning` | `none`, `low`, `medium`, `high`, `xhigh`, or GPT-5.6 `max` |
| `--verbosity` | Responses `text.verbosity`: `low`, `medium`, or `high` |
| `--output` | Saves request, typed output items, citations, usage, and raw response |

## Verification

```bash
python -m pytest -q test_responses_agent.py
python -m py_compile agent.py config.py main.py run_experiment_1_3.py
```

The validator checks exact model identity, direct-vs-proxy provenance, both
hosted tool types, citations, clarification order, continuation linkage, token
usage, reported provider cost when available, and credential-free raw evidence.

## Official sources

- [GPT-5.6 Sol model](https://developers.openai.com/api/docs/models/gpt-5.6-sol)
- [Web search](https://developers.openai.com/api/docs/guides/tools-web-search)
- [Code Interpreter](https://developers.openai.com/api/docs/guides/tools-code-interpreter)
- [GPT-5.6 model guidance](https://developers.openai.com/api/docs/guides/model-guidance?model=gpt-5.6-sol)
- [Alibaba Model Studio code interpreter (DashScope)](https://help.aliyun.com/zh/model-studio/qwen-code-interpreter)
