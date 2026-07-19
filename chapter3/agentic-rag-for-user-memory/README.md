# Agentic RAG for User Memory Evaluation

An educational project that combines **Retrieval-Augmented Generation (RAG)** with **User Memory Evaluation** to demonstrate how AI agents can effectively manage and query long-term conversation histories.

## 🎯 Learning Objectives

This project teaches you:
1. **How to chunk long conversations** into manageable segments for indexing
2. **How to integrate with external retrieval pipelines** for hybrid search
3. **How to implement agentic RAG** with tool-calling and the ReAct pattern
4. **How to evaluate memory systems** with automatic LLM-based scoring
5. **How to optimize retrieval** for conversation-based queries
6. **How to integrate evaluation frameworks** from different projects

## 🏗️ Architecture Overview

```
┌─────────────────────────────────────────┐
│         User Memory Test Cases          │
│     (60 test cases, 3 difficulty layers) │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        Conversation Chunker              │
│  (Splits into 20-round segments with    │
│   overlap and contextual enrichment)     │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    External Retrieval Pipeline           │
│      (Port 4242 - Hybrid Search)         │
│  ┌─────────────┐  ┌──────────────────┐  │
│  │Dense Search │  │ Sparse Search    │  │
│  │ (Embeddings)│  │    (BM25)        │  │
│  └─────────────┘  └──────────────────┘  │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│       Agentic RAG Agent                  │
│   (ReAct pattern with memory tools)      │
│                                          │
│  Tools:                                  │
│  • search_memory                         │
│  • get_conversation_context              │
│  • get_full_conversation                 │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│        LLM Evaluation System              │
│   (Automatic scoring and reasoning)      │
│  • Reward score (0.0-1.0)                │
│  • Pass/Fail determination               │
│  • Detailed reasoning                    │
└─────────────────────────────────────────┘
```

## 📚 Key Concepts

### 1. Conversation Chunking
Long conversation histories are divided into chunks of approximately 20 rounds (user-assistant exchanges). This makes them:
- **Searchable**: Smaller units are easier to index and retrieve
- **Contextual**: Each chunk maintains context from surrounding conversations
- **Efficient**: Reduces the amount of text the LLM needs to process

### 2. Hybrid Retrieval (via External Pipeline)
The system integrates with an external retrieval pipeline service that provides:
- **Dense Retrieval**: Uses embeddings for semantic similarity search
- **Sparse Retrieval**: Uses BM25 for keyword matching and exact phrase search
- **Hybrid Fusion**: Combines scores from both methods for optimal results
- **Scalable Architecture**: Offloads indexing and search to dedicated service

### 3. Agentic RAG Pattern
The agent follows the ReAct (Reasoning + Acting) pattern:
1. **Reason** about what information is needed
2. **Act** by calling search tools
3. **Observe** the results
4. **Iterate** until sufficient information is found

### 4. Automatic LLM Evaluation
The system integrates with week2/user-memory-evaluation to provide:
- **Reward Scoring**: Continuous score from 0.0 to 1.0
- **Pass/Fail Assessment**: Automatic determination (≥0.6 passes)
- **Detailed Reasoning**: Explanation of evaluation decisions
- **Full Visibility**: Enhanced logging of LLM responses and tool calls

### 5. Contextual Enrichment
Chunks are enhanced with:
- Metadata about the conversation (business, department, timestamps)
- Context from previous and next chunks
- Semantic tags for better retrieval

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- **Retrieval Pipeline Service on port 4242 is now OPTIONAL.** By default the indexer
  uses `retrieval_backend="auto"`: it uses the external pipeline if it is reachable,
  otherwise it transparently falls back to a **built-in, dependency-free local BM25
  index** so the whole chunk → index → retrieve path runs fully offline.
- API keys are only needed for the LLM-driven parts:
  - A supported LLM provider (Kimi/Moonshot, OpenAI, SiliconFlow, DeepSeek, ...) for
    agent answer generation (`--mode batch`/`interactive`/`demo`).
  - The **offline comparison demo (`--mode offline-demo`) needs NO API key and NO
    port 4242 service.**

