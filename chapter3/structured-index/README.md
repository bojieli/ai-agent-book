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

### Using the Command Line Interface

1. **Build an index from a document:**
```bash
# Build both RAPTOR and GraphRAG indexes
python main.py build path/to/document.pdf

# Build only RAPTOR index
python main.py build path/to/document.pdf --type raptor

# Build only GraphRAG index
python main.py build path/to/document.pdf --type graphrag
```

2. **Query the indexes:**
```bash
# Query both indexes
python main.py query "What are the MOV instruction variants?"

# Query specific index with custom result count
python main.py query "explain SSE instructions" --type raptor --top-k 10
```

3. **Start the API server:**
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
