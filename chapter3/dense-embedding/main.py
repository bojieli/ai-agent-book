"""Main FastAPI application for vector similarity search service."""

import time
import argparse
from typing import List, Optional, Dict, Any
from contextlib import asynccontextmanager
import uvicorn
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import numpy as np

from config import ServiceConfig, IndexType
from logger import setup_logger, VectorSearchLogger
from embedding_service import EmbeddingService
from indexing import AnnoyIndex, HNSWIndex, VectorIndex
from document_store import DocumentStore


# Request/Response models
class IndexRequest(BaseModel):
    """Request model for indexing documents."""
    text: str = Field(..., description="Text content to index")
    doc_id: Optional[str] = Field(None, description="Optional document ID")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict, description="Optional metadata")


class SearchRequest(BaseModel):
    """Request model for searching documents."""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=10, ge=1, le=100, description="Number of results to return")
    return_documents: bool = Field(default=True, description="Whether to return full documents")


class DeleteRequest(BaseModel):
    """Request model for deleting documents."""
    doc_id: str = Field(..., description="Document ID to delete")


class SearchResult(BaseModel):
    """Search result model."""
    doc_id: str
    score: float
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    rank: int


class IndexResponse(BaseModel):
    """Response model for indexing operations."""
    success: bool
    doc_id: str
    message: str
    index_size: int


class DeleteResponse(BaseModel):
    """Response model for deletion operations."""
    success: bool
    message: str
    index_size: int


class SearchResponse(BaseModel):
    """Response model for search operations."""
    success: bool
    query: str
    results: List[SearchResult]
    total_results: int
    search_time_ms: float


class StatsResponse(BaseModel):
    """Response model for service statistics."""
    index_type: str
    index_size: int
    document_count: int
    embedding_dimension: int
    model_name: str


