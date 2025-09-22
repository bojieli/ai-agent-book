"""
Memory Tools for Agentic RAG
Provides tools for searching and retrieving user memories
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from memory_indexer import ContextualMemoryIndexer, ConversationChunk
from config import Config, SearchStrategy

logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a memory search result"""
    chunk_id: str
    conversation_id: str
    text: str
    context: Optional[str]
    score: float
    metadata: Dict[str, Any]
    messages: Optional[List[Dict[str, str]]] = None


class MemorySearchTools:
    """
    Tools for searching and retrieving memories from the contextual index
    Designed to be used by an agentic RAG system
    """
    
    def __init__(self, 
                 user_id: str,
                 indexer: Optional[ContextualMemoryIndexer] = None,
                 config: Optional[Config] = None):
        """
        Initialize memory search tools
        
        Args:
            user_id: User identifier
            indexer: Pre-initialized indexer (optional)
            config: Configuration
        """
        self.user_id = user_id
        self.config = config or Config.from_env()
        
        # Use provided indexer or create new one
        self.indexer = indexer or ContextualMemoryIndexer(
            user_id=user_id,
            config=self.config,
            enable_contextual=self.config.indexing.enable_contextual
        )
        
        # Track search history for analysis
        self.search_history: List[Dict[str, Any]] = []
        
        logger.info(f"Initialized MemorySearchTools for user {user_id}")
    
    def memory_search(self, 
                     query: str,
                     filters: Optional[Dict[str, Any]] = None,
                     top_k: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Search for relevant memories
        
        This is the main tool exposed to the agent for memory retrieval.
        
        Args:
            query: Natural language search query
            filters: Optional filters (conversation_id, date_range, etc.)
            top_k: Number of results to return
            
        Returns:
            List of relevant memory chunks with scores
        """
        top_k = top_k or self.config.agent.search_top_k
        
        # Log search
        search_log = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "filters": filters,
            "top_k": top_k
        }
        
        try:
            # Determine search strategy based on configuration
            strategy = SearchStrategy.HYBRID_RRF
            if self.config.agent.bm25_weight == 0:
                strategy = SearchStrategy.EMBEDDING_ONLY
            elif self.config.agent.embedding_weight == 0:
                strategy = SearchStrategy.BM25_ONLY
            
            # Perform search
            results = self.indexer.search(
                query=query,
                top_k=top_k,
                use_contextual=self.config.indexing.enable_contextual,
                strategy=strategy
            )
            
            # Apply filters if provided
            if filters:
                results = self._apply_filters(results, filters)
            
            # Rerank if enabled
            if self.config.agent.enable_reranking and len(results) > self.config.agent.rerank_top_k:
                results = self._rerank_results(query, results)[:self.config.agent.rerank_top_k]
            
            # Format results for agent
            formatted_results = []
            for r in results:
                formatted_results.append({
                    "chunk_id": r["chunk_id"],
                    "conversation_id": r["conversation_id"],
                    "relevance_score": round(r["score"], 3),
                    "context_description": r.get("context", ""),
                    "content_preview": r["text"][:300] + "..." if len(r["text"]) > 300 else r["text"],
                    "metadata": r.get("metadata", {})
                })
            
            # Log results
            search_log["results_count"] = len(formatted_results)
            search_log["top_scores"] = [r["relevance_score"] for r in formatted_results[:3]]
            self.search_history.append(search_log)
            
            logger.info(f"Memory search for '{query}' returned {len(formatted_results)} results")
            
            return formatted_results
            
        except Exception as e:
            logger.error(f"Error in memory_search: {e}")
            search_log["error"] = str(e)
            self.search_history.append(search_log)
            return []
    
    def get_full_memory(self, chunk_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve full content of a specific memory chunk
        
        Args:
            chunk_id: Chunk identifier
            
        Returns:
            Full memory content or None if not found
        """
        chunk = self.indexer.chunk_map.get(chunk_id)
        
        if not chunk:
            logger.warning(f"Chunk {chunk_id} not found")
            return None
        
        # Format full memory
        full_memory = {
            "chunk_id": chunk.chunk_id,
            "conversation_id": chunk.conversation_id,
            "timestamp": chunk.timestamp,
            "conversation_rounds": f"{chunk.start_round}-{chunk.end_round}",
            "messages": chunk.messages,
            "full_text": chunk.original_text,
            "context_description": chunk.context_description,
            "metadata": chunk.metadata
        }
        
        logger.info(f"Retrieved full memory for chunk {chunk_id}")
        
        return full_memory
    
    def get_conversation_context(self,
                                conversation_id: str,
                                around_chunk: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all chunks from a specific conversation
        
        Args:
            conversation_id: Conversation identifier
            around_chunk: Optional chunk ID to get context around
            
        Returns:
            List of chunks from the conversation
        """
        # Find all chunks from this conversation
        conv_chunks = [
            chunk for chunk in self.indexer.chunks
            if chunk.conversation_id == conversation_id
        ]
        
        # Sort by start_round
        conv_chunks.sort(key=lambda x: x.start_round)
        
        # If around_chunk specified, prioritize nearby chunks
        if around_chunk:
            target_chunk = self.indexer.chunk_map.get(around_chunk)
            if target_chunk:
                # Sort by distance from target chunk
                conv_chunks.sort(
                    key=lambda x: abs(x.start_round - target_chunk.start_round)
                )
        
        # Format results
        results = []
        for chunk in conv_chunks:
            results.append({
                "chunk_id": chunk.chunk_id,
                "rounds": f"{chunk.start_round}-{chunk.end_round}",
                "summary": chunk.context_description or chunk.original_text[:200],
                "timestamp": chunk.timestamp
            })
        
        logger.info(f"Retrieved {len(results)} chunks for conversation {conversation_id}")
        
        return results
    
    def expand_search(self,
                     original_query: str,
                     previous_results: List[str]) -> List[Dict[str, Any]]:
        """
        Expand search with query reformulation
        Used by agent for iterative refinement
        
        Args:
            original_query: Original search query
            previous_results: Chunk IDs already retrieved
            
        Returns:
            New search results
        """
        # Generate expanded queries
        expanded_queries = self._generate_query_expansions(original_query)
        
        all_results = []
        seen_chunks = set(previous_results)
        
        for query in expanded_queries:
            results = self.memory_search(query, top_k=5)
            
            # Filter out already seen chunks
            new_results = [
                r for r in results 
                if r["chunk_id"] not in seen_chunks
            ]
            
            all_results.extend(new_results)
            seen_chunks.update(r["chunk_id"] for r in new_results)
        
        # Sort by relevance
        all_results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        logger.info(f"Expanded search found {len(all_results)} new results")
        
        return all_results[:self.config.agent.search_top_k]
    
    def _apply_filters(self, 
                      results: List[Dict[str, Any]], 
                      filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to search results"""
        filtered = results
        
        # Filter by conversation_id
        if "conversation_id" in filters:
            conv_id = filters["conversation_id"]
            filtered = [r for r in filtered if r["conversation_id"] == conv_id]
        
        # Filter by date range
        if "date_range" in filters:
            start_date = filters["date_range"].get("start")
            end_date = filters["date_range"].get("end")
            # Implementation would require parsing timestamps from chunks
            # Simplified for educational purposes
        
        # Filter by metadata
        if "metadata" in filters:
            for key, value in filters["metadata"].items():
                filtered = [
                    r for r in filtered
                    if r.get("metadata", {}).get(key) == value
                ]
        
        return filtered
    
    def _rerank_results(self,
                       query: str,
                       results: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Rerank results using a more sophisticated method
        Could use an LLM or a specialized reranking model
        """
        if not self.config.agent.reranking_model:
            # Simple reranking based on query term overlap
            query_terms = set(query.lower().split())
            
            for result in results:
                text = result.get("text", "").lower()
                text_terms = set(text.split())
                
                # Calculate term overlap
                overlap = len(query_terms & text_terms)
                
                # Boost score based on overlap
                result["score"] = result["score"] * (1 + overlap * 0.1)
        
        else:
            # Use LLM for reranking (simplified)
            # In production, this would batch results and use a specialized model
            pass
        
        # Sort by new scores
        results.sort(key=lambda x: x["score"], reverse=True)
        
        return results
    
    def _generate_query_expansions(self, query: str) -> List[str]:
        """Generate query expansions for better recall"""
        expansions = [query]  # Original query
        
        if self.config.agent.enable_query_expansion:
            # Simple expansion strategies
            # In production, could use LLM or synonyms
            
            # Add question variations
            if "when" in query.lower():
                expansions.append(query.replace("when", "what time"))
                expansions.append(query.replace("when", "what date"))
            
            if "where" in query.lower():
                expansions.append(query.replace("where", "what location"))
                expansions.append(query.replace("where", "which place"))
            
            # Add tense variations
            if "is" in query:
                expansions.append(query.replace("is", "was"))
            if "are" in query:
                expansions.append(query.replace("are", "were"))
        
        return expansions[:3]  # Limit expansions
    
    def get_search_analytics(self) -> Dict[str, Any]:
        """Get analytics about search patterns"""
        if not self.search_history:
            return {"total_searches": 0}
        
        total_searches = len(self.search_history)
        avg_results = sum(
            s.get("results_count", 0) for s in self.search_history
        ) / total_searches
        
        # Find common query patterns
        queries = [s["query"] for s in self.search_history]
        query_words = []
        for q in queries:
            query_words.extend(q.lower().split())
        
        # Count word frequency
        word_freq = {}
        for word in query_words:
            if len(word) > 3:  # Skip short words
                word_freq[word] = word_freq.get(word, 0) + 1
        
        # Sort by frequency
        top_terms = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "total_searches": total_searches,
            "average_results_per_search": round(avg_results, 2),
            "searches_with_errors": sum(1 for s in self.search_history if "error" in s),
            "top_search_terms": top_terms,
            "recent_searches": [
                {"query": s["query"], "results": s.get("results_count", 0)}
                for s in self.search_history[-5:]
            ]
        }


def get_tool_definitions() -> List[Dict[str, Any]]:
    """
    Get OpenAI function definitions for memory tools
    Used by the agentic RAG system
    """
    return [
        {
            "type": "function",
            "function": {
                "name": "memory_search",
                "description": "Search through user's conversation history and memories to find relevant information",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Natural language search query describing what information to find"
                        },
                        "filters": {
                            "type": "object",
                            "description": "Optional filters to narrow search",
                            "properties": {
                                "conversation_id": {
                                    "type": "string",
                                    "description": "Specific conversation to search within"
                                },
                                "date_range": {
                                    "type": "object",
                                    "properties": {
                                        "start": {"type": "string"},
                                        "end": {"type": "string"}
                                    }
                                }
                            }
                        },
                        "top_k": {
                            "type": "integer",
                            "description": "Number of results to return (default: 10)",
                            "minimum": 1,
                            "maximum": 50
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_full_memory",
                "description": "Retrieve the complete content of a specific memory chunk",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "chunk_id": {
                            "type": "string",
                            "description": "The unique identifier of the memory chunk to retrieve"
                        }
                    },
                    "required": ["chunk_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "get_conversation_context",
                "description": "Get all memory chunks from a specific conversation for broader context",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "conversation_id": {
                            "type": "string",
                            "description": "The conversation identifier"
                        },
                        "around_chunk": {
                            "type": "string",
                            "description": "Optional chunk ID to get surrounding context"
                        }
                    },
                    "required": ["conversation_id"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "expand_search",
                "description": "Expand search with query reformulation to find additional relevant memories",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "original_query": {
                            "type": "string",
                            "description": "The original search query"
                        },
                        "previous_results": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Chunk IDs already retrieved to avoid duplicates"
                        }
                    },
                    "required": ["original_query", "previous_results"]
                }
            }
        }
    ]
