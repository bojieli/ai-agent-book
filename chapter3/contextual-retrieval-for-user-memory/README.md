# Experiment 3-11: Contextual Retrieval for User Memory / 实验 3-11：利用上下文感知检索增强用户记忆

## 两辆车，究竟约了几次保养？

用户问自己约了哪些汽车保养。记录里有两辆车：本田雅阁已经预约保养，特斯拉 Model 3 只问过轮胎换位，最后没有预约。假如助理只列本田，用户怎么知道它核对过特斯拉？如果把两辆车都列为已预约，又错在哪里？在下面逐题记录中搜索 `layer2_01_multiple_vehicles`，先比较三组的 `answer`。前两组讲了本田的预约，双层组还交代了特斯拉的询价结果。这道题要找回的不仅是第二辆车的名字，还有两项服务各自的状态。

正式运行与实验 3-9 共用 60 个用例和查询轨迹，比较普通分块、LLM 上下文前缀、前缀检索加结构化卡片三组。通过数为 47、52、57；三层分别为 19/15/13、19/15/18、19/20/18。检索配置为每块八轮、重叠两轮、top-4、最多三次搜索。转账最终状态 95,000 美元、10 月 1 日的用例，以及护照与东京行程用例，三组均通过；车辆用例由双层组补齐第二辆车。下文八查询离线 compare 示例独立展示前缀对排名的影响。

**先对同一道题比较，再看总分。** 本次三组沿用同一串查询词。程序先在普通索引上生成查询计划，再让普通索引和带前缀的索引各自检索。回答模型读到的是命中片段的原文；双层组在前缀组所用的同一批片段之外，还能读到一张记忆卡片。可以沿着[检索和答题代码](../memory_rag_campaign.py)核对哪些输入发生了变化。

打开逐题结果找 `layer2_02_multiple_properties`。用户说自己的房产遭了水损，记录里既有自住房，也有出租房。三组共用的第三条查询词已经指向出租房，前缀组最后却只提到自住房；普通组和双层组的回答都覆盖了两处。把 60 题按这种方式一一配对，从普通组换到前缀组，有 8 题从未通过变为通过，也有 3 题从通过变为未通过，净增 5 题。从前缀组换到双层组，有 7 题改善、2 题退步，同样净增 5 题。遇到退步的题，可以打开 `arms` 逐组对照命中的片段、回答和评审理由，再判断遗漏发生在哪里。

运行索引：[validation/latest.json](validation/latest.json)；结果与请求记录：[20260729T214519Z-3_11-9b99feb4](validation/runs/20260729T214519Z-3_11-9b99feb4/)。


“他已经改了时间”这样的句子离开对话很难理解，而单独保存“周三开会”又可能丢掉来源。本实验结合带背景的对话检索和结构化记忆卡片，学习两种表示如何互补。

