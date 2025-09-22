# Agentic RAG for User Memory Evaluation

An educational project that combines Retrieval-Augmented Generation (RAG) with user memory management for evaluating conversational AI systems. This system chunks conversation histories, indexes them for efficient retrieval, and provides an agentic interface for querying historical conversations with memory persistence.

## 🎯 Purpose

This project demonstrates how to:
- **Chunk conversations** into manageable segments (20 rounds per chunk)
- **Index conversation history** using RAG for efficient retrieval
- **Integrate user memory** from previous conversations
- **Provide agentic tools** for querying and analyzing conversation data
- **Evaluate memory consistency** across long conversation histories

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    User Query                            │
└────────────────────────┬────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────┐
│              UserMemoryRAGAgent                          │
│  ┌──────────────────────────────────────────────────┐   │
│  │            ReAct Pattern Loop                     │   │
│  │  1. Thought → 2. Action → 3. Observation         │   │
│  └──────────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
          ┌──────────────┴──────────────┐
          │                             │
          ▼                             ▼
┌──────────────────────┐     ┌──────────────────────┐
│   RAG Indexer         │     │  Memory Integration  │
│                       │     │                      │
│  • Local Storage      │     │  • Memory Notes      │
│  • Chroma DB          │     │  • Memory Cards      │
│  • FAISS              │     │  • Consolidation     │
└───────────┬───────────┘     └──────────┬───────────┘
            │                             │
            ▼                             ▼
┌──────────────────────┐     ┌──────────────────────┐
│  Conversation Chunks  │     │   User Memories      │
│                       │     │                      │
│  20 rounds per chunk  │     │  Extracted from      │
│  with 2-round overlap │     │  conversations       │
└───────────────────────┘     └──────────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd projects/week3/agentic-rag-for-user-memory

# Install dependencies
pip install -r requirements.txt

# Copy and configure environment variables
cp env.example .env
# Edit .env with your API keys
```

### 2. Run the Demo

```bash
# Run the quickstart script to see everything in action
python quickstart.py
```

This will:
1. Create sample conversation histories
2. Chunk them into 20-round segments
3. Build a RAG index
4. Extract memories
5. Run test queries

### 3. Interactive Mode

```bash
# Enter interactive query mode
python main.py query

# Build index from your own conversation history
python main.py build your_history.json --save-chunks

# Query with a specific question
python main.py query "What medications does the user take?"
```

## 📁 Project Structure

```
agentic-rag-for-user-memory/
├── config.py                 # Configuration management
├── conversation_chunker.py   # Chunks conversations into segments
├── rag_indexer.py           # RAG indexing and retrieval
├── memory_integration.py    # User memory management
├── agent.py                 # Main agentic RAG system
├── main.py                  # CLI interface
├── quickstart.py            # Demo script
├── requirements.txt         # Python dependencies
├── env.example             # Environment variables template
└── README.md               # This file
```

## 🛠️ Core Components

### 1. Conversation Chunker
Splits long conversation histories into chunks of 20 rounds (user-assistant pairs) with configurable overlap for context preservation.

```python
from conversation_chunker import ConversationChunker
from config import ChunkingConfig

config = ChunkingConfig(rounds_per_chunk=20, overlap_rounds=2)
chunker = ConversationChunker(config)
chunks, metadata = chunker.chunk_conversation_history("history.json")
```

### 2. RAG Indexer
Indexes conversation chunks for efficient semantic retrieval using embeddings.

```python
from rag_indexer import RAGIndexerFactory
from config import RAGConfig

config = RAGConfig(kb_type="local", top_k=5)
indexer = RAGIndexerFactory.create(config)
results = indexer.search("user's travel plans")
```

### 3. Memory Integration
Manages user memories extracted from conversations with RAG-enhanced context.

```python
from memory_integration import MemoryRAGIntegration

memory_integration = MemoryRAGIntegration()
memories = memory_integration.search_memories_with_context(
    "user preferences",
    include_conversation_context=True
)
```

### 4. Agent Tools

The agent provides several tools for querying and managing the indexed data:

- **search_conversations**: Search indexed conversation chunks
- **search_memories**: Search user memories with context
- **get_conversation_details**: Get details of specific chunks
- **extract_memory_from_conversation**: Extract memories from conversations
- **update_memory**: Update existing memories
- **consolidate_memories**: Merge similar memories

## 📊 Data Format

### Input: Conversation History
```json
{
  "conversations": [
    {
      "conversation_id": "conv_001",
      "timestamp": "2024-01-01T10:00:00",
      "messages": [
        {"role": "user", "content": "Hello!"},
        {"role": "assistant", "content": "Hi there!"}
      ]
    }
  ]
}
```

### Output: Conversation Chunks
```json
{
  "chunk_id": "abc123",
  "conversation_id": "conv_001",
  "chunk_index": 0,
  "start_round": 1,
  "end_round": 20,
  "text": "Conversation conv_001, Rounds 1-20:\n...",
  "metadata": {
    "total_rounds": 20,
    "has_overlap": false
  }
}
```

## 🔧 Configuration

### Environment Variables
```bash
# LLM Provider (openai, kimi, moonshot, doubao)
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o-mini

