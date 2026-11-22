# Multimodal Agent — Three Extraction Paradigms / 多模态 Agent——三种抽取范式对比

同一张季度收入图上，模型读出了最低收入 9500 万美元，却把季度答错了。要找原因，先看它收到的是整张图，还是从图里抽出来的一串文字。你可以在本地生成样例，打开归档回答，跟着这条错误一路查到输入。

[English](#english)

[同一份图表怎样进入模型](#learning-0) · [选择已有样本与模型](#learning-1) · [对照三条信息提取路径](#learning-2) · [定位数值或季度在哪一步丢失](#learning-3) · [文件与模型接口](#learning-4) · [参考资料](#learning-5)

<a id="learning-0"></a>

## 同一份图表怎样进入模型

先在原图中找到最低的柱子，读出柱顶的金额和正下方的季度。模型直接看图时，这两条线索在同一张图上；只读文字时，就要检查提取结果有没有保留两者的对应关系。第三条路径让模型在文字不足时调用工具回看图表。

### 功能——三种抽取模式

1. **原生多模态**：直接用模型内置能力（Gemini PDF/图/音频；GPT/豆包图像等）  
2. **先抽文本再推理**：PDF OCR、图像描述、Whisper/Gemini 转写  
3. **多模态分析工具**：跟进问题的图像 / 音频 / PDF 工具

### 架构

```
MultimodalAgent
├── Configuration (config.py)
├── Agent Core (agent.py)
└── Multimodal Tools
```

### 模式对比

| 模式 | 优势 | 劣势 | 适用 |
|------|------|------|------|
| **原生** | 上下文与视觉完整 | 模型支持有限、token 多 | 复杂混排文档 |
| **抽文本** | 通用、可缓存 | 丢视觉细节 | 文本向 / 控成本 |
| **工具** | 可追问、按需深挖 | 多次 API | 交互式问答 |

<a id="learning-1"></a>

## 选择已有样本与模型

先看同一张图对应的图片、提取文本和工具输出。等你能认出哪份材料保留了季度与数字的对应关系，再按下文配置要重跑的模型。

### 安装

```bash
# 在仓库根目录安装绘图、文档生成和模型接口依赖
uv sync --locked --python 3.12 --extra viz --extra docs --extra providers

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[viz,docs,providers]"

cd chapter4/multimodal-agent

# 如需使用项目原有的依赖清单：
# python -m pip install -r requirements.txt

# 只做离线样例可跳过这一步。在线交互演示从 .env 读取所选服务的密钥。
cp env.example .env
```

### API Key

- `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`  
- `OPENAI_API_KEY`  
- `DOUBAO_API_KEY` 或 `ARK_API_KEY`

<a id="learning-2"></a>

## 对照三条信息提取路径

先运行样例生成器，打开生成的图表与报告，人工确认正确答案。随后按下文配置模型，对同一文件提出同一问题，分别观察直接读取、提取文本和工具分析的过程。

### 离线快速开始（无需 API Key）

生成带图表的样例报告——**精确季度数字只在柱状图里**，方便测三种范式取舍：

```bash
python create_sample.py
```

先自己看图，写下最低的季度、该季度的收入和第四季度比它高出的金额。装有 Tesseract 和 Poppler 时，可以在本地运行与归档相同的两条提取命令：

```bash
tesseract test_files/sample_chart.png stdout --psm 6
pdftotext -layout test_files/sample_report.pdf -
```

先在 OCR 输出里找 95M，再试着只凭这些文字确定它属于哪个季度。接着读 PDF 的文本层，找一找哪句话能说明第四季度的走势、哪句话给出了金额。本机版本的 OCR 排版可能不同，可以对照[原始记录](validation/runs/20260729T185433Z-4_2-e028c9db/evidence.json)中两项材料的 `artifacts[].extracted_text`。没有安装这两个工具也能直接读记录做题。

下面用交互演示程序比较三条路径，需要视觉模型的 API Key。书中汇总的十二个回答来自 [campaign.py](campaign.py) 对两种材料、两道问题和三条路径的固定对照。

```bash
python demo.py \
  --file test_files/sample_chart.png \
  --query "Which quarter had the highest revenue, and what was the exact value?" \
  --model gpt-5.6-luna
```

要复跑书中的固定对照，请在本目录准备 Tesseract 和 Poppler（含 `pdftotext`、`pdftoppm`）。在环境中设置 `ARK_API_KEY` 或 `DOUBAO_API_KEY` 供回答模型使用，另设 `MOONSHOT_API_KEY` 供评审模型使用，然后运行 `python campaign.py`。如果密钥写在本目录的 `.env`，可用 `uv run --no-sync --env-file .env python campaign.py` 显式加载。新运行会生成自己的回执和用量记录。

### 用法

```bash
python main.py --interactive
# /file /mode /model /tools /history /clear /quit

python main.py --file document.pdf --query "What is the main topic?"
python main.py --mode extract_to_text --file image.jpg --query "Describe this image"
python main.py --tools --mode extract_to_text --file audio.mp3 --query "What's the content?"
```

程序化用法见 English 节 `asyncio` 示例。

### 对比演示

```bash
python demo.py --file document.pdf --query "What are the key findings?" --model gpt-5.6-luna
python demo.py --file test_files/sample_chart.png \
  --query "Which quarter had the highest revenue?" \
  --model gpt-5.6-luna --skip-model-comparison --output result.txt
```

| 标志 | 说明 |
|------|------|
| `--file` | 多模态文件 |
| `--query` | 问题 |
| `--model` | 默认 `gemini-3.5-flash` |
| `--skip-model-comparison` | 只做三范式对比 |
| `--generate-sample` | 离线生成样例后退出 |
| `--output`, `-o` | 保存完整记录 |

### 测试

```bash
python test_multimodal.py
```

<a id="learning-3"></a>

## 定位数值或季度在哪一步丢失

### 从输入内容定位错误

先打开原始材料，记录问题需要用到的数值与对应关系，再比较各模式实际交给模型的内容。读错数值时，检查坐标轴、单位和图例；漏掉关系时，检查文本抽取是否保留布局。若所需信息已在抽取阶段丢失，应先改进提取或补充视觉输入；若信息完整，再分析模型的理解与引用。

### 已保存的三路径对照

正式记录见 [`evidence.json`](validation/runs/20260729T185433Z-4_2-e028c9db/evidence.json)，原始请求、响应与用量见同目录的 `receipts.json`。历史文件中的实验编号 `4-2` 对应当前书中的实验 4-3。

本次使用 `doubao-seed-1-6-250615` 完成三条路径的回答，`moonshot-v1-8k` 对照参考答案评判。材料为同一组季度收入数据的 PNG 图表和含图 PDF，每种材料回答最高收入、最低收入及差额两个问题，共四个材料—问题组合。PDF 经页面渲染后进入视觉路径；文本路径分别使用 Tesseract OCR 和 `pdftotext -layout`。

| 路径 | 完整答对 | 平均耗时（秒） | 回答模型调用数 | 输入 token 合计 | 输出 token 合计 |
| --- | ---: | ---: | ---: | ---: | ---: |
| 直接看图 | 4/4 | 8.01 | 4 | 4,472 | 1,415 |
| 提取为文本 | 0/4 | 10.87 | 4 | 854 | 1,932 |
| 按需调用视觉工具 | 4/4 | 29.79 | 12 | 8,677 | 5,392 |

用量由原始回执汇总，不含外部裁判。工具路径包含决策、视觉分析和最终回答三次调用，四个组合都调用了 `inspect_visual`。文本和工具路径的计时包含本地文本提取；直接看图的计时从模型调用前开始，PDF 页面渲染发生在此前。该表描述当前运行的计时口径。

先比较文本组收到的两份材料。PNG 的 OCR 结果有 180M、150M、120M、95M，也混着纵轴刻度，季度标签另在末行。PDF 的文本层则只提到年中回落、最后一季反弹。前一种情况下，模型要判断哪个数属于哪一季；后一种情况下，它连可以拿来计算的金额都没有。

工具路径的系统提示词明确要求：提取文本无法确定数值或空间对应时，调用视觉工具。这个设置用于展示补充视觉证据的过程。扩展实验时，可增加纯文字即可作答的问题，检验模型能否合理决定何时使用工具，并分别统计正确率、调用次数、输入输出用量和端到端耗时。

读 `png:extract:lowest_gap` 这条回答：它报出 95M 和 85M，却把最低收入归给 Q1。核对时，把三项事实分开勾选：最低的是 Q3，它的收入为 95M，Q4 高出 85M。脚本的 `exact_correct` 只检查这三个标记是否出现；即使都出现了，仍要读完整句子，查清两个金额分别指什么。记录另附评审模型对照参考答案给出的判断。直接看图和工具路径均完整答对，文本路径均未完整答对。记录完整性检查已核对 `evidence.json` 与 `receipts.json` 的 manifest 哈希。

<a id="learning-4"></a>

## 文件与模型接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 4 — **Experiment 4-3**: native multimodal vs extract-to-text vs tool-based analysis.  
> 配套《深入理解 AI Agent》第 4 章 **实验 4-3**：原生多模态 vs 先抽文本 vs 工具化分析。

← [Chapter 4 index / 返回第 4 章目录](../README.md)

---

### 文件与模型能力

支持 PDF / 常见图像 / 常见音频；大小限制 PDF/图 20MB、音频 25MB。能力矩阵与 English 表相同。

<a id="learning-5"></a>

## 参考资料

### 许可

MIT — 教学项目。

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

Chat / vision can route via OpenRouter when `OPENROUTER_API_KEY` is set and primary keys are missing. **Audio transcription (Whisper) and native-PDF extraction still need direct OpenAI/Gemini keys.**

## English

### Features — three extraction modes

1. **Native Multimodality**: model built-in multimodal  
   - Gemini 2.5 Pro: PDF, image, audio  
   - GPT-5/GPT-4o: images (OpenAI multimodal format)  
   - Doubao 1.6: images  

2. **Extract to Text**: convert first, then reason  
   - PDF OCR (Gemini or GPT-5)  
   - Image captions (GPT-5 or Doubao 1.6)  
   - Audio: Whisper or Gemini  

3. **Multimodal analysis tools**: add-on for follow-ups  
   - Image / audio / PDF analysis tools  

### Architecture

```
MultimodalAgent
├── Configuration (config.py)
├── Agent Core (agent.py) — messages, history, modes, streaming
└── Multimodal Tools — image, audio, PDF analysis
```

### Installation

```bash
# From the repository root: install the plotting, document and provider extras
uv sync --locked --python 3.12 --extra viz --extra docs --extra providers

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[viz,docs,providers]"

cd chapter4/multimodal-agent

# To use the original project requirements instead:
# python -m pip install -r requirements.txt

# For the online interactive demo, enter the chosen provider key in .env.
cp env.example .env
```

### Quick offline start (no API key)

Generate a chart-bearing sample so Experiment 4-3 is measurable—**exact quarterly figures live only in the chart bars**, not surrounding text:

```bash
python create_sample.py           # or: python demo.py --generate-sample
# → test_files/sample_chart.png, test_files/sample_report.pdf
```

Then compare three paradigms (needs vision API key):

```bash
python demo.py \
  --file test_files/sample_chart.png \
  --query "Which quarter had the highest revenue, and what was the exact value?" \
  --model gpt-5.6-luna
```

Chinese `--help` on `demo.py` / `main.py` / `create_sample.py`.

### Usage

#### Interactive

```bash
python main.py --interactive
```

Commands: `/file <path>`, `/mode <native|extract_to_text>`, `/model <name>`, `/tools <on|off>`, `/history`, `/clear`, `/quit`.

#### Single file

```bash
python main.py --file document.pdf --query "What is the main topic?"
python main.py --mode extract_to_text --file image.jpg --query "Describe this image"
python main.py --tools --mode extract_to_text --file audio.mp3 --query "What's the content?"
```

#### Programmatic

```python
import asyncio
from agent import MultimodalAgent, MultimodalContent
from config import ExtractionMode

async def example():
    agent = MultimodalAgent(
        model="gemini-3.5-flash",
        mode=ExtractionMode.NATIVE,
        enable_tools=True
    )
    content = MultimodalContent(type="pdf", path="document.pdf")
    result = await agent.process_multimodal_content(content, "Summarize this document")
    print(result)
    async for chunk in agent.chat("Tell me more about the key points", stream=True):
        print(chunk, end="", flush=True)

asyncio.run(example())
```

### Demo comparison

```bash
python demo.py --file document.pdf --query "What are the key findings?" --model gpt-5.6-luna
python demo.py document.pdf "What are the key findings?"   # positional still works
python demo.py --file test_files/sample_chart.png \
  --query "Which quarter had the highest revenue?" \
  --model gpt-5.6-luna --skip-model-comparison --output result.txt
```

Runs: (1) native (2) extract-to-text (3) extract + tools (4) cross-model unless skipped.

| Flag | Description |
|------|-------------|
| `--file` / positional | Image / PDF / audio |
| `--query` / positional | Question |
| `--model` | Default `gemini-3.5-flash` |
| `--skip-model-comparison` | Only three-paradigm compare |
| `--generate-sample` | Offline sample then exit |
| `--output`, `-o` | Transcript file |

### Mode comparison

| Mode | Advantages | Disadvantages | Best for |
|------|------------|---------------|----------|
| **Native** | Full context; better vision | Limited models; more tokens | Mixed complex docs |
| **Extract to Text** | Any text model; cacheable | Loses visual context | Text-heavy / cost |
| **With Tools** | Follow-ups; selective depth | More API calls | Interactive Q&A |

### Supported files / models

- PDF (best native Gemini), images (JPEG/PNG/GIF/BMP/WebP), audio (MP3/WAV/M4A/FLAC/AAC/OGG)  
- Size limits: PDF/images 20MB, audio 25MB  

| Model | Native PDF | Native Image | Native Audio | Extract | Tools |
|-------|------------|--------------|--------------|---------|-------|
| Gemini 2.5 Pro | ✅ | ✅ | ✅ | ✅ | ✅ |
| GPT-5/GPT-4o | ❌ | ✅ | ❌ | ✅ | ✅ |
| Doubao 1.6 | ❌ | ✅ | ❌ | ✅ | ✅ |

### API keys

- `GOOGLE_API_KEY` or `GEMINI_API_KEY` — PDF/audio native  
- `OPENAI_API_KEY` — GPT + Whisper  
- `DOUBAO_API_KEY` or `ARK_API_KEY`  

### Testing / best practices

```bash
python test_multimodal.py
```

Prefer native when vision/audio fidelity matters; extract-to-text for cost/cache; tools for multi-turn. Validate files and keys; handle rate limits.

### License

MIT License — educational project.

---
