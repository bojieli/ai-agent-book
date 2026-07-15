"""
HTTP API service for querying RAPTOR and GraphRAG indexes.
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks, UploadFile, File
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional, Literal
from pathlib import Path
import asyncio
from concurrent.futures import ThreadPoolExecutor
import uvicorn
from loguru import logger
import json
import aiofiles
import tempfile
import shutil

from config import get_raptor_config, get_graphrag_config, get_api_config
from raptor_indexer import RaptorIndexer
from graphrag_indexer import GraphRAGIndexer
from document_processor import DocumentProcessor

# Initialize FastAPI app
app = FastAPI(
    title="Structured Index API",
    description="API for querying RAPTOR tree-based and GraphRAG graph-based document indexes",
    version="1.0.0"
)

# Thread pool for CPU-intensive operations
executor = ThreadPoolExecutor(max_workers=4)

# Global indexers
raptor_indexer: Optional[RaptorIndexer] = None
graphrag_indexer: Optional[GraphRAGIndexer] = None
document_processor: Optional[DocumentProcessor] = None


class BuildIndexRequest(BaseModel):
    """Request model for building an index."""
    text: Optional[str] = Field(None, description="Text content to index")
    file_path: Optional[str] = Field(None, description="Path to document file")
    index_type: Literal["raptor", "graphrag", "both"] = Field("both", description="Type of index to build")
    force_rebuild: bool = Field(False, description="Force rebuild even if index exists")


class QueryRequest(BaseModel):
    """Request model for querying an index."""
    query: str = Field(..., description="Search query")
    index_type: Literal["raptor", "graphrag", "hybrid"] = Field("hybrid", description="Index to query")
    top_k: int = Field(5, description="Number of results to return")
    search_type: Optional[str] = Field("hybrid", description="Search type for GraphRAG")


class IndexResponse(BaseModel):
    """Response model for index operations."""
    status: str
    message: str
    statistics: Optional[Dict[str, Any]] = None


class QueryResponse(BaseModel):
    """Response model for query operations."""
    query: str
    results: List[Dict[str, Any]]
    index_type: str
    total_results: int


@app.on_event("startup")
async def startup_event():
    """Initialize indexers on startup."""
    global raptor_indexer, graphrag_indexer, document_processor
    
    logger.info("Initializing indexers...")
    
    # Initialize configurations
    raptor_config = get_raptor_config()
    graphrag_config = get_graphrag_config()
    
    # Initialize indexers
    raptor_indexer = RaptorIndexer(raptor_config)
    graphrag_indexer = GraphRAGIndexer(graphrag_config)
    document_processor = DocumentProcessor()
    
    # Try to load existing indexes
    try:
        if (raptor_config.index_dir / "raptor_index.pkl").exists():
            raptor_indexer.load_index()
            logger.info("Loaded existing RAPTOR index")
    except Exception as e:
        logger.warning(f"Could not load RAPTOR index: {e}")
    
    try:
        if (graphrag_config.index_dir / "graphrag_index.pkl").exists():
            graphrag_indexer.load_index()
            logger.info("Loaded existing GraphRAG index")
    except Exception as e:
        logger.warning(f"Could not load GraphRAG index: {e}")
    
    logger.info("API service started successfully")


@app.get("/")
async def root():
    """Root endpoint."""
    return {
        "service": "Structured Index API",
        "version": "1.0.0",
        "endpoints": {
            "build": "/build",
            "query": "/query",
            "status": "/status",
            "statistics": "/statistics"
        }
    }


@app.post("/build", response_model=IndexResponse)
async def build_index(
    request: BuildIndexRequest,
    background_tasks: BackgroundTasks
):
    """Build RAPTOR and/or GraphRAG index from text or file."""
    try:
        # Get text content
        if request.text:
            text_content = request.text
        elif request.file_path:
            file_path = Path(request.file_path)
            if not file_path.exists():
                raise HTTPException(status_code=404, detail=f"File not found: {request.file_path}")
            text_content = await document_processor.process_file(file_path)
        else:
            raise HTTPException(status_code=400, detail="Either text or file_path must be provided")
        
        # Check if we should rebuild
        if not request.force_rebuild:
            existing_indexes = []
            if request.index_type in ["raptor", "both"]:
                if (raptor_indexer.config.index_dir / "raptor_index.pkl").exists():
                    existing_indexes.append("RAPTOR")
            if request.index_type in ["graphrag", "both"]:
                if (graphrag_indexer.config.index_dir / "graphrag_index.pkl").exists():
                    existing_indexes.append("GraphRAG")
            
            if existing_indexes:
                return IndexResponse(
                    status="exists",
                    message=f"Indexes already exist: {', '.join(existing_indexes)}. Use force_rebuild=true to rebuild."
                )
        
        # Build indexes in background
        async def build_indexes():
            results = {}
            
            if request.index_type in ["raptor", "both"]:
                logger.info("Building RAPTOR index...")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(executor, raptor_indexer.build_index, text_content)
                await loop.run_in_executor(executor, raptor_indexer.save_index)
                results["raptor"] = raptor_indexer.get_tree_statistics()
            
            if request.index_type in ["graphrag", "both"]:
                logger.info("Building GraphRAG index...")
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(executor, graphrag_indexer.build_knowledge_graph, text_content)
                await loop.run_in_executor(executor, graphrag_indexer.detect_communities)
                await loop.run_in_executor(executor, graphrag_indexer.hierarchical_summarization)
                await loop.run_in_executor(executor, graphrag_indexer.save_index)
                results["graphrag"] = graphrag_indexer.get_graph_statistics()
            
            return results
        
        # Start building in background
        background_tasks.add_task(build_indexes)
        
        return IndexResponse(
            status="building",
            message=f"Started building {request.index_type} index(es) in background"
        )
        
    except Exception as e:
        logger.error(f"Error building index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/upload", response_model=IndexResponse)
async def upload_and_build(
    file: UploadFile = File(...),
    index_type: Literal["raptor", "graphrag", "both"] = "both",
    background_tasks: BackgroundTasks = None
):
    """Upload a document and build index."""
    try:
        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=Path(file.filename).suffix) as tmp_file:
            content = await file.read()
            tmp_file.write(content)
            tmp_path = tmp_file.name
        
        # Process the file
        text_content = await document_processor.process_file(Path(tmp_path))
        
        # Clean up temp file
        Path(tmp_path).unlink()
        
        # Build index
        request = BuildIndexRequest(
            text=text_content,
            index_type=index_type,
            force_rebuild=True
        )
        
        return await build_index(request, background_tasks)
        
    except Exception as e:
        logger.error(f"Error processing uploaded file: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/query", response_model=QueryResponse)
async def query_index(request: QueryRequest):
    """Query the RAPTOR or GraphRAG index."""
    try:
        results = []
        
        if request.index_type == "raptor":
            # Query RAPTOR index
            if not raptor_indexer.nodes:
                raise HTTPException(status_code=404, detail="RAPTOR index not built")
            
            loop = asyncio.get_event_loop()
            raptor_results = await loop.run_in_executor(
                executor, 
                raptor_indexer.search, 
                request.query, 
                request.top_k
            )
            results = raptor_results
            
        elif request.index_type == "graphrag":
            # Query GraphRAG index
            if not graphrag_indexer.entities:
                raise HTTPException(status_code=404, detail="GraphRAG index not built")
            
            loop = asyncio.get_event_loop()
            graphrag_results = await loop.run_in_executor(
                executor,
                graphrag_indexer.search,
                request.query,
                request.top_k,
                request.search_type
            )
            results = graphrag_results
            
        elif request.index_type == "hybrid":
            # Query both indexes and combine results
            all_results = []
            
            # Query RAPTOR
            if raptor_indexer.nodes:
                loop = asyncio.get_event_loop()
                raptor_results = await loop.run_in_executor(
                    executor,
                    raptor_indexer.search,
                    request.query,
                    request.top_k
                )
                for r in raptor_results:
                    r["source"] = "raptor"
                all_results.extend(raptor_results)
            
            # Query GraphRAG
            if graphrag_indexer.entities:
                loop = asyncio.get_event_loop()
                graphrag_results = await loop.run_in_executor(
                    executor,
                    graphrag_indexer.search,
                    request.query,
                    request.top_k,
                    request.search_type
                )
                for r in graphrag_results:
                    r["source"] = "graphrag"
                all_results.extend(graphrag_results)
            
            # Sort by score and return top-k
            all_results.sort(key=lambda x: x.get("score", 0), reverse=True)
            results = all_results[:request.top_k]
        
        return QueryResponse(
            query=request.query,
            results=results,
            index_type=request.index_type,
            total_results=len(results)
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error querying index: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get the status of the indexes."""
    status = {
        "raptor": {
            "built": len(raptor_indexer.nodes) > 0 if raptor_indexer else False,
            "node_count": len(raptor_indexer.nodes) if raptor_indexer else 0
        },
        "graphrag": {
            "built": len(graphrag_indexer.entities) > 0 if graphrag_indexer else False,
            "entity_count": len(graphrag_indexer.entities) if graphrag_indexer else 0,
            "relationship_count": len(graphrag_indexer.relationships) if graphrag_indexer else 0
        }
    }
    return status