# Global instances
config: ServiceConfig = None
logger = None
vec_logger: VectorSearchLogger = None
embedding_service: EmbeddingService = None
vector_index: VectorIndex = None
document_store: DocumentStore = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle."""
    # Startup
    global config, logger, vec_logger, embedding_service, vector_index, document_store
    
    logger.info("=" * 80)
    logger.info("🚀 Starting Vector Similarity Search Service")
    logger.info("=" * 80)
    
    # Initialize embedding service
    logger.info("Initializing BGE-M3 embedding service...")
    embedding_service = EmbeddingService(
        model_name=config.model_name,
        use_fp16=config.use_fp16,
        max_seq_length=config.max_seq_length,
        logger=vec_logger
    )
    
    # Initialize vector index based on configuration
    embedding_dim = embedding_service.get_embedding_dimension()
    logger.info(f"Initializing {config.index_type.value.upper()} vector index...")
    
    if config.index_type == IndexType.ANNOY:
        vector_index = AnnoyIndex(
            dimension=embedding_dim,
            n_trees=config.annoy_n_trees,
            metric=config.annoy_metric,
            logger=vec_logger
        )
    else:  # HNSW
        vector_index = HNSWIndex(
            dimension=embedding_dim,
            max_elements=config.max_documents,
            ef_construction=config.hnsw_ef_construction,
            M=config.hnsw_M,
            ef_search=config.hnsw_ef_search,
            space=config.hnsw_space,
            logger=vec_logger
        )
    
    # Initialize document store
    logger.info("Initializing document store...")
    document_store = DocumentStore(logger=vec_logger)
    
    logger.info("=" * 80)
    logger.info("✅ Service initialized successfully!")
    logger.info(f"📍 API available at http://{config.host}:{config.port}")
    logger.info(f"📚 Docs available at http://{config.host}:{config.port}/docs")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown
    logger.info("Shutting down service...")


# Create FastAPI app
app = FastAPI(
    title="Vector Similarity Search Service",
    description="Educational service for vector similarity search using BGE-M3 embeddings with ANNOY/HNSW indexing",
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


@app.get("/", response_model=Dict[str, str])
async def root():
    """Root endpoint."""
    return {
        "service": "Vector Similarity Search",
        "status": "running",
        "index_type": config.index_type.value,
        "model": config.model_name
    }


@app.post("/index", response_model=IndexResponse)
async def index_document(request: IndexRequest):
    """
    Index a new document.
    
    This endpoint:
    1. Generates embeddings using BGE-M3
    2. Adds the document to the document store
    3. Adds the embedding to the vector index
    """
    try:
        vec_logger.log_indexing_start(request.doc_id or "auto-generated", request.text)
        
        # Generate embedding
        start_time = time.time()
        embedding_result = embedding_service.encode_text(request.text)
        embedding = embedding_result['dense']
        embedding_time = time.time() - start_time
        
        vec_logger.log_embedding_generation(
            request.text, 
            embedding.shape,
            embedding_time
        )
        
        # Store document
        doc_id = document_store.add_document(
            text=request.text,
            doc_id=request.doc_id,
            metadata=request.metadata
        )
        
        # Update document with embedding
        document_store.update_document_embedding(doc_id, embedding.tolist())
        
        # Add to vector index
        vector_index.add_item(doc_id, embedding)
        vec_logger.log_index_update(
            config.index_type.value,
            doc_id,
            vector_index.get_size()
        )
        
        # Rebuild index if necessary (for ANNOY)
        if config.index_type == IndexType.ANNOY:
            vector_index.rebuild_index()
        
        return IndexResponse(
            success=True,
            doc_id=doc_id,
            message=f"Document indexed successfully using {config.index_type.value.upper()}",
            index_size=vector_index.get_size()
        )
        
    except Exception as e:
        vec_logger.log_error("indexing", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=SearchResponse)
async def search_documents(request: SearchRequest):
    """
    Search for similar documents.
    
    This endpoint:
    1. Generates query embedding using BGE-M3
    2. Searches the vector index for similar documents
    3. Returns ranked results with scores
    """
    try:
        vec_logger.log_search_start(request.query, request.top_k)
        
        # Generate query embedding
        start_time = time.time()
        embedding_result = embedding_service.encode_text(request.query)
        query_embedding = embedding_result['dense']
        embedding_time = time.time() - start_time
        
        logger.debug(f"Query embedding generated in {embedding_time:.4f}s")
        vec_logger.log_embedding_vector(query_embedding, sample_size=10)
        
        # Search in index
        search_start = time.time()
        doc_ids, distances = vector_index.search(query_embedding, request.top_k)
        search_time = time.time() - search_start
        
        vec_logger.log_search_results(doc_ids, distances, search_time)
        
        # Prepare results
        results = []
        if request.return_documents:
            documents = document_store.get_documents_by_ids(doc_ids)
            doc_map = {doc.id: doc for doc in documents}
            
            for rank, (doc_id, distance) in enumerate(zip(doc_ids, distances), 1):
                doc = doc_map.get(doc_id)
                if doc:
                    results.append(SearchResult(
                        doc_id=doc_id,
                        score=float(1.0 / (1.0 + distance)),  # Convert distance to similarity score
                        text=doc.text,
                        metadata=doc.metadata,
                        rank=rank
                    ))
        else:
            for rank, (doc_id, distance) in enumerate(zip(doc_ids, distances), 1):
                results.append(SearchResult(
                    doc_id=doc_id,
                    score=float(1.0 / (1.0 + distance)),
                    rank=rank
                ))
        
        total_time_ms = (time.time() - start_time) * 1000
        
        return SearchResponse(
            success=True,
            query=request.query,
            results=results,
            total_results=len(results),
            search_time_ms=total_time_ms
        )
        
    except Exception as e:
        vec_logger.log_error("search", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.delete("/index", response_model=DeleteResponse)
async def delete_document(request: DeleteRequest):
    """
    Delete a document from the index.
    
    This endpoint:
    1. Removes the document from the document store
    2. Removes the embedding from the vector index
    """
    try:
        vec_logger.log_deletion(request.doc_id)
        
        # Delete from document store
        doc_deleted = document_store.delete_document(request.doc_id)
        
        if not doc_deleted:
            return DeleteResponse(
                success=False,
                message=f"Document {request.doc_id} not found",
                index_size=vector_index.get_size()
            )
        
        # Delete from vector index
        index_deleted = vector_index.delete_item(request.doc_id)
        
        if index_deleted:
            return DeleteResponse(
                success=True,
                message=f"Document {request.doc_id} deleted successfully",
                index_size=vector_index.get_size()
            )
        else:
            return DeleteResponse(
                success=False,
                message=f"Document {request.doc_id} deleted from store but not from index",
                index_size=vector_index.get_size()
            )
            
    except Exception as e:
        vec_logger.log_error("deletion", e)
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/stats", response_model=StatsResponse)
async def get_stats():
    """Get service statistics."""
    return StatsResponse(
        index_type=config.index_type.value,
        index_size=vector_index.get_size(),
        document_count=document_store.get_size(),
        embedding_dimension=embedding_service.get_embedding_dimension(),
        model_name=config.model_name
    )


@app.get("/documents", response_model=List[Dict[str, Any]])
async def list_documents(limit: int = Query(default=10, ge=1, le=100)):
    """List documents in the store."""
    docs = document_store.list_documents(limit=limit)
    return [
        {
            "id": doc.id,
            "text": doc.text[:200] + "..." if len(doc.text) > 200 else doc.text,
            "metadata": doc.metadata,
            "created_at": doc.created_at.isoformat()
        }
        for doc in docs
    ]


def main():
    """Main entry point."""
    global config, logger, vec_logger
    
    # Parse command line arguments
    parser = argparse.ArgumentParser(description="Vector Similarity Search Service")
    parser.add_argument(
        "--index-type",
        type=str,
        choices=["annoy", "hnsw"],
        default="hnsw",
        help="Type of index to use (default: hnsw)"
    )
    parser.add_argument(
        "--host",
        type=str,
        default="0.0.0.0",
        help="Host to bind to (default: 0.0.0.0)"
    )
    parser.add_argument(
        "--port",
        type=int,
        default=4240,
        help="Port to bind to (default: 4240)"
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode"
    )
    parser.add_argument(
        "--show-embeddings",
        action="store_true",
        help="Show embedding vectors in logs"
    )
    
    args = parser.parse_args()
    
    # Create configuration
    config = ServiceConfig(
        index_type=IndexType(args.index_type),
        host=args.host,
        port=args.port,
        debug=args.debug,
        show_embeddings=args.show_embeddings
    )
    
    # Setup logging
    logger = setup_logger("vector_search", config.log_level)
    vec_logger = VectorSearchLogger(logger, config.show_embeddings)
    
    # Run the service
    uvicorn.run(
        app,
        host=config.host,
        port=config.port,
        log_level=config.log_level.lower(),
        reload=False
    )


if __name__ == "__main__":
    main()
