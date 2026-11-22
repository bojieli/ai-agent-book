# User Memory System / 用户记忆系统

保存全部聊天记录，不等于下次对话能用上相关信息。本实验把交互与后台记忆处理分开，学习怎样从对话提取候选事实、更新存储，并在后续回答中检索它们。

[English](#english)

建议按以下顺序阅读：[理解问题与方法](#learning-0) → [准备环境与输入](#learning-1) → [按照步骤完成实验](#learning-2) → [分析结果与形成判断](#learning-3) → [阅读实现与继续探索](#learning-4)。

<a id="learning-0"></a>

## 理解问题与方法

对话模块负责当前响应，后台模块负责整理长期信息。这样可以区分“刚才说过什么”与“值得长期保留什么”。不同存储模式改变组织方式，却都需要处理来源、冲突和时间变化。

### 关键特性

- **分离架构**：对话 Agent 与后台记忆处理器解耦  
- **多种记忆模式**：简单笔记 → 增强笔记 → JSON 卡片 → Advanced JSON Cards  
- **多提供商**：Kimi、SiliconFlow、豆包、OpenRouter  
- **React + 工具** 结构化记忆操作  
- **流式输出**、**评测集成**、**按间隔后台更新**、**JSON 持久化**

### 架构

用户界面 → **ConversationalAgent**（对话、读记忆、流式）+ **BackgroundMemoryProcessor**（分析并写记忆）→ **MemoryManager**（笔记/JSON 卡片）。

核心文件：`conversational_agent.py`、`background_memory_processor.py`、`agent.py`、`memory_manager.py`。

### 记忆模式

1. **`notes`** — 短事实  
2. **`enhanced_notes`** — 带上下文的段落  
3. **`json_cards`** — 层次化 JSON  
4. **`advanced_json_cards`** — 含 backstory / person / relationship 等完整卡片

### 说明

记忆后台异步处理；工具调用可记录；支持流式；状态跨会话持久。教学材料。

---

<a id="learning-1"></a>

## 准备环境与输入

下面会用到模型服务。先按配置说明选择一个提供商，准备对应的模型名称、服务地址和 API Key，再运行小规模例子。一次完整运行的费用取决于模型、输入长度和调用次数。

### 安装

```bash
# 在仓库根目录使用统一的第 3 章环境
uv sync --locked --python 3.12 --extra ch3

# 切换目录前先激活环境：
# macOS/Linux：
source .venv/bin/activate
# Windows PowerShell：.venv\Scripts\Activate.ps1
# Windows cmd：.venv\Scripts\activate.bat

# 未安装 uv 时可用 pip 兜底：
# python -m pip install -e ".[ch3]"

cd chapter3/user-memory

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt

cp env.example .env
# 配置 MOONSHOT_API_KEY / SILICONFLOW_API_KEY / DOUBAO_API_KEY / OPENROUTER_API_KEY
```

### 提供商

见 English 表与 `--provider` / `--model` 示例。

### 高级配置与项目结构

环境变量、`main.py` CLI 参数、目录树与 English 节相同。

<a id="learning-2"></a>

## 按照步骤完成实验

配置模型后先运行演示。对照一轮原始对话、后台提取的内容和后续回答，再修改一个用户事实继续观察。读代码时先看对话模块怎样读取记忆，再看后台处理器什么时候提交更新。

### 用一次写入和一次追问检查记忆

先输入一条容易核对、且不涉及真实隐私的偏好，例如“演示用户希望回答附带单位”。完成写入后，查看实际保存的记录，再用一个确实需要单位的问题追问。最后提出一个与该偏好无关的问题，检查系统是否错误地到处套用它。这样能依次检查保存、检索和使用三个环节。

### 快速开始

```bash
python quickstart.py
python main.py --mode interactive --user your_name
# memory | process | save | reset | quit/exit

python main.py --mode demo --memory-mode enhanced_notes
python main.py --mode evaluation --memory-mode advanced_json_cards
```

### 运行模式

```bash
python main.py --mode interactive --user john_doe --memory-mode enhanced_notes --conversation-interval 2
python main.py --mode demo --provider siliconflow --memory-mode json_cards
python main.py --mode evaluation --memory-mode advanced_json_cards --provider kimi
```

### 冒烟测试

```bash
python quickstart.py
python -c "from memory_manager import NotesMemoryManager; m=NotesMemoryManager('smoke'); print(m.consolidate_memories())"
```

<a id="learning-3"></a>

## 分析结果与形成判断

检查系统是否把临时计划误写成永久偏好，或把模型自己的猜测保存成用户事实。回答提到了某条信息，也应能追溯到用户真正说过的内容。

### 评测

```bash
python main.py --mode evaluation --memory-mode advanced_json_cards
```

对接 `user-memory-evaluation` 的用例与打分。

### 检查自己的解释

哪些信息只应该保留在本轮上下文，哪些适合长期存储？用户纠正事实时应发生哪些更新？

<a id="learning-4"></a>

## 阅读实现与继续探索

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — long-term user memory with separated conversation vs background processing, multiple memory modes, multi-provider support.  
> 配套《深入理解 AI Agent》第 3 章——长期用户记忆：对话与后台记忆处理分离、多种记忆模式、多模型提供商。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 编程接口

见 English 节 `ConversationalAgent` / `BackgroundMemoryProcessor` / `UserMemoryAgent` 示例。

### 代码阅读顺序

- **Run first:** python main.py --mode demo --memory-mode enhanced_notes.
- **Start here:** conversational_agent.py::ConversationalAgent.chat reads memory without directly persisting it.
- **Core behavior:** background_memory_processor.py::BackgroundMemoryProcessor.process_recent_conversations extracts candidates and applies updates.
- **State / protocol:** memory_manager.py owns mode-specific storage; conversation history remains separate.
- **Verifier:** user-memory-evaluation and the evaluation mode compare evidence, not only generated summaries.
- **Experiment variable:** notes, enhanced notes, JSON cards and advanced JSON cards.
- **Skip on first pass:** provider adapters, streaming presentation and benchmark helpers.

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

Primary provider keys take precedence; else `OPENROUTER_API_KEY` routes chat LLM via OpenRouter with automatic model id mapping. See `env.example`. Related: [`../user-memory-evaluation/`](../user-memory-evaluation/), [`../mem0/`](../mem0/), [`../memobase/`](../memobase/).

## English

### Key features

- **Separated architecture**: conversational agent vs background memory processor  
- **Memory modes**: notes → enhanced notes → JSON cards → advanced JSON cards  
- **Providers**: Alibaba Cloud DashScope/Bailian (Qwen), Kimi/Moonshot, SiliconFlow, Doubao, OpenRouter
- **React + tools** for structured memory ops  
- **Streaming** with tool calls  
- **Evaluation** integration with `user-memory-evaluation`  
- **Background processing** on conversation intervals  
- **Persistent** JSON storage + conversation history  

### Installation

Python 3.12 with the root `ch3` extra, plus at least one LLM API key.

```bash
# From the repository root: use the shared Chapter 3 environment
uv sync --locked --python 3.12 --extra ch3

# Activate it before changing directories:
# macOS/Linux:
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
# Windows cmd: .venv\Scripts\activate.bat

# pip fallback when uv is not installed:
# python -m pip install -e ".[ch3]"

cd chapter3/user-memory

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt

cp env.example .env
# DASHSCOPE_API_KEY / MOONSHOT_API_KEY / SILICONFLOW_API_KEY / DOUBAO_API_KEY / OPENROUTER_API_KEY
```

### Quick start

```bash
python quickstart.py

python main.py --mode interactive --user your_name
# interactive: memory | process | save | reset | quit/exit

python main.py --mode demo --memory-mode enhanced_notes
python main.py --mode evaluation --memory-mode advanced_json_cards
```

### Architecture

```
User Interface
  → Conversational Agent (dialogue, read memory, stream; no direct writes)
  → Background Memory Processor (analyze, update via tools)
  → Memory Manager (notes / JSON cards storage)
```

**Core modules:** `conversational_agent.py`, `background_memory_processor.py`, `agent.py` (UserMemoryAgent + tools), `memory_manager.py`.

### Memory modes

1. **`notes`** — short facts/preferences  
2. **`enhanced_notes`** — contextual paragraphs  
3. **`json_cards`** — hierarchical JSON  
4. **`advanced_json_cards`** — full cards with backstory, person, relationship, timestamps  

### Execution modes

```bash
python main.py --mode interactive \
    --user john_doe \
    --memory-mode enhanced_notes \
    --conversation-interval 2

python main.py --mode demo --provider siliconflow --memory-mode json_cards
python main.py --mode evaluation --memory-mode advanced_json_cards --provider kimi
```

### Providers

| Provider | Models (examples) | Notes |
|----------|-------------------|--------|
| DashScope / Bailian (Qwen) | qwen3.7-plus | Alibaba Cloud Model Studio; `qwen` and `bailian` are aliases |
| Kimi/Moonshot | kimi-k3 | Chinese, general |
| SiliconFlow | Qwen3-235B-… | High performance |
| Doubao | doubao-seed-1-6-thinking-… | ByteDance |
| OpenRouter | Gemini / GPT / Claude | Multi-model |

```bash
python main.py --provider siliconflow --model "Qwen/Qwen3-235B-A22B-Thinking-2507"
python main.py --provider openrouter --model "google/gemini-3.5-flash"
python main.py --provider doubao --model "doubao-seed-1-6-thinking-250715"
python main.py --provider dashscope --model "qwen3.7-plus"
```

### API usage

```python
from conversational_agent import ConversationalAgent, ConversationConfig
from config import MemoryMode

agent = ConversationalAgent(
    user_id="user123",
    provider="kimi",
    config=ConversationConfig(enable_memory_context=True, temperature=0.7),
    memory_mode=MemoryMode.ENHANCED_NOTES
)
response = agent.chat("Hi, I'm Alice and I work at TechCorp")
```

```python
from background_memory_processor import BackgroundMemoryProcessor, MemoryProcessorConfig

processor = BackgroundMemoryProcessor(
    user_id="user123",
    provider="kimi",
    config=MemoryProcessorConfig(conversation_interval=2, enable_auto_processing=True),
    memory_mode=MemoryMode.JSON_CARDS
)
processor.start_background_processing()
results = processor.process_recent_conversations()
```

```python
from agent import UserMemoryAgent, UserMemoryConfig

agent = UserMemoryAgent(
    user_id="user123",
    provider="siliconflow",
    config=UserMemoryConfig(enable_memory_updates=True, memory_mode=MemoryMode.ADVANCED_JSON_CARDS)
)
result = agent.execute_task("Remember that I prefer Python and my email is john@example.com")
```

### Evaluation

```bash
python main.py --mode evaluation --memory-mode advanced_json_cards
```

Uses test cases from `user-memory-evaluation` (histories → question → score/feedback; 60+ cases).

### Advanced configuration

```bash
PROVIDER=kimi
# For DashScope/Bailian, use PROVIDER=dashscope (or qwen/bailian) and set DASHSCOPE_API_KEY.
MODEL_TEMPERATURE=0.3
MODEL_MAX_TOKENS=4096
MEMORY_MODE=enhanced_notes
MAX_MEMORY_ITEMS=100
MEMORY_UPDATE_TEMPERATURE=0.2
SESSION_TIMEOUT=3600
MAX_CONTEXT_LENGTH=8000
MEMORY_STORAGE_DIR=data/memories
CONVERSATION_HISTORY_DIR=data/conversations
```

```bash
python main.py \
    --mode interactive \
    --user custom_user \
    --memory-mode advanced_json_cards \
    --provider openrouter \
    --model "google/gemini-3.5-flash" \
    --conversation-interval 3 \
    --background-processing True \
    --no-verbose
```

### Project structure

```
user-memory/
├── main.py, quickstart.py, agent.py
├── conversational_agent.py, background_memory_processor.py
├── memory_manager.py, config.py, conversation_history.py
├── memory_operation_formatter.py, run_evaluation.py, locomo_benchmark.py
├── PROVIDERS.md, requirements.txt, env.example
├── data/{memories,conversations}/, logs/
```

### Development smoke tests

```bash
python quickstart.py
python -c "from memory_manager import NotesMemoryManager; m=NotesMemoryManager('smoke'); print(m.consolidate_memories())"
```

### Notes / license

Background processing is async; tools logged; streaming supported; state persists. Educational materials.

---
