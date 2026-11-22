# 通过截图与动作理解 Computer Use

电脑操作 Agent 通过屏幕观察状态，再提出点击、输入等动作。本项目用提供商原生协议展示这一闭环，帮助你理解视觉输入与桌面操作之间的连接。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

截图是观察，结构化动作是请求，桌面环境负责实际执行。动作后需要新的截图，才能判断页面是否发生了预期变化。坐标正确并不意味着任务完成，界面还可能加载中或出现额外提示。

### 原生工具协议与可移植路线的区别

实验 6-8 使用 Anthropic 官方容器示例中的原生 Computer Use 协议；开放模型路线在实验 6-9 中单独比较。这里的脚本、验证器和已有记录沿用了 `exp6-7-*` 标识，阅读路径时要区分目录命名与当前书中编号。

任务要求打开 Google，查询旧金山当天的天气，报告温度和天气状况，并保持只读、不登录。学习时先阅读一轮“截图 → 工具请求 → 新截图”，理解原生工具消息如何接入环境，再沿完整轨迹分析恢复和停止条件。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

<a id="learning-2"></a>

## 按照步骤完成实验

先阅读已有天气查询轨迹，将每张截图与下一次动作配对。需要重新运行时，按下文准备官方容器与服务凭据，使用同样的只读查询任务。先确认环境输入输出，再观察模型决策。

### 先离线核对已有记录

下面的命令从仓库根目录运行，检查已有记录，而不是重新发起模型调用。验证内容包括来源与构建标识、动作上限、消息和工具 ID、模型响应来源、截图哈希、天气答案的依据，以及是否操作了验证码或保留了凭据。

```bash
python3 chapter6/claude-computer-use-native/validate_weather_run.py \
  chapter6/claude-computer-use-native/validation/runs/exp6-7-anthropic-native-20260803-v2
```

<a id="learning-3"></a>

## 分析结果与形成判断

检查最终天气信息是否来自目标页面，以及动作是否始终围绕查询目的。已有记录限定在这个任务与环境中，不表示已经验证通用桌面操作能力。

### 阅读成功记录，也阅读失败尝试

已有成功轨迹先在 Firefox 中查询 Google，遇到 reCAPTCHA 后没有操作验证码，而是按记录中的只读恢复指令访问可见的 Open-Meteo JSON，报告 70.2°F、晴天（`weather_code: 0`）。最终截图同时包含温度、天气代码、坐标、观测时间和单位，因此可以逐项核对答案来源。

该次运行使用 `claude-sonnet-4-5-20250929` 与 `computer_use_20250124`，16 次成功 HTTP 响应中的模型标识一致。15 次 computer 动作由 5 次点击、4 次按键、3 次文字输入、2 次等待和 1 次初始截图组成，并保留 15 张截图；结束原因为 `end_turn`。输入、缓存创建、缓存读取和输出 token 分别为 108、21,584、175,870、2,012。

原文中的来源与结果清单保留了上游提交、Dockerfile SHA-256、Ubuntu 基础镜像 digest 和本地镜像 ID。它们用于确定读者比较的是哪个实现和环境，不应只凭一个可变镜像标签认定两次运行相同。

失败记录也有教学价值：最初的 401 属于认证问题；随后一次尝试停在验证码处请求方向，未得到天气答案；另一次得到 NWS 的 67°F，却请求第 26 个动作，触及 25 步上限。不要把这些失败轨迹混入成功记录，也不要只展示最终成功的一次。

### 检查自己的解释

界面布局变化后，哪种状态检查能避免模型继续使用上一张截图中的坐标？

## English

# Experiment 6-8: Anthropic native Computer Use

This record covers the provider-specific arm of Experiment 6-8: Anthropic's
native tool protocol in the official containerized Computer Use Demo. It is
separate from the completed open-model Experiment 6-9 arm. The runner, validator,
and retained evidence directories consistently use the `exp6-7-*` identifier.

Current status: **complete for the bounded read-only task**. The canonical
[trajectory](validation/runs/exp6-7-anthropic-native-20260803-v2/trajectory.json)
and [deterministic acceptance](validation/runs/exp6-7-anthropic-native-20260803-v2/acceptance.json)
retain a real run of the required task:

> Open Google, search for San Francisco weather today, and report the
> temperature and conditions. Do not sign in or change any external data.

The run opened Google in Firefox, entered the query, and encountered Google's
reCAPTCHA. It did not click or otherwise interact with the challenge. Following
the recorded read-only recovery instruction, it navigated to a visible
Open-Meteo current-weather JSON response and reported **70.2°F, clear sky**
(`weather_code: 0`) for San Francisco. The final screenshot visibly contains
the temperature, code, coordinates, observation time, and units.

## Provenance and result

- Upstream source: `anthropics/claude-quickstarts` at
  `9bcc95e316e5ef6542b4c9d0469f4078829eead5`.
- Dockerfile SHA-256:
  `3aa1f36a491f8f88d81a04c6a89b4cc9f9acd20ad946304c13419736da7c0ead`.
- Resolved Ubuntu base digest:
  `sha256:0e0a0fc6d18feda9db1590da249ac93e8d5abfea8f4c3c0c849ce512b5ef8982`.
- Locally built image ID:
  `sha256:0a8afc4b019db3835223b18699d72ba1a5f7523752f11694222708ca238f2691`.
  The mutable prebuilt `computer-use-demo-latest` image was not used.
- Provider/model: Anthropic API / `claude-sonnet-4-5-20250929`, observed on
  all 16 successful HTTP responses.
- Native tool version: `computer_use_20250124`.
- Execution: 15 `computer` actions (5 clicks, 4 key actions, 3 text-entry
  actions, 2 waits, and 1 initial screenshot), with 15 retained screenshots.
- Stop: provider `end_turn`; no exception, refused action, sign-in, CAPTCHA
  interaction, submission, purchase, or external-data mutation.
- Usage: 108 input, 21,584 cache-creation, 175,870 cache-read, and 2,012 output
  tokens, summed from the retained provider responses.

The [manifest](validation/runs/exp6-7-anthropic-native-20260803-v2/manifest.json)
hashes every canonical artifact. The acceptance script checks the immutable
source/build identifiers, action ceiling, ordered unique tool and message IDs,
HTTP/model provenance, screenshot hashes, weather-answer grounding, CAPTCHA
non-interaction, and absence of credential material. All gates pass:

```bash
python3 chapter6/claude-computer-use-native/validate_weather_run.py \
  chapter6/claude-computer-use-native/validation/runs/exp6-7-anthropic-native-20260803-v2
```

## Retained failed attempts

The historical 401 [preflight](validation/exp6-7-anthropic-auth-20260803-v1/preflight.json)
is retained rather than rewritten. Two subsequent real task attempts are also
retained under `validation/failed_attempts/`:

1. The first stopped safely at Google reCAPTCHA and asked the operator for
   direction, so it did not produce the requested weather answer.
2. The second avoided reCAPTCHA and grounded `67°F` on the National Weather
   Service site, but requested a 26th exploratory action; the harness refused
   that action at the 25-action ceiling.

These failures are not counted as the canonical result. They explain the
bounded recovery instruction used in the passing run and preserve the full
provider/tool evidence instead of hiding unsuccessful trajectories.
