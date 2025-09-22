# Contextual Retrieval System - Educational Implementation

An educational implementation of Anthropic's Contextual Retrieval technique, demonstrating how contextualizing chunks before indexing dramatically improves retrieval accuracy in RAG systems.

## 🌟 Key Insight

**The Problem**: Traditional RAG systems lose context when chunking documents. A chunk saying "The company's revenue grew by 3%" loses meaning without knowing which company or time period.

**The Solution**: Contextual Retrieval prepends chunk-specific explanatory context to each chunk before embedding and indexing, preserving semantic meaning.

## 📚 Educational Features

This implementation includes extensive logging and comparison capabilities to understand:

1. **How Context Generation Works**: Watch the LLM generate context for each chunk
2. **Dual Indexing Strategy**: See how both BM25 and embeddings benefit from context
3. **Side-by-Side Comparison**: Compare contextual vs non-contextual retrieval
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
        ┌────────┴────────┐
        │                 │
        ▼                 ▼
┌──────────────┐  ┌──────────────────────┐
│ Non-Contextual│  │ Context Generation   │
│    Path      │  │   (Using LLM)        │
└──────┬───────┘  └──────┬───────────────┘
       │                 │
       │                 ▼
       │         ┌──────────────────────┐
       │         │ Contextual Chunks    │
       │         │ (Context + Original) │
       │         └──────┬───────────────┘
       │                 │
       ▼                 ▼
┌──────────────────────────────────────┐
│         Dual Indexing                │
│   • BM25 Index (Lexical)             │
│   • Embedding Index (Semantic)       │
└──────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────┐
│      Hybrid Search (Rank Fusion)     │
│   Combines BM25 + Embedding scores   │
└──────────────────────────────────────┘
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

### 3. Run the Demo

```bash
# Full demonstration with example document
python contextual_main.py --mode demo

# Index a specific document
python contextual_main.py --mode index --document path/to/document.txt

# Compare search results
python contextual_main.py --mode search --query "Your question here"

# Compare agent responses
python contextual_main.py --mode compare --query "Your question here"
```

## 📖 Detailed Usage

### Context Generation Process

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

### Indexing Documents

```python
from contextual_chunking import ContextualChunker
from contextual_tools import ContextualKnowledgeBaseTools

# Initialize with contextual mode
chunker = ContextualChunker(use_contextual=True)
kb_tools = ContextualKnowledgeBaseTools(use_contextual=True)

# Chunk and contextualize document
chunks = chunker.chunk_document(
    text=document_text,
    doc_id="doc_1",
    doc_metadata={"source": "example.pdf"}
)

# Index chunks
kb_tools.index_contextual_chunks(chunks)
```

### Searching with Context

```python
# Perform contextual search
results = kb_tools.contextual_search(
    query="What is the revenue growth?",
    method="hybrid",  # or "bm25" or "embedding"
    top_k=10
)

# Each result includes:
for result in results:
    print(f"Score: {result.score}")
    print(f"Context: {result.context_text}")
    print(f"Text: {result.text}")
```

### Comparing Methods

```python
# Compare contextual vs non-contextual
comparison = kb_tools.compare_retrieval_methods(
    query="Your question",
    top_k=20
)

# View analysis
print(f"Improvement: {comparison['analysis']['contextual_improvement']}")
```

## 📊 Example Results

Based on Anthropic's research, contextual retrieval shows:

| Method | Retrieval Failure Rate | Improvement |
|--------|------------------------|-------------|
| Standard Embeddings | 5.7% | Baseline |
| Contextual Embeddings | 3.7% | 35% reduction |
| Contextual Embeddings + BM25 | 2.9% | 49% reduction |
| + Reranking | 1.9% | 67% reduction |

## 🔍 Understanding the Logs

The system provides detailed educational logging:

### Context Generation Logs
```
[CONTEXTUAL INDEXING]
Generating contextual chunks...
Progress: 10/50 chunks, avg time: 0.85s
Generated context in 0.92s: "This chunk discusses Q2 2023 financial results for ACME Corp..."
```

### Retrieval Comparison Logs
```
[SEARCH COMPARISON]
Query: What is the revenue growth?

[CONTEXTUAL SEARCH]
  Result 1:
    Score: 0.8234
    Context: This chunk is from ACME Corp's Q2 2023 financial report...
    Text: The company's revenue grew by 3%...

[NON-CONTEXTUAL SEARCH]  
  Result 1:
    Score: 0.5123
    Text: The company's revenue grew by 3%...

IMPROVEMENT: 60.8%
```

## 🎓 Educational Insights

### When Context Helps Most

1. **Ambiguous References**: "The company", "it", "this method"
2. **Technical Terms**: Context provides domain information
3. **Temporal Information**: Dates and time periods
4. **Hierarchical Documents**: Section and subsection context
5. **Multi-topic Documents**: Distinguishes between topics

### Trade-offs

| Aspect | Contextual | Non-Contextual |
|--------|------------|----------------|
| **Indexing Time** | Slower (LLM calls) | Fast |
| **Indexing Cost** | ~$1 per million tokens | Free |
| **Storage** | Larger (context added) | Smaller |
| **Retrieval Quality** | High | Moderate |
| **Best For** | Production, accuracy-critical | Prototyping, cost-sensitive |

## 🛠️ Configuration Options

### Chunking Parameters
```python
config.chunking.chunk_size = 2048  # Characters per chunk
config.chunking.max_chunk_size = 4096  # Maximum chunk size
config.chunking.chunk_overlap = 200  # Overlap between chunks
config.chunking.respect_paragraph_boundary = True  # Preserve paragraphs
```

### Context Generation
```python
config.llm.provider = "openai"  # LLM for context generation
config.llm.model = "gpt-3.5-turbo"  # Model choice
config.llm.temperature = 0.3  # Lower = more consistent
```

### Search Methods
- **BM25**: Best for exact matches, technical terms
- **Embedding**: Best for semantic similarity
- **Hybrid**: Combines both using rank fusion

## 📈 Performance Optimization

### Caching Strategy
The system caches generated contexts to avoid regenerating for identical chunks:
```python
Cache hit rate: 45% (saving ~$0.45 per 1000 chunks)
```

### Batch Processing
Process multiple documents efficiently:
```bash
python batch_index.py --input documents/ --output indexes/
```

## 🔬 Experimental Features

### Multi-level Context
Generate context at different granularities:
- Chunk-level context (current)
- Section-level context
- Document-level summary

### Dynamic Context Length
Adjust context length based on chunk complexity:
- Simple chunks: 1-2 sentences
- Complex chunks: 3-4 sentences

## 📚 References

- [Anthropic's Contextual Retrieval Blog Post](https://www.anthropic.com/engineering/contextual-retrieval)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Reciprocal Rank Fusion](https://plg.uwaterloo.ca/~gvcormac/cormacksigir09-rrf.pdf)

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