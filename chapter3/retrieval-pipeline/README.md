# Hybrid Retrieval Pipeline with Neural Reranking

An educational retrieval pipeline that combines dense embeddings, sparse search, and neural reranking to demonstrate the strengths and weaknesses of different retrieval methods.

## 🎯 Educational Goals

This project demonstrates:
1. **Dense vs Sparse Retrieval**: When each method excels and why
2. **Hybrid Search**: Combining multiple retrieval methods for better results
3. **Neural Reranking**: Using transformer models to reorder search results
4. **Parallel Processing**: Efficient indexing and searching across multiple services
5. **Real-world Patterns**: Production-ready API design and error handling

## 🏗️ Architecture

```
┌──────────────────────────────────────────────┐
│            Client Application                 │
└────────────────────┬─────────────────────────┘
                     │
                     ▼
┌──────────────────────────────────────────────┐
│         Retrieval Pipeline (Port 4242)        │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │     Document Store (In-Memory)        │   │
│  └──────────────────────────────────────┘   │
│                                              │
│  ┌──────────────────────────────────────┐   │
│  │    BGE-Reranker-v2 (Local Model)     │   │
│  └──────────────────────────────────────┘   │
└────────┬──────────────────┬─────────────────┘
         │                  │
         ▼                  ▼
┌─────────────────┐  ┌─────────────────┐
│  Dense Service  │  │  Sparse Service │
│   (Port 4240)   │  │   (Port 4241)   │
│                 │  │                 │
│   BGE-M3 Model  │  │   BM25 Engine   │
└─────────────────┘  └─────────────────┘
```

## 📚 Key Concepts

### Dense Embeddings (Semantic Search)
- **Model**: BGE-M3 (multilingual, 1024-dim vectors)
- **Strengths**:
  - Semantic similarity (finds related concepts)
  - Cross-lingual search (works across languages)
  - Conceptual understanding (handles synonyms)
  - Context awareness (understands meaning)
- **Weaknesses**:
  - May miss exact strings
  - Less effective for codes/IDs
  - Computationally expensive

### Sparse Search (BM25)
- **Algorithm**: BM25 (Best Matching 25)
- **Strengths**:
  - Exact term matching
  - Specific names and codes
  - Technical identifiers
  - Fast and efficient
- **Weaknesses**:
  - No semantic understanding
  - Language-specific
  - Requires exact terms

### Result Fusion (RRF / Weighted)
- **Module**: `fusion.py`
- **Purpose**: Merge the separately-ranked dense and sparse candidate lists into
  one unified pool before reranking (the *fusion* stage)
- **Two strategies** (both discussed in the book):
  - **Reciprocal Rank Fusion (RRF)**: `score(d) = Σ 1/(k + rank_r(d))`, `k=60`.
    Uses only ranks, so it never has to compare a cosine similarity against a
    BM25 score — robust and scale-free.
  - **Weighted score fusion**: min-max normalize each list to `[0,1]`, then take a
    weighted sum. Keeps the raw relevance signal, at the cost of tuning the scale
    alignment.

### Neural Reranking
- **Model**: BGE-Reranker-v2-M3 (production); `BAAI/bge-reranker-base` (lighter, used by `evaluate.py`)
- **Purpose**: Re-score and reorder the fused candidate pool
- **Benefits**:
  - Better relevance ranking
  - Combines signals from both methods
  - Context-aware scoring

## 🚀 Quick Start

### Prerequisites

1. Python 3.8+
2. macOS with M1/M2 chip (or modify device settings for other platforms)
3. At least 8GB RAM
4. About 5GB disk space for models

### Installation

```bash
# Clone the repository
cd projects/week3/retrieval-pipeline

# Install dependencies
pip install -r requirements.txt

# The models will be downloaded automatically on first run:
# - BGE-M3: ~2.3GB
# - BGE-Reranker-v2-M3: ~1.1GB
```

### Running the Services

