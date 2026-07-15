"""Contextual Agentic RAG System

This module extends the base AgenticRAG to use contextual retrieval,
demonstrating the improved answer quality from better retrieval.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Generator
from datetime import datetime

from agent import AgenticRAG, Message
from config import Config
from contextual_tools import ContextualKnowledgeBaseTools, ContextualSearchResult

logger = logging.getLogger(__name__)


class ContextualAgenticRAG(AgenticRAG):
    """
    Enhanced Agentic RAG with contextual retrieval support.
    
    Educational Features:
    - Shows how better retrieval leads to better answers
    - Logs retrieval quality metrics
    - Compares contextual vs non-contextual results
    """
    
    def __init__(self, 
                 config: Optional[Config] = None,
                 kb_tools: Optional[ContextualKnowledgeBaseTools] = None,
                 use_contextual: bool = True):
        """
        Initialize contextual agent.
        
        Args:
            config: Configuration object
            kb_tools: Contextual knowledge base tools
            use_contextual: Whether to use contextual retrieval
        """
        self.use_contextual = use_contextual
        
        # Initialize base class but skip KB tools initialization
        self.config = config or Config.from_env()
        self._init_llm_client()
        
        # Use provided contextual KB tools or create new ones
        if kb_tools:
            self.kb_tools = kb_tools
        else:
            self.kb_tools = ContextualKnowledgeBaseTools(
                self.config.knowledge_base,
                use_contextual=use_contextual,
                enable_comparison=False
            )
        
        # Initialize other components
        self.conversation_history = []
        self.tools = self._get_contextual_tool_definitions()
        
        # Track retrieval metrics
        self.retrieval_metrics = {
            "queries_executed": 0,
            "total_chunks_retrieved": 0,
            "avg_retrieval_score": 0.0,
            "contextual_chunks_used": 0,
            "non_contextual_chunks_used": 0
        }
        
        mode = "CONTEXTUAL" if use_contextual else "NON-CONTEXTUAL"
        logger.info(f"Initialized ContextualAgenticRAG in {mode} mode")
    
    def _get_system_prompt(self) -> str:
        """Enhanced system prompt that leverages contextual information"""
        base_prompt = super()._get_system_prompt()
        
        if self.use_contextual:
            contextual_addition = """

## Using Contextual Information:

When you receive search results, pay attention to the contextual information provided. Each chunk may include:
- Context that situates the chunk within the larger document
- Information about what section or topic the chunk belongs to
- Related entities and concepts mentioned

Use this contextual information to:
1. Better understand the relevance of each chunk
2. Identify connections between different pieces of information
3. Provide more accurate and complete answers

