# 附加项目：完整音频链路的 WebRTC 电话 Agent

语音 Agent 不应只读取文字模拟用户说话。本项目通过本地浏览器 WebRTC 通话，把麦克风音频送到识别、对话与合成模块，再将回复音频送回浏览器。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3)。

<a id="learning-0"></a>

## 理解问题与方法

音频链路承载用户说的话，字幕只用于展示。把这两条通道分清，才能知道系统是否真正处理了声音。任务完成还需要用户确认关键内容，而不是模型自己宣布已经安排好。

本实验把“呼叫用户”实现为用户主动加入的本地浏览器 WebRTC 通话，不要求 PSTN、E.164 号码、电话运营商账户或公网 webhook。浏览器授权麦克风后向本地 `aiortc` peer 发送音频 RTP；服务端把实际收到的音频重采样并交给 Whisper ASR，把 ASR transcript 交给真实外部 LLM，再把 Agent 回复通过系统 TTS 合成为 PCM，送进 WebRTC 下行音轨。data channel 只传“音频提交”控制事件及 ASR/TTS 的无障碍字幕镜像，不提供用户语义。

完整链路是：

```text
browser microphone → WebRTC RTP → aiortc PCM buffer → Whisper ASR
    → external LLM dialogue / complete_task → real TTS PCM → WebRTC RTP → browser audio
```

服务端不提供 local planner、正则 parser、mock 或模型失败 fallback。ReAct 规划和通话后的结构化对话都必须收到 provider response ID、精确模型、usage、finish status 和正 latency；任何字段缺失都会中止。交互通话的音频和 transcript 只在本地进程内存在，不写盘。自动验收只使用明确标记为非隐私的合成语音 fixture，因此可以保留其音频、transcript 和 hash 做复核。

<a id="learning-1"></a>

## 准备环境与输入

本项目包含多条路径。先选定要观察的流程，再阅读对应的依赖和输入要求。下文保留了各条路径的完整配置，运行时应保持模型、文件路径与所选入口一致。

### 安装与运行

```bash
# 仓库根目录；uv.lock 同时固定 aiortc、Playwright、Torch 和 Whisper
uv sync --locked --python 3.12 --extra ch6 --extra dev

cd chapter6/phone-agent
cp env.example .env
# 填入 ARK_API_KEY；也可按 env.example 显式改用 OpenAI/OpenRouter

# ReAct treatment
uv run --extra ch6 python demo.py \
  --task "Call me about a dental checkup; ask for the missing exact time and confirmation code"

# Direct control
uv run --extra ch6 python direct_call.py \
  --name "Jane Doe" \
  --goal "Confirm a dental-checkup time and code" \
  --context "Tuesday 2pm to 4pm is available" \
  --instructions "Ask for one time and code, require explicit confirmation, then complete_task"
```

也可以运行 `uv run --extra ch6 uvicorn webrtc_app:app --host 127.0.0.1 --port 8765`，再打开 <http://127.0.0.1:8765>。听到 Agent 通过远端音轨播放的澄清问题后，对麦克风说出时间、确认码及明确确认，然后点击“Finish speaking”。页面不提供 typed semantic fallback 或浏览器 speech recognition；字幕只是服务端 ASR/TTS 结果的镜像。

默认配置使用 ARK `doubao-seed-1-6-flash-250615`、锁定的 `openai-whisper==20231106` tiny checkpoint，以及本机 `say`（macOS）或 eSpeak（Linux）TTS。可用 `PHONE_*` 与 `WHISPER_*` 环境变量显式覆盖；所选路径仍然 fail closed，不会换 provider 重试。`localhost` 可以直接使用麦克风；部署到其他主机时浏览器要求 HTTPS。本实验验证 localhost host-candidate 路径，不代表跨 NAT/TURN 或生产电话网络。

<a id="learning-2"></a>

## 按照步骤完成实验

按下文准备识别模型、TTS 与对话服务后，启动本地演示并在浏览器加入通话。先回答一个时间或确认信息，观察识别文本与实际声音是否一致，再听模型如何复述并请求确认。

### 直接调用与 ReAct 对照

两组使用相同的浏览器麦克风 → ASR → LLM → TTS → 下行 RTP 路径，唯一实验变量是规划方式：

| 组别 | 调用者输入 | 规划行为 |
| --- | --- | --- |
| 直接组（control） | 姓名、目标、上下文、指令四项全部填写 | 不调用规划 LLM，直接建立固定参数会话 |
| ReAct 组（treatment） | 一段故意漏掉时间与确认码的自然语言任务 | 真实外部 LLM 留下 observation/reason/action 摘要，识别缺失字段并生成澄清话语 |

两组在 Whisper 转录用户明确确认的时间和确认码后，都由真实外部 LLM 生成 `complete_task` 结构及最终播报。实验只保存“本地确认记录”，不会声称诊所或其他外部系统已经完成预约。

<a id="learning-3"></a>

## 分析结果与形成判断

检查音频收发、识别和任务状态三个层次。字幕正确但没有音频传输，不能证明通话链路完整；模型听错后得到的确认，也可能让错误进入任务结果。

### 完整音频实验的检查方法

```bash
# 必须存在所选外部 LLM credential；其值不会写入证据
uv run --extra ch6 python run_acceptance.py \
  --output validation/runs/phone-agent-webrtc-audio-20260731-v1

uv run --extra ch6 python verify_acceptance.py \
  validation/runs/phone-agent-webrtc-audio-20260731-v1

uv run --extra ch6 --extra dev ruff check .
uv run --extra ch6 --extra dev pytest -q
node --check static/app.js
```

验收分别用 Chrome 的 one-shot fake microphone device 播放两条安全合成 WAV。它不是文本注入：语音仍经过 `getUserMedia`、Opus/RTP、服务端解码、PCM 缓冲和真实 Whisper inference。每组必须同时通过 20 个门禁，包括 SDP/ICE、data channel、双向音轨与 RTP packet/byte、RTP-derived WAV、Whisper checkpoint hash、真实外部 LLM raw receipt、两条真实 TTS asset 的 hash 与完整下行发送、媒体 transcript source、缺失字段澄清、明确确认、结构化完成、无 fallback 及隐私边界。

[`validation/runs/phone-agent-webrtc-audio-20260731-v1/`](validation/runs/phone-agent-webrtc-audio-20260731-v1/) 保留 direct/react 原始记录、对照结论、安全 fixture、服务端收到的 ASR WAV、Agent TTS WAV、日志与 manifest。`verify_acceptance.py` 独立重算源码/产物/LLM raw receipt hash，并拒绝缺文件、改媒体、改 response ID、无 usage、错误 transcript source 或任何 gate 降级。安全合成验收证明技术链路，不等同于真人可用性研究。

---

### 检查自己的解释

用户更正刚才说的时间时，系统应怎样更新状态并确认新值？

## English

This unnumbered add-on uses the stable `phone-agent` project identifier. It calls a consenting participant in a local browser rather than dialing the PSTN. Browser microphone audio is sent over RTP to aiortc, buffered and transcribed by real local Whisper. Only that ASR transcript enters the real external LLM dialogue. Every Agent utterance is synthesized by a real system TTS engine and queued on the WebRTC downlink audio track; the data channel carries only audio-commit control and accessibility mirrors.

The direct control requires four fixed parameters. The ReAct treatment accepts one incomplete task and requires a no-fallback external planning receipt with the credential-free raw request/response, provider response ID, exact model, usage, finish status, latency, and hashes. The retained safe campaign and standalone validator are in the directory linked above. PSTN and E.164 are intentionally outside this local “call the user” acceptance scope.
