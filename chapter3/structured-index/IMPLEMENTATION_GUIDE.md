# Structured Index Implementation Guide

## Overview

This project implements two advanced document indexing approaches for handling large technical documentation:

1. **RAPTOR** (Recursive Abstractive Processing for Tree-Organized Retrieval)
2. **GraphRAG** (Graph-based Retrieval Augmented Generation)

Both approaches are designed to handle complex technical documentation like the Intel® 64 and IA-32 Architectures Software Developer's Manual (5000+ pages).

## Architecture

### RAPTOR Tree-Based Index

RAPTOR creates a hierarchical tree structure through recursive summarization:

```
Document
    ↓
[Chunks] → [Embeddings] → [Clusters]
    ↓           ↓              ↓
Level 0: Leaf nodes (original chunks with summaries)
    ↓
Level 1: Parent nodes (cluster summaries)
    ↓
Level 2: Higher-level summaries
    ↓
Root: Top-level abstraction
```

**Key Features:**
- Multi-level abstraction hierarchy
- Gaussian Mixture Model clustering
- Recursive summarization at each level
- Cross-level search capability

### GraphRAG Knowledge Graph

GraphRAG builds a knowledge graph with entities and relationships:

```
Document
    ↓
[Chunks] → [Entity Extraction] → [Relationship Discovery]
    ↓              ↓                        ↓
Entities ←→ Relationships → Knowledge Graph
    ↓
[Community Detection]
    ↓
Community Summaries
    ↓
Hierarchical Communities
```

**Key Features:**
- LLM-based entity and relationship extraction
- Community detection (Leiden/Louvain algorithms)
- Hierarchical community summarization
- Graph-based search across entities and communities

## Implementation Details

### Core Components

1. **Document Processor** (`document_processor.py`)
   - Handles multiple file formats (PDF, TXT, MD, HTML)
   - Optimized for technical documentation
   - Special handling for Intel manual format
   - Table extraction and formatting

2. **RAPTOR Indexer** (`raptor_indexer.py`)
   - Text chunking with configurable overlap
   - Embedding generation using sentence transformers
   - GMM clustering for node grouping
   - Recursive summarization using LLMs
   - Tree persistence and loading

3. **GraphRAG Indexer** (`graphrag_indexer.py`)
   - Entity extraction focused on technical concepts
   - Relationship discovery between entities
   - NetworkX graph construction
   - Community detection and summarization
   - Graph persistence and querying

4. **API Service** (`api_service.py`)
   - RESTful API using FastAPI
   - Asynchronous processing for large documents
   - Support for file uploads
   - Unified interface for both indexing approaches
   - Real-time status and statistics

### Processing Pipeline

#### Building Indexes

1. **Document Processing**
   ```python
   processor = DocumentProcessor()
   text = await processor.process_file(Path("intel_manual.pdf"))
   ```

2. **RAPTOR Indexing**
   ```python
   raptor = RaptorIndexer(config)
   raptor.build_index(text)  # Creates tree structure
   raptor.save_index()       # Persists to disk
   ```

3. **GraphRAG Indexing**
   ```python
   graphrag = GraphRAGIndexer(config)
   graphrag.build_knowledge_graph(text)  # Extract entities
   graphrag.detect_communities()          # Find communities
   graphrag.hierarchical_summarization()  # Create hierarchies
   graphrag.save_index()                  # Persist graph
   ```

#### Querying

1. **RAPTOR Search**
   - Creates query embedding
   - Searches across all tree levels
   - Returns nodes with different abstraction levels
   - Includes level-specific summaries

2. **GraphRAG Search**
   - Supports entity, community, or hybrid search
   - Returns entities with relationships
   - Includes community summaries
   - Provides graph context

### API Endpoints

| Endpoint | Method | Purpose |
|----------|--------|---------|
| `/build` | POST | Build index from text/file |
| `/upload` | POST | Upload and index document |
| `/query` | POST | Query indexes |
| `/status` | GET | Check index status |
| `/statistics` | GET | Get index statistics |
| `/indexes` | DELETE | Clear indexes |

### Integration with Agentic RAG

The structured indexes integrate seamlessly with the Agentic RAG system:

1. **Configuration** (`agentic-rag/config.py`)
   ```python
   KnowledgeBaseType.RAPTOR   # Tree-based backend
   KnowledgeBaseType.GRAPHRAG # Graph-based backend
   ```

2. **Tool Integration** (`agentic-rag/tools.py`)
   - `_search_raptor()`: Queries RAPTOR API
   - `_search_graphrag()`: Queries GraphRAG API
   - Unified search interface for agents

