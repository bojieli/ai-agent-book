# User Memory System / 用户记忆系统

用户先后谈过 Netflix、Disney+ 和 Max 三份订阅。等他想省点钱，问“我现在每个月都在付哪些订阅费”时，助手能不能列全？你可以直接翻看下方两份已经跑完的记录，沿着三次更新找出旧订阅是怎样留下或丢失的。随后再运行交互程序，看看后台如何从新对话中提取长期记忆。

[English](#english)

[订阅记录怎样跨会话保留](#learning-0) · [选择记忆格式与模型](#learning-1) · [写入订阅并在新会话追问](#learning-2) · [核对每一笔订阅是否保留](#learning-3) · [实现与接口](#learning-4)

<a id="learning-0"></a>

## 订阅记录怎样跨会话保留

对话模块负责当前响应，后台模块负责整理长期信息。这样可以区分“刚才说过什么”与“值得长期保留什么”。不同存储模式改变组织方式，却都需要处理来源、冲突和时间变化。

### 关键特性

- **分离架构**：对话 Agent 与后台记忆处理器解耦  
- **多种记忆模式**：简单笔记 → 增强笔记 → JSON 卡片 → Advanced JSON Cards  
- **多提供商**：Kimi、SiliconFlow、豆包、OpenRouter  
- **ReAct + 工具** 结构化记忆操作
- **流式输出**、**评测集成**、**按间隔后台更新**、**JSON 持久化**

### 架构

用户界面 → **ConversationalAgent**（对话、读记忆、流式）+ **BackgroundMemoryProcessor**（分析并写记忆）→ **MemoryManager**（笔记/JSON 卡片）。

核心文件：`conversational_agent.py`、`background_memory_processor.py`、`agent.py`、`memory_manager.py`。

### 记忆模式

1. **`notes`** — 短事实  
2. **`enhanced_notes`** — 带上下文的段落  
3. **`json_cards`** — 层次化 JSON  
4. **`advanced_json_cards`** — 含 backstory / person / relationship 等完整卡片

把上面的程序分工放回订阅例子：新消息先交给对话模块，后台处理器按配置的间隔整理本轮材料，写入持久化存储。要验证下一次会话还能不能读到 Netflix，得先等写入完成，再开新会话追问。若这里出了错，可以对照记忆操作记录，找出是哪一次更新改变了内容。

---

<a id="learning-1"></a>

## 选择记忆格式与模型

阅读[三次更新后的订阅记录](#learning-3)无需模型账号。如果要自己做一遍，先选笔记或 JSON 卡片，再配置模型；重复同一组对话，才便于找出哪次更新丢失了早先的订阅。

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

## 写入订阅并在新会话追问

配置模型后先运行演示。对照一轮原始对话、后台提取的内容和后续回答，再修改一个用户事实继续观察。读代码时先看对话模块怎样读取记忆，再看后台处理器什么时候提交更新。

### 第三份订阅加入后，前两份还在吗

按页首的顺序依次输入 Netflix、Disney+ 和 Max 三份订阅。每次等后台更新完，查看这一轮实际保存的笔记或卡片，再开始下一轮。最后询问每个月在付哪些订阅费。如果缺少最早的一笔，往前逐轮查：它从未写入，还是在保存后来那笔费用时被覆盖了？

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

## 核对每一笔订阅是否保留

## 实验 3-1、3-2：正文对应运行

统一使用 60 个用例，每层 20 个，逐会话更新记忆后回答新问题。Simple Notes、Enhanced Notes、JSON Cards、Advanced JSON Cards 分别通过 48、52、51、49 个用例。生成与回答采用 Doubao Seed 1.6，独立评审采用 Moonshot。token 统计包含记忆维护、回答与评审调用；四种模式分别约为 110 万、99 万、113 万、155 万。

运行索引：[validation/latest.json](validation/latest.json)；结果与请求记录：[20260730T043652Z-3_1_and_3_2-16200e94](validation/runs/20260730T043652Z-3_1_and_3_2-16200e94/)。

先对照同一道题的[增强笔记记录](validation/checkpoints/full-60x4/layer2_04_multiple_subscriptions--enhanced_notes.json)和[高级 JSON 卡片记录](validation/checkpoints/full-60x4/layer2_04_multiple_subscriptions--advanced_json_cards.json)。两份文件都按会话顺序保存了三次 `memory_states`。打开每一项的 `memory`，圈出其中还能找到的订阅。增强笔记在最后一次更新后仍保存了三家；高级卡片到第二次更新时已经找不到 Netflix，第三次更新后连 Disney+ 也消失了。再看 `answer`：两组都答对了 Max 的月费 19.99 美元，只有第一组列全了三家。这样就能把前两份订阅的遗漏定位到记忆更新这一步。

### 三次修改，说的是几笔转账？

订阅题考查能否把三笔不同的费用列全。换成[转账更正题的三段原始对话](../user-memory-evaluation/test_cases/layer2/12_contradictory_financial_instructions.yaml)，三次来电改的是同一笔安排。9 月 15 日先约了 10 月 1 日转 85,000 美元；9 月 25 日改为 9 月 27 日转 100,000 美元；9 月 26 日又改为 10 月 1 日转 95,000 美元。用户问“现在安排的是哪一天、多少钱”，不能把三个金额都算进去；若问“为什么改回来”，就需要之前的记录。

打开[增强笔记组的逐次更新](validation/checkpoints/full-60x4/layer2_12_contradictory_financial_instructions--enhanced_notes.json)，在 `memory_states` 第三项的 `memory` 里查找三个确认编号：`WT-89045`、`WT-89067` 和 `WT-89089` 都还在。先遮住 `answer`，试着只凭笔记指出当前有效的是哪一版，再和最终回答对照。它给出的是 10 月 1 日**已安排**转 95,000 美元。从对话能核对预约，至于后来有没有实际扣款，还需要届时的交易记录。四种记忆格式在这道题上都通过了评分。

[评分代码](run_evaluation.py)的 `judge_summary` 同时给出通过标记和综合分。以[宽带账号题](validation/checkpoints/full-60x4/layer1_05_internet_service--enhanced_notes.json)为例，打开 `result.judge` 可以读到 4、4、4、1 四项分数。前三项都达到 3 分，评审也没有标记重大事实错误，因此 `passed` 为真。主动性得 1 分，会拉低综合分：四项之和除以 16，得到 `reward = 0.8125`。如果评审标记了重大事实错误，程序会把综合分直接置零。

检查系统是否把临时计划误写成永久偏好，或把模型自己的猜测保存成用户事实。回答提到了某条信息，也应能追溯到用户真正说过的内容。

### 评测

```bash
python main.py --mode evaluation --memory-mode advanced_json_cards
```

对接 `user-memory-evaluation` 的用例与打分。

### 检查自己的解释

哪些信息只应该保留在本轮上下文，哪些适合长期存储？用户纠正事实时应发生哪些更新？

<a id="learning-4"></a>

## 实现与接口

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
