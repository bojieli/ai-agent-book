# Vector Similarity Search Service

An educational HTTP service for vector similarity search using BGE-M3 embeddings with configurable ANNOY or HNSW indexing backends.

---

## 命令行工具：稠密检索与 ANN 对比（cli.py，实验 3-4）

除了上面的 HTTP 服务，本项目还提供一个**开箱即用、可离线复现**的命令行工具 `cli.py`，
把书中实验 3-4 的两个观察点直接跑成可量化的数字，无需先启动服务：

1. **稠密嵌入检索的语义能力**——在带标注的小型语料上计算 `recall@k / precision@k / MRR`；
2. **ANN 索引后端对比**（实验 3-4 的重点）——复用服务端 `indexing.py` 里的 ANNOY / HNSW
   实现，测量二者相对**精确暴力检索**的召回率、建索引耗时与查询延迟。

### 用法

```bash
# 1) 单条稠密查询（默认查询 "a cat playing"，需要嵌入模型）
python cli.py -q "model distillation" -k 3

# 2) 检索质量评测：recall@k / precision@k / MRR
python cli.py --eval

# 2') 离线复现：用已缓存的小模型（无需下载 2.3GB 的 BGE-M3）
python cli.py --embedding-model sentence-transformers/all-MiniLM-L6-v2 --eval

# 3) ANN 后端对比（合成向量，完全离线、无需任何模型）
python cli.py --compare-ann -k 10
python cli.py --compare-ann --backend hnsw --hnsw-ef-search 200 -k 10   # 调 ef_search 看召回随之上升

# 自定义语料 / 标注 / 输出
python cli.py --corpus my.json --labels my_labels.json --eval -o result.json
```

`python cli.py --help` 提供完整的中文参数说明（`--corpus / --query / --embedding-model /
--top-k / --output`，以及 ANN 对比的各项索引超参）。

### 常用参数

| 参数 | 说明 |
| --- | --- |
| `-q, --query` | 查询字符串（默认 `a cat playing`） |
| `-c, --corpus` | 语料文件（`.json` 数组 或 `.jsonl` 每行一篇）；缺省用内置示例语料 |
| `-k, --top-k` | 返回前 k 条结果（默认 5） |
| `-o, --output` | 把结果 / 评测指标写入 JSON 文件 |
| `--embedding-model` | 嵌入模型名（默认 `BAAI/bge-m3`；离线可用 `sentence-transformers/all-MiniLM-L6-v2`） |
| `--pooling` | 池化方式 `auto`（bge* 用 cls，其余 mean）/ `mean` / `cls` |
| `--eval` | 在标注集上评测 recall@k / precision@k / MRR |
| `--compare-ann` | 对比 ANNOY / HNSW（合成向量，无需模型） |
| `--ann-base / --ann-dim / --ann-queries` | 合成底库规模 / 维度 / 查询数（默认 3000 / 128 / 100） |
| `--annoy-n-trees / --hnsw-M / --hnsw-ef-search` | 两类 ANN 的关键索引超参 |

### 实测结果（真实运行，非杜撰）

**稠密检索质量**（内置 12 篇语料，`all-MiniLM-L6-v2`，离线）：

```
宏平均  recall@5=1.000  precision@5=0.320  MRR=1.000
```

其中查询 `a cat playing` 的相关文档只用 `kitten` / `feline` 表达、**不含字面 "cat"**，
稠密检索仍把它们排到第 1、2 名——这正是稠密相对稀疏 BM25（实验 3-5 会漏召回）的语义优势。

**ANN 后端对比**（3000 条 128 维随机单位向量，100 条查询，top-10）：HNSW 的召回率随
`ef_search` 单调上升，体现"精度 / 速度"取舍：

| 配置 | recall@10 | 平均查询延迟 |
| --- | --- | --- |
| HNSW `ef_search=20` | 0.562 | 0.05 ms |
| HNSW `ef_search=200` | 0.991 | 0.25 ms |

> **环境提示**：本工具对每个后端会先做"自查询自身向量"的健康检查。在部分 macOS/arm64 环境下，
> `annoy==1.17.3` 的预编译轮子存在缺陷（连查询库中已有向量都只返回它自己），此时工具会打印
> `[警告] ...疑似当前环境下损坏` 并把该后端的数字标记为不可信。HNSW 不受影响。若要复现完整的
> ANNOY vs HNSW 对比，请在 annoy 正常工作的环境（如 Linux x86_64）中运行。

## Features