Remember that contextual chunks have been enhanced with additional information to improve retrieval accuracy."""
            
            return base_prompt + contextual_addition
        
        return base_prompt
    
    def _execute_tool(self, tool_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Execute tool with enhanced logging for educational purposes.
        
        This override adds detailed logging to show how contextual
        retrieval improves the search results.
        """
        logger.debug(f"Executing tool: {tool_name} with args: {arguments}")
        
        try:
            if tool_name == "contextual_knowledge_search":
                query = arguments.get("query", "")
                method = arguments.get("method", "hybrid")
                top_k = arguments.get("top_k", 20)
                
                logger.info(f"\n{'='*60}")
                logger.info(f"CONTEXTUAL SEARCH EXECUTION")
                logger.info(f"{'='*60}")
                logger.info(f"Query: {query}")
                logger.info(f"Method: {method}")
                logger.info(f"Top-K: {top_k}")
                logger.info(f"Mode: {'Contextual' if self.use_contextual else 'Non-contextual'}")
                
                # Perform search
                results = self.kb_tools.contextual_search(query, method, top_k)
                
                if not results:
                    logger.info("No results found")
                    return {"status": "no_results", "message": "No relevant documents found"}
                
                # Log retrieval quality
                avg_score = sum(r.score for r in results) / len(results)
                logger.info(f"\nRetrieval Statistics:")
                logger.info(f"  Results found: {len(results)}")
                logger.info(f"  Average score: {avg_score:.4f}")
                logger.info(f"  Top score: {results[0].score:.4f}")
                
                # Show distribution of retrieval methods if hybrid
                if method == "hybrid":
                    bm25_only = sum(1 for r in results if r.bm25_score > 0 and r.embedding_score == 0)
                    embedding_only = sum(1 for r in results if r.embedding_score > 0 and r.bm25_score == 0)
                    both = sum(1 for r in results if r.bm25_score > 0 and r.embedding_score > 0)
                    
                    logger.info(f"\nRetrieval Method Distribution:")
                    logger.info(f"  BM25 only: {bm25_only}")
                    logger.info(f"  Embedding only: {embedding_only}")
                    logger.info(f"  Both methods: {both}")
                
                # Update metrics
                self.retrieval_metrics["queries_executed"] += 1
                self.retrieval_metrics["total_chunks_retrieved"] += len(results)
                
                # Calculate running average score
                prev_avg = self.retrieval_metrics["avg_retrieval_score"]
                n = self.retrieval_metrics["queries_executed"]
                self.retrieval_metrics["avg_retrieval_score"] = (
                    (prev_avg * (n - 1) + avg_score) / n
                )
                
                if self.use_contextual:
                    self.retrieval_metrics["contextual_chunks_used"] += len(results)
                else:
                    self.retrieval_metrics["non_contextual_chunks_used"] += len(results)
                
                # Format results for agent
                formatted_results = []
                for i, r in enumerate(results, 1):
                    result_dict = {
                        "rank": i,
                        "doc_id": r.doc_id,
                        "chunk_id": r.chunk_id,
                        "text": r.text,
                        "score": r.score
                    }
                    
                    formatted_results.append(result_dict)
                    
                    # Log top results
                    if i <= 3:
                        logger.info(f"\nTop Result {i}:")
                        logger.info(f"  Score: {r.score:.4f}")
                        logger.info(f"  Text: {r.text}")
                
                logger.info(f"{'='*60}\n")
                
                return {
                    "status": "success",
                    "results": formatted_results,
                    "total_found": len(results),
                    "avg_score": avg_score,
                    "search_method": method,
                    "is_contextual": self.use_contextual
                }
            
            elif tool_name == "get_document":
                # Use parent implementation
                return super()._execute_tool(tool_name, arguments)
            
            else:
                return {"status": "error", "message": f"Unknown tool: {tool_name}"}
                
        except Exception as e:
            logger.error(f"Tool execution error: {e}")
            return {"status": "error", "message": str(e)}
    
    def _get_contextual_tool_definitions(self) -> List[Dict[str, Any]]:
        """Get tool definitions with contextual search capabilities"""
        return [
            {
                "type": "function",
                "function": {
                    "name": "contextual_knowledge_search",
                    "description": "Search the knowledge base using contextual or non-contextual retrieval. Returns chunks with optional context information that helps understand their relevance.",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "query": {
                                "type": "string",
                                "description": "Natural language search query"
                            },
                            "method": {
                                "type": "string",
                                "enum": ["bm25", "embedding", "hybrid"],
                                "description": "Search method to use (default: hybrid)",
                                "default": "hybrid"
                            },
                            "top_k": {
                                "type": "integer",
                                "description": "Number of results to retrieve (default: 20)",
                                "default": 20
                            }
                        },
                        "required": ["query"]
                    }
                }
            },
            {
                "type": "function",
                "function": {
                    "name": "get_document",
                    "description": "Retrieve the complete content of a specific document",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "doc_id": {
                                "type": "string",
                                "description": "Document ID to retrieve"
                            }
                        },
                        "required": ["doc_id"]
                    }
                }
            }
        ]
    
    def query(self, user_query: str, stream: bool = None) -> Any:
        """
        Process query with contextual retrieval and detailed logging.
        
        This override adds educational logging to show the retrieval process.
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"PROCESSING QUERY: {user_query}")
        logger.info(f"Mode: {'CONTEXTUAL' if self.use_contextual else 'NON-CONTEXTUAL'}")
        logger.info(f"{'='*80}\n")
        
        # Call parent implementation
        result = super().query(user_query, stream)
        
        # Log final metrics
        logger.info(f"\n{'='*60}")
        logger.info("QUERY PROCESSING COMPLETE")
        logger.info(f"{'='*60}")
        logger.info("Retrieval Metrics:")
        logger.info(f"  Queries executed: {self.retrieval_metrics['queries_executed']}")
        logger.info(f"  Total chunks retrieved: {self.retrieval_metrics['total_chunks_retrieved']}")
        logger.info(f"  Average retrieval score: {self.retrieval_metrics['avg_retrieval_score']:.4f}")
        
        if self.use_contextual:
            logger.info(f"  Contextual chunks used: {self.retrieval_metrics['contextual_chunks_used']}")
        else:
            logger.info(f"  Non-contextual chunks used: {self.retrieval_metrics['non_contextual_chunks_used']}")
        
        logger.info(f"{'='*60}\n")
        
        return result
    
    def get_retrieval_metrics(self) -> Dict[str, Any]:
        """Get detailed retrieval metrics for analysis"""
        metrics = self.retrieval_metrics.copy()
        
        # Add KB statistics
        kb_stats = self.kb_tools.get_statistics()
        metrics["kb_stats"] = kb_stats
        
        # Add mode information
        metrics["mode"] = "contextual" if self.use_contextual else "non_contextual"
        metrics["timestamp"] = datetime.now().isoformat()
        
        return metrics
    
    def compare_modes(self, user_query: str) -> Dict[str, Any]:
        """
        Compare contextual vs non-contextual modes for the same query.
        
        Educational method to demonstrate the difference in retrieval quality.
        """
        comparison = {
            "query": user_query,
            "timestamp": datetime.now().isoformat(),
            "modes": {}
        }
        
        # Test contextual mode
        logger.info("Testing CONTEXTUAL mode...")
        self.use_contextual = True
        self.kb_tools.use_contextual = True
        contextual_response = self.query(user_query, stream=False)
        comparison["modes"]["contextual"] = {
            "response": contextual_response,
            "metrics": self.get_retrieval_metrics()
        }
        
        # Reset metrics
        self.retrieval_metrics = {
            "queries_executed": 0,
            "total_chunks_retrieved": 0,
            "avg_retrieval_score": 0.0,
            "contextual_chunks_used": 0,
            "non_contextual_chunks_used": 0
        }
        
        # Test non-contextual mode
        logger.info("Testing NON-CONTEXTUAL mode...")
        self.use_contextual = False
        self.kb_tools.use_contextual = False
        non_contextual_response = self.query(user_query, stream=False)
        comparison["modes"]["non_contextual"] = {
            "response": non_contextual_response,
            "metrics": self.get_retrieval_metrics()
        }
        
        # Analyze differences
        contextual_score = comparison["modes"]["contextual"]["metrics"]["avg_retrieval_score"]
        non_contextual_score = comparison["modes"]["non_contextual"]["metrics"]["avg_retrieval_score"]
        
        improvement = ((contextual_score - non_contextual_score) / non_contextual_score * 100) if non_contextual_score > 0 else 0
        
        comparison["analysis"] = {
            "score_improvement_pct": improvement,
            "contextual_avg_score": contextual_score,
            "non_contextual_avg_score": non_contextual_score,
            "recommendation": (
                "Use contextual retrieval" if improvement > 10
                else "Consider cost-benefit of contextual retrieval"
            )
        }
        
        return comparison
