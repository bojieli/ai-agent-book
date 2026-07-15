# Contextual Retrieval System - Educational Implementation

An educational implementation of Anthropic's Contextual Retrieval technique, demonstrating how contextualizing chunks before indexing dramatically improves retrieval accuracy in RAG systems.

## 🌟 Key Insight

**The Problem**: Traditional RAG systems lose context when chunking documents. A chunk saying "The company's revenue grew by 3%" loses meaning without knowing which company or time period.

**The Solution**: Contextual Retrieval prepends chunk-specific explanatory context to each chunk before embedding and indexing, preserving semantic meaning.

## 📚 Educational Features

This implementation includes extensive logging and comparison capabilities to understand:

1. **How Context Generation Works**: Watch the LLM generate context for each chunk
2. **Dual Indexing Strategy**: See how both BM25 and embeddings benefit from context
3. **Comparison Mode**: Run with `use_contextual=False` to compare against standard chunking
4. **Performance Metrics**: Track improvements in retrieval accuracy
5. **Cost Analysis**: Understand the token usage and costs

## 🏗️ Architecture

```
┌─────────────────────────────────────────┐
│           Document Input                │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│          Basic Chunking                 │
│   (Respects paragraph boundaries)       │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│     Context Generation (Optional)       │
│         Using LLM API                   │
│   (Enabled with use_contextual=True)   │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Enhanced Chunks                    │
│  • Contextual: Context + Original Text  │
│  • Standard: Original Text Only         │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│      Retrieval Pipeline Indexing        │
│   • Sparse Index (BM25)                 │
│   • Dense Index (Embeddings)            │
└────────────────┬────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│    Hybrid Search with Reranking         │
│   Combines BM25 + Embedding scores      │
│   Cross-encoder reranking for accuracy  │
└─────────────────────────────────────────┘
```

## 🚀 Quick Start

### 1. Installation

```bash
pip install -r requirements.txt
```

### 2. Configure Environment

```bash
cp env.example .env

# Edit .env and add your API keys:
# - MOONSHOT_API_KEY for Kimi
# - ARK_API_KEY for Doubao
# - OPENAI_API_KEY for OpenAI
# - etc.
```

### 3. Start the Retrieval Pipeline

```bash
# In a separate terminal, start the retrieval pipeline server
cd ../retrieval-pipeline
python main.py
# Server will run on http://localhost:4242
```

### 4. Index Documents

```bash
# Index Chinese law documents with contextual enhancement
python index_local_laws_contextual.py

# Or index without contextual enhancement for comparison
python index_local_laws_contextual.py --no-contextual
```

### 5. Run Queries

```bash
# Interactive mode with contextual retrieval
python main.py

# Query with specific mode
python main.py --query "宪法第一条是什么" --mode agentic

# Compare agentic vs non-agentic modes
python main.py --query "宪法第一条是什么" --mode compare
```

## Context Generation Process

The system generates context for each chunk by:

1. **Providing the full document** (or surrounding context) to the LLM
2. **Showing the specific chunk** to be contextualized
3. **Asking for concise context** (2-3 sentences) that situates the chunk

Example prompt template:
```
<document>
[Full document or surrounding context]
</document>

Here is the chunk we want to situate:
<chunk>
[Specific chunk text]
</chunk>

Please give a short, succinct context to situate this chunk within the overall document...
```

## 📚 References

- [Anthropic's Contextual Retrieval Blog Post](https://www.anthropic.com/engineering/contextual-retrieval)

## 🤝 Contributing

This is an educational implementation. Contributions welcome for:
- Additional chunking strategies
- Alternative context generation prompts
- Performance optimizations
- Evaluation metrics
- Visualization tools

## 📝 License

Educational project for learning purposes.

## 🙏 Acknowledgments

Based on research by Anthropic's engineering team on improving RAG retrieval accuracy through contextual enhancement.