- **BGE-M3 Model**: State-of-the-art multilingual embedding model supporting:
  - Dense embeddings for semantic search
  - Multi-language support (100+ languages)
  - Long context (up to 8192 tokens)
  
- **Dual Indexing Backends**:
  - **ANNOY** (Approximate Nearest Neighbors Oh Yeah): Fast, memory-efficient tree-based index
  - **HNSW** (Hierarchical Navigable Small World): High-precision graph-based index

- **Educational Logging**: Extensive debug logs showing:
  - Embedding generation process
  - Index operations (insert/delete/search)
  - Performance metrics
  - Vector statistics

- **RESTful API**: Clean HTTP endpoints for:
  - Document indexing (insert/update)
  - Document deletion
  - Similarity search
  - Statistics and monitoring

- **In-Memory Storage**: Pure in-memory operation for simplicity (no persistence)

## Architecture

```
┌──────────────────┐
│   HTTP Client    │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│  FastAPI Server  │
└────────┬─────────┘
         │
         ▼
    ┌────┴────┐
    │         │
    ▼         ▼
┌──────────┐ ┌──────────────┐
│ Document │ │  Embedding   │
│  Store   │ │   Service    │
└──────────┘ │  (BGE-M3)    │
             └──────┬─────────┘
                    │
                    ▼
          ┌─────────┴──────────┐
          │                    │
          ▼                    ▼
    ┌──────────┐        ┌──────────┐
    │  ANNOY   │        │   HNSW   │
    │  Index   │        │  Index   │
    └──────────┘        └──────────┘
```

## Installation

### Prerequisites

- Python 3.8 or higher
- macOS (optimized for M1/M2 chips) or Linux
- At least 4GB RAM (8GB recommended)
- CUDA-compatible GPU (optional, for faster embedding generation)

### Setup

1. Install dependencies:

```bash
cd projects/week3/dense-embedding
pip install -r requirements.txt
```

2. Download BGE-M3 model (will be downloaded automatically on first run):
   - Model size: ~2.3GB
   - Will be cached in HuggingFace cache directory

## Usage

### Starting the Service

#### With HNSW Index (Default)

```bash
python main.py
```

#### With ANNOY Index

```bash
python main.py --index-type annoy
```

#### With Custom Configuration

```bash
python main.py --index-type hnsw --host 0.0.0.0 --port 4242 --debug --show-embeddings
```

#### Available Options

- `--index-type`: Choose index backend (`annoy` or `hnsw`, default: `hnsw`)
- `--host`: Server host (default: `0.0.0.0`)
- `--port`: Server port (default: `4240`)
- `--debug`: Enable debug mode with verbose logging
- `--show-embeddings`: Show embedding vectors in logs (educational)

### API Documentation

Once the service is running, visit:
- Interactive docs: http://localhost:4240/docs
- OpenAPI schema: http://localhost:4240/openapi.json

### API Endpoints

#### 1. Index Document

```bash
POST /index
```

Index a new document or update existing one.

**Request:**
```json
{
  "text": "Machine learning is a subset of artificial intelligence.",
  "doc_id": "doc_001",  // Optional, auto-generated if not provided
  "metadata": {         // Optional metadata
    "category": "AI",
    "author": "John Doe"
  }
}
```

**Response:**
```json
{
  "success": true,
  "doc_id": "doc_001",
  "message": "Document indexed successfully using hnsw",
  "index_size": 1
}
```

#### 2. Search Documents

```bash
POST /search
```

Search for similar documents.

**Request:**
```json
{
  "query": "What is deep learning?",
  "top_k": 5,
  "return_documents": true
}
```

**Response:**
```json
{
  "success": true,
  "query": "What is deep learning?",
  "results": [
    {
      "doc_id": "doc_001",
      "score": 0.8543,
      "text": "Machine learning is a subset...",
      "metadata": {"category": "AI"},
      "rank": 1
    }
  ],
  "total_results": 5,
  "search_time_ms": 12.5
}
```

#### 3. Delete Document

```bash
DELETE /index
```

Delete a document from the index.

**Request:**
```json
{
  "doc_id": "doc_001"
}
```

**Response:**
```json
{
  "success": true,
  "message": "Document doc_001 deleted successfully",
  "index_size": 0
}
```

#### 4. Get Statistics

```bash
GET /stats
```

Get service statistics.

**Response:**
```json
{
  "index_type": "hnsw",
  "index_size": 100,
  "document_count": 100,
  "embedding_dimension": 1024,
  "model_name": "BAAI/bge-m3"
}
```

