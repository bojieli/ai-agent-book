# 用可替换模型运行截图操作循环

理解 Computer Use 后，可以进一步问：如果换一个视觉模型，哪些部分需要改变？本实验把模型接入与浏览器执行分开，便于观察协议兼容与实际操作能力的区别。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

模型接收截图并返回结构化动作，浏览器执行后产生新的观察。兼容接口让模型更容易替换，但动作格式、坐标理解和任务规划仍需要逐项检查。

### 把模型接口与浏览器动作分开理解

这个实现对应实验 6-8、6-9 中可更换提供商的路线：模型读取截图，返回结构化动作，浏览器执行一个动作，再把新观察送回模型。文档中的托管示例使用 OpenRouter 上的 `qwen/qwen3-vl-32b-instruct`；也可以连接自己的 vLLM、SGLang 或其他兼容服务。

兼容端点需要接收包含截图的 OpenAI 风格消息，能通过原生 `json_schema` 或提示中的 schema 返回 Browser Use 动作，每轮提供足以选择一个浏览器动作的信息，并保留实际模型标识。“开放模型”描述权重与许可，OpenRouter 只是其中一条托管路线；通过同一个网关访问的不同模型仍是不同实验条件。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 安装固定版本的浏览器依赖

使用 Python 3.11 或更新版本，从本目录创建环境。这里的依赖固定到 Browser Use 的 `ec9277c…` 提交（包版本显示为 `0.9.5`）；同名 PyPI 版本不能替代对这个提交的核对。

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

<a id="learning-2"></a>

## 按照步骤完成实验

先按下文安装浏览器依赖，运行 dry-run 查看任务配置。再接入所选模型，在不登录、不修改外部数据的查询任务上观察每轮截图与动作。保留视频有助于定位等待或重复操作。

### 先做一个小规模观察

以下命令从本实验目录执行。先完成前面的环境准备，再观察这条路径的输入和输出。

```bash
python main.py --dry-run
```

### 先检查配置，再执行只读天气任务

`--dry-run` 用于检查计划采用的配置。完整命令会打开浏览器、逐步观察页面，并在不登录、不修改外部数据的条件下查询天气；`--max-steps 25` 限定最多执行的步数，`--record-video` 保留过程录像。

```bash
cp env.example .env
export OPENROUTER_API_KEY='replace-with-your-key'

python main.py --dry-run
python main.py \
  --task "Open Google, search for San Francisco weather today, and report the temperature and conditions. Do not sign in or change any external data." \
  --max-steps 25 \
  --record-video
```

默认模型为 `qwen/qwen3-vl-32b-instruct`，可通过 `OPEN_MODEL_MODEL` 指定另一视觉模型。自托管时，先启动具备视觉能力的兼容端点，再使用以下配置；这条路线不需要 OpenRouter Key。

```bash
export OPEN_MODEL_API_KEY=local
export OPEN_MODEL_BASE_URL=http://127.0.0.1:8000/v1
export OPEN_MODEL_MODEL=Qwen/Qwen3-VL-32B-Instruct
python main.py --dry-run
python main.py --headless
```

如果端点能接收图片，但不接受 `response_format: json_schema`，可以设置 `OPEN_MODEL_SCHEMA_MODE=prompt`。这会把结构要求放入提示中；应单独记录该设置，因为模型是否严格遵循动作 schema 也可能影响结果。

<a id="learning-3"></a>

## 分析结果与形成判断

dry-run 只检查准备路径，不证明模型可以操作页面。真实运行应检查动作合法性、页面状态和答案来源；接口可调用也不等于模型理解了目标。

### 用观察核对 Agent 的完成声明

已有开放模型运行记录在 2026-08-01 使用指定模型完成了 16 次调用、16 步交互。它遇到 Google CAPTCHA 后改用 weather.com，最后给出 64°F、Sunny。验证器将答案与保留的浏览器观察对应，核对了 15 张截图的哈希、每轮一个动作的限制和凭据扫描。这是当时地点、时间与模型下的记录，不是新的天气查询结果。

每次非 dry-run 都会创建 `runs/open-model-<UTC>/`。其中 `preflight.json` 记录脱敏端点、模型与执行限制，`api-receipts.json` 记录请求哈希和提供商响应，`history.json` 记录动作顺序，`screenshots/` 与 `screenshots.json` 保存视觉观察，`summary.json` 或 `failure.json` 描述结果，`manifest.json` 记录文件哈希与大小。

