# Structured Document Indexing with RAPTOR and GraphRAG

This educational project demonstrates two advanced approaches for indexing and querying large technical documents:

1. **RAPTOR** (Recursive Abstractive Processing for Tree-Organized Retrieval) - Creates a hierarchical tree structure with recursive summarization
2. **GraphRAG** (Graph-based Retrieval Augmented Generation) - Builds a knowledge graph with entities, relationships, and community detection

Both approaches are optimized for handling large technical documentation like the Intel® 64 and IA-32 Architectures Software Developer's Manual.

## Features

### RAPTOR Tree-Based Indexing
- Hierarchical tree structure with multiple levels of abstraction
- Recursive summarization for information compression
- Multi-level search capability (leaf nodes to root summaries)
- Clustering-based node grouping using Gaussian Mixture Models
- UMAP dimensionality reduction for efficient clustering

### GraphRAG Knowledge Graph Indexing
- Entity and relationship extraction using LLMs
- Community detection for identifying related concepts
- Hierarchical community summarization
- Graph-based search with multiple strategies
- **Multi-hop relation traversal** (`GraphRAGIndexer.multi_hop_search`)：沿关系边做多跳遍历，
  回答扁平向量检索无法表达的「A 通过什么与 B 相连」这类关系性问题（对应书中「多跳关系推理」）
- Support for different entity types (instructions, registers, features, etc.)

### HTTP API Service
- RESTful API for building and querying indexes
- Support for file uploads
- Asynchronous processing for large documents
- Hybrid search across both index types
- Real-time index statistics and status monitoring

## Installation

1. Clone the repository and navigate to the project directory:
```bash
cd projects/week3/structured-index
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Copy and configure the environment file:
```bash
cp env.example .env
# Edit .env with your API keys and preferences
```

## Quick Start

### 命令行接口（CLI）

所有子命令都提供中文 `--help`：`python main.py --help`、`python main.py demo --help` 等。

```
usage: main.py [-h] {build,query,demo,serve} ...
  build   从文档构建结构化索引（需要 OPENAI_API_KEY）
  query   查询已构建的索引（需要 OPENAI_API_KEY 及已有索引）
  demo    离线对比演示：结构化索引 vs 扁平检索（无需 API Key）
  serve   启动 HTTP API 服务
```

#### 0. 离线对比演示（无需 API Key，推荐先跑这个）

这是理解实验 3-8 的最快入口：它用一个手工整理的 Intel x86 SIMD 小知识库，
直观对比「扁平检索」与「结构化索引」在三类查询上的差异，全程无需 OpenAI API：

```bash
# 运行内置的三组对比查询（多跳关系推理 / 跨节点综合对比 / 多层次导航）
python main.py demo

# 自定义查询，同时给出扁平检索与图多跳遍历两种视角
python main.py demo --query "VADDPS 用到哪个寄存器"

# 把结果写入 JSON
python main.py demo --output demo_result.json
```

演示输出示例（多跳关系推理，扁平检索答不了、图检索沿关系边可达）：

```
【查询 1｜多跳关系推理】运行 ADDPS 指令前，操作系统必须把哪个控制寄存器位置 1？
-- 扁平检索（按词面相似度返回独立片段）--
  1. [control-bit] CR4.OSFXSR  (score=0.459)
  ...
  ✗ 只能召回词面相近的孤立片段，无法把 ADDPS 与某个控制位「连」起来。
-- 结构化图检索（沿关系边多跳遍历）--
  ADDPS --属于--> SSE --需要启用--> CR4.OSFXSR
  ✓ 答案：CR4.OSFXSR（从 ADDPS 经 2 跳可达）
```

> 说明：`build` 与 `query` 需要真实索引，而索引构建依赖 LLM（实体抽取、递归摘要），
> 因此需要设置 `OPENAI_API_KEY`（嵌入用本地 `sentence-transformers`）。`demo`
> 则把索引结果预先手工写好，让读者无需 API Key 也能看到结构化索引解决的问题。

#### 1. 构建索引（需要 OPENAI_API_KEY）

```bash
# 同时构建 RAPTOR 与 GraphRAG 索引
python main.py build path/to/document.pdf

