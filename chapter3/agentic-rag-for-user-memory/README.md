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
- **Retrieval Pipeline Service** running on port 4242 (see below)
- API keys for:
  - Kimi/Moonshot or another supported LLM provider (for agent responses)
  - OpenAI API (optional, for LLM evaluation)

### Installation

```bash
# Clone the project
cd projects/week3/agentic-rag-for-user-memory

# Install dependencies
pip install -r requirements.txt

# Setup environment variables
cp env.example .env
# Edit .env with your API keys
```

### Start the Retrieval Pipeline (Required)

This project uses the external retrieval pipeline service for indexing and search:

```bash
# In a separate terminal, start the retrieval pipeline
cd projects/week3/retrieval-pipeline
python api_server.py
```

The retrieval pipeline must be running on `http://localhost:4242` before using this system.

### Running the Demo

```bash
# Test the system setup
python test_pipeline.py

# Run interactive mode
python main.py

# Quick demo with a simple test case
python main.py --mode demo

# Batch evaluation of a category
python main.py --mode batch --category layer1
```

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
**Solution**: 
- Start the service: `cd projects/week3/retrieval-pipeline && python main.py`
- Verify it's running on `http://localhost:4242`
- Check firewall settings if connection fails

## 📄 License

This project is part of the AI Agent training curriculum and is intended for educational purposes.

## 🔗 Related Projects

- `week2/user-memory`: Basic user memory system
- `week2/user-memory-evaluation`: Evaluation framework
- `week3/agentic-rag`: Original agentic RAG implementation
- `week3/contextual-retrieval`: Advanced retrieval techniques