3. **Agent Usage**
   ```python
   config.knowledge_base.type = KnowledgeBaseType.RAPTOR
   agent = AgenticRAG(config)
   response = agent.query("What are x86 registers?")
   ```

## Usage Examples

### Command Line Interface

```bash
# Build both indexes
python main.py build intel_manual.pdf --type both

# Query RAPTOR
python main.py query "MOV instruction syntax" --type raptor

# Query GraphRAG
python main.py query "CPU register relationships" --type graphrag

# Start API server
python main.py serve
```

### Python API

```python
from config import get_raptor_config, get_graphrag_config
from raptor_indexer import RaptorIndexer
from graphrag_indexer import GraphRAGIndexer

# RAPTOR Example
raptor_config = get_raptor_config()
raptor = RaptorIndexer(raptor_config)
raptor.build_index(document_text)
results = raptor.search("SSE instructions", top_k=5)

# GraphRAG Example
graphrag_config = get_graphrag_config()
graphrag = GraphRAGIndexer(graphrag_config)
graphrag.build_knowledge_graph(document_text)
results = graphrag.search("instruction relationships", top_k=5)
```

### HTTP API

```bash
# Build index
curl -X POST http://localhost:4242/build \
  -H "Content-Type: application/json" \
  -d '{"file_path": "intel_manual.pdf", "index_type": "both"}'

# Query
curl -X POST http://localhost:4242/query \
  -H "Content-Type: application/json" \
  -d '{"query": "vector instructions", "index_type": "hybrid"}'
```

## Performance Considerations

### RAPTOR
- **Indexing Time**: O(n log n) for clustering
- **Memory**: Stores embeddings for all nodes
- **Query Time**: Fast similarity search
- **Best For**: Hierarchical information, long documents

### GraphRAG
- **Indexing Time**: O(n²) for relationship extraction
- **Memory**: Graph structure can be large
- **Query Time**: Graph traversal overhead
- **Best For**: Complex relationships, entity-centric queries

## Configuration Options

### RAPTOR Settings
```python
chunk_size: 1000          # Words per chunk
chunk_overlap: 200        # Overlap between chunks
tree_depth: 3            # Maximum tree levels
summarization_length: 200 # Summary word count
```

### GraphRAG Settings
```python
chunk_size: 1200              # Words per chunk
max_knowledge_triples: 10     # Triples per chunk
community_detection: "leiden" # Algorithm choice
summarization_model: "gpt-4o-mini"
```

## Extending the System

### Adding New Document Types
1. Extend `DocumentProcessor` with new format handlers
2. Add format-specific extraction logic
3. Update supported_formats dictionary

### Custom Entity Extraction
1. Modify prompt in `extract_entities_relationships()`
2. Add domain-specific entity types
3. Customize relationship types

### Alternative Clustering
1. Replace GMM in RAPTOR with other algorithms
2. Implement custom similarity metrics
3. Add dimensionality reduction options

### Graph Algorithms
1. Add new community detection algorithms
2. Implement graph embedding techniques
3. Add path-finding for relationship queries

## Troubleshooting

### Common Issues

1. **Out of Memory**
   - Reduce chunk_size
   - Process documents in sections
   - Use smaller embedding models

2. **Slow Indexing**
   - Use faster/smaller LLMs
   - Reduce tree_depth or max_triples
   - Enable caching

3. **Poor Search Results**
   - Adjust chunk_size and overlap
   - Fine-tune clustering parameters
   - Improve entity extraction prompts

4. **API Errors**
   - Check API keys in .env
   - Monitor rate limits
   - Verify index exists before querying

## Future Enhancements

1. **Hybrid Indexing**: Combine RAPTOR and GraphRAG
2. **Incremental Updates**: Add documents without rebuilding
3. **Multi-modal Support**: Handle images and tables
4. **Cross-lingual**: Support multiple languages
5. **Active Learning**: Improve extraction with feedback
6. **Distributed Processing**: Scale to larger documents
7. **Query Optimization**: Cache frequent queries
8. **Visualization**: Interactive graph/tree exploration

## References

- [RAPTOR Paper](https://arxiv.org/abs/2401.18059)
- [GraphRAG by Microsoft](https://github.com/microsoft/graphrag)
- [Intel SDM](https://www.intel.com/content/www/us/en/developer/articles/technical/intel-sdm.html)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [NetworkX Documentation](https://networkx.org/)