# 只构建 RAPTOR，或只构建 GraphRAG
python main.py build path/to/document.pdf --type raptor
python main.py build path/to/document.pdf --type graphrag

# 将索引统计写入 JSON
python main.py build path/to/document.pdf --output stats.json
```

#### 2. 查询索引

```bash
# 查询两种索引
python main.py query "What are the MOV instruction variants?"

# 指定索引类型与返回条数
python main.py query "explain SSE instructions" --type raptor --top-k 10

# GraphRAG 多跳关系遍历：以召回的最佳实体为起点，沿关系边走 N 跳
python main.py query "SSE registers" --type graphrag --multi-hop 2

# 将查询结果写入 JSON
python main.py query "control registers" --output result.json
```

#### 3. 启动 API 服务

```bash
python main.py serve
```

### Using the HTTP API

1. **Start the server:**
```bash
python main.py serve
# Server runs on http://localhost:4242
```

2. **Build an index via API:**
```bash
# Upload a file and build index
curl -X POST "http://localhost:4242/upload" \
  -F "file=@path/to/intel_manual.pdf" \
  -F "index_type=both"

# Build from text
curl -X POST "http://localhost:4242/build" \
  -H "Content-Type: application/json" \
  -d '{
    "file_path": "/path/to/document.pdf",
    "index_type": "both",
    "force_rebuild": false
  }'
```

3. **Query the index:**
```bash
curl -X POST "http://localhost:4242/query" \
  -H "Content-Type: application/json" \
  -d '{
    "query": "What are vector instructions?",
    "index_type": "hybrid",
    "top_k": 5
  }'
```

4. **Check index status:**
```bash
curl http://localhost:4242/status
curl http://localhost:4242/statistics
```

## API Endpoints

| Endpoint | Method | Description |
|----------|---------|-------------|
| `/` | GET | API information and available endpoints |
| `/build` | POST | Build index from text or file |
| `/upload` | POST | Upload file and build index |
| `/query` | POST | Query the indexes |
| `/status` | GET | Get index status |
| `/statistics` | GET | Get detailed index statistics |
| `/indexes` | DELETE | Clear indexes |

## Project Structure

```
structured-index/
├── config.py              # Configuration management
├── raptor_indexer.py      # RAPTOR tree-based indexing
├── graphrag_indexer.py    # GraphRAG graph-based indexing
├── document_processor.py  # Document parsing and preprocessing
├── api_service.py         # HTTP API service
├── structured_vs_flat_demo.py  # 离线对比演示：结构化索引 vs 扁平检索（无需 API）
├── main.py               # CLI interface
├── requirements.txt      # Python dependencies
├── env.example          # Environment variables template
├── indexes/             # Saved index files
│   ├── raptor/         # RAPTOR index storage
│   └── graphrag/       # GraphRAG index storage
└── cache/              # Temporary cache directory
```

## How It Works

### RAPTOR Indexing Process

1. **Text Chunking**: Document is split into manageable chunks with overlap
2. **Embedding Generation**: Each chunk is converted to vector embeddings
3. **Leaf Node Creation**: Chunks become leaf nodes with summaries
4. **Hierarchical Clustering**: Nodes are clustered using GMM
5. **Parent Node Generation**: Clusters are summarized to create parent nodes
6. **Tree Building**: Process repeats for multiple levels
7. **Multi-level Search**: Queries search across all tree levels

### GraphRAG Indexing Process

1. **Entity Extraction**: LLM identifies entities (instructions, registers, etc.)
2. **Relationship Discovery**: Connections between entities are extracted
3. **Graph Construction**: NetworkX graph built from entities and relationships
4. **Community Detection**: Related entities grouped using Leiden/Louvain
5. **Community Summarization**: Each community gets a descriptive summary
6. **Hierarchical Aggregation**: Similar communities are merged and summarized
7. **Graph Search**: Queries match against entities and community summaries

## Example: Processing Intel Architecture Manual

```python
import asyncio
from pathlib import Path
from config import get_raptor_config, get_graphrag_config
from raptor_indexer import RaptorIndexer
from graphrag_indexer import GraphRAGIndexer
from document_processor import DocumentProcessor

