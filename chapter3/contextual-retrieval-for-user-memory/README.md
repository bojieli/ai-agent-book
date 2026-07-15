# 实验 3.9：利用上下文感知检索增强用户记忆

将上下文感知检索技术应用于用户记忆的构建，是解决传统对话历史分块所面临的核心痛点，并迈向更高层次记忆能力的关键。本项目实现了一个双层记忆系统，结合了：

1. **上下文感知检索（Contextual RAG）**：对话历史的精准检索
2. **高级 JSON 卡片（Advanced JSON Cards）**：结构化的核心事实存储

## 🆕 最新更新

### LLM-Based Memory Card Generation
- **自动提取**：使用 LLM 从对话中智能提取结构化记忆卡片
- **完整结构**：每张卡片包含 backstory、person、relationship 等必要字段
- **智能降级**：当 LLM 不可用时自动降级到关键词提取

### LLM Judge Integration  
- **自动评估**：集成 LLM Judge 对 Agent 回答进行自动评分
- **双路径支持**：支持导入模块或直接 API 调用
- **详细反馈**：提供 0-1 分数、通过/失败状态和评估理由

### Enhanced Debugging
- **内存卡片可视化**：评估时自动打印所有记忆卡片的完整 JSON
- **测试用例排序**：按名称字母顺序显示测试用例
- **评估透明度**：清晰显示 LLM Judge 使用状态

## 核心创新

### 1. 上下文增强的对话分块

传统的对话分块会丢失上下文信息。例如，一段孤立的对话片段"好的，就订这个吧"本身毫无信息量。只有知道上文是在讨论"从上海到西雅图的、价格为500美元的单程机票"，这段对话才有意义。

本系统在索引对话历史之前，增加了关键的"上下文生成"步骤：
- 每个对话块都会调用 LLM 生成包含关键背景信息的前缀摘要
- 上下文包括时间、人物和意图等关键线索
- 极大提升了检索的准确性和相关性

### 2. 双层记忆结构

**Advanced JSON Cards（常驻记忆）**
- 存储结构化的、总结性的核心事实
- 始终固定在 Agent 的上下文中
- 包含 backstory（信息来源）和 relationship（关联人员）等元数据
- 如："用户 Jessica 的护照将于2025年2月18日过期"

**Contextual RAG（按需检索）**
- 提供对非结构化的原始对话细节的精准访问
- 快速找到具体讨论的完整上下文
- 作为决策的"证据"支持

### 3. LLM-Based Memory Extraction

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

## 项目结构

```
contextual-retrieval-for-user-memory/
├── contextual_chunking.py      # 上下文感知分块
├── advanced_memory_manager.py  # 高级JSON卡片管理
├── contextual_indexer.py       # 双层记忆索引器（含LLM提取）
├── contextual_agent.py         # 结合双层记忆的Agent
├── contextual_evaluator.py     # 评估框架（含LLM Judge）
├── main.py                     # 主入口（支持测试用例排序）
├── config.py                   # 配置管理
├── chunker.py                  # 基础分块器
├── tools.py                    # Agent工具
└── requirements.txt            # 依赖项
```

## 安装与配置

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 配置环境变量

创建 `.env` 文件：

```bash
# LLM Provider Configuration
MOONSHOT_API_KEY=your_api_key_here
ARK_API_KEY=your_api_key_here
SILICONFLOW_API_KEY=your_api_key_here
OPENAI_API_KEY=your_api_key_here

# Default Provider
LLM_PROVIDER=kimi  # Options: kimi, doubao, siliconflow, openai

# Model Settings
LLM_MODEL=kimi-k2-0905-preview  # 或其他模型
```

### 3. 启动检索管道服务

```bash
cd ../retrieval-pipeline
python api_server.py
```

## 使用示例

### 运行评估

```bash
# 交互式界面（推荐）
python main.py

# 评估特定分类
python main.py --mode evaluate --category layer3

# 评估单个测试用例
python main.py --mode single --test-id layer1_01_bank_account
```

### 交互式测试界面

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

### 评估输出示例

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

## 工作流程示例

当用户询问"为我一月的东京之行，还有什么要准备的吗？"时：

1. **事实回顾**：Agent 首先审视 Advanced JSON Cards 中的内容
   - 发现"东京之行"信息（1月25日出发）
   - 发现"护照信息"（2月18日过期）

2. **关联与推理**：通过对比核心事实
   - 识别出机票日期与护照过期日期接近的风险

3. **细节验证**：启动 RAG 检索
   - 搜索与"护照"和"东京机票"相关的对话片段
   - 获取原始讨论的所有细节

4. **主动服务**：结合两种记忆
   - 给出关键建议："您的护照即将过期，强烈建议您立即加急办理续签"

5. **自动评估**：LLM Judge 评估答案
   - 评分：0.95/1.0
   - 理由：正确识别风险并给出适当建议

## 参考资料

- [Anthropic's Contextual Retrieval](https://www.anthropic.com/news/contextual-retrieval)
- [RAG 技术综述](https://arxiv.org/abs/2005.11401)
- [Memory Systems in AI Agents](https://arxiv.org/abs/2203.14680)
- [LLM as Judge](https://arxiv.org/abs/2306.05685)

## 许可证

MIT License