### Installation

```bash
# Enter the project
cd chapter3/agentic-rag-for-user-memory

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
# Edit .env with your API keys
```

### Retrieval Backend (offline by default, pipeline optional)

The retrieval backend is selectable via `--backend` (or `IndexConfig.retrieval_backend`):

| value      | behavior                                                                 |
|------------|--------------------------------------------------------------------------|
| `auto`     | default — use the port-4242 pipeline if reachable, else local BM25        |
| `local`    | always use the built-in offline BM25 index (no external service)         |
| `pipeline` | always use the external retrieval pipeline on port 4242                   |

To use the external pipeline (for dense/hybrid embeddings + reranking), start it first:

```bash
# In a separate terminal (OPTIONAL)
cd ../retrieval-pipeline
python api_server.py   # serves http://localhost:4242
```

### Running the Demo

```bash
# Offline comparison demo — NO API key, NO port 4242 needed.
# Shows agentic multi-hop memory retrieval beating naive single-query recall,
# on the multi-session layer2_01_multiple_vehicles case, with a metric table.
python main.py --mode offline-demo
python offline_demo.py                     # equivalent, standalone entry point
python offline_demo.py --output results/offline_demo.json   # also dump JSON

# Test the system setup
python test_pipeline.py

# Run interactive mode
python main.py

# Quick demo with a simple test case (needs an LLM API key)
python main.py --mode demo

# Batch evaluation of a category (needs an LLM API key; --backend local stays offline)
python main.py --mode batch --category layer1 --backend local
```

### Offline demo result (reproducible)

Running `python offline_demo.py` on `layer2_01_multiple_vehicles` (user owns a Honda
Accord with a scheduled Firestone service and a Tesla Model 3 without one, discussed
across two separate calls) yields, from real BM25 retrieval:

| metric                              | naive single-query | agentic multi-hop |
|-------------------------------------|:------------------:|:-----------------:|
| retrieval queries issued            | 1                  | 5                 |
| memory chunks retrieved             | 3                  | 5                 |
| decisive-evidence recall            | **50%**            | **100%**          |
| can fully disambiguate & answer     | no                 | yes               |

The naive query is dominated by "schedule service" keywords and misses the Honda
appointment-confirmation chunk (`FS-447291`). The agentic strategy discovers the
second vehicle from the first-round results, issues focused follow-up queries per
vehicle, and recovers the missing evidence. The recall numbers are computed from
actual retrieval, not hard-coded.

### CLI flags (`main.py`)

`--mode {interactive,batch,demo,offline-demo}`, `--category`, `--test-id`, `--query`,
`--provider`, `--model`, `--index-mode {dense,sparse,hybrid}`,
`--backend {auto,local,pipeline}`, `--top-k`, `--rounds-per-chunk`, `--store-path`,
`--test-cases-dir`, `--output`, `--config`. Run `python main.py --help` for the
(Chinese) descriptions.

## 📖 Usage Guide

### Interactive Mode

The interactive interface provides these options:

1. **Load Test Cases**: Load test cases from the evaluation framework
2. **View Test Cases**: Browse loaded test cases and their details
3. **Configure Settings**: Adjust chunking, indexing, and agent parameters
4. **Evaluate Single Test**: Run evaluation on a specific test case
5. **Evaluate by Category**: Test all cases in a difficulty layer
6. **Generate Report**: Create detailed evaluation reports

### Example Workflow

```python
# 1. Initialize the evaluator
from config import Config
from evaluator import UserMemoryEvaluator

config = Config.from_env()
evaluator = UserMemoryEvaluator(config)

# 2. Load test cases
test_cases = evaluator.load_test_cases(category="layer1")

# 3. Evaluate a test case
result = evaluator.evaluate_test_case("layer1_01_bank_account")

# 4. Generate report
report = evaluator.generate_report("results/evaluation_report.txt")
```

### Configuring the System

Key configuration options in `config.py`:

