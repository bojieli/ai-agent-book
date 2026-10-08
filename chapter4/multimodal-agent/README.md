# Multimodal Agent — Three Extraction Paradigms / 多模态 Agent——三种抽取范式对比

回答图表问题时，模型可以直接读取图像，也可以先通过工具提取文字和数据。本实验比较几种输入路径，学习选择方式时需要考虑哪些信息可能丢失。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4) → [排查问题与查阅资料](#learning-5)。

<a id="learning-0"></a>

## 理解问题与方法

直接多模态输入保留视觉布局，文本抽取便于后续检索与计算，工具化分析还可以针对局部内容处理。每条路径都会改变模型看到的材料，因而不能只比较最终回答长度。

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

## 准备环境与输入

先从本地示例开始。依赖安装可能需要联网，但下面标明的离线路径不需要模型 API Key。若随后切换到真实模型，请再完成相应的服务配置。

### 安装

```bash
# 在仓库根目录使用统一的第 4 章环境
uv sync --locked --python 3.12 --extra ch3

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch3]"

cd chapter4/multimodal-agent

# 精确复现旧版单项目环境，含 python-magic 文件类型检测：
# python -m pip install -r requirements.txt

cp env.example .env
# 编辑 API Key
export $(cat .env | xargs)   # Unix 可选
```

### API Key

- `GOOGLE_API_KEY` 或 `GEMINI_API_KEY`  
- `OPENAI_API_KEY`  
- `DOUBAO_API_KEY` 或 `ARK_API_KEY`

<a id="learning-2"></a>

## 按照步骤完成实验

先运行样例生成器，打开生成的图表与报告，人工确认正确答案。随后按下文配置模型，对同一文件提出同一问题，分别观察直接读取、提取文本和工具分析的过程。

### 离线快速开始（无需 API Key）

生成带图表的样例报告——**精确季度数字只在柱状图里**，方便测三种范式取舍：

```bash
python create_sample.py
```

再对比三种范式（需视觉 API Key）：

```bash
python demo.py \
  --file test_files/sample_chart.png \
  --query "Which quarter had the highest revenue, and what was the exact value?" \
  --model gpt-5.6-luna
```

各 CLI 均有中文 `--help`。

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

## 分析结果与形成判断

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

PNG 的 OCR 结果保留了 180M、150M、120M、95M 等数值，却混入纵轴刻度并丢失季度对应关系，文本组把最高和最低收入都误配给 Q1。PDF 的文本层只有趋势说明，提取结果中没有图表的精确数值。两个视觉路径都恢复了正确关系：Q4 为 180M，Q3 为 95M，差额为 85M。

工具路径的系统提示词明确要求：提取文本无法确定数值或空间对应时，调用视觉工具。这个设置用于展示补充视觉证据的过程。扩展实验时，可增加纯文字即可作答的问题，检验模型能否合理决定何时使用工具，并分别统计正确率、调用次数、输入输出用量和端到端耗时。

判分脚本检查参考答案中的季度与数字是否出现，并保留了外部裁判的解释；本轮已逐条复核十二个回答。直接看图和工具路径均完整答对，文本路径均未完整答对。记录完整性检查已核对 `evidence.json` 与 `receipts.json` 的 manifest 哈希。

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 4 — **Experiment 4-3**: native multimodal vs extract-to-text vs tool-based analysis.  
> 配套《深入理解 AI Agent》第 4 章 **实验 4-3**：原生多模态 vs 先抽文本 vs 工具化分析。

← [Chapter 4 index / 返回第 4 章目录](../README.md)

---

### 文件与模型能力

支持 PDF / 常见图像 / 常见音频；大小限制 PDF/图 20MB、音频 25MB。能力矩阵与 English 表相同。

<a id="learning-5"></a>

## 排查问题与查阅资料

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
# From the repository root: use the shared Chapter 4 environment
uv sync --locked --python 3.12 --extra ch3

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch3]"

cd chapter4/multimodal-agent

# Exact legacy parity path, including python-magic file sniffing:
# python -m pip install -r requirements.txt

cp env.example .env
# Edit .env with API keys
export $(cat .env | xargs)   # optional on Unix
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
