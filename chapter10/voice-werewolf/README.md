# 用游戏状态机协调多角色语音交互

狼人杀同时包含公开发言、私有信息、回合规则和多人决策，适合观察多 Agent 协调。本实验将确定的游戏规则交给代码，把角色表达与选择交给模型。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

裁判状态机负责阶段、技能、死亡与胜负，角色只接收各自允许看到的信息。语音是交互通道，不能改变信息边界。独立用户模拟器与真人参与也需要明确区分。

系统现在有两条正式用户路径：授权真人麦克风，以及 `--simulate-user` 独立真实 LLM 用户模拟器。模拟器只读本席上下文，必须调用发言/选人工具；工具表达先生成真实音频，再由真实 ASR 转写，游戏只消费转写结果，选人不一致时失败关闭。真人路径继续覆盖 VAD、播放与打断。

2026-08-01 的严格复核否决了两个把误转写当成弃权的早期运行，并据此加固了解析器。2026-08-03 的 v11 在同一局内完成 3 个完整循环、6 次真实工具→语音→ASR 回环、信息隔离、规则胜负和四项策略验收，严格总体状态为 `pass`。报告保留 13 个唯一响应 ID、1,650 个音频输入 token、27 个非空 TTS 事件、动作历史及裁判尝试溯源，独立验证再次核对 6/6 音频动作边界。`--ai-only` 与 `--offline` 只是补充诊断。

### 规则状态与玩家知识分别由谁管理

游戏包含 6–8 个席位、两名狼人、一名预言家、一名女巫和村民。代码实现的 Judge 管理夜晚、白天、投票、技能库存、死亡和胜负；每个玩家只拥有自己的 memory。公共广播、单人私信和狼人队内消息是不同的交付通道，因此身份信息能否隔离应由轨迹检查，而不是依赖模型自觉保密。

用户席位可以是真人，也可以是独立的真实 LLM 模拟器。模拟器只读取本席获准的信息，并调用本轮合法的 `speak_publicly` 或 `choose_player`；其表达经过真实 TTS 与 ASR，游戏只接收转写。选人转写与工具选择不一致时，记录 `simulator_action_mismatch` 并停止该动作。

<a id="learning-1"></a>

## 准备环境与输入

先从本地示例开始。依赖安装可能需要联网，但下面标明的离线路径不需要模型 API Key。若随后切换到真实模型，请再完成相应的服务配置。

### 选择模拟用户或真人音频路径

模拟用户可以使用 OpenRouter，加上本地 `espeak`（macOS 可用 `say`）与 `ffmpeg`；也可以选择有额度的 OpenAI Audio，或本地合成加 Gemini ASR。真人路径使用麦克风能量 VAD、静音结束检测、真实 TTS 播放与 ASR；检测到插话时取消播放，再将转写作为公共打断轮次记录。佩戴耳机有助于避免回声触发检测，嘈杂环境可用 `--no-interruptions`。

```bash
# From the repository root: use the shared Chapter 10 environment
uv sync --locked --python 3.12 --extra ch10

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch10]"

cd chapter10/voice-werewolf

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
python demo.py --simulate-user \
  --model google/gemini-2.5-flash \
  --simulator-model anthropic/claude-sonnet-4 \
  --simulator-speech-provider openrouter-system # unattended real-API E2E
python demo.py --confirm-human-consent                # 1 consenting human + 6 real LLM Agents
python demo.py --confirm-human-consent --human-seat 3 # human is P3; role remains randomized
```

<a id="learning-2"></a>

## 按照步骤完成实验

先运行离线演示，跟踪一轮夜晚、白天与投票，检查不同角色看到的信息。随后按下文接入真实模型与语音路径，再观察表达、选择和裁判状态是否一致。

### 先做一个小规模观察

以下命令从本实验目录执行。先完成前面的环境准备，再观察这条路径的输入和输出。

```bash
python demo.py --offline
```

### 从离线状态机走到完整语音回合

先用下面的补充入口核对状态机与信息隔离，再选择真实模拟器或授权真人模式。`--ai-only` 是全 AI 文本诊断，`--offline` 是确定性补充检查，它们不经过完整音频链路。

```bash
python demo.py --ai-only          # real LLM, all-AI text diagnostic
python demo.py --offline          # deterministic CI/privacy supplement
pytest -q
```

一个完整循环只有在夜晚、讨论和投票都结束后才计数。达到轮数上限仍无规则胜者时，结果是“未决”；不能把流程停止当作任一阵营获胜。

<a id="learning-3"></a>