Agent 返回 `done` 只表示它认为已经完成。使用下面的检查命令，继续核对最终答案、截图和动作轨迹：

```bash
python validate_run.py runs/<run-id> --latest validation/latest.json
```

### 检查自己的解释

如果换模型后点击经常偏移，应先检查图像缩放、坐标约定还是任务提示？怎样逐项排除？

## English

# Open-model Computer Use companion

This is the provider-portable arm for Experiments 6-8 and 6-9. It runs the
same screenshot → structured action → browser execution loop without requiring
an Anthropic or OpenAI model account. The documented hosted route uses the
open-weight `qwen/qwen3-vl-32b-instruct` model through OpenRouter. The same
runner accepts a self-hosted vLLM/SGLang endpoint or another OpenAI-compatible
host.

The Anthropic Computer Use Demo remains a useful reference implementation for
its native `computer`, `bash`, and editor tools. This companion does not claim
that Qwen and Claude are interchangeable. Runs from different models are
separate experimental arms and must retain the actual endpoint and model ID.

## Current evidence

The [canonical open-model run](validation/latest.json) passed on 2026-08-01.
OpenRouter returned the requested `qwen/qwen3-vl-32b-instruct` model for all
16/16 calls. The Agent hit a Google CAPTCHA, recovered through weather.com,
and completed in 16 steps. The deterministic validator matched the final
64°F/Sunny answer to the retained browser observation, verified 15 screenshot
hashes and the one-action-per-step read-only trajectory, and found no retained
credential. This completes the Experiment 6-9 open-model arm only; the
Anthropic-native Experiment 6-8 arm remains separate.

## Endpoint contract

An endpoint is eligible when it:

- accepts screenshot images in OpenAI-compatible chat messages;
- can produce the Browser Use action schema, either with native `json_schema`
  support or with schema-in-prompt JSON;
- returns enough information for the Agent to choose one browser action per
  step; and
- does not silently replace the requested model.

The reference open model is Qwen3-VL 32B Instruct. “Open model” describes the
weights/license; OpenRouter is only one hosted API route. Readers can use their
own compatible host instead.

## Install

Use Python 3.11 or newer. The isolated requirement pins the exact Browser Use
commit audited by the chapter (`ec9277c…`, package version `0.9.5`); the PyPI
release carrying the same version string is not substituted for that commit:

```bash
python3.11 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python -m playwright install chromium
```

## Hosted open-model route

```bash
cp env.example .env
export OPENROUTER_API_KEY='replace-with-your-key'

python main.py --dry-run
python main.py \
  --task "Open Google, search for San Francisco weather today, and report the temperature and conditions. Do not sign in or change any external data." \
  --max-steps 25 \
  --record-video
```

The default model is `qwen/qwen3-vl-32b-instruct`. Override
`OPEN_MODEL_MODEL` to select another explicitly open-weight vision model; do
not describe a proprietary model reached through the same gateway as an open
model.

## Self-hosted or another compatible API

Start a vision-capable OpenAI-compatible server, then configure its URL and
served model name. The runner does not require an OpenRouter key in this mode:

```bash
export OPEN_MODEL_API_KEY=local
export OPEN_MODEL_BASE_URL=http://127.0.0.1:8000/v1
export OPEN_MODEL_MODEL=Qwen/Qwen3-VL-32B-Instruct
python main.py --dry-run
python main.py --headless
```

If the host accepts images but rejects `response_format: json_schema`, set
`OPEN_MODEL_SCHEMA_MODE=prompt`. This is a compatibility fallback, and its
reliability should be reported separately because schema adherence can change.

## Retained evidence

Every non-dry run creates a new `runs/open-model-<UTC>/` directory containing:

- `preflight.json`: redacted endpoint, exact model, task, and execution limits;
- `api-receipts.json`: credential-free request hashes and raw provider responses,
  including provider-reported model IDs when supplied;
- `history.json`: ordered model decisions, actions, observations, and results;
- `screenshots/` plus `screenshots.json`: retained per-step visual observations;
- `summary.json` or `failure.json`: outcome and honest failure state; and
- `manifest.json`: SHA-256 and byte size for every retained artifact.

No API-key value is written. The Agent's `done` result is only an
agent-reported outcome; manuscript-level completion still requires independent
checking of the weather answer and action trajectory. A dry run, model-list
lookup, or browser launch alone is not completion evidence.

Validate a retained run against its provider receipts, one-action-per-step
limit, final browser observation, screenshot hashes, and credential scan:

```bash
python validate_run.py runs/<run-id> --latest validation/latest.json
```