#### 5. List Documents

```bash
GET /documents?limit=10
```

List documents in the store.

## Testing

### Run Demo Client

The demo client showcases all features with sample documents:

```bash
python test_client.py
```

### Run Performance Test

Test indexing and search performance with synthetic data:

```bash
python test_client.py --performance
```

### Manual Testing with curl

Index a document:
```bash
curl -X POST http://localhost:4240/index \
  -H "Content-Type: application/json" \
  -d '{"text": "This is a test document about machine learning."}'
```

Search for similar documents:
```bash
curl -X POST http://localhost:4240/search \
  -H "Content-Type: application/json" \
  -d '{"query": "artificial intelligence", "top_k": 5}'
```

## Index Comparison

### ANNOY (Approximate Nearest Neighbors Oh Yeah)

**Pros:**
- Very fast indexing
- Low memory footprint
- Good for static datasets
- Supports multiple distance metrics

**Cons:**
- Requires rebuild for deletion
- No incremental updates after build
- Trade-off between speed and accuracy (controlled by n_trees)

**Best for:**
- Large-scale similarity search
- Read-heavy workloads
- Memory-constrained environments

### HNSW (Hierarchical Navigable Small World)

**Pros:**
- High recall accuracy
- Supports incremental updates
- Fast search with good precision
- Supports soft deletion

**Cons:**
- Higher memory usage
- Slower indexing than ANNOY
- More complex parameter tuning

**Best for:**
- Dynamic datasets
- High-precision requirements
- Balanced read/write workloads

## Configuration

### Environment Variables

You can configure the service using environment variables with the `VEC_` prefix:

```bash
export VEC_INDEX_TYPE=hnsw
export VEC_MODEL_NAME=BAAI/bge-m3
export VEC_USE_FP16=true
export VEC_MAX_SEQ_LENGTH=512
export VEC_MAX_DOCUMENTS=100000
export VEC_LOG_LEVEL=DEBUG

# ANNOY specific
export VEC_ANNOY_N_TREES=50
export VEC_ANNOY_METRIC=angular

# HNSW specific
export VEC_HNSW_EF_CONSTRUCTION=200
export VEC_HNSW_M=32
export VEC_HNSW_EF_SEARCH=100
export VEC_HNSW_SPACE=cosine
```

## Educational Features

This service includes extensive logging for educational purposes:

1. **Embedding Generation Logs**: Shows the process of converting text to vectors
2. **Index Operation Logs**: Detailed information about index updates
3. **Search Process Logs**: Step-by-step search execution
4. **Performance Metrics**: Timing information for all operations
5. **Vector Statistics**: Min/max/mean values of embeddings (when enabled)

Enable full educational logging:
```bash
python main.py --debug --show-embeddings
```

## Performance Considerations

### Memory Usage

- BGE-M3 model: ~2.3GB
- Per document overhead: ~4KB (1024-dim float32 embedding)
- ANNOY index: ~(4 * dimension * n_items * n_trees / 2) bytes
- HNSW index: ~(4 * dimension * n_items * M * 2) bytes

### Optimization Tips

1. **For ANNOY**:
   - Increase `n_trees` for better accuracy (slower build)
   - Use `angular` metric for normalized vectors
   - Build index after batch insertions

2. **For HNSW**:
   - Increase `M` for better recall (more memory)
   - Increase `ef_construction` for better index quality (slower build)
   - Adjust `ef_search` for speed/accuracy trade-off

3. **General**:
   - Use FP16 for faster inference (slight accuracy loss)
   - Batch document insertions when possible
   - Limit `max_seq_length` based on your documents

## Troubleshooting

### Common Issues

1. **Out of Memory**:
   - Reduce batch size
   - Use FP16 mode
   - Lower max_seq_length
   - Use ANNOY instead of HNSW

2. **Slow Indexing**:
   - Reduce HNSW ef_construction
   - Reduce ANNOY n_trees
   - Use GPU if available

3. **Poor Search Quality**:
   - Increase ANNOY n_trees
   - Increase HNSW M and ef_search
   - Check if documents are too short/long

## References

- [BGE-M3 Paper](https://arxiv.org/abs/2402.03216)
- [BGE-M3 Model](https://huggingface.co/BAAI/bge-m3)
- [ANNOY Library](https://github.com/spotify/annoy)
- [HNSWlib](https://github.com/nmslib/hnswlib)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## License

This is an educational project for learning purposes.