## 分析结果与形成判断

离线路径是确定性示例，不代表真实对话质量。多角色游戏还应检查私有信息泄漏、同时死亡与技能消耗等边界，而不只看最后是否分出胜负。

### 把角色策略与音频动作逐项检查

赛后策略评审分别判断狼人隐藏身份、预言家揭示时机与证据、村民基于证据推理，以及一般角色一致性；每项必须返回 pass、fail 或 insufficient，通过项还必须引用轨迹证据。一个笼统的 `overall_pass: true` 不足以通过。

已有早期记录曾把 `P1 is not` 等含糊转写误当弃权，独立复核因此否决了对应动作；另有运行虽然完成三轮和音频流程，但村民误投未被质疑的预言家，策略项失败。2026-08-03 的 v11 才在同一局内完成三个循环、六次一致的工具—语音—ASR 动作、信息隔离、规则胜负和四项策略检查。原文保留了各次失败、响应 ID、音频 token、事件数、报告 SHA-256 和独立验证链接。

不要把不同局里的通过项拼成一份结果。真人麦克风仍可补充检查 VAD 和插话体验，但自动模拟器的成功不能替代真人体验结论。

### 检查自己的解释

一个角色在公开发言中声称知道私有信息，怎样判断这是游戏内推测还是系统真的泄露了上下文？

## English

# Experiment 10-6 · Voice Werewolf with a real-LLM user simulator

The experiment supports two first-class user seats: a consenting live human, or an independent real-LLM user simulator for unattended end-to-end testing. Both use the same seeded role shuffle and protected private memory in a 6–8 seat game with two Werewolves, one Seer, one Witch, and Villagers. The code-driven Judge—not an LLM—owns the state machine, night/day/vote phases, skill inventory, deaths, and deterministic win rule.

## Automated user simulator

`python demo.py --simulate-user` does not insert canned answers or turn the user into an ordinary omniscient AI player:

1. The simulator receives only the private and public memory authorized for its randomized seat.
2. A separately configurable real LLM must call the sole legal tool for the turn: `speak_publicly` or `choose_player`.
3. The chosen utterance is synthesized into a real waveform. The automatic provider order is OpenAI Audio, local `espeak` (or macOS `say`) plus OpenRouter native-audio ASR, then local synthesis plus Gemini ASR.
4. The game consumes only the real ASR transcript. It never receives the LLM's pre-audio utterance directly.
5. For skills and votes, the parsed ASR action must exactly equal the tool-selected action; a mismatch fails closed and is retained as `simulator_action_mismatch`.

The OpenRouter speech path records response IDs, provider-reported models, token usage (including nonzero audio tokens), audio hashes, transcripts, and latency without retaining credentials. The local synthesizer is a real audio component rather than an API; both the user reasoning call and audio transcription call are real external model APIs.

## Live two-way voice

`python demo.py` is no longer an all-AI text demonstration. It creates a real human seat and a `LiveVoiceSession`:

1. AI/Judge speech is sent to a real OpenAI TTS endpoint and played immediately.
2. Human speech is captured from the microphone with energy VAD and end-of-speech silence detection.
3. Captured WAV audio is sent to a real OpenAI ASR endpoint.
4. Spoken player numbers drive human night skills and voting; daytime speech is broadcast to every Agent context.
5. During public AI speech, microphone activity cancels playback, transcribes the barge-in, and records it as a public interruption turn. Headphones are recommended to prevent acoustic echo from triggering the detector.

Audio files and a timestamped `voice_trace.json` record TTS, ASR latency, and interruptions. `--no-interruptions` disables barge-in for noisy rooms.

## Information asymmetry and strategy acceptance

Every player owns a separate `memory`. The Judge has only three delivery capabilities: public broadcast, single-player private send, and Werewolf-team send. The same boundary applies to both kinds of user seat. The post-game audit proves Werewolf teammates never enter good-player contexts, Seer investigations enter only the Seer context, and all public events reach everyone.

The game also records role-labelled actions and runs a real LLM post-game acceptance judge over four explicit criteria: Werewolf concealment, Seer reveal timing/evidence, Villager evidence-based reasoning, and general role consistency. It quotes logged evidence and may return `insufficient`; it cannot substitute an Agent's unsupported claim for observed actions.
The returned JSON is schema-checked: all four named criteria need a valid
`pass|fail|insufficient` status, and every passing criterion needs evidence. A bare
model claim of `overall_pass: true` cannot pass the gate.

`artifacts/acceptance_report.json` records:

- exactly one user seat, its kind, and its randomized role;
- exact role counts and player count;
- completed night–day–vote cycles and deterministic winner;
- privacy audit result;
- real strategy audit;
- whether real LLM tools, TTS, ASR, and action agreement occurred, plus barge-in count for a human run.

The end-to-end result requires 6–8 players, the exact role mix, one protected user seat, privacy pass, observed ASR + TTS, a rule-based winner, and—on the simulator path—real tool calls and matching audio-round-trip actions. The stricter experiment-wide result additionally requires at least three complete cycles and all four strategy criteria in the same run.
The Judge increments the cycle counter only after night, day discussion, and voting all
finish. Reaching the safety round limit without a rule-based winner is reported as
`未决`, not silently awarded to either faction, and therefore cannot pass acceptance.

## Run

```bash
# From the repository root: use the shared Chapter 10 environment
uv sync --locked --python 3.12 --extra ch10

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch10]"

cd chapter10/voice-werewolf

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
python demo.py --simulate-user \
  --model google/gemini-2.5-flash \
  --simulator-model anthropic/claude-sonnet-4 \
  --simulator-speech-provider openrouter-system # unattended real-API E2E
python demo.py --confirm-human-consent                # 1 consenting human + 6 real LLM Agents
python demo.py --confirm-human-consent --human-seat 3 # human is P3; role remains randomized
```

The simulator can use `OPENROUTER_API_KEY` alone when `espeak` and `ffmpeg` are installed. It can instead use a funded `OPENAI_API_KEY`, or `GEMINI_API_KEY` with local synthesis. AI reasoning and the post-game strategy audit can also use ARK or Moonshot via their OpenAI-compatible endpoints.
The live path refuses to open the microphone unless `--confirm-human-consent` is present.

Text-only and deterministic paths remain supplemental:

```bash
python demo.py --ai-only          # real LLM, all-AI text diagnostic
python demo.py --offline          # deterministic CI/privacy supplement
pytest -q
```

## Real validation results (2026-08-01 through 2026-08-03)

The retained [`validation/runs/`](validation/runs/) evidence contains four formal eight-seat games and an independent validation file for each. The independent validator supersedes the run's embedded status when it finds a boundary defect. Credential scans over reports, validations, and logs found zero hits.

- `exp10-6-simulated-user-openrouter-20260801`: the embedded report claimed action agreement and all four strategy criteria passed, but strict revalidation correctly rejects its abstention because ASR returned `P1 is not`, not an explicit abstention.
- `...-v2`: the unaffected formal E2E result. It completed three full cycles with two user tool/audio/ASR actions, unique response IDs and nonzero audio-token receipts, information isolation, and a rule-based winner. The independent strategy judge failed Villager reasoning because the simulated Villager voted out the uncontested Seer.
- `...-v3`: used `anthropic/claude-sonnet-4` for the user and retained four tool/audio/ASR actions. Strict revalidation rejects two ambiguous abstentions, and the strategy judge also caught a Werewolf fabricating a public event.

The completed 2026-08-03 campaign is
[`exp10-6-simulated-user-openrouter-20260803-v11`](validation/runs/exp10-6-simulated-user-openrouter-20260803-v11/acceptance_report.json).
In one seed-2 game it completed three night/day/vote cycles, preserved information
isolation, reached a rule-determined good-faction win, and passed all four strategy
criteria. The randomized P1 Villager performed six real LLM tool calls, six matching
speech/ASR round trips, and three public votes across the full game. The report retains
13 unique response IDs across simulator, ASR, and strategy-judge calls; 1,650 input
audio tokens; 27 positive-byte TTS events; action history; provider-reported models;
usage; audio hashes; and judge-attempt provenance. The
[`independent validation`](validation/runs/exp10-6-simulated-user-openrouter-20260803-v11/independent_validation.json)
rechecked all six tool/audio/action boundaries against report SHA-256
`655b4eed74ad4f4d741dc89f97c86a68c547e4f82d1dea9fea71449dfef797e9`.

The parser still fails closed unless an abstention transcript explicitly contains
`abstain`, `skip`, `none`, or the supported Chinese equivalents; the synthetic
utterance is the real-audio-probed phrase “I choose to abstain.” A schema-invalid
strategy grade is now retained as an attempt and the next real endpoint is tried,
rather than accepting or discarding malformed evidence. Earlier negative runs remain
useful regression evidence, but stale gates from different games are never combined.
A real human microphone session is optional manual coverage for VAD and barge-in, not
a blocker for automated system E2E.

---
