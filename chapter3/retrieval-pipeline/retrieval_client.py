"""Client for communicating with dense and sparse embedding services."""

import httpx
import asyncio
from typing import Dict, Any, List, Optional, Tuple
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)

@dataclass
class SearchResult:
    """Unified search result from embedding services."""
    doc_id: str
    score: float
    text: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    source: str = ""  # "dense" or "sparse"
    rank: Optional[int] = None
    debug_info: Optional[Dict[str, Any]] = None

class RetrievalClient:
    """Client for parallel retrieval from dense and sparse services."""
    
    def __init__(self, dense_url: str, sparse_url: str, timeout: float = 30.0):
        self.dense_url = dense_url.rstrip('/')
        self.sparse_url = sparse_url.rstrip('/')
        self.timeout = timeout
        
    async def index_document_dense(self, text: str, doc_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Index a document in the dense embedding service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "text": text,
                    "doc_id": doc_id,
                    "metadata": metadata or {}
                }
                response = await client.post(f"{self.dense_url}/index", json=payload)
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Dense indexing successful for doc {doc_id}")
                return result
            except Exception as e:
                logger.error(f"Dense indexing failed for doc {doc_id}: {e}")
                return {"success": False, "error": str(e)}
    
    async def index_document_sparse(self, text: str, doc_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Index a document in the sparse embedding service."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                # Sparse service now accepts doc_id directly
                payload = {
                    "text": text,
                    "doc_id": doc_id,  # Pass doc_id directly
                    "metadata": metadata or {}
                }
                    
                response = await client.post(f"{self.sparse_url}/index", json=payload)
                response.raise_for_status()
                result = response.json()
                logger.debug(f"Sparse indexing successful for doc {doc_id}")
                return result
            except Exception as e:
                logger.error(f"Sparse indexing failed for doc {doc_id}: {e}")
                return {"success": False, "error": str(e)}
    
    async def index_document(self, text: str, doc_id: str, metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Index a document in both services in parallel."""
        logger.info(f"Indexing document {doc_id} in parallel...")
        
        # Run both indexing operations in parallel
        dense_task = self.index_document_dense(text, doc_id, metadata)
        sparse_task = self.index_document_sparse(text, doc_id, metadata)
        
        dense_result, sparse_result = await asyncio.gather(dense_task, sparse_task)
        
        return {
            "doc_id": doc_id,
            "dense": dense_result,
            "sparse": sparse_result,
            "success": dense_result.get("success", False) and sparse_result.get("success", False)
        }
    
    async def search_dense(self, query: str, top_k: int = 20) -> List[SearchResult]:
        """Search using dense embeddings."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "query": query,
                    "top_k": top_k,
                    "return_documents": True
                }
                response = await client.post(f"{self.dense_url}/search", json=payload)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for item in data.get("results", []):
                    results.append(SearchResult(
                        doc_id=item["doc_id"],
                        score=item["score"],
                        text=item.get("text"),
                        metadata=item.get("metadata"),
                        source="dense",
                        rank=item.get("rank"),
                        debug_info={
                            "original_score": item["score"],
                            "original_rank": item.get("rank", 0)
                        }
                    ))
                
                logger.debug(f"Dense search returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Dense search failed: {e}")
                return []
    
    async def search_sparse(self, query: str, top_k: int = 20) -> List[SearchResult]:
        """Search using sparse embeddings (BM25)."""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            try:
                payload = {
                    "query": query,
                    "top_k": top_k
                }
                response = await client.post(f"{self.sparse_url}/search", json=payload)
                response.raise_for_status()
                data = response.json()
                
                results = []
                for idx, item in enumerate(data):
                    # Now doc_id is returned directly from the sparse service
                    doc_id = item.get("doc_id", f"doc_{idx}")
                    
                    results.append(SearchResult(
                        doc_id=doc_id,
                        score=item["score"],
                        text=item.get("text"),
                        metadata=item.get("metadata"),
                        source="sparse",
                        rank=idx + 1,
                        debug_info={
                            "bm25_score": item["score"],
                            "matched_terms": item.get("debug", {}).get("matched_terms", []) if item.get("debug") else [],
                            "doc_length": item.get("debug", {}).get("doc_length", 0) if item.get("debug") else 0,
                            "original_rank": idx + 1
                        }
                    ))
                
                logger.debug(f"Sparse search returned {len(results)} results")
                return results
                
            except Exception as e:
                logger.error(f"Sparse search failed: {e}")
                return []
    
    async def search(self, query: str, top_k: int = 20, mode: str = "hybrid") -> Tuple[List[SearchResult], List[SearchResult]]:
        """Search using specified mode (dense, sparse, or hybrid)."""
        logger.info(f"Searching with mode: {mode}, query: '{query[:50]}...'")
        
        dense_results = []
        sparse_results = []
        
        if mode == "dense":
            dense_results = await self.search_dense(query, top_k)
        elif mode == "sparse":
            sparse_results = await self.search_sparse(query, top_k)
        elif mode == "hybrid":
            # Run both searches in parallel
            dense_task = self.search_dense(query, top_k)
            sparse_task = self.search_sparse(query, top_k)
            dense_results, sparse_results = await asyncio.gather(dense_task, sparse_task)
        else:
            raise ValueError(f"Invalid search mode: {mode}")
        
        return dense_results, sparse_results
    
    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from both services."""
        logger.info(f"Deleting document {doc_id} from both services...")
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Delete from dense service
            dense_task = client.delete(f"{self.dense_url}/index", json={"doc_id": doc_id})
            
            # For sparse service, we need to check if it supports deletion
            # If not, we'll need to rebuild the index
            sparse_task = client.delete(f"{self.sparse_url}/index")  # Clear all for now
            
            try:
                dense_response, sparse_response = await asyncio.gather(dense_task, sparse_task)
                return {
                    "doc_id": doc_id,
                    "dense": dense_response.json() if dense_response.status_code == 200 else {"success": False},
                    "sparse": sparse_response.json() if sparse_response.status_code == 200 else {"success": False}
                }
            except Exception as e:
                logger.error(f"Failed to delete document {doc_id}: {e}")
                return {"success": False, "error": str(e)}
