# 实验 6-5：Qwen2-Audio 递增前缀模拟流式感知

“麻烦你帮我把明天下午的会议改到两点半，地点……”对方停了近一秒，又接着说“还是在三号会议室，别忘了通知大家”。如果助理一听见停顿就开始答话，很可能错过后半句。先听听[带停顿的录音](validation/scenarios/long_pause.wav)，想一想：在哪一刻，你觉得可以接话了？

[English](#english)

<a id="learning-0"></a>

## 理解问题与方法

实验让两套程序听同一段话。一套每收到两秒新音频，就把从开头到当前位置的录音重新交给 Qwen2-Audio，要求它写下已经听见的文字和声学事件。另一套用语音活动检测（VAD）找端点：静音持续到 600 毫秒，就把前一段送给 Whisper 转写。前者可以在话还没说完时给出暂时的理解，代价是每次都要重新编码已经听过的声音；后者可以分段处理，但一句话里也会有停顿。

从[原始录音](audio/sentence.wav)出发，实验准备了正常、插入 900 毫秒静音、混入粉红噪声三个版本。每个版本都保留了各次转写、处理耗时和最终字错率（CER）。读记录时留意两种时间：模型听到了录音的第几秒，以及处理这段输入花了多少秒。本实验用的是 `Qwen/Qwen2-Audio-7B-Instruct` 架构，运行文件沿用实验调整编号前的 `exp6-4-*` 标识。

<a id="learning-1"></a>

## 准备环境与输入

读者可以先用下文的[逐段对照练习](#learning-2)查看已有运行，无需安装模型。要自行生成识别结果，再准备下面的环境。

### 安装

```bash
# From the repository root: use the shared Chapter 6 core environment
uv sync --locked --python 3.12 --extra ch6

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch6]"

cd chapter6/streaming-speech

# Install this experiment's local audio/model runtime dependencies.
python -m pip install -r requirements.txt
```

下面是一条完整的 Apple Silicon 命令，使用 4-bit MLX 权重，语言模型量化，音频编码器和投影层保持 BF16。在 NVIDIA GPU 上，把同一条命令的 `--model` 和 `--device` 分别改为 `Qwen/Qwen2-Audio-7B-Instruct` 和 `cuda`，其余音频与问题可以保持一致。

```bash
run=$(mktemp -d validation/my-run.XXXXXX)
python prepare_scenarios.py audio/sentence.wav "$run/scenarios"

python demo.py \
  --model mlx-community/Qwen2-Audio-7B-Instruct-4bit --device mlx \
  --chunk-seconds 2 --whisper-model tiny --evidence "$run/evidence.json" \
  --audio "$run/scenarios/normal.wav" --scenario normal \
  --reference '麻烦你帮我把明天下午的会议改到两点半，地点还是在三号会议室，别忘了通知大家。' \
  --audio "$run/scenarios/long_pause.wav" --scenario pause \
  --reference '麻烦你帮我把明天下午的会议改到两点半，地点还是在三号会议室，别忘了通知大家。' \
  --audio "$run/scenarios/background_noise.wav" --scenario noise \
  --reference '麻烦你帮我把明天下午的会议改到两点半，地点还是在三号会议室，别忘了通知大家。'
```

这条命令把重建的录音和结果放进新目录。生成粉红噪声时没有固定随机种子；如需逐字复核书中的输出，可直接使用仓库保留的三个场景 WAV。`--skip-whisper` 只用于单独调试 Qwen，不能完成书中的对照验收。原始 BF16 模型约 16.8GB；MLX 量化权重约 6.6GB。

保持上述科学设计不变并生成完整验收 manifest：

```bash
python run_official_experiment.py --run-id exp6-4-qwen2audio-whisper-provenance-YYYYMMDD-vN
```

官方 runner 在运行前后核对源码 hash，并绑定三类测试音频、原始源音频、Whisper
checkpoint、Qwen2-Audio snapshot 的每个文件（包括 6.56GB 权重）、13 个原始前缀
输出、运行日志和独立 acceptance 文件。

<a id="learning-2"></a>

## 按照步骤完成实验

在本实验目录运行以下命令，查看长停顿样本的每一次判断。第一列是送入模型的音频长度，第二列是本次推理耗时。

```bash
python3 - <<'PYTHON'
import json
from pathlib import Path

run = Path("validation/runs/exp6-4-qwen2audio-whisper-provenance-20260730-v3")
cases = json.loads((run / "evidence.json").read_text())["cases"]
case = next(item for item in cases if item["scenario"] == "pause")
for step in case["qwen2_audio"]:
    print(step["prefix_seconds"], round(step["inference_seconds"], 2),
          step["transcript"], step["acoustic_events"])
vad = case["whisper_vad"]
print("首段末尾与作出分段判断的时刻：", vad["first_endpoint_audio_seconds"],
      vad["first_decision_audio_seconds"])
print("分段转写：", vad["segment_transcripts"])
PYTHON
```

在录音时间轴上，首段末尾位于 4.04 秒，VAD 到 4.64 秒才作出判断，中间正好等了 600 毫秒。读一读两段转写，连起来才是完整的改会请求。再看另一套程序：只给前两秒音频，它已经写出了“明天下午的会议”，但这次推理本身用了约 8.41 秒。一个程序能根据半句话给出部分转写，并不能保证它赶得上说话人的速度。

<a id="learning-3"></a>

## 分析结果与形成判断

部分转写后来可能被修正；越早输出不一定越准确。比较时同时看文字错误率、单次处理时间和停止判断，尤其检查长停顿是否造成错误分段。

### 已有运行结果

本节引用的运行清单是 [`validation/runs/exp6-4-qwen2audio-whisper-provenance-20260730-v3/manifest.json`](validation/runs/exp6-4-qwen2audio-whisper-provenance-20260730-v3/manifest.json)。
2026-07-30 在 Apple Silicon 上严格复跑 `mlx-community/Qwen2-Audio-7B-Instruct-4bit`；8/8
执行与溯源门禁通过，但六项行为预期只观察到两项。13 次前缀推理实测 8.4–11.3s，不能据此声称
100–200ms；传统路径也未在三类输入上全部落入 800–1100ms。900ms 停顿被 VAD 分为两段，
但 Qwen 漏报 `<|silence|>`；强噪声样本检出 `<|noise|>`，同时误报 `<|cough|>` 与
`<|laughter|>`。这些负结果与所有原始响应都保留在验收记录中。2026-07-29 的 `latest.json`
和 `latest_v2.json` 作为历史运行保留，可供对照早期结果。

仅核对已归档的文字和事件结果，可用下列第一条命令。第二条还要核对原运行的依赖与本地模型缓存；普通 Git 检出只带运行记录和音频。

```bash
python -m pytest -q test_official_experiment.py::test_official_run_retains_raw_prefixes_and_negative_manuscript_results
pytest -q
```

---

### 检查自己的解释

如果前缀越长处理越慢，怎样区分模型本身的实时能力与反复重编码带来的开销？

## English

This is actual Qwen2-Audio growing-prefix inference, not a Whisper substitute. Every `[0:t]` prefix is fully re-encoded and compared with a real 600ms-VAD + open-source Whisper pipeline on normal, long-pause, and noisy speech. CUDA uses the original model; Apple Silicon can use the published 4-bit MLX conversion of the same Qwen2-Audio architecture. The canonical v3 manifest binds raw responses, sources, audio, the Whisper checkpoint, and every Qwen snapshot file. Execution passed while the manuscript result bundle did not: only 2/6 claims reproduced, with 8.4–11.3s prefix inference and retained acoustic-event errors.

### 归档材料复核（2026-10-07）

本次只读复核中，manifest 列出的三个场景音频及三个运行产物哈希一致；当时的工作树缺少原始输入。此次修订已从原实验工作区补回 `audio/sentence.wav`，其 SHA-256 与清单一致。模型缓存与运行源码另有各自的版本记录，场景音频是本次回看前缀输入的依据。历史 manifest 保持原样。
