"""Main retrieval pipeline combining dense, sparse, and reranking."""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import uuid

from config import PipelineConfig, SearchMode
from document_store import DocumentStore
from retrieval_client import RetrievalClient, SearchResult
from reranker import Reranker, RerankResult

logger = logging.getLogger(__name__)

class RetrievalPipeline:
    """Main retrieval pipeline orchestrating dense, sparse, and reranking."""
    
    def __init__(self, config: Optional[PipelineConfig] = None):
        self.config = config or PipelineConfig()
        
        # Initialize components
        self.document_store = DocumentStore()
        self.retrieval_client = RetrievalClient(
            dense_url=self.config.services.dense_service_url,
            sparse_url=self.config.services.sparse_service_url
        )
        self.reranker = Reranker(
            model_name=self.config.reranker.model_name,
            device=self.config.reranker.device,
            use_fp16=self.config.reranker.use_fp16,
            max_length=self.config.reranker.max_length
        )
        
        logger.info("Retrieval pipeline initialized")
    
    async def index_document(self, 
                            text: str, 
                            doc_id: Optional[str] = None,
                            metadata: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Index a document in both dense and sparse services.
        
        Args:
            text: Document text
            doc_id: Optional document ID (generated if not provided)
            metadata: Optional metadata
            
        Returns:
            Indexing result with status from both services
        """
        # Generate doc_id if not provided
        if not doc_id:
            doc_id = f"doc_{uuid.uuid4().hex[:8]}"
        
        logger.info(f"Indexing document {doc_id}")
        
        # Store document locally
        self.document_store.add_document(doc_id, text, metadata)
        
        # Index in both services in parallel
        result = await self.retrieval_client.index_document(text, doc_id, metadata)
        
        # Add timestamp and document info
        result["timestamp"] = datetime.now().isoformat()
        result["text_length"] = len(text)
        
        if self.config.debug:
            logger.debug(f"Indexing result: dense={result['dense'].get('success')}, "
                        f"sparse={result['sparse'].get('success')}")
        
        return result
    
    async def search(self, 
                    query: str,
                    mode: SearchMode = SearchMode.HYBRID,
                    top_k: Optional[int] = None,
                    rerank_top_k: Optional[int] = None,
                    skip_reranking: bool = False) -> Dict[str, Any]:
        """Search for documents using specified mode.
        
        Args:
            query: Search query
            mode: Search mode (dense, sparse, or hybrid)
            top_k: Number of candidates to retrieve from each service
            rerank_top_k: Number of results after reranking
            skip_reranking: Skip reranking step (for comparison)
            
        Returns:
            Search results with scores and rankings
        """
        top_k = top_k or self.config.default_top_k
        rerank_top_k = rerank_top_k or self.config.rerank_top_k
        
        logger.info(f"Searching with mode={mode}, top_k={top_k}, rerank_top_k={rerank_top_k}")
        
        start_time = datetime.now()
        
        # Retrieve from services
        dense_results, sparse_results = await self.retrieval_client.search(
            query, top_k, mode.value
        )
        
        retrieval_time = (datetime.now() - start_time).total_seconds()
        
        # Prepare response structure
        response = {
            "query": query,
            "mode": mode.value,
            "timestamp": start_time.isoformat(),
            "retrieval_time_ms": retrieval_time * 1000,
            "dense_results": [],
            "sparse_results": [],
            "combined_results": [],
            "reranked_results": [],
            "statistics": {}
        }
        
        # Process dense results
        if dense_results:
            response["dense_results"] = [
                {
                    "doc_id": r.doc_id,
                    "score": r.score,
                    "rank": r.rank or idx + 1,
                    "text": r.text[:200] if r.text else None
                }
                for idx, r in enumerate(dense_results[:10])  # Show top 10 for educational purposes
            ]
        
        # Process sparse results
        if sparse_results:
            response["sparse_results"] = [
                {
                    "doc_id": r.doc_id,
                    "score": r.score,
                    "rank": r.rank or idx + 1,
                    "text": r.text[:200] if r.text else None,
                    "matched_terms": r.debug_info.get("matched_terms", []) if r.debug_info else []
                }
                for idx, r in enumerate(sparse_results[:10])  # Show top 10 for educational purposes
            ]
        
        # Combine results for reranking
        combined_docs = self._combine_results(dense_results, sparse_results)
        
        if not combined_docs:
            logger.warning("No documents to rerank")
            return response
        
        response["combined_results"] = [
            {
                "doc_id": doc["doc_id"],
                "dense_score": doc.get("dense_score"),
                "sparse_score": doc.get("sparse_score"),
                "dense_rank": doc.get("dense_rank"),
                "sparse_rank": doc.get("sparse_rank")
            }
            for doc in combined_docs[:20]  # Show top 20 combined
        ]
        
        # Perform reranking if not skipped
        if not skip_reranking and combined_docs:
            rerank_start = datetime.now()
            
            reranked = self.reranker.rerank(
                query=query,
                documents=combined_docs,
                top_k=rerank_top_k,
                return_scores=self.config.show_scores
            )
            
            rerank_time = (datetime.now() - rerank_start).total_seconds()
            response["rerank_time_ms"] = rerank_time * 1000
            
            # Format reranked results
            response["reranked_results"] = self._format_reranked_results(reranked)
        
        # Calculate statistics
        response["statistics"] = self._calculate_statistics(
            dense_results, sparse_results, response.get("reranked_results", [])
        )
        
        total_time = (datetime.now() - start_time).total_seconds()
        response["total_time_ms"] = total_time * 1000
        
        return response
    
    def _combine_results(self, 
                        dense_results: List[SearchResult], 
                        sparse_results: List[SearchResult]) -> List[Dict[str, Any]]:
        """Combine dense and sparse results for reranking.
        
        Args:
            dense_results: Results from dense search
            sparse_results: Results from sparse search
            
        Returns:
            Combined document list with scores and ranks from both sources
        """
        combined = {}
        
        # Add dense results
        for idx, result in enumerate(dense_results):
            doc_id = result.doc_id
            if doc_id not in combined:
                # Get full document from store
                doc = self.document_store.get_document(doc_id)
                combined[doc_id] = {
                    "doc_id": doc_id,
                    "text": doc["text"] if doc else result.text,
                    "metadata": doc["metadata"] if doc else result.metadata,
                    "dense_score": result.score,
                    "dense_rank": idx + 1,
                    "sparse_score": None,
                    "sparse_rank": None
                }
            else:
                combined[doc_id]["dense_score"] = result.score
                combined[doc_id]["dense_rank"] = idx + 1
        
        # Add sparse results
        for idx, result in enumerate(sparse_results):
            doc_id = result.doc_id
            if doc_id not in combined:
                # Get full document from store
                doc = self.document_store.get_document(doc_id)
                combined[doc_id] = {
                    "doc_id": doc_id,
                    "text": doc["text"] if doc else result.text,
                    "metadata": doc["metadata"] if doc else result.metadata,
                    "dense_score": None,
                    "dense_rank": None,
                    "sparse_score": result.score,
                    "sparse_rank": idx + 1
                }
            else:
                combined[doc_id]["sparse_score"] = result.score
                combined[doc_id]["sparse_rank"] = idx + 1
        
        # Convert to list and sort by average rank (lower is better)
        combined_list = list(combined.values())
        
        # Calculate combined score for initial ordering
        for doc in combined_list:
            ranks = []
            if doc["dense_rank"] is not None:
                ranks.append(doc["dense_rank"])
            if doc["sparse_rank"] is not None:
                ranks.append(doc["sparse_rank"])
            
            if ranks:
                doc["avg_rank"] = sum(ranks) / len(ranks)
            else:
                doc["avg_rank"] = float('inf')
        
        # Sort by average rank
        combined_list.sort(key=lambda x: x["avg_rank"])
        
        return combined_list
    
    def _format_reranked_results(self, reranked: List[RerankResult]) -> List[Dict[str, Any]]:
        """Format reranked results for response.
        
        Args:
            reranked: List of reranked results
            
        Returns:
            Formatted results with educational information
        """
        formatted = []
        
        for idx, result in enumerate(reranked):
            item = {
                "rank": idx + 1,
                "doc_id": result.doc_id,
                "rerank_score": result.rerank_score,
                "text": result.text,
                "metadata": result.metadata
            }
            
            # Add educational information about rank changes
            if self.config.show_scores:
                item["original_scores"] = {
                    "dense": result.original_dense_score,
                    "sparse": result.original_sparse_score
                }
                item["original_ranks"] = {
                    "dense": result.original_dense_rank,
                    "sparse": result.original_sparse_rank
                }
                
                # Calculate rank changes
                rank_changes = []
                if result.original_dense_rank:
                    change = result.original_dense_rank - (idx + 1)
                    rank_changes.append(f"dense: {change:+d}")
                if result.original_sparse_rank:
                    change = result.original_sparse_rank - (idx + 1)
                    rank_changes.append(f"sparse: {change:+d}")
                
                item["rank_changes"] = rank_changes
            
            formatted.append(item)
        
        return formatted
    
    def _calculate_statistics(self, 
                             dense_results: List[SearchResult],
                             sparse_results: List[SearchResult],
                             reranked_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calculate statistics for educational purposes.
        
        Args:
            dense_results: Dense search results
            sparse_results: Sparse search results
            reranked_results: Reranked results
            
        Returns:
            Statistics dictionary
        """
        stats = {
            "dense_retrieved": len(dense_results),
            "sparse_retrieved": len(sparse_results),
            "total_unique_documents": 0,
            "reranked_count": len(reranked_results)
        }
        
        # Count unique documents
        unique_docs = set()
        for r in dense_results:
            unique_docs.add(r.doc_id)
        for r in sparse_results:
            unique_docs.add(r.doc_id)
        
        stats["total_unique_documents"] = len(unique_docs)
        
        # Calculate overlap
        if dense_results and sparse_results:
            dense_ids = {r.doc_id for r in dense_results}
            sparse_ids = {r.doc_id for r in sparse_results}
            overlap = dense_ids & sparse_ids
            stats["overlap_count"] = len(overlap)
            stats["overlap_percentage"] = (len(overlap) / len(unique_docs)) * 100 if unique_docs else 0
        
        # Analyze rank changes if available
        if reranked_results and self.config.show_scores:
            avg_dense_change = []
            avg_sparse_change = []
            
            for r in reranked_results:
                if "original_ranks" in r:
                    if r["original_ranks"]["dense"]:
                        avg_dense_change.append(r["original_ranks"]["dense"] - r["rank"])
                    if r["original_ranks"]["sparse"]:
                        avg_sparse_change.append(r["original_ranks"]["sparse"] - r["rank"])
            
            if avg_dense_change:
                stats["avg_dense_rank_change"] = sum(avg_dense_change) / len(avg_dense_change)
            if avg_sparse_change:
                stats["avg_sparse_rank_change"] = sum(avg_sparse_change) / len(avg_sparse_change)
        
        return stats
    
    async def delete_document(self, doc_id: str) -> Dict[str, Any]:
        """Delete a document from all services.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            Deletion result
        """
        logger.info(f"Deleting document {doc_id}")
        
        # Delete from local store
        local_deleted = self.document_store.delete_document(doc_id)
        
        # Delete from remote services
        remote_result = await self.retrieval_client.delete_document(doc_id)
        
        return {
            "doc_id": doc_id,
            "local_deleted": local_deleted,
            "remote_result": remote_result,
            "success": local_deleted
        }
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get pipeline statistics.
        
        Returns:
            Statistics dictionary
        """
        return {
            "document_store": self.document_store.get_stats(),
            "pipeline_config": {
                "default_top_k": self.config.default_top_k,
                "rerank_top_k": self.config.rerank_top_k,
                "reranker_model": self.config.reranker.model_name,
                "device": self.config.reranker.device
            },
            "services": {
                "dense_url": self.config.services.dense_service_url,
                "sparse_url": self.config.services.sparse_service_url
            }
        }
