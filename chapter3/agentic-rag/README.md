# Agentic RAG System

An educational implementation of an Agentic Retrieval-Augmented Generation (RAG) system with ReAct pattern, supporting multiple LLM providers and knowledge base backends.

## 🌟 Features

- **Agentic RAG with ReAct Pattern**: Uses reasoning and tool-calling to iteratively search and retrieve information
- **Non-Agentic RAG Mode**: Simple retrieval + LLM response for comparison
- **Multiple LLM Provider Support**: 
  - Kimi/Moonshot
  - Doubao
  - SiliconFlow
  - OpenAI
  - OpenRouter
  - Groq
  - Together AI
  - DeepSeek
- **Flexible Knowledge Base**:
  - **Offline BM25 (内置，零依赖离线运行)**: in-process BM25 over the bundled `laws/` corpus — no server, no API key required
  - Local retrieval pipeline (requires ../retrieval-pipeline)
  - Dify knowledge base API
- **Document Chunking**: Configurable chunking with paragraph boundary respect
- **Evaluation Framework**: Comprehensive evaluation with Chinese legal dataset
- **Conversation History**: Support for follow-up questions
- **Verbose Logging**: Detailed logging to understand agent reasoning

## 📦 Installation

```bash
pip install -r requirements.txt
```

## ⚙️ Configuration

Set environment variables in `.env` file:

```bash
# LLM API Keys (set the one you're using)
MOONSHOT_API_KEY=your_kimi_api_key
ARK_API_KEY=your_doubao_api_key
SILICONFLOW_API_KEY=your_siliconflow_api_key
OPENAI_API_KEY=your_openai_api_key
OPENROUTER_API_KEY=your_openrouter_api_key
GROQ_API_KEY=your_groq_api_key
TOGETHER_API_KEY=your_together_api_key
DEEPSEEK_API_KEY=your_deepseek_api_key

# Knowledge Base Configuration (optional, defaults to local)
KB_TYPE=local  # Options: "offline" (内置离线 BM25，无需服务/API), "local", "dify"
DIFY_API_KEY=your_dify_api_key  # if using Dify
DIFY_DATASET_ID=your_dataset_id  # optional

# LLM Configuration (optional)
LLM_PROVIDER=kimi  # default provider
LLM_MODEL=kimi-k3  # optional, uses provider defaults
```

## 🚀 Usage

### 0. 零依赖离线对比实验（推荐先跑，无需 API / 无需外部服务）

本实验的核心论点是：**面对复杂问题，让 Agent 自主分解、多轮迭代检索，其证据召回显著优于单次检索**。
`compare_offline.py` 用内置的离线 BM25 检索器（`offline_retriever.py`，直接读取 `laws/` 语料）
在小型中文司法问答集上量化这一差距，**完全离线、无需任何 API Key**：

```bash
python compare_offline.py
# 可选参数：--corpus laws  --top-k 5  --dataset evaluation/offline_qa.json  --output result.json
```

真实输出（本机实测，21372 个法条分块 / 288 篇文档）：

```
问题                          难度    单次检索    分解检索    检索次数
------------------------------------------------------------------------------
故意伤害致人重伤的，如何处…  easy    100%        100%        1 → 1
正当防卫是怎么规定的？        easy    100%        100%        1 → 1
醉酒驾驶机动车如何处罚？      easy    100%        100%        1 → 1
故意杀人罪判几年？            hard    0%          100%        1 → 1
盗窃罪的立案标准是什么？      hard    0%          100%        1 → 1
诈骗罪的量刑标准是什么？      hard    0%          100%        1 → 1
醉酒过失致人重伤且有盗窃前…  hard    33%         100%        1 → 3
------------------------------------------------------------------------------
聚合指标（平均证据召回率）:
  全部                                48%         100%        1.0 → 1.3
  简单题                              100%        100%        1.0 → 1.0
  复杂题                              8%          100%        1.0 → 1.5
```

解读（与书中实验 3-9 一致）：**简单问题两种范式相差无几（均 100%）**，一次直接检索就够；
**复杂/措辞欠佳的问题上差距显著（8% → 100%）**，单次检索因关键词不精确而漏检关键法条，
分解式多轮检索则能逐一补齐证据。该指标为纯检索层的『证据召回率』，是回答质量的上界
——检索不到证据，生成阶段无从谈起。金标准法条均已确认存在于 `laws/` 语料中。