1. **Start all services** (recommended):
```bash
./start_all_services.sh
```

This will start:
- Dense embedding service on port 4240
- Sparse embedding service on port 4241
- Retrieval pipeline on port 4242

2. **Or start individually**:
```bash
# Terminal 1: Dense service
cd ../dense-embedding
python main.py --port 4240

# Terminal 2: Sparse service
cd ../sparse-embedding
python server.py --port 4241

# Terminal 3: Pipeline
cd ../retrieval-pipeline
python main.py --port 4242
```

### Testing the Pipeline

1. **Run educational tests**:
```bash
python test_client.py
```

This runs comprehensive test cases showing when dense vs sparse excels.

2. **Run interactive demo**:
```bash
python demo.py
```

This demonstrates real queries with explanations.

3. **Access API documentation**:
```
http://localhost:4242/docs
```

## 🧪 Offline Evaluation CLI (`evaluate.py`)

`test_client.py` / `demo.py` above require the three microservices (ports
4240/4241/4242) to be running. **`evaluate.py` runs the entire pipeline in a
single process, fully offline**, so you can reproduce the "each stage improves
the ranking" story with local models and no services.

It walks the complete pipeline — **chunk → embed → retrieve → fuse → rerank** —
on a small labelled eval set and prints a stage-by-stage comparison table plus a
per-query breakdown. The CLI has a full Chinese `--help`:

```bash
python evaluate.py --help          # 中文帮助：语料/查询/阶段/top-k/模型/输出等
python evaluate.py                 # 内置评测集，完整对比表（默认）
python evaluate.py --no-dense      # 仅 BM25，纯离线、无需任何模型
python evaluate.py --no-rerank     # 跳过重排阶段
python evaluate.py --query "XR-7003"   # 单条查询逐阶段排名追踪
python evaluate.py --embed-model BAAI/bge-m3 --pooling cls   # 换稠密模型
python evaluate.py --output result.json                      # 结果写入 JSON
```

Local components (each stage is a real model / algorithm, not a mock):

| Stage    | Component (default)                              | Offline? |
|----------|--------------------------------------------------|----------|
| chunk    | character-window splitter                         | ✅ pure Python |
| sparse   | BM25 (`rank_bm25`)                                | ✅ no model download |
| dense    | `sentence-transformers/all-MiniLM-L6-v2` (~90MB) | ✅ via `transformers` (multilingual: swap in `Qwen/Qwen3-Embedding-0.6B` / `BAAI/bge-m3`) |
| fuse     | RRF + weighted (`fusion.py`)                      | ✅ pure Python |
| rerank   | `BAAI/bge-reranker-base` (~1.1GB, first run downloads) | ✅ once cached |

> **Note**: `--no-dense` needs no ML model at all (BM25 only). The dense and
> rerank stages need local models; on first run they download from HuggingFace,
> after which `--offline` keeps everything on the local cache. On Apple Silicon,
> some `transformers` builds emit `NaN` on the MPS device — the CLI detects this
> and automatically falls back to CPU, so results are always finite.

### Real output (reproduced on this machine)

