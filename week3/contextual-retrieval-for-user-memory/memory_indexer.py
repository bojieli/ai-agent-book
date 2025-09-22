"""
Contextual Memory Indexer - Implements contextual retrieval for conversation histories
Based on Anthropic's Contextual Retrieval technique
"""

import json
import logging
import pickle
import os
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
import numpy as np
from rank_bm25 import BM25Okapi
from openai import OpenAI
import tiktoken
from collections import defaultdict
import hashlib

from config import Config, IndexingConfig, SearchStrategy

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ConversationChunk:
    """Represents a chunk of conversation with optional context"""
    chunk_id: str
    conversation_id: str
    user_id: str
    messages: List[Dict[str, str]]  # List of {role, content} dicts
    start_round: int
    end_round: int
    timestamp: str
    
    # Original text
    original_text: str
    
    # Contextual enhancement
    contextual_text: Optional[str] = None
    context_description: Optional[str] = None
    
    # Embeddings
    original_embedding: Optional[np.ndarray] = None
    contextual_embedding: Optional[np.ndarray] = None
    
    # Metadata
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def get_text_for_indexing(self, use_contextual: bool = True) -> str:
        """Get the text to use for indexing"""
        if use_contextual and self.contextual_text:
            return self.contextual_text
        return self.original_text
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage"""
        return {
            "chunk_id": self.chunk_id,
            "conversation_id": self.conversation_id,
            "user_id": self.user_id,
            "messages": self.messages,
            "start_round": self.start_round,
            "end_round": self.end_round,
            "timestamp": self.timestamp,
            "original_text": self.original_text,
            "contextual_text": self.contextual_text,
            "context_description": self.context_description,
            "metadata": self.metadata
        }


class ContextualMemoryIndexer:
    """
    Indexes conversation histories with contextual retrieval
    Implements both BM25 and embedding-based search with context enhancement
    """
    
    def __init__(self, 
                 user_id: str,
                 config: Optional[Config] = None,
                 enable_contextual: bool = True):
        """
        Initialize the contextual memory indexer
        
        Args:
            user_id: User identifier for the memory index
            config: Configuration object
            enable_contextual: Whether to generate contextual descriptions
        """
        self.user_id = user_id
        self.config = config or Config.from_env()
        self.enable_contextual = enable_contextual and self.config.indexing.enable_contextual
        
        # Initialize LLM clients
        self._init_llm_clients()
        
        # Storage
        self.chunks: List[ConversationChunk] = []
        self.chunk_map: Dict[str, ConversationChunk] = {}
        
        # BM25 indexes (separate for contextual and non-contextual)
        self.bm25_contextual = None
        self.bm25_original = None
        self.tokenized_corpus_contextual = []
        self.tokenized_corpus_original = []
        
        # Embedding indexes
        self.embeddings_contextual = []
        self.embeddings_original = []
        
        # Index directory
        self.index_dir = Path(self.config.indexing.index_dir) / user_id
        self.index_dir.mkdir(parents=True, exist_ok=True)
        
        # Load existing index if available
        if self.config.indexing.enable_persistence:
            self._load_index()
        
        logger.info(f"Initialized ContextualMemoryIndexer for user {user_id} "
                   f"(contextual={self.enable_contextual})")
    
    def _init_llm_clients(self):
        """Initialize LLM clients for context generation and embeddings"""
        # Main LLM for context generation
        llm_config = self.config.llm
        api_key = llm_config.get_api_key()
        base_url = llm_config.get_base_url()
        
        if base_url:
            self.llm_client = OpenAI(api_key=api_key, base_url=base_url)
        else:
            self.llm_client = OpenAI(api_key=api_key)
        
        self.llm_model = llm_config.get_model_name()
        
        # Embedding client (OpenAI for embeddings)
        self.embedding_client = OpenAI(api_key=os.getenv("OPENAI_API_KEY", ""))
        self.embedding_model = self.config.indexing.embedding_model
        
        # Tokenizer for chunking
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
    
    def index_conversation(self,
                          conversation_history: Dict[str, Any],
                          chunk_size: Optional[int] = None,
                          show_progress: bool = True) -> List[str]:
        """
        Index a conversation history with contextual retrieval
        
        Args:
            conversation_history: Conversation history with messages
            chunk_size: Number of rounds per chunk (default from config)
            show_progress: Show indexing progress
            
        Returns:
            List of chunk IDs created
        """
        chunk_size = chunk_size or self.config.indexing.chunk_size
        
        # Extract messages
        messages = conversation_history.get("messages", [])
        conversation_id = conversation_history.get("conversation_id", f"conv_{len(self.chunks)}")
        timestamp = conversation_history.get("timestamp", datetime.now().isoformat())
        
        # Create chunks
        chunks = self._create_chunks(
            messages, 
            conversation_id, 
            timestamp,
            chunk_size
        )
        
        # Generate contextual descriptions if enabled
        if self.enable_contextual:
            if show_progress:
                logger.info(f"Generating contextual descriptions for {len(chunks)} chunks...")
            
            full_conversation = self._format_conversation(messages)
            for chunk in chunks:
                self._generate_context(chunk, full_conversation)
        
        # Generate embeddings
        if show_progress:
            logger.info(f"Generating embeddings for {len(chunks)} chunks...")
        
        for chunk in chunks:
            self._generate_embeddings(chunk)
        
        # Add to indexes
        chunk_ids = []
        for chunk in chunks:
            self.chunks.append(chunk)
            self.chunk_map[chunk.chunk_id] = chunk
            chunk_ids.append(chunk.chunk_id)
            
            # Update BM25 indexes
            self._update_bm25_index(chunk)
        
        # Rebuild BM25 models
        self._rebuild_bm25()
        
        # Persist if enabled
        if self.config.indexing.enable_persistence:
            self._save_index()
        
        if show_progress:
            logger.info(f"Indexed {len(chunks)} chunks from conversation {conversation_id}")
        
        return chunk_ids
    
    def _create_chunks(self,
                      messages: List[Dict[str, str]],
                      conversation_id: str,
                      timestamp: str,
                      chunk_size: int) -> List[ConversationChunk]:
        """Create chunks from conversation messages"""
        chunks = []
        
        # Group messages into rounds (user + assistant pairs)
        rounds = []
        current_round = []
        for msg in messages:
            current_round.append(msg)
            if msg.get("role") in ["assistant", "representative", "agent"]:
                rounds.append(current_round)
                current_round = []
        
        # Add remaining messages if any
        if current_round:
            rounds.append(current_round)
        
        # Create chunks with overlap
        overlap = self.config.indexing.chunk_overlap
        for i in range(0, len(rounds), chunk_size - overlap):
            chunk_rounds = rounds[i:i + chunk_size]
            
            # Skip if too small
            if len(chunk_rounds) < self.config.indexing.min_chunk_size:
                continue
            
            # Flatten messages
            chunk_messages = []
            for round_msgs in chunk_rounds:
                chunk_messages.extend(round_msgs)
            
            # Create chunk
            chunk_text = self._format_conversation(chunk_messages)
            chunk_id = self._generate_chunk_id(conversation_id, i)
            
            chunk = ConversationChunk(
                chunk_id=chunk_id,
                conversation_id=conversation_id,
                user_id=self.user_id,
                messages=chunk_messages,
                start_round=i,
                end_round=min(i + chunk_size, len(rounds)),
                timestamp=timestamp,
                original_text=chunk_text,
                metadata={
                    "round_count": len(chunk_rounds),
                    "message_count": len(chunk_messages)
                }
            )
            chunks.append(chunk)
        
        return chunks
    
    def _generate_context(self, chunk: ConversationChunk, full_conversation: str):
        """Generate contextual description for a chunk"""
        # Prepare the context generation prompt
        prompt = f"""<document>
{full_conversation}
</document>

