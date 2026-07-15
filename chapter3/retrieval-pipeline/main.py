"""FastAPI server for the retrieval pipeline."""

import logging
import sys
from typing import Dict, Any, Optional, List
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uvicorn
import asyncio

from config import PipelineConfig, SearchMode
from retrieval_pipeline import RetrievalPipeline

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

# Initialize pipeline
config = PipelineConfig()
pipeline: Optional[RetrievalPipeline] = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup and shutdown events."""
    global pipeline
    # Startup
    try:
        logger.info("Starting retrieval pipeline...")
        pipeline = RetrievalPipeline(config)
        logger.info("Pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize pipeline: {e}")
        raise
    
    yield
    
    # Shutdown (cleanup if needed)
    logger.info("Shutting down retrieval pipeline...")

# Create FastAPI app with lifespan
app = FastAPI(
    title="Hybrid Retrieval Pipeline",
    description="Educational retrieval pipeline combining dense embeddings, sparse search, and neural reranking",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models
class IndexRequest(BaseModel):
    """Request model for document indexing."""
    text: str = Field(..., description="Document text to index")
    doc_id: Optional[str] = Field(None, description="Optional document ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional metadata")

class SearchRequest(BaseModel):
    """Request model for search."""
    query: str = Field(..., description="Search query")
    mode: SearchMode = Field(SearchMode.HYBRID, description="Search mode: dense, sparse, or hybrid")
    top_k: int = Field(20, ge=1, le=100, description="Number of candidates to retrieve")
    rerank_top_k: int = Field(10, ge=1, le=50, description="Number of results after reranking")
    skip_reranking: bool = Field(False, description="Skip reranking for comparison")

class DeleteRequest(BaseModel):
    """Request model for document deletion."""
    doc_id: str = Field(..., description="Document ID to delete")

@app.get("/")
async def root():
    """Root endpoint with service information."""
    return {
        "service": "Hybrid Retrieval Pipeline",
        "status": "running" if pipeline else "not initialized",
        "endpoints": {
            "index": "/index",
            "search": "/search",
            "delete": "/delete",
            "stats": "/stats",
            "health": "/health"
        },
        "modes": ["dense", "sparse", "hybrid"],
        "features": [
            "Parallel dense and sparse indexing",
            "Hybrid search with both embedding types",
            "Neural reranking with BGE-Reranker-v2",
            "Educational score visualization",
            "Rank change analysis"
        ]
    }

@app.get("/health")
async def health():
    """Health check endpoint."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    return {"status": "healthy"}

@app.post("/index")
async def index_document(request: IndexRequest):
    """Index a document in both dense and sparse services.
    
    This endpoint:
    1. Stores the document locally
    2. Indexes in dense embedding service (semantic search)
    3. Indexes in sparse service (BM25 keyword search)
    4. Returns status from both services
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        logger.info(f"Indexing document: {request.doc_id or 'auto-generated'}")
        result = await pipeline.index_document(
            text=request.text,
            doc_id=request.doc_id,
            metadata=request.metadata
        )
        return result
    except Exception as e:
        logger.error(f"Indexing failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/search")
async def search_documents(request: SearchRequest):
    """Search for documents using specified mode with optional reranking.
    
    Educational features:
    - Shows original rankings from dense and sparse search
    - Displays similarity scores from each method
    - Shows final reranked results with score changes
    - Provides statistics on rank changes and overlap
    
    Modes:
    - dense: Semantic search using dense embeddings
    - sparse: Keyword search using BM25
    - hybrid: Both methods combined with reranking
    """
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        logger.info(f"Search request: mode={request.mode}, query='{request.query[:50]}...'")
        result = await pipeline.search(
            query=request.query,
            mode=request.mode,
            top_k=request.top_k,
            rerank_top_k=request.rerank_top_k,
            skip_reranking=request.skip_reranking
        )
        return result
    except Exception as e:
        logger.error(f"Search failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/delete")
async def delete_document(request: DeleteRequest):
    """Delete a document from all services."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        logger.info(f"Deleting document: {request.doc_id}")
        result = await pipeline.delete_document(request.doc_id)
        return result
    except Exception as e:
        logger.error(f"Deletion failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stats")
async def get_statistics():
    """Get pipeline statistics and configuration."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        stats = pipeline.get_statistics()
        return stats
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents")
async def list_documents(limit: int = 100, offset: int = 0):
    """List indexed documents."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        docs = pipeline.document_store.list_documents(limit=limit, offset=offset)
        return {
            "documents": docs,
            "total": pipeline.document_store.size(),
            "limit": limit,
            "offset": offset
        }
    except Exception as e:
        logger.error(f"Failed to list documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/documents/{doc_id}")
async def get_document(doc_id: str):
    """Get a specific document by ID."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        doc = pipeline.document_store.get_document(doc_id)
        if doc is None:
            raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
        
        # Return in the format expected by agentic RAG
        return {
            "doc_id": doc_id,
            "content": doc.get("text", ""),
            "metadata": doc.get("metadata", {})
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get document {doc_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/clear")
async def clear_all():
    """Clear all documents from the pipeline (for testing)."""
    if not pipeline:
        raise HTTPException(status_code=503, detail="Pipeline not initialized")
    
    try:
        pipeline.document_store.clear()
        # Note: This only clears local store, not remote services
        return {
            "success": True,
            "message": "Local document store cleared. Note: Remote services not cleared."
        }
    except Exception as e:
        logger.error(f"Failed to clear documents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

def main():
    """Run the server."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Retrieval Pipeline Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind")
    parser.add_argument("--port", type=int, default=4242, help="Port to bind (default: 4242)")
    parser.add_argument("--debug", action="store_true", help="Enable debug mode")
    parser.add_argument("--dense-url", default="http://localhost:4240", help="Dense service URL")
    parser.add_argument("--sparse-url", default="http://localhost:4241", help="Sparse service URL")
    
    args = parser.parse_args()
    
    # Update config
    config.services.dense_service_url = args.dense_url
    config.services.sparse_service_url = args.sparse_url
    config.debug = args.debug
    
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info(f"Starting server on {args.host}:{args.port}")
    logger.info(f"Dense service: {config.services.dense_service_url}")
    logger.info(f"Sparse service: {config.services.sparse_service_url}")
    
    uvicorn.run(
        app,
        host=args.host,
        port=args.port,
        log_level="debug" if args.debug else "info"
    )

if __name__ == "__main__":
    main()