> 说明：离线模式用数据集中预先标注的 `subqueries` 表示『Agent 分解后发起的检索』，
> 以隔离出**检索策略**本身的贡献；在真实系统中，这些子查询由 LLM 在 ReAct 循环中动态生成。
> 需要 LLM 生成、端到端评测答案质量时，请使用 `evaluation/evaluate.py`（需配置 API Key）。

也可以让完整 Agent 直接跑在离线知识库上（检索离线，仅**答案生成**需要 API Key）：

```bash
python main.py --kb-type offline --query "醉酒过失致人重伤且有盗窃前科如何量刑"
python main.py --kb-type offline --query "故意杀人罪判几年" --mode compare
```

### 1. Start the Retrieval Pipeline

First, start the retrieval pipeline server (required for local knowledge base):

```bash
# In a separate terminal
cd ../retrieval-pipeline
python main.py
# Server will run on http://localhost:4242
```

### 2. Index Documents

#### Option A: Index Chinese Law Documents (Pre-included)

```bash
# Index the included Chinese law documents
python index_local_laws.py

# With specific categories
python index_local_laws.py --categories 宪法 民法典

# With document limit
python index_local_laws.py --max-docs 10
```

#### Option B: Index Custom Documents

```bash
# Index a single file
python main.py --index path/to/document.txt

# Index a directory
python main.py --index path/to/documents/

# Custom chunk size
python main.py --index documents/ --chunk-size 2048
```

### 3. Run the Agentic RAG System

#### Interactive Mode (Default)

```bash
# Start in agentic mode (default)
python main.py

# Start in non-agentic mode  
python main.py --mode non-agentic

# Enable verbose logging (default is enabled)
python main.py --verbose

# Disable verbose logging
python main.py --no-verbose
```

In interactive mode:
- Type your questions and press Enter
- Type 'quit' or 'exit' to stop
- Type 'clear' to clear conversation history
- Type 'mode' to switch between agentic/non-agentic modes

#### Single Query

```bash
# Agentic mode
python main.py --query "宪法第一条是什么？" --mode agentic

# Non-agentic mode
python main.py --query "盗窃罪的立案标准是什么？" --mode non-agentic

# Compare both modes
python main.py --query "故意杀人罪判几年？" --mode compare
```

#### Batch Processing

```bash
# Create a file with queries (one per line)
echo "故意杀人罪判几年？
盗窃罪的立案标准是什么？
醉酒驾驶如何处罚？" > queries.txt

# Run batch
python main.py --batch queries.txt --output results.json

# Batch with specific mode
python main.py --batch queries.txt --mode non-agentic
```

#### With Different Providers

```bash
python main.py --provider openai --model gpt-5.6-luna
python main.py --provider doubao --model doubao-seed-1-6-thinking-250715
python main.py --provider siliconflow --query "你好"
```

### 4. Run Evaluation

```bash
# Build evaluation dataset
cd evaluation
python dataset_builder.py

# Run evaluation
python evaluate.py

# With specific configuration
python evaluate.py --provider kimi --kb-type local --output custom_results
```

## 📁 Project Structure

```
agentic-rag/
├── config.py              # Configuration classes
├── agent.py               # Main AgenticRAG implementation
├── tools.py               # Knowledge base tools (含 offline BM25 后端)
├── offline_retriever.py   # 内置离线 BM25 检索器（读取 laws/，无需服务/API）
├── compare_offline.py     # 离线对比实验：分解检索 vs 单次检索（证据召回率表）
├── chunking.py            # Document chunking and indexing
├── main.py                # Main entry point
├── index_local_laws.py    # Index Chinese law documents
├── quickstart.py          # Quick demo script
├── test_simple.py         # Simple test script
├── requirements.txt       # Dependencies
├── README.md              # This file
├── document_store.json    # Local document storage
├── laws/                  # Chinese law documents
│   ├── 1-宪法/
│   ├── 2-宪法相关法/
│   ├── 3-民法典/
│   ├── 3-民法商法/
│   ├── 4-行政法/
│   ├── 5-经济法/
│   ├── 6-社会法/
│   ├── 7-刑法/
│   └── 8-诉讼与非诉讼程序法/
└── evaluation/
    ├── dataset_builder.py # Build evaluation dataset
    ├── offline_qa.json    # 离线对比数据集（问题 + 金标准法条 + Agent 分解子查询）
    └── evaluate.py        # Evaluation framework (端到端答案质量，需 API)
```

