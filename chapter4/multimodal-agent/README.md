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

如果读错数值，检查坐标轴、单位和图例有没有保留；如果漏掉关系，检查文本抽取是否丢失布局。示例正确不代表任意扫描件或复杂表格都适用。

### 区分抽取错误与理解错误

先打开原始文档，选一个包含表格、图像或复杂版面的页面，手工记录需要回答的信息。比较各抽取模式交给模型的实际内容：如果数字或布局关系已经在抽取时丢失，后续问答无法凭空补回。若抽取结果完整而回答仍然错误，再分析模型的理解与证据引用。

### 检查自己的解释

哪些问题只需要文字，哪些问题必须保留版面或空间关系？

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