The built-in eval set has two deliberately hard clusters: **near-duplicate codes**
(`XR-7001..XR-7006`, `HTTP-400..HTTP-500`) that break dense retrieval (the vectors
are almost identical, only exact term matching finds the right one), and
**zero-lexical-overlap paraphrases** (query "reclaiming unused heap space without
programmer effort" → doc "Automatic memory management frees developers…") that
break BM25.

```
Stage / Method            Recall@3         MRR      nDCG@3
------------------------------------------------------------------------------
BM25 (sparse)               0.9000      0.8500      0.8631
Dense                       1.0000      0.9000      0.9262
Hybrid-RRF                  1.0000      1.0000      1.0000
Hybrid-Weighted             1.0000      0.9500      0.9631
Hybrid-RRF+Rerank           1.0000      0.9500      0.9631

逐条查询 MRR 明细（1.00=正确文档排在第 1 位）
Query                                        BM25  Dense    RRF    Wgt Rerank
------------------------------------------------------------------------------
XR-7003                                      1.00   0.50   1.00   1.00   1.00
XR-7005                                      1.00   0.50   1.00   1.00   1.00
HTTP-403                                     1.00   1.00   1.00   1.00   1.00
HTTP-400                                     1.00   1.00   1.00   1.00   0.50
a beginner friendly language with tidy...    1.00   1.00   1.00   1.00   1.00
reclaiming unused heap space without p...    0.00   1.00   1.00   1.00   1.00
how vegetation turns light into food         0.50   1.00   1.00   0.50   1.00
hiding a note so eavesdroppers cannot ...    1.00   1.00   1.00   1.00   1.00
how does water move between the ocean ...    1.00   1.00   1.00   1.00   1.00
how are volcanoes formed from molten rock    1.00   1.00   1.00   1.00   1.00
```

**How to read it:**
- **BM25 (sparse)** nails every exact code but collapses on the two paraphrase
  queries (`reclaiming…`=0.00, `vegetation…`=0.50).
- **Dense** is the mirror image: perfect on paraphrases, but confuses the
  near-duplicate codes (`XR-7003`/`XR-7005`=0.50 — it ranks a sibling code first).
- **Hybrid-RRF** combines the two and reaches a **perfect 1.00** across the board:
  fusion rescues *both* single-method failures. This is the headline of Exp. 3-6.
- **Weighted fusion** is strong too but less robust than RRF here (the `vegetation`
  query drops to 0.50 because a lexical near-match distorts the normalized scores —
  exactly the "scale alignment is hard to tune" caveat).
- **Reranking**: on this 17-doc toy corpus RRF is *already* optimal, so reranking
  has no headroom; a cross-encoder is a semantic matcher and can even slightly
  reorder a trivial exact-code lookup (`HTTP-400`). Its value grows on larger
  candidate pools and natural-language queries — see the single-query trace below.

The single-query trace makes the fusion mechanism concrete:

```
$ python evaluate.py --query "XR-7003"
[BM25 (sparse)]
  1. xr_7003        score=  3.2260  Product model XR-7003 is a smartphone available now.
[Dense]
  1. xr_7001        score=  0.5247  Product model XR-7001 ...   # dense ranks the wrong sibling first
  2. xr_7003        score=  0.5195  Product model XR-7003 ...
[Hybrid-RRF]
  1. xr_7003        score=  0.0325  Product model XR-7003 ...   # fusion promotes the exact match to #1
```

## 📊 Educational Test Cases

### Test Case 1: Semantic Similarity (Dense Wins)
```python
# Query: "kitty behavior"
# Documents contain: "feline", "cat"
# Dense finds semantic match, sparse misses
```

### Test Case 2: Exact Names (Sparse Wins)
```python
# Query: "Alexander Humphrey"
# Sparse finds exact name match
# Dense might return other people
```

### Test Case 3: Multilingual (Dense Wins)
```python
# Query: "人工智能" (Chinese for AI)
# Dense finds AI docs in any language
# Sparse only finds Chinese text
```

### Test Case 4: Technical Codes (Sparse Wins)
```python
# Query: "HTTP-403"
# Sparse finds exact error code
# Dense might return other errors
```

### Test Case 5: Concepts (Dense Wins)
```python
# Query: "happiness and excitement"
# Documents contain: "joy", "elation"
# Dense understands emotional concepts
```

## 🔧 API Endpoints

### Index Document
```bash
POST /index
{
  "text": "Document content",
  "doc_id": "optional_id",
  "metadata": {"category": "example"}
}
```

### Search
```bash
POST /search
{
  "query": "search terms",
  "mode": "hybrid",  # or "dense" or "sparse"
  "top_k": 20,
  "rerank_top_k": 10
}
```

Response includes:
- Original dense rankings and scores
- Original sparse rankings and scores
- Final reranked results
- Rank change statistics
- Performance metrics

### Statistics
```bash
GET /stats
```

### List Documents
```bash
GET /documents?limit=10&offset=0
```

## 📈 Understanding the Results

The search response provides educational insights:

```json
{
  "dense_results": [...],    # Top results from semantic search
  "sparse_results": [...],   # Top results from BM25
  "reranked_results": [      # Final reranked results
    {
      "rank": 1,
      "doc_id": "doc_1",
      "rerank_score": 0.95,
      "original_ranks": {
        "dense": 3,         # Was rank 3 in dense
        "sparse": 5         # Was rank 5 in sparse
      },
      "rank_changes": [
        "dense: +2",        # Moved up 2 positions
        "sparse: +4"        # Moved up 4 positions
      ]
    }
  ],
  "statistics": {
    "overlap_percentage": 30.0,  # How much dense/sparse agree
    "avg_dense_rank_change": 1.5,
    "avg_sparse_rank_change": 2.1
  }
}
```

## 🎓 Learning Exercises

1. **Experiment with queries**:
   - Try synonyms vs exact terms
   - Test multilingual queries
   - Use technical codes

2. **Modify parameters**:
   - Change `top_k` to retrieve more/fewer candidates
   - Skip reranking to see raw results
   - Try different search modes

3. **Analyze patterns**:
   - When does hybrid outperform single methods?
   - How much do dense and sparse results overlap?
   - Which queries benefit most from reranking?

## 🔍 Troubleshooting

### Services won't start
- Check ports 4240-4242 are free
- Ensure models downloaded properly
- Check Python version (3.8+)

### Out of memory
- Reduce batch sizes in config.py
- Use CPU instead of MPS/CUDA
- Enable FP16 mode

### Slow performance
- First run downloads models (be patient)
- Subsequent runs use cached models
- Consider using GPU if available

## 📝 Configuration

Edit `config.py` to adjust:
- Service URLs
- Model parameters
- Retrieval settings
- Reranking parameters

## 🏛️ Project Structure

```
retrieval-pipeline/
├── config.py               # Configuration settings (incl. fusion_method / rrf_k)
├── document_store.py       # In-memory document storage
├── retrieval_client.py     # Client for dense/sparse services
├── reranker.py            # BGE-Reranker implementation
├── fusion.py              # Result fusion: RRF + weighted score fusion
├── retrieval_pipeline.py   # Main pipeline orchestration (uses fusion.py)
├── evaluate.py            # Offline single-process eval CLI (Chinese --help)
├── main.py                # FastAPI server
├── test_client.py         # Educational test cases
├── demo.py                # Interactive demonstration
├── requirements.txt       # Python dependencies
├── start_all_services.sh  # Start script
├── stop_all_services.sh   # Stop script
└── README.md             # This file
```

## 🚦 Performance Considerations

- **Indexing**: Parallel indexing to both services
- **Search**: Parallel retrieval, then sequential reranking
- **Memory**: ~4GB for models, plus document storage
- **Latency**: 
  - Dense: ~50-100ms per query
  - Sparse: ~10-30ms per query  
  - Reranking: ~100-200ms for 20 documents

## 🎯 Key Takeaways

1. **No single method is best**: Dense and sparse have complementary strengths
2. **Hybrid search wins**: Combining methods typically improves results
3. **Reranking matters**: Neural reranking significantly improves relevance
4. **Parallel processing**: Essential for production performance
5. **Educational value**: Understanding trade-offs helps choose the right approach

## 📚 Further Reading

- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216)
- [BM25 Algorithm](https://en.wikipedia.org/wiki/Okapi_BM25)
- [Neural Information Retrieval](https://arxiv.org/abs/2301.09191)
- [Dense vs Sparse Retrieval](https://arxiv.org/abs/2104.08396)

## 📄 License

This is an educational project for learning purposes.