[English](#english)

[会话背景怎样帮助找回事实](#learning-0) · [准备离线样例与检索服务](#learning-1) · [对照带前缀和普通分块](#learning-2) · [回查漏掉的房产或车辆](#learning-3) · [实现与接口](#learning-4) · [排错与参考](#learning-5)

<a id="learning-0"></a>

## 会话背景怎样帮助找回事实

对话片段保留具体语境，记忆卡片便于查询相对稳定的事实。背景前缀帮助检索定位人物与事件；卡片则需要记录更新和冲突。两层信息应能相互核对，而不是各自形成一套无法追溯的结论。

### 本实验是什么

用户隔了一周再问“酒店订了吗”，助理要找到当时的答复，还要知道说的是哪家酒店。这个系统从两个地方取材料：

1. **上下文感知检索（Contextual RAG）**：对话历史的精准检索  
2. **高级 JSON 卡片（Advanced JSON Cards）**：结构化的核心事实存储

### 本项目采用的方法

#### 1. 上下文增强的对话分块

传统的对话分块会丢失上下文信息。例如，一段孤立的对话片段“好的，就订这个吧”本身毫无信息量。只有知道上文是在讨论“从上海到西雅图的、价格为500美元的单程机票”，这段对话才有意义。

本系统在索引对话历史之前，增加了关键的“上下文生成”步骤：

- 每个对话块都会调用 LLM 生成包含关键背景信息的前缀摘要  
- 上下文包括时间、人物和意图等关键线索  
- 把前缀与原文一起建索引，使查询中的地名、人物或事项有机会匹配到原本只有一句简短答复的片段

#### 2. 双层记忆结构

**Advanced JSON Cards（常驻记忆）**

- 存储结构化的、总结性的核心事实  
- 始终固定在 Agent 的上下文中  
- 包含 backstory（信息来源）和 relationship（关联人员）等元数据  
- 如：“用户 Jessica 的护照将于2025年2月18日过期”  

**Contextual RAG（按需检索）**

- 提供对非结构化的原始对话细节的精准访问  
- 快速找到具体讨论的完整上下文  
- 作为决策的“证据”支持  

#### 3. LLM-Based Memory Extraction

系统现在能够从对话中智能提取结构化记忆卡片：

```python
# 自动从对话生成记忆卡片
cards = indexer._generate_summary_cards(chunks, conversation_id)

# 生成的卡片示例：
{
    "category": "financial",
    "card_key": "bank_account_primary", 
    "backstory": "用户在开设账户时提供了银行信息",
    "date_created": "2024-01-15 10:30:00",
    "person": "John Smith (primary)",
    "relationship": "primary account holder",
    "bank_name": "Chase Bank",
    "account_type": "checking",
    "account_ending": "4567"
}
```

<a id="learning-1"></a>

## 准备离线样例与检索服务

先用 `contextual_compare.py` 查看八道演示题。正文里 47、52、57 三个通过数来自另一组 60 道题；要解释其中一道为何改善或退步，请打开本页开头的共享运行记录。

### 安装与配置

#### 1. 安装依赖

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

cd chapter3/contextual-retrieval-for-user-memory

# 迁移期间仍支持单项目兼容路径：
# python -m pip install -r requirements.txt
```

#### 2. 配置环境变量

创建 `.env` 文件：

```bash
# LLM Provider Configuration
MOONSHOT_API_KEY=your_api_key_here
ARK_API_KEY=your_api_key_here
SILICONFLOW_API_KEY=your_api_key_here
DASHSCOPE_API_KEY=your_dashscope_api_key_here
# DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=your_api_key_here

# Default Provider
LLM_PROVIDER=kimi  # Options: dashscope/qwen/bailian, kimi, doubao, siliconflow, openai

# Model Settings
LLM_MODEL=kimi-k3  # 或其他模型
```

#### 3. 启动检索管道服务

```bash
cd ../retrieval-pipeline
python api_server.py
```

<a id="learning-2"></a>

## 对照带前缀和普通分块

先阅读 `contextual_compare.py` 中的对照方式，再选一组存在后续修正的对话。观察原始片段、补充背景和记忆卡片分别保存了什么。按下文准备后端后，再运行模型驱动的问答比较。

### 使用示例

#### 离线对比：上下文化到底有没有用？（无需 API，推荐先跑这个）

打开[教学数据集](memory_qa_eval.json)，对照 `hotel_detail` 和 `hotel_confirm`。前一块有城市、酒店名、日期和报价，但说到的是推荐；后一块写着“可以，帮我订下来”和“已锁定房间”，却没说是哪家。用户问“我订的西雅图酒店确认了吗，是哪家？”时，两段材料各能回答哪一半？

离线程序对同样的 12 个记忆块运行两次 BM25。第一遍只索引原文；第二遍把数据集里备好的背景说明加在相应原文前，再建索引。两遍都用原来的八条查询。这样可以单独检查前缀有没有改变目标块的排名，也可以用纯 Python 运行全部步骤。

```bash
# 打印对比指标表（Recall@1 / Recall@3 / MRR）
python contextual_compare.py

# 对单条查询做 plain vs contextual 的 Top-K 检索对比
python contextual_compare.py --query '我最后确认预订的那张机票是哪个航班？'

# 保存完整结果（含逐查询名次明细）到 JSON
python contextual_compare.py --output results/compare.json
```

实测输出（12 个记忆块、8 条查询的受控集）：

```
方法                            Recall@1  Recall@3       MRR
--------------------------------------------------------------------
Plain（直接索引原始块）               0.625     1.000     0.792
Contextual（上下文化后索引）        0.750     1.000     0.875
--------------------------------------------------------------------
差值（Δ）                         +0.125    +0.000    +0.083
```

酒店确认题的目标块从第三升到第一，其余七题的目标块名次相同。只取第一块时，八题中命中的从五题变成六题，所以 Recall@1 增加 1/8；取前三块时，两种方法都能找到八题各自的目标，所以 Recall@3 没变。MRR 衡量第一个相关结果排得多靠前。只有酒店题的倒数排名从 1/3 变成 1，八题平均就增加了约 0.083。

再看机票确认题。加了前缀，目标块仍排第二。实际系统如果只取一块，仍可能错过确认记录；若取三块，还要检查回答模型能否把报价、用户决定和订单状态区分开。离线程序只把命中块排出先后。要检查助理最后怎么回答，可以读开头车辆用例的归档回答，或运行下面的端到端评估。

#### 端到端评估（需 API / 检索服务）

```bash
# 交互式界面（默认）
python main.py

# 评估特定分类（需 LLM 与检索管道服务）
python main.py --mode evaluate --category layer1

# 关闭上下文化做对照，并指定模型与输出
python main.py --mode evaluate --category layer1 --no-contextual --model gpt-5.6-luna --output results/plain_eval.json
```

完整命令行参数见 `python main.py --help`（含中文说明）。

#### 交互式测试界面

运行 `python main.py` 进入交互式界面：

```
Main Menu:
1. 🚀 Demo Mode (Quick Start)
2. 📚 Load & Index Conversations
3. 🎴 Manage Memory Cards
4. 🔍 Test Query
5. 📊 Evaluate All Test Cases (by Category) [LLM Judge]
6. 🎯 Evaluate Specific Test Case [LLM Judge]
7. 📈 Show Statistics
8. ⚙️  Configure Settings
0. Exit
```

#### 评估输出示例

```
============================================================
DEBUG: All Memory Cards in System
============================================================

[financial.bank_account_primary]
{
  "backstory": "用户开设银行账户时提供的信息",
  "date_created": "2024-06-12 14:30:00",
  "person": "Michael James Robertson (primary)",
  "relationship": "primary account holder",
  "bank_name": "First National Bank",
  "account_number": "4429853327",
  "routing_number": "123006800"
}

Total Memory Cards: 5
============================================================

LLM Judge Evaluation Results
============================================================
Reward: 1.000/1.000
Passed: Yes
Reasoning: The agent correctly provided the checking account number...
============================================================
```

### 工作流程示例

当用户询问“为我一月的东京之行，还有什么要准备的吗？”时：

1. **事实回顾**：Agent 首先审视 Advanced JSON Cards 中的内容  
   - 发现“东京之行”信息（1月25日出发）  
   - 发现“护照信息”（2月18日过期）  

2. **关联与推理**：通过对比核心事实  
   - 识别出机票日期与护照过期日期接近的风险  

3. **细节验证**：启动 RAG 检索  
   - 搜索与“护照”和“东京机票”相关的对话片段  
   - 获取原始讨论的所有细节  

4. **主动服务**：结合两种记忆  
   - 给出关键建议：“您的护照即将过期，强烈建议您立即加急办理续签”  

5. **自动评估**：LLM Judge 评估答案  
   - 评分：0.95/1.0  
   - 理由：正确识别风险并给出适当建议

<a id="learning-3"></a>

## 回查漏掉的房产或车辆

除了答案是否正确，还要检查引用的是哪次对话、记忆有没有时间条件，以及一条错误摘要是否被多层重复放大。更多记忆不一定更好，关键是能否取到当前问题需要的证据。

### 出租房的线索送到了哪一步

回到页首的房产题，依次抄下三组共用的查询词、各自命中的对话、回答中提到的房产。查询词写着“出租房”，只说明模型想查它；只有命中片段确实交代了出租房的情况，这条线索才送到了答题模型面前。对于额外读取卡片的那一组，还要检查所需事实来自片段还是卡片。

### 最新更新

#### LLM-Based Memory Card Generation
- **自动提取**：使用 LLM 从对话中智能提取结构化记忆卡片  
- **完整结构**：每张卡片包含 backstory、person、relationship 等必要字段  
- **智能降级**：当 LLM 不可用时自动降级到关键词提取  

#### LLM Judge Integration
- **自动评估**：集成 LLM Judge 对 Agent 回答进行自动评分  
- **双路径支持**：支持导入模块或直接 API 调用  
- **详细反馈**：提供 0-1 分数、通过/失败状态和评估理由  

#### Enhanced Debugging
- **内存卡片可视化**：评估时自动打印所有记忆卡片的完整 JSON  
- **测试用例排序**：按名称字母顺序显示测试用例  
- **评估透明度**：清晰显示 LLM Judge 使用状态

### 检查自己的解释

如果卡片与原始对话冲突，应优先采用哪一个？系统应怎样向读者解释不确定性？

<a id="learning-4"></a>

## 实现与接口

### 项目说明

> Companion material for *AI Agents in Depth*, Chapter 3 — dual-layer memory: Contextual RAG + Advanced JSON Cards.  
> 配套《深入理解 AI Agent》第 3 章——双层记忆：上下文感知 RAG + Advanced JSON Cards。

← [Chapter 3 index / 返回第 3 章目录](../README.md)

---

### 项目结构

```
contextual-retrieval-for-user-memory/
├── contextual_chunking.py      # 上下文感知分块
├── advanced_memory_manager.py  # 高级JSON卡片管理
├── contextual_indexer.py       # 双层记忆索引器（含LLM提取）
├── contextual_agent.py         # 结合双层记忆的Agent
├── contextual_evaluator.py     # 评估框架（含LLM Judge）
├── contextual_compare.py       # 离线对比脚本：上下文化 vs 原始块的召回（无需 API）
├── memory_qa_eval.json         # 离线对比用的受控记忆问答对照集
├── main.py                     # 主入口（argparse，含 --mode compare 离线对比）
├── config.py                   # 配置管理
├── chunker.py                  # 基础分块器
├── tools.py                    # Agent工具
└── requirements.txt            # 依赖项
```

<a id="learning-5"></a>

## 排错与参考

### 参考资料

- [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [RAG 技术综述](https://arxiv.org/abs/2005.11401)
- [Memory Systems in AI Agents](https://arxiv.org/abs/2203.14680)
- [LLM as Judge](https://arxiv.org/abs/2306.05685)

### 许可证

MIT License

---

## Notes / 说明

### OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.

## English

### Canonical live campaign

`python campaign.py` evaluates all 60 three-layer cases with a preregistered
plain/contextual/dual-layer ablation. A live ReAct planner's exact queries are
replayed across plain and contextual fixed-window indexes; the dual arm adds
the live Advanced JSON Card checkpoint from Experiment 3-1. Prefixes, cards,
raw chunks, trajectories, per-layer external-judge metrics, and credential-free
receipts are retained under `validation/`; `validation/latest.json` is the
canonical gate report.

### What this experiment is

Applying contextual retrieval to user memory addresses a core pain point of naive conversation chunking and steps toward higher-level memory. This project implements a dual-layer memory system:

1. **Contextual Retrieval (Contextual RAG)**: precise retrieval over conversation history  
2. **Advanced JSON Cards**: structured storage of core facts  

### Latest updates

#### LLM-Based Memory Card Generation
- **Auto extract**: LLM extracts structured memory cards from conversations  
- **Full structure**: each card includes backstory, person, relationship, and related fields  
- **Graceful fallback**: falls back to keyword extraction when the LLM is unavailable  

#### LLM Judge Integration
- **Auto evaluation**: LLM Judge scores agent answers automatically  
- **Dual path**: import evaluation module or call the API directly  
- **Detailed feedback**: 0–1 score, pass/fail, and reasoning  

#### Enhanced Debugging
- **Memory card dump**: prints full JSON of all memory cards during evaluation  
- **Test case sorting**: test cases listed alphabetically by name  
- **Eval transparency**: clearly shows whether LLM Judge is in use  

### Core ideas

#### 1. Context-enriched conversation chunking

Traditional chunking drops context. An isolated fragment like “OK, book that one” means little until you know the prior turn discussed “a one-way Shanghai→Seattle flight for $500.”

Before indexing conversation history, the system adds a **context generation** step:

- Each conversation chunk gets an LLM-generated prefix summary with key background  
- Context includes time, people, intent, and other cues  
- Greatly improves retrieval accuracy and relevance  

#### 2. Dual-layer memory

**Advanced JSON Cards (always-on memory)**

- Structured, summarized core facts  
- Always fixed in the Agent’s context  
- Metadata such as backstory (source) and relationship (related people)  
- Example: “User Jessica’s passport expires on 2025-02-18”  

**Contextual RAG (on-demand retrieval)**

- Precise access to unstructured raw dialogue detail  
- Quickly finds full context of a specific discussion  
- Acts as “evidence” for decisions  

#### 3. LLM-based memory extraction

The system can extract structured memory cards from dialogue:

```python
# Auto-generate memory cards from conversation
cards = indexer._generate_summary_cards(chunks, conversation_id)

# Example card:
{
    "category": "financial",
    "card_key": "bank_account_primary", 
    "backstory": "用户在开设账户时提供了银行信息",
    "date_created": "2024-01-15 10:30:00",
    "person": "John Smith (primary)",
    "relationship": "primary account holder",
    "bank_name": "Chase Bank",
    "account_type": "checking",
    "account_ending": "4567"
}
```

### Project structure

```
contextual-retrieval-for-user-memory/
├── contextual_chunking.py      # Context-aware chunking
├── advanced_memory_manager.py  # Advanced JSON card manager
├── contextual_indexer.py       # Dual-layer memory indexer (incl. LLM extract)
├── contextual_agent.py         # Agent combining dual-layer memory
├── contextual_evaluator.py     # Evaluation (incl. LLM Judge)
├── contextual_compare.py       # Offline compare: contextual vs plain recall (no API)
├── memory_qa_eval.json         # Controlled memory Q&A set for offline compare
├── main.py                     # Main entry (argparse; --mode compare offline)
├── config.py                   # Config
├── chunker.py                  # Base chunker
├── tools.py                    # Agent tools
└── requirements.txt            # Dependencies
```

### Install and configure

#### 1. Install dependencies

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

cd chapter3/contextual-retrieval-for-user-memory

# Single-project compatibility path, still supported during migration:
# python -m pip install -r requirements.txt
```

#### 2. Environment variables

Create a `.env` file:

```bash
# LLM Provider Configuration
MOONSHOT_API_KEY=your_api_key_here
ARK_API_KEY=your_api_key_here
SILICONFLOW_API_KEY=your_api_key_here
DASHSCOPE_API_KEY=your_dashscope_api_key_here
# DASHSCOPE_BASE_URL=https://dashscope-intl.aliyuncs.com/compatible-mode/v1
OPENAI_API_KEY=your_api_key_here

# Default Provider
LLM_PROVIDER=kimi  # Options: dashscope/qwen/bailian, kimi, doubao, siliconflow, openai

# Model Settings
LLM_MODEL=kimi-k3  # or another model
```

#### 3. Start the retrieval pipeline (for full e2e eval)

```bash
cd ../retrieval-pipeline
python api_server.py
```

### Usage

#### Offline compare: does contextualization help? (no API; recommended first)

Core claim: **before embedding/indexing memory chunks, generating a “context prefix” per chunk improves recall of out-of-context fragments** (e.g. “OK, book that one”). `--mode compare` is a **fully offline, no API key / no retrieval service** controlled experiment.

It measures “plain” (no prefix) vs “contextual” (prefix then index) on the same context; the only variable is whether the indexed text includes the context prefix. Retrieval is deterministic pure-Python BM25 as an offline stand-in for neural embeddings. Dataset: [`memory_qa_eval.json`](memory_qa_eval.json) (teaching set; override with `--dataset`).

```bash
# Print comparison metrics (Recall@1 / Recall@3 / MRR)
python contextual_compare.py

# Single-query plain vs contextual Top-K
python contextual_compare.py --query '我最后确认预订的那张机票是哪个航班？'

# Save full results (per-query ranks) to JSON
python contextual_compare.py --output results/compare.json
```

Measured output (12 memory chunks, 8 queries):

```
方法                            Recall@1  Recall@3       MRR
--------------------------------------------------------------------
Plain（直接索引原始块）               0.625     1.000     0.792
Contextual（上下文化后索引）        0.750     1.000     0.875
--------------------------------------------------------------------
差值（Δ）                         +0.125    +0.000    +0.083
```

For queries like “is my Seattle hotel confirmed,” the gold chunk (“yes, book it”) ranks 3rd under Plain and 1st after contextualization—the prefix re-anchors an isolated confirmation to “Hyatt Seattle.”

> Note: this is an **offline lexical proxy** to show mechanism and directional gain without APIs. In production, prefixes are LLM-generated per chunk and indexed with neural embeddings + hybrid search (see `--mode evaluate` below), which needs an API key.

#### End-to-end evaluation (needs API / retrieval service)

```bash
# Interactive UI (default)
python main.py

# Evaluate a category (needs LLM + retrieval pipeline)
python main.py --mode evaluate --category layer1

# Ablate contextualization; set model and output
python main.py --mode evaluate --category layer1 --no-contextual --model gpt-5.6-luna --output results/plain_eval.json
```

Full CLI: `python main.py --help` (includes Chinese descriptions).

#### Interactive menu

Run `python main.py`:

```
Main Menu:
1. 🚀 Demo Mode (Quick Start)
2. 📚 Load & Index Conversations
3. 🎴 Manage Memory Cards
4. 🔍 Test Query
5. 📊 Evaluate All Test Cases (by Category) [LLM Judge]
6. 🎯 Evaluate Specific Test Case [LLM Judge]
7. 📈 Show Statistics
8. ⚙️  Configure Settings
0. Exit
```

#### Evaluation output example

```
============================================================
DEBUG: All Memory Cards in System
============================================================

[financial.bank_account_primary]
{
  "backstory": "用户开设银行账户时提供的信息",
  "date_created": "2024-06-12 14:30:00",
  "person": "Michael James Robertson (primary)",
  "relationship": "primary account holder",
  "bank_name": "First National Bank",
  "account_number": "4429853327",
  "routing_number": "123006800"
}

Total Memory Cards: 5
============================================================

LLM Judge Evaluation Results
============================================================
Reward: 1.000/1.000
Passed: Yes
Reasoning: The agent correctly provided the checking account number...
============================================================
```

### Workflow example

When the user asks “Anything else to prepare for my January Tokyo trip?”:

1. **Fact review**: Agent inspects Advanced JSON Cards  
   - Finds “Tokyo trip” (departs Jan 25)  
   - Finds “passport” (expires Feb 18)  

2. **Link and reason**: compares core facts  
   - Flags passport expiry near flight date  

3. **Detail check**: starts RAG  
   - Searches dialogue chunks about passport / Tokyo flights  
   - Loads full original discussion  

4. **Proactive service**: both memory layers  
   - Advises: “Your passport is about to expire; strongly consider expedited renewal.”  

5. **Auto eval**: LLM Judge  
   - Score: 0.95/1.0  
   - Reason: correctly identified risk and gave appropriate advice  

### References

- [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [RAG survey](https://arxiv.org/abs/2005.11401)
- [Memory Systems in AI Agents](https://arxiv.org/abs/2203.14680)
- [LLM as Judge](https://arxiv.org/abs/2306.05685)

### License

MIT License

---
