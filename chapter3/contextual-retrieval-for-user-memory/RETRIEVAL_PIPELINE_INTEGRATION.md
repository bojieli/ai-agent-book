# Retrieval Pipeline Integration

This project uses the existing retrieval pipeline service instead of directly embedding FAISS or BM25 libraries.

## Architecture

```
┌─────────────────────────────────┐
│   User Memory RAG Agent          │
│                                  │
│  - Chunks conversations          │
│  - Prepares documents            │
│  - Manages local chunk storage   │
└────────────┬────────────────────┘
             │
             │ HTTP API
             ▼
┌─────────────────────────────────┐
│   Retrieval Pipeline Service     │
│   (Port 4242)                    │
│                                  │
│  - Dense indexing (FAISS)        │
│  - Sparse indexing (BM25)        │
│  - Hybrid search                 │
│  - Reranking                     │
└─────────────────────────────────┘
```

## Setup

### 1. Start the Retrieval Pipeline

The retrieval pipeline must be running before using this system:

```bash
cd projects/week3/retrieval-pipeline
python api_server.py
```

This will start the retrieval pipeline service on `http://localhost:4242`

### 2. Install Dependencies

This project no longer requires FAISS or BM25 directly:

```bash
pip install -r requirements.txt
```

Required packages:
- `openai` - For LLM interactions
- `requests` - For communicating with retrieval pipeline
- `pyyaml` - For loading test cases
- `rich` - For terminal UI
- `python-dotenv` - For environment variables

### 3. Configure Environment

Create a `.env` file with your API keys:

```env
# LLM Provider (at least one required)
KIMI_API_KEY=your_kimi_api_key
OPENAI_API_KEY=your_openai_api_key  # Optional, for other providers

# Configuration
LLM_PROVIDER=kimi
INDEX_MODE=hybrid
```

## How It Works

### Document Indexing

Documents are sent to the retrieval pipeline in this format:

```python
{
    "text": "Document content to index",
    "metadata": {
        "doc_id": "unique_identifier",
        "test_id": "test_case_id",
        "conversation_id": "conv_123",
        # ... other metadata
    }
}
```

The retrieval pipeline:
1. Generates embeddings for dense search
2. Builds BM25 index for sparse search
3. Returns a generated `doc_id` which we map to our chunk IDs

### Search Process

1. **Query Submission**: Sends search query to retrieval pipeline
2. **Retrieval**: Pipeline performs dense/sparse/hybrid search
3. **ID Resolution**: Maps returned doc_ids back to our chunk IDs
4. **Result Construction**: Builds SearchResult objects with local chunks

### API Endpoints Used

- `GET /health` - Check if service is available
- `POST /clear` - Clear existing index
- `POST /index` - Index a single document
- `POST /search` - Search indexed documents

## Testing

### Quick Test

Run the pipeline integration test:

```bash
python test_pipeline.py
```

This verifies:
- Retrieval pipeline connectivity
- Document indexing
- Search functionality

### Startup Test

Test system initialization:

```bash
python test_startup.py
```

### Full Demo

Run the interactive demo:

```bash
python main.py --mode demo
```

Or use the interactive interface:

```bash
python main.py
```

## Troubleshooting

### "Retrieval pipeline not available"

**Solution**: Start the retrieval pipeline service:
```bash
cd projects/week3/retrieval-pipeline
python api_server.py
```

### "422 Unprocessable Entity" errors

**Cause**: Document format mismatch
**Solution**: Ensure documents have `text` field at root level, not in a `documents` array

### "Chunk not found in local storage"

**Cause**: Doc ID mapping issue
**Solution**: The system now handles this automatically by:
- Storing doc_id mappings during indexing
- Checking metadata in search results
- Using fallback to mapped IDs

## Key Changes from Direct FAISS/BM25

1. **No Direct Index Management**: The retrieval pipeline handles all indexing
2. **HTTP Communication**: All operations go through REST API
3. **Doc ID Mapping**: We maintain mapping between our chunk IDs and pipeline's generated IDs
4. **Simplified Dependencies**: No need for faiss-cpu, rank-bm25, or nltk
5. **Service Dependency**: Requires retrieval pipeline to be running

## Performance Considerations

- **Latency**: HTTP overhead adds ~10-50ms per operation
- **Batch Operations**: Documents are indexed one at a time (pipeline limitation)
- **Caching**: Local chunk storage reduces retrieval overhead
- **Scalability**: Retrieval pipeline can be scaled independently

## Future Enhancements

1. **Batch Indexing**: Add batch endpoint to retrieval pipeline
2. **Persistent Mapping**: Save doc_id mappings to disk
3. **Connection Pooling**: Reuse HTTP connections
4. **Retry Logic**: Add exponential backoff for failures
5. **Async Operations**: Use async HTTP client for better performance