async def process_intel_manual():
    # Process the Intel manual PDF
    processor = DocumentProcessor()
    intel_manual_path = Path("intel_x86_64_manual.pdf")
    text = await processor.process_file(intel_manual_path)
    
    # Build RAPTOR index
    raptor_config = get_raptor_config()
    raptor = RaptorIndexer(raptor_config)
    raptor.build_index(text)
    raptor.save_index()
    
    # Build GraphRAG index
    graphrag_config = get_graphrag_config()
    graphrag = GraphRAGIndexer(graphrag_config)
    graphrag.build_knowledge_graph(text)
    graphrag.detect_communities()
    graphrag.hierarchical_summarization()
    graphrag.save_index()
    
    # Example queries
    queries = [
        "What are the different addressing modes?",
        "Explain SIMD instructions",
        "How does the MOV instruction work?",
        "What are control registers?"
    ]
    
    for query in queries:
        print(f"\nQuery: {query}")
        print("-" * 50)
        
        # RAPTOR search
        raptor_results = raptor.search(query, top_k=3)
        print("RAPTOR Results:")
        for r in raptor_results:
            print(f"  Level {r['level']}: {r['summary'][:100]}...")
        
        # GraphRAG search
        graphrag_results = graphrag.search(query, top_k=3)
        print("\nGraphRAG Results:")
        for r in graphrag_results:
            if r['type'] == 'entity':
                print(f"  Entity: {r['name']} - {r['description'][:100]}...")
            else:
                print(f"  Community: {r['summary'][:100]}...")

# Run the example
asyncio.run(process_intel_manual())
```

## Advanced Configuration

### RAPTOR Parameters

- `chunk_size`: Size of text chunks (default: 1000 words)
- `chunk_overlap`: Overlap between chunks (default: 200 words)
- `tree_depth`: Maximum tree depth (default: 3)
- `summarization_length`: Target summary length (default: 200 words)

### GraphRAG Parameters

- `chunk_size`: Size of text chunks (default: 1200 words)
- `max_knowledge_triples`: Max triples per chunk (default: 10)
- `community_detection_algorithm`: "leiden" or "louvain"
- `summarization_model`: Model for generating summaries

## Performance Considerations

1. **Large Documents**: Processing 5000+ page documents may take significant time
2. **API Rate Limits**: Consider OpenAI API rate limits when processing
3. **Memory Usage**: Large graphs require substantial memory
4. **Caching**: Results are cached to improve subsequent query performance
5. **Parallel Processing**: Use the API service for concurrent operations

## Integration with Agentic RAG

This project provides backend services for the agentic-rag project. See the agentic-rag README for integration details.

## Troubleshooting

1. **Out of Memory**: Reduce chunk_size or process document in sections
2. **API Errors**: Check API keys and rate limits
3. **Slow Indexing**: Consider using faster/smaller models for initial testing
4. **Import Errors**: Ensure all dependencies are installed correctly

## References

- [RAPTOR Paper](https://arxiv.org/abs/2401.18059)
- [GraphRAG by Microsoft](https://github.com/microsoft/graphrag)
- [Intel Architecture Manuals](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)


## OpenRouter 通用回退 / Universal OpenRouter fallback

This experiment now supports a **universal OpenRouter fallback** for its chat LLM.

- If the primary provider key (e.g. `MOONSHOT_API_KEY` / `KIMI_API_KEY` / `OPENAI_API_KEY` / `DOUBAO_API_KEY` …) is present, behavior is unchanged.
- Else if `OPENROUTER_API_KEY` is set, the chat LLM is automatically routed through OpenRouter (`https://openrouter.ai/api/v1`). Model names are mapped automatically: `gpt-*`/`o1-*` → `openai/…`, `claude-*` → `anthropic/claude-opus-4.8`, `kimi-*` → `moonshotai/kimi-k2.6`, ids already containing `/` are kept as-is, and other provider-native ids (e.g. `doubao-*`) fall back to `openai/gpt-5.6-luna`. Set `OPENROUTER_MODEL` to force a specific OpenRouter model id.
- Else a clear error lists the accepted keys.

Add `OPENROUTER_API_KEY=...` to your `.env` (see `env.example`) to enable it.

> Note: embeddings here are local SentenceTransformers (all-MiniLM-L6-v2), so they are unaffected — only the chat LLM used for RAPTOR summarization and GraphRAG entity extraction is routed through OpenRouter.