Here is the chunk we want to situate within the whole conversation:
<chunk>
{chunk.original_text}
</chunk>

Please provide a short, succinct context (max 150 tokens) to situate this chunk within the overall conversation. Include:
- The conversation ID and approximate date
- The main topics being discussed in this chunk
- Key user preferences, decisions, or information mentioned
- Any relevant background from earlier in the conversation

Answer only with the succinct context and nothing else."""
        
        try:
            response = self.llm_client.chat.completions.create(
                model=self.llm_model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=self.config.indexing.max_context_length
            )
            
            context = response.choices[0].message.content.strip()
            
            # Combine context with original text
            chunk.context_description = context
            chunk.contextual_text = f"{context}\n\n{chunk.original_text}"
            
            logger.debug(f"Generated context for chunk {chunk.chunk_id}: {context[:100]}...")
            
        except Exception as e:
            logger.error(f"Error generating context for chunk {chunk.chunk_id}: {e}")
            chunk.contextual_text = chunk.original_text
    
    def _generate_embeddings(self, chunk: ConversationChunk):
        """Generate embeddings for a chunk"""
        try:
            # Generate embedding for original text
            response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=chunk.original_text
            )
            chunk.original_embedding = np.array(response.data[0].embedding)
            
            # Generate embedding for contextual text if available
            if chunk.contextual_text and chunk.contextual_text != chunk.original_text:
                response = self.embedding_client.embeddings.create(
                    model=self.embedding_model,
                    input=chunk.contextual_text
                )
                chunk.contextual_embedding = np.array(response.data[0].embedding)
            else:
                chunk.contextual_embedding = chunk.original_embedding
                
        except Exception as e:
            logger.error(f"Error generating embeddings for chunk {chunk.chunk_id}: {e}")
    
    def _update_bm25_index(self, chunk: ConversationChunk):
        """Update BM25 tokenized corpus"""
        # Tokenize for BM25
        original_tokens = chunk.original_text.lower().split()
        self.tokenized_corpus_original.append(original_tokens)
        
        if chunk.contextual_text:
            contextual_tokens = chunk.contextual_text.lower().split()
            self.tokenized_corpus_contextual.append(contextual_tokens)
        else:
            self.tokenized_corpus_contextual.append(original_tokens)
    
    def _rebuild_bm25(self):
        """Rebuild BM25 models"""
        if self.tokenized_corpus_original:
            self.bm25_original = BM25Okapi(
                self.tokenized_corpus_original,
                k1=self.config.indexing.bm25_k1,
                b=self.config.indexing.bm25_b
            )
        
        if self.tokenized_corpus_contextual:
            self.bm25_contextual = BM25Okapi(
                self.tokenized_corpus_contextual,
                k1=self.config.indexing.bm25_k1,
                b=self.config.indexing.bm25_b
            )
    
    def search(self,
              query: str,
              top_k: int = 10,
              use_contextual: bool = True,
              strategy: SearchStrategy = SearchStrategy.HYBRID_RRF) -> List[Dict[str, Any]]:
        """
        Search for relevant memory chunks
        
        Args:
            query: Search query
            top_k: Number of results to return
            use_contextual: Whether to use contextual index
            strategy: Search strategy (bm25, embedding, hybrid, hybrid_rrf)
            
        Returns:
            List of search results with scores
        """
        if not self.chunks:
            logger.warning("No chunks indexed yet")
            return []
        
        results = []
        
        if strategy == SearchStrategy.BM25_ONLY:
            results = self._search_bm25(query, top_k * 2, use_contextual)
            
        elif strategy == SearchStrategy.EMBEDDING_ONLY:
            results = self._search_embedding(query, top_k * 2, use_contextual)
            
        elif strategy == SearchStrategy.HYBRID:
            results = self._search_hybrid(query, top_k * 2, use_contextual)
            
        elif strategy == SearchStrategy.HYBRID_RRF:
            results = self._search_hybrid_rrf(query, top_k * 2, use_contextual)
        
        # Sort by score and limit to top_k
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:top_k]
        
        return results
    
    def _search_bm25(self, query: str, top_k: int, use_contextual: bool) -> List[Dict[str, Any]]:
        """BM25 search"""
        if use_contextual and self.bm25_contextual:
            bm25 = self.bm25_contextual
        else:
            bm25 = self.bm25_original
        
        if not bm25:
            return []
        
        # Tokenize query
        query_tokens = query.lower().split()
        
        # Get BM25 scores
        scores = bm25.get_scores(query_tokens)
        
        # Get top k indices
        top_indices = np.argsort(scores)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            if idx < len(self.chunks) and scores[idx] > 0:
                chunk = self.chunks[idx]
                results.append({
                    "chunk_id": chunk.chunk_id,
                    "conversation_id": chunk.conversation_id,
                    "text": chunk.original_text[:500],
                    "context": chunk.context_description,
                    "score": float(scores[idx]),
                    "method": "bm25",
                    "metadata": chunk.metadata
                })
        
        return results
    
    def _search_embedding(self, query: str, top_k: int, use_contextual: bool) -> List[Dict[str, Any]]:
        """Embedding-based semantic search"""
        # Generate query embedding
        try:
            response = self.embedding_client.embeddings.create(
                model=self.embedding_model,
                input=query
            )
            query_embedding = np.array(response.data[0].embedding)
        except Exception as e:
            logger.error(f"Error generating query embedding: {e}")
            return []
        
        # Calculate cosine similarities
        similarities = []
        for chunk in self.chunks:
            if use_contextual and chunk.contextual_embedding is not None:
                embedding = chunk.contextual_embedding
            elif chunk.original_embedding is not None:
                embedding = chunk.original_embedding
            else:
                continue
            
            # Cosine similarity
            similarity = np.dot(query_embedding, embedding) / (
                np.linalg.norm(query_embedding) * np.linalg.norm(embedding)
            )
            similarities.append((chunk, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Get top k results
        results = []
        for chunk, score in similarities[:top_k]:
            results.append({
                "chunk_id": chunk.chunk_id,
                "conversation_id": chunk.conversation_id,
                "text": chunk.original_text[:500],
                "context": chunk.context_description,
                "score": float(score),
                "method": "embedding",
                "metadata": chunk.metadata
            })
        
        return results
    
    def _search_hybrid(self, query: str, top_k: int, use_contextual: bool) -> List[Dict[str, Any]]:
        """Hybrid search with weighted combination"""
        bm25_results = self._search_bm25(query, top_k, use_contextual)
        embedding_results = self._search_embedding(query, top_k, use_contextual)
        
        # Normalize scores
        bm25_max = max([r["score"] for r in bm25_results], default=1.0)
        embedding_max = max([r["score"] for r in embedding_results], default=1.0)
        
        # Combine results
        combined = defaultdict(lambda: {"score": 0, "sources": []})
        
        for result in bm25_results:
            chunk_id = result["chunk_id"]
            normalized_score = result["score"] / bm25_max if bm25_max > 0 else 0
            combined[chunk_id]["score"] += normalized_score * self.config.agent.bm25_weight
            combined[chunk_id]["sources"].append("bm25")
            combined[chunk_id].update(result)
        
        for result in embedding_results:
            chunk_id = result["chunk_id"]
            normalized_score = result["score"] / embedding_max if embedding_max > 0 else 0
            combined[chunk_id]["score"] += normalized_score * self.config.agent.embedding_weight
            if "bm25" not in combined[chunk_id].get("sources", []):
                combined[chunk_id]["sources"].append("embedding")
            if "text" not in combined[chunk_id]:
                combined[chunk_id].update(result)
        
        # Convert to list
        results = []
        for chunk_id, data in combined.items():
            data["chunk_id"] = chunk_id
            data["method"] = "hybrid"
            results.append(data)
        
        return results
    
    def _search_hybrid_rrf(self, query: str, top_k: int, use_contextual: bool) -> List[Dict[str, Any]]:
        """Hybrid search with Reciprocal Rank Fusion"""
        bm25_results = self._search_bm25(query, top_k, use_contextual)
        embedding_results = self._search_embedding(query, top_k, use_contextual)
        
        # Calculate RRF scores
        k = 60  # RRF constant
        rrf_scores = defaultdict(float)
        chunk_data = {}
        
        # Process BM25 results
        for rank, result in enumerate(bm25_results):
            chunk_id = result["chunk_id"]
            rrf_scores[chunk_id] += 1 / (k + rank + 1)
            chunk_data[chunk_id] = result
        
        # Process embedding results
        for rank, result in enumerate(embedding_results):
            chunk_id = result["chunk_id"]
            rrf_scores[chunk_id] += 1 / (k + rank + 1)
            if chunk_id not in chunk_data:
                chunk_data[chunk_id] = result
        
        # Create results
        results = []
        for chunk_id, rrf_score in rrf_scores.items():
            result = chunk_data[chunk_id].copy()
            result["score"] = rrf_score
            result["method"] = "hybrid_rrf"
            results.append(result)
        
        return results
    
    def compare_retrieval(self,
                         query: str,
                         top_k: int = 10,
                         show_details: bool = True) -> Dict[str, Any]:
        """
        Compare contextual vs non-contextual retrieval
        
        Args:
            query: Search query
            top_k: Number of results
            show_details: Show detailed comparison
            
        Returns:
            Comparison results
        """
        # Search with contextual
        contextual_results = self.search(
            query, top_k, use_contextual=True, 
            strategy=SearchStrategy.HYBRID_RRF
        )
        
        # Search without contextual
        non_contextual_results = self.search(
            query, top_k, use_contextual=False,
            strategy=SearchStrategy.HYBRID_RRF
        )
        
        # Calculate overlap
        contextual_ids = {r["chunk_id"] for r in contextual_results}
        non_contextual_ids = {r["chunk_id"] for r in non_contextual_results}
        overlap = contextual_ids & non_contextual_ids
        
        comparison = {
            "query": query,
            "contextual": contextual_results,
            "non_contextual": non_contextual_results,
            "overlap_count": len(overlap),
            "overlap_percentage": len(overlap) / top_k * 100 if top_k > 0 else 0,
            "unique_contextual": list(contextual_ids - non_contextual_ids),
            "unique_non_contextual": list(non_contextual_ids - contextual_ids)
        }
        
        if show_details:
            logger.info(f"\n{'='*60}")
            logger.info(f"Retrieval Comparison for: '{query}'")
            logger.info(f"{'='*60}")
            logger.info(f"Overlap: {len(overlap)}/{top_k} ({comparison['overlap_percentage']:.1f}%)")
            logger.info(f"Unique to contextual: {len(comparison['unique_contextual'])}")
            logger.info(f"Unique to non-contextual: {len(comparison['unique_non_contextual'])}")
            
            if contextual_results:
                logger.info("\nTop Contextual Result:")
                logger.info(f"  Score: {contextual_results[0]['score']:.3f}")
                if contextual_results[0].get('context'):
                    logger.info(f"  Context: {contextual_results[0]['context'][:200]}...")
            
            if non_contextual_results:
                logger.info("\nTop Non-Contextual Result:")
                logger.info(f"  Score: {non_contextual_results[0]['score']:.3f}")
                logger.info(f"  Text: {non_contextual_results[0]['text'][:200]}...")
        
        return comparison
    
    def _format_conversation(self, messages: List[Dict[str, str]]) -> str:
        """Format messages into conversation text"""
        lines = []
        for msg in messages:
            role = msg.get("role", "unknown")
            content = msg.get("content", "")
            lines.append(f"{role.upper()}: {content}")
        return "\n".join(lines)
    
    def _generate_chunk_id(self, conversation_id: str, index: int) -> str:
        """Generate unique chunk ID"""
        data = f"{self.user_id}_{conversation_id}_{index}"
        return hashlib.md5(data.encode()).hexdigest()[:12]
    
    def _save_index(self):
        """Save index to disk"""
        try:
            # Save chunks
            chunks_file = self.index_dir / "chunks.json"
            with open(chunks_file, "w") as f:
                chunks_data = [chunk.to_dict() for chunk in self.chunks]
                json.dump(chunks_data, f, indent=2)
            
            # Save embeddings
            if self.chunks:
                embeddings_file = self.index_dir / "embeddings.npz"
                original_embeddings = [c.original_embedding for c in self.chunks if c.original_embedding is not None]
                contextual_embeddings = [c.contextual_embedding for c in self.chunks if c.contextual_embedding is not None]
                
                if original_embeddings:
                    np.savez_compressed(
                        embeddings_file,
                        original=np.array(original_embeddings),
                        contextual=np.array(contextual_embeddings) if contextual_embeddings else np.array([])
                    )
            
            # Save BM25 corpus
            bm25_file = self.index_dir / "bm25_corpus.pkl"
            with open(bm25_file, "wb") as f:
                pickle.dump({
                    "original": self.tokenized_corpus_original,
                    "contextual": self.tokenized_corpus_contextual
                }, f)
            
            logger.info(f"Saved index for user {self.user_id}")
            
        except Exception as e:
            logger.error(f"Error saving index: {e}")
    
    def _load_index(self):
        """Load index from disk"""
        try:
            # Load chunks
            chunks_file = self.index_dir / "chunks.json"
            if chunks_file.exists():
                with open(chunks_file, "r") as f:
                    chunks_data = json.load(f)
                
                self.chunks = []
                for data in chunks_data:
                    chunk = ConversationChunk(
                        chunk_id=data["chunk_id"],
                        conversation_id=data["conversation_id"],
                        user_id=data["user_id"],
                        messages=data["messages"],
                        start_round=data["start_round"],
                        end_round=data["end_round"],
                        timestamp=data["timestamp"],
                        original_text=data["original_text"],
                        contextual_text=data.get("contextual_text"),
                        context_description=data.get("context_description"),
                        metadata=data.get("metadata", {})
                    )
                    self.chunks.append(chunk)
                    self.chunk_map[chunk.chunk_id] = chunk
                
                # Load embeddings
                embeddings_file = self.index_dir / "embeddings.npz"
                if embeddings_file.exists():
                    embeddings = np.load(embeddings_file)
                    original = embeddings["original"]
                    contextual = embeddings.get("contextual", [])
                    
                    for i, chunk in enumerate(self.chunks):
                        if i < len(original):
                            chunk.original_embedding = original[i]
                        if i < len(contextual):
                            chunk.contextual_embedding = contextual[i]
                
                # Load BM25 corpus
                bm25_file = self.index_dir / "bm25_corpus.pkl"
                if bm25_file.exists():
                    with open(bm25_file, "rb") as f:
                        corpus = pickle.load(f)
                        self.tokenized_corpus_original = corpus["original"]
                        self.tokenized_corpus_contextual = corpus.get("contextual", [])
                    
                    # Rebuild BM25 models
                    self._rebuild_bm25()
                
                logger.info(f"Loaded {len(self.chunks)} chunks for user {self.user_id}")
                
        except Exception as e:
            logger.error(f"Error loading index: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get index statistics"""
        return {
            "user_id": self.user_id,
            "total_chunks": len(self.chunks),
            "total_conversations": len(set(c.conversation_id for c in self.chunks)),
            "has_contextual": any(c.contextual_text for c in self.chunks),
            "avg_chunk_size": np.mean([len(c.messages) for c in self.chunks]) if self.chunks else 0,
            "index_size_mb": sum(
                f.stat().st_size for f in self.index_dir.glob("*") if f.is_file()
            ) / (1024 * 1024) if self.index_dir.exists() else 0
        }