```python
# Chunking settings
config.chunking.rounds_per_chunk = 20  # Rounds per chunk
config.chunking.overlap_rounds = 2     # Overlapping rounds

# Index settings
config.index.mode = "hybrid"           # dense, sparse, or hybrid
config.index.enable_contextual = True  # Add contextual enrichment

# Agent settings
config.agent.max_search_results = 5    # Results per search
config.evaluation.max_iterations = 10  # Max ReAct iterations
```

## 🧪 Test Case Structure

Test cases follow the user-memory-evaluation framework format:

### Test Case Fields
- `test_id`: Unique identifier
- `category`: Difficulty layer (layer1, layer2, layer3)
- `title`: Descriptive title
- `conversation_histories`: Past conversations to index
- `user_question`: The question to answer
- `evaluation_criteria`: Criteria for evaluating responses
- `expected_behavior`: Optional expected agent behavior

### Layer 1: Simple Information Retrieval
- Single conversation with clear information
- Direct questions about specific details
- Example: "What is my checking account number?"

### Layer 2: Multi-Conversation Correlation
- Multiple related conversations
- Questions requiring information synthesis
- Example: "Which of my vehicles needs service first?"

### Layer 3: Complex Reasoning
- Hidden patterns and implicit connections
- Questions requiring deep analysis
- Example: "What urgent issues should I address before my trip?"

## 🔧 Component Details

### Chunker (`chunker.py`)
- Splits conversations into fixed-size chunks
- Maintains conversation flow with overlapping rounds
- Adds contextual information to each chunk

### Indexer (`indexer.py`)
- Integrates with external retrieval pipeline service
- Sends documents for indexing via HTTP API
- Manages document ID mapping
- Performs hybrid searches through the pipeline

### Tools (`tools.py`)
- `search_memory`: Main search interface with full content retrieval
- `get_conversation_context`: Retrieves surrounding chunks
- `get_full_conversation`: Gets entire conversation history
Note: All tools return complete content (not truncated)

### Agent (`agent.py`)
- Implements ReAct pattern with tool calling
- Manages conversation state
- Generates responses based on retrieved information

### Evaluator (`evaluator.py`)
- Loads test cases from YAML files
- Manages the indexing pipeline
- Tracks evaluation metrics and results
- Integrates automatic LLM evaluation

## 📊 Evaluation Metrics

The system tracks comprehensive metrics:
- **Success Rate**: Percentage of correctly answered questions
- **LLM Evaluation Score**: Automatic reward score (0.0-1.0) with detailed reasoning
- **Iterations**: Number of ReAct reasoning steps
- **Tool Calls**: Number and types of tools used
- **Processing Time**: Response generation time
- **Indexing Time**: Time to build search indexes
- **Result Quality**: Controlled by reranking with configurable top_k

## 🔍 Troubleshooting

### Top-K Results Issue
**Problem**: Getting 10 results regardless of `top_k` setting  
**Solution**: The retrieval pipeline uses two parameters:
- `top_k`: Initial retrieval count (for candidates)
- `rerank_top_k`: Final result count (what you actually get)

The system now correctly sets both parameters to respect your requested result count.

### LLM Evaluation Not Running
**Problem**: No automatic evaluation after agent response  
**Solution**: Ensure you have:
- Valid OpenAI API key for evaluation
- Access to week2/user-memory-evaluation module
- Proper test case format with evaluation_criteria

### Retrieval Pipeline Connection
**Problem**: Cannot connect to retrieval pipeline  
**Solution**: This is no longer fatal — with `--backend auto` (default) the system logs a
warning and falls back to the built-in local BM25 backend. If you specifically want the
external pipeline:
- Start the service: `cd ../retrieval-pipeline && python api_server.py`
- Verify it's running on `http://localhost:4242`
- Or force offline mode explicitly with `--backend local`

## 📄 License

This project is part of the AI Agent training curriculum and is intended for educational purposes.

## 🔗 Related Projects

- `week2/user-memory`: Basic user memory system
- `week2/user-memory-evaluation`: Evaluation framework
- `week3/agentic-rag`: Original agentic RAG implementation
- `week3/contextual-retrieval`: Advanced retrieval techniques


## OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment now supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.