@app.get("/statistics")
async def get_statistics():
    """Get detailed statistics about the indexes."""
    stats = {}
    
    if raptor_indexer and raptor_indexer.nodes:
        stats["raptor"] = raptor_indexer.get_tree_statistics()
    
    if graphrag_indexer and graphrag_indexer.entities:
        stats["graphrag"] = graphrag_indexer.get_graph_statistics()
    
    if not stats:
        raise HTTPException(status_code=404, detail="No indexes built")
    
    return stats


@app.delete("/indexes")
async def clear_indexes(index_type: Literal["raptor", "graphrag", "both"] = "both"):
    """Clear the specified indexes."""
    try:
        cleared = []
        
        if index_type in ["raptor", "both"]:
            raptor_indexer.nodes = {}
            raptor_indexer.root_nodes = []
            # Delete saved index
            index_file = raptor_indexer.config.index_dir / "raptor_index.pkl"
            if index_file.exists():
                index_file.unlink()
            cleared.append("RAPTOR")
        
        if index_type in ["graphrag", "both"]:
            graphrag_indexer.entities = {}
            graphrag_indexer.relationships = []
            graphrag_indexer.communities = {}
            graphrag_indexer.graph.clear()
            # Delete saved index
            index_file = graphrag_indexer.config.index_dir / "graphrag_index.pkl"
            if index_file.exists():
                index_file.unlink()
            cleared.append("GraphRAG")
        
        return {
            "status": "success",
            "message": f"Cleared indexes: {', '.join(cleared)}"
        }
        
    except Exception as e:
        logger.error(f"Error clearing indexes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


def run_server():
    """Run the API server."""
    config = get_api_config()
    logger.info(f"Starting API server on {config.host}:{config.port}")
    
    uvicorn.run(
        "api_service:app",
        host=config.host,
        port=config.port,
        reload=config.reload
    )


if __name__ == "__main__":
    run_server()