# API Keys
OPENAI_API_KEY=your_key_here

# Knowledge Base Type (local, chroma, faiss)
KB_TYPE=local

# Memory Mode
MEMORY_MODE=advanced_json_cards
```

### Python Configuration
```python
from config import Config

config = Config.from_env()
config.chunking.rounds_per_chunk = 20
config.rag.top_k = 5
config.agent.max_iterations = 10
```

## 🎓 Educational Concepts

### 1. Conversation Chunking
Learn how to segment long conversations into manageable chunks while preserving context through overlapping rounds.

### 2. RAG Implementation
Understand how to build a retrieval-augmented generation system from scratch using embeddings and semantic search.

### 3. Memory Management
Explore different memory storage patterns (notes vs. cards) and consolidation strategies for reducing redundancy.

### 4. Agentic Reasoning
Implement the ReAct (Reasoning + Acting) pattern for systematic problem-solving with tool usage.

### 5. Evaluation Framework
Build a system for evaluating memory consistency and retrieval accuracy across conversation histories.

## 📈 Performance Optimization

### Chunking Strategy
- **Optimal chunk size**: 20 rounds balances context and retrieval precision
- **Overlap**: 2-round overlap maintains conversation flow
- **Minimum chunk size**: 10 rounds to avoid fragmentation

### Indexing Options
- **Local**: Fast, simple, good for < 1000 chunks
- **Chroma**: Persistent, scalable, good for 1000-10000 chunks
- **FAISS**: High performance, good for > 10000 chunks

### Memory Consolidation
- Run consolidation when memory count > 100
- Use similarity threshold of 0.8 for automatic merging
- Manual review recommended for critical memories

## 🧪 Testing

### Run Basic Tests
```bash
# Test chunking
python main.py chunk test_data/history.json --verbose

# Test indexing
python main.py build test_data/history.json

# Test queries
python main.py query "What did we discuss about health?"
```

### Evaluation Metrics
- **Retrieval Accuracy**: Precision@K for relevant chunks
- **Memory Consistency**: Contradiction detection rate
- **Response Relevance**: Semantic similarity scores
- **Factual Accuracy**: Verification against ground truth

## 🤝 Integration with Week2 Projects

This project integrates with:
- **week2/user-memory**: Memory management system
- **week2/user-memory-evaluation**: Evaluation framework

To use the full user-memory system:
```python
import sys
sys.path.append("../../week2/user-memory")
from memory_manager import MemoryManager
```

## 📚 Learning Resources

### Key Papers
- [Retrieval-Augmented Generation](https://arxiv.org/abs/2005.11401)
- [ReAct: Reasoning and Acting](https://arxiv.org/abs/2210.03629)
- [Memory-Augmented Networks](https://arxiv.org/abs/1605.06065)

### Tutorials
1. [Building RAG from Scratch](https://www.example.com)
2. [Conversation Chunking Strategies](https://www.example.com)
3. [Memory Management in AI](https://www.example.com)

## 🐛 Troubleshooting

### Common Issues

1. **Import Error for user-memory**
   - Ensure week2/user-memory is in the correct path
   - Fallback implementations are provided if imports fail

2. **Embedding API Errors**
   - Check your OpenAI API key is valid
   - Ensure you have sufficient credits

3. **Memory Not Found**
   - Run indexing first: `python main.py build history.json`
   - Check the memories directory exists

4. **Slow Retrieval**
   - Consider using Chroma or FAISS for large datasets
   - Reduce chunk size or increase overlap

## 📝 License

This project is for educational purposes as part of the AI Agent Development course.

## 🙏 Acknowledgments

- Built upon concepts from week2/user-memory and week3/agentic-rag projects
- Inspired by OpenAI's RAG implementations
- Uses the ReAct pattern for agent reasoning

---

**Note**: This is an educational project designed to teach RAG concepts and memory management in conversational AI. For production use, consider additional optimizations and error handling.