## 🧠 How It Works

### Agentic RAG Mode

The agent uses the ReAct (Reasoning + Acting) pattern:

1. **Reasoning**: Analyzes what information is needed to answer the question
2. **Tool Calling**: Uses `knowledge_base_search` tool to find relevant chunks
3. **Iterative Search**: May perform multiple searches with refined queries
4. **Document Retrieval**: Can fetch complete documents with `get_document` for context
5. **Answer Synthesis**: Combines retrieved information with citations
6. **Conversation Memory**: Maintains context for follow-up questions

Example flow:
```
User: 宪法第一条是什么？
Agent: [Thinks] Need to find information about Article 1 of the Constitution
       [Tool] knowledge_base_search("宪法第一条")
       [Result] Found relevant chunks about constitutional articles
       [Answer] Based on the retrieved information, Article 1 states...
```

### Non-Agentic RAG Mode

Simple retrieval-augmented generation:

1. **Direct Search**: Searches once with the user's query as-is
2. **Context Injection**: Puts top-K results in the prompt
3. **Single Response**: LLM answers based on provided context
4. **No Iteration**: Single-shot approach without refinement

## 📊 Configuration Options

### Top-K Results

Control how many search results to retrieve:

```python
# In config.py or via environment
local_top_k = 3  # Number of results to retrieve
```

### Verbose Mode

See detailed agent reasoning:

```bash
# Enable verbose (default)
python main.py --verbose

# Disable for cleaner output
python main.py --no-verbose
```

### LLM Temperature

Control response randomness:

```python
# In config.py
temperature = 0.7  # 0.0 = deterministic, 1.0 = more creative
```

## 🎯 Evaluation Results

**检索层（离线、可复现、真实实测）**：见上文 [第 0 节](#0-零依赖离线对比实验推荐先跑无需-api--无需外部服务)
的证据召回率表——分解式多轮检索把复杂题的召回率从 **8% 提升到 100%**，而简单题两种范式打平（均 100%）。

**生成层（端到端答案质量，需 LLM API）**：`evaluation/evaluate.py` 在此基础上真正调用 LLM 生成答案，
统计关键词/分析点召回、引用覆盖率、响应时间等指标。以下为该框架产出的指标与典型模式：

### Metrics
- **Success Rate**: Whether the answer contains key legal concepts
- **Response Time**: Time to generate response
- **Retrieval Quality**: Relevance of retrieved chunks
- **Citation Coverage**: Proper source attribution

### Expected Patterns

**Agentic RAG** typically shows:
- ✅ Better coverage of complex multi-faceted questions
- ✅ More accurate citations through explicit tool use  
- ✅ Ability to refine searches based on initial results
- ⚠️ Slower response time (multiple LLM calls)

**Non-Agentic RAG** typically shows:
- ✅ Faster responses (single retrieval step)
- ✅ Good performance on simple, direct questions
- ⚠️ May miss relevant information with poor query formulation
- ⚠️ Limited ability to handle ambiguous queries

## 🔧 Troubleshooting

### Retrieval Pipeline Not Responding

```bash
# Check if the service is running
curl http://localhost:4242/health

# If not, start it:
cd ../retrieval-pipeline
python main.py
```

### No Search Results

1. Ensure documents are indexed:
```bash
python index_local_laws.py
```

2. Check document store:
```bash
ls -la document_store.json
```

3. Verify retrieval pipeline has documents:
```bash
curl http://localhost:4242/stats
```

### API Key Issues

```bash
# Check if environment variable is set
echo $MOONSHOT_API_KEY

# Or use .env file
cat .env | grep API_KEY
```

### Indexing Errors

- Ensure retrieval pipeline is running before indexing
- Check file encodings (UTF-8 expected)
- Verify network connectivity to localhost:4242

## 🤝 Contributing

Areas for potential enhancement:

- Additional evaluation metrics
- More sophisticated chunking strategies
- Better reranking algorithms
- Additional knowledge base backends (RAPTOR, GraphRAG)
- Multi-language support
- Query expansion techniques
- Hybrid retrieval strategies

## 📄 License

This is an educational project for learning purposes.


## OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment now supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.
