# 实验 6-6：本地运行 MiniCPM-o 4.5 端到端全模态语音

先听[第一段录音](fixtures/pace-fast.wav)，再听[第二段录音](fixtures/pace-slow.wav)。两段说的都是 “Please send the report before lunch.” 假如你只收到聊天窗口里的这行字，还能知道哪一遍说得快吗？

[English](#english)

<a id="learning-0"></a>

## 理解问题与方法

这句英语提出了两个不同的问题。“报告什么时候交？”可以从文字中找到答案。“这句话说得快还是慢？”则要用到声音里的线索。怎样检验模型有没有用上这些线索？让同一个模型做两遍题：一遍直接听录音，另一遍先把录音转成文字，答题时只给它看文字。两遍都用同一条录音、同一个问题。比较回答时，也留下转写，看看信息究竟在哪一步发生了变化。

本目录对应正文实验 6-6。运行器与已归档证据沿用历史标识 `exp6-5-*`，复核时按原路径读取。

本实验属于正文的“**范式二 · 端到端全模态模型（Omni）**”，不属于后文的“边想边说”方案。它用同一个开放权重模型 MiniCPM-o 4.5 比较两条路径：

- **端到端路径**：WAV 直接进入模型的音频编码器与隐空间，模型直接回答；
- **自级联路径**：同一模型先把 WAV 转成纯文字，再只依据文字回答，主动丢弃语速等副语言信息。

另加一条 audio-to-audio 检查，确认模型不仅能听，还能在本地生成 24kHz 语音。实验关闭 `enable_thinking`，因此结果不能用来声称复现 Step-Audio R1 的 MPS、Speak-First、Think-First 或“边想边说”。

### 实验设计

`fixtures/cases.json` 固定四条小型合成语音：两道只依赖语义的口述算术题，以及文字完全相同、语速分别为快和慢的两条副语言题。每条都运行端到端与自级联两臂。小样本只用于验证机制与本地可运行性，不是模型排行榜；合成音也不能替代真人、多口音与噪声数据集。

| 维度 | 端到端臂 | 自级联臂 |
| --- | --- | --- |
| 输入 | 单声道 WAV（读取时重采样为模型要求的 16kHz） | MiniCPM-o 生成的纯文字转录 |
| 回答模型 | MiniCPM-o 4.5 | 同一个 MiniCPM-o 4.5 |
| 是否保留语速 | 是 | 否（转录提示明确只保留说出的文字） |
| 采样 | 关闭 | 关闭 |
| 思考模式 | 关闭 | 关闭 |

固定模型为 `openbmb/MiniCPM-o-4_5@1f761131fa83f5ed3cd6f2f22b225c4501d154fa`。官方实现由 SigLip2、Whisper-medium、CosyVoice2 与 Qwen3-8B 组成，总计约 9B 参数；本实验只初始化音频与 TTS 分支，不初始化视觉分支。

<a id="learning-1"></a>

## 准备环境与输入

想先跟着录音读结果，可以直接进入[两段录音的对照练习](#learning-2)，普通电脑即可。要自己运行两条模型路径，再准备以下环境。

### 安装

上游明确测试 Python 3.10、`transformers==4.51.0`、PyTorch 2.3–2.8。该组合与仓库共享环境里的其他实验可能冲突，因此这里有意使用独立虚拟环境：

```bash
cd chapter6/end-to-end-speech
uv venv .venv --python 3.10
uv pip install --python .venv/bin/python -r requirements.txt
source .venv/bin/activate

hf download openbmb/MiniCPM-o-4_5 \
  --revision 1f761131fa83f5ed3cd6f2f22b225c4501d154fa
```

需要 Linux、NVIDIA CUDA GPU 和约 21GB 可用显存。只有扩展到视频输入/输出时才需要 FFmpeg；本次 WAV→文本/语音 campaign 不调用 FFmpeg。模型权重与上游 Python 自定义代码会被下载到 Hugging Face cache，运行前应按自己的供应链策略审查并固定 revision。

<a id="learning-2"></a>

## 按照步骤完成实验

在本实验目录执行下面的命令。它从 WAV 文件读取采样帧数和采样率，算出整段录音的时长，再从已保存的运行记录中取出同一条录音对应的转写和两次回答。只需 Python 标准库。

```bash
python3 - <<'PYTHON'
import json
import wave
from pathlib import Path

run = Path("validation/runs/exp6-5-minicpmo45-20260801-v1")
cases = json.loads((run / "evidence.json").read_text())["cases"]
for case in cases:
    if case["category"] == "paralinguistic":
        with wave.open(case["audio_path"]) as audio:
            seconds = audio.getnframes() / audio.getframerate()
        cascade = case["self_cascade"]
        print(case["audio"], round(seconds, 2), "秒", cascade["transcript"])
        print("直接听录音：", case["direct"]["response"], "只读转写：", cascade["response"])
PYTHON
```

两份文件分别长 1.46 秒和 4.79 秒。它们说的是同一句话，所以值得对照着听；如果换成两段长短不同的文字，单凭录音总时长就判断语速，理由还充分吗？

### 运行

```bash
run=$(mktemp -d validation/runs/my-run.XXXXXX)
python demo.py --local-files-only --evidence "$run/evidence.json"
python validate_evidence.py "$run/evidence.json"
```

`demo.py` 一次加载模型，随后保存每条输入的 SHA-256、两臂原始回复、模型自产转录、分阶段延迟、模型 revision、软件版本、GPU 信息，以及语音输出的 SHA-256/采样率/时长。验收只要求真实本地路径完整且证据闭环，**不要求假设必须为正**。

没有 GPU 时可运行离线单元测试，但不能据此宣称完成真实实验：

```bash
python -m pytest -q tests
python demo.py --help
```

合成输入可用 `python prepare_fixtures.py` 重建（需要 `espeak`）；正式证据以仓库中 WAV 的 hash 为准。

<a id="learning-3"></a>

## 分析结果与形成判断

直接音频路径更好时，要确认不是转写错误造成差距。文本相同但语速不同的案例尤其适合观察声音信息。音频生成检查是另一项能力，不应与输入理解混为一个分数。

### 本地结果

2026-08-01 的[本地运行记录](validation/runs/exp6-5-minicpmo45-20260801-v1/evidence.json)附有[当时的 11 项验收结果](validation/runs/exp6-5-minicpmo45-20260801-v1/acceptance.json)。硬件是单张 96GB RTX PRO 6000 Blackwell，PyTorch 2.8.0+cu128、Transformers 4.51.0、BF16/SDPA；模型加载 6.154 秒，峰值分配显存 20.269GiB。

在当前版本用校验器复查这份旧记录，11 项中有 10 项通过。未通过的是实现文件哈希检查：现在的 `demo.py`、`speech_model.py`、`validate_evidence.py` 与旧记录中的 SHA-256 不同。输出 WAV 的哈希仍然吻合。上面的离线练习读取归档回答；若要判断当前代码运行后会怎样回答，请把新结果写到自己的运行目录里再比较。

| 任务 | 端到端 | 自级联 |
| --- | ---: | ---: |
| 语义算术（2 条） | 1/2 | 2/2 |
| 副语言语速（2 条） | 2/2 | 1/2 |
| 合计 | 3/4 | 3/4 |

两条路径都答对三题，错的却是不同的题。第一题有 12 盒铅笔，每盒 8 支，送出 17 支。直接听录音的模型在回答中写出了 `8 × 8 − 17 = 47`。这道算式本身算得对，错的是代入的盒数。自级联路径先把 “twelve boxes” 转写正确，再算出 `12 × 8 − 17 = 79`。相反，快/慢两条音频在自级联中都被压成完全相同的 `Please send the report before lunch.`，于是它把 fast 样本也猜成 slow；端到端保留了速度信息，两条都正确。

加载完成后的平均整次调用为端到端 0.686 秒、自级联 0.551 秒。由于端到端固定先跑、回复长度不同且只有四条，这不是可推广的延迟排名。audio-to-audio 臂另生成了[11.56 秒、24kHz 单声道 WAV](validation/runs/exp6-5-minicpmo45-20260801-v1/outputs/spoken-math-boxes-response.wav)，但它继承了第一题的感知错误。试听这段输出时，可以分开记下两件事：模型能把答案说出来，它说出的数是否符合原题。

---

### 检查自己的解释

如果模型能识别语速却不能据此调整回复，说明感知与决策之间还缺少什么？

## English

Experiment 6-6 belongs to Paradigm 2, end-to-end omni models. Historical canonical paths retain the `exp6-5-*` identifier. It runs the pinned MiniCPM-o 4.5 checkpoint locally and compares native audio-to-answer inference against a self-cascade that first flattens the same audio to text. A separate audio-output arm retains a real 24kHz waveform. Thinking is deliberately disabled; this experiment makes no MPS or “thinking while speaking” claim.
