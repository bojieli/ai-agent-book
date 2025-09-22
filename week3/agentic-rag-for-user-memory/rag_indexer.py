"""
RAG Indexing and Retrieval System

Indexes conversation chunks and provides retrieval capabilities.
Supports multiple backend implementations: Local, Chroma, FAISS.
"""

import json
import logging
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass
import hashlib

from openai import OpenAI

from config import RAGConfig, KnowledgeBaseType, LLMConfig
from conversation_chunker import ConversationChunk


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SearchResult:
    """Represents a search result from RAG retrieval"""
    chunk_id: str
    conversation_id: str
    text: str
    score: float
    start_round: int
    end_round: int
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "conversation_id": self.conversation_id,
            "text": self.text,
            "score": self.score,
            "start_round": self.start_round,
            "end_round": self.end_round,
            "metadata": self.metadata
        }


class BaseRAGIndexer:
    """Base class for RAG indexers"""
    
    def __init__(self, config: RAGConfig, llm_config: Optional[LLMConfig] = None):
        """Initialize the indexer"""
        self.config = config
        self.llm_config = llm_config or LLMConfig()
        
        # Initialize OpenAI client for embeddings
        self.openai_client = OpenAI(
            api_key=self.llm_config.api_key or os.getenv("OPENAI_API_KEY")
        )
        
        # Ensure index directory exists
        Path(self.config.index_path).mkdir(parents=True, exist_ok=True)
    
    def index_chunks(self, chunks: List[ConversationChunk]) -> Dict[str, Any]:
        """Index conversation chunks"""
        raise NotImplementedError
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Search for relevant chunks"""
        raise NotImplementedError
    
    def get_embedding(self, text: str) -> List[float]:
        """Get embedding for text using OpenAI"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.config.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error getting embedding: {e}")
            return [0.0] * self.config.embedding_dim
    
    def get_embeddings_batch(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings for multiple texts"""
        try:
            response = self.openai_client.embeddings.create(
                model=self.config.embedding_model,
                input=texts
            )
            return [item.embedding for item in response.data]
        except Exception as e:
            logger.error(f"Error getting batch embeddings: {e}")
            return [[0.0] * self.config.embedding_dim] * len(texts)
    
    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        vec1 = np.array(vec1)
        vec2 = np.array(vec2)
        
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return float(dot_product / (norm1 * norm2))


class LocalRAGIndexer(BaseRAGIndexer):
    """Local file-based RAG indexer"""
    
    def __init__(self, config: RAGConfig, llm_config: Optional[LLMConfig] = None):
        """Initialize local indexer"""
        super().__init__(config, llm_config)
        self.index_file = Path(self.config.index_path) / "local_index.json"
        self.embeddings_file = Path(self.config.index_path) / "embeddings.json"
        self.chunks_store = {}
        self.embeddings_store = {}
        self._load_index()
    
    def _load_index(self):
        """Load existing index if available"""
        if self.index_file.exists():
            with open(self.index_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.chunks_store = data.get("chunks", {})
                logger.info(f"Loaded {len(self.chunks_store)} chunks from index")
        
        if self.embeddings_file.exists():
            with open(self.embeddings_file, 'r', encoding='utf-8') as f:
                self.embeddings_store = json.load(f)
                logger.info(f"Loaded {len(self.embeddings_store)} embeddings")
    
    def _save_index(self):
        """Save index to disk"""
        # Save chunks
        with open(self.index_file, 'w', encoding='utf-8') as f:
            json.dump({
                "chunks": self.chunks_store,
                "metadata": {
                    "updated_at": datetime.now().isoformat(),
                    "total_chunks": len(self.chunks_store)
                }
            }, f, ensure_ascii=False, indent=2)
        
        # Save embeddings
        with open(self.embeddings_file, 'w', encoding='utf-8') as f:
            json.dump(self.embeddings_store, f)
        
        logger.info(f"Saved {len(self.chunks_store)} chunks to index")
    
    def index_chunks(self, chunks: List[ConversationChunk]) -> Dict[str, Any]:
        """Index conversation chunks"""
        indexed_count = 0
        skipped_count = 0
        errors = []
        
        # Prepare texts for batch embedding
        texts_to_embed = []
        chunk_ids_to_embed = []
        
        for chunk in chunks:
            chunk_id = chunk.chunk_id
            
            # Skip if already indexed
            if chunk_id in self.chunks_store:
                skipped_count += 1
                continue
            
            # Store chunk data
            self.chunks_store[chunk_id] = {
                "chunk_id": chunk_id,
                "conversation_id": chunk.conversation_id,
                "text": chunk.to_text(),
                "start_round": chunk.start_round,
                "end_round": chunk.end_round,
                "created_at": chunk.created_at,
                "metadata": chunk.metadata
            }
            
            texts_to_embed.append(chunk.to_text())
            chunk_ids_to_embed.append(chunk_id)
        
        # Get embeddings in batch
        if texts_to_embed:
            embeddings = self.get_embeddings_batch(texts_to_embed)
            for chunk_id, embedding in zip(chunk_ids_to_embed, embeddings):
                self.embeddings_store[chunk_id] = embedding
                indexed_count += 1
        
        # Save index
        self._save_index()
        
        result = {
            "indexed": indexed_count,
            "skipped": skipped_count,
            "total": len(chunks),
            "errors": errors
        }
        
        logger.info(f"Indexing complete: {indexed_count} indexed, {skipped_count} skipped")
        return result
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Search for relevant chunks"""
        if not self.chunks_store:
            logger.warning("No chunks in index")
            return []
        
        top_k = top_k or self.config.top_k
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Calculate similarities
        similarities = []
        for chunk_id, chunk_data in self.chunks_store.items():
            if chunk_id not in self.embeddings_store:
                continue
            
            chunk_embedding = self.embeddings_store[chunk_id]
            similarity = self.cosine_similarity(query_embedding, chunk_embedding)
            
            if similarity >= self.config.similarity_threshold:
                similarities.append((chunk_id, similarity, chunk_data))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for chunk_id, score, chunk_data in similarities[:top_k]:
            result = SearchResult(
                chunk_id=chunk_id,
                conversation_id=chunk_data["conversation_id"],
                text=chunk_data["text"],
                score=score,
                start_round=chunk_data["start_round"],
                end_round=chunk_data["end_round"],
                metadata=chunk_data.get("metadata")
            )
            results.append(result)
        
        logger.info(f"Found {len(results)} results for query: {query[:50]}...")
        return results
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """Delete a chunk from the index"""
        if chunk_id in self.chunks_store:
            del self.chunks_store[chunk_id]
            if chunk_id in self.embeddings_store:
                del self.embeddings_store[chunk_id]
            self._save_index()
            return True
        return False
    
    def clear_index(self):
        """Clear the entire index"""
        self.chunks_store = {}
        self.embeddings_store = {}
        self._save_index()
        logger.info("Index cleared")


class ChromaRAGIndexer(BaseRAGIndexer):
    """Chroma vector database indexer"""
    
    def __init__(self, config: RAGConfig, llm_config: Optional[LLMConfig] = None):
        """Initialize Chroma indexer"""
        super().__init__(config, llm_config)
        
        try:
            import chromadb
            from chromadb.config import Settings
            
            # Initialize Chroma client
            self.chroma_client = chromadb.PersistentClient(
                path=self.config.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            
            # Get or create collection
            self.collection = self.chroma_client.get_or_create_collection(
                name=self.config.collection_name,
                metadata={"description": "User conversation chunks for RAG"}
            )
            
            logger.info(f"Initialized Chroma collection: {self.config.collection_name}")
            
        except ImportError:
            raise ImportError("Chroma is not installed. Install with: pip install chromadb")
    
    def index_chunks(self, chunks: List[ConversationChunk]) -> Dict[str, Any]:
        """Index conversation chunks in Chroma"""
        indexed_count = 0
        skipped_count = 0
        errors = []
        
        documents = []
        embeddings = []
        ids = []
        metadatas = []
        
        # Get existing IDs to avoid duplicates
        try:
            existing_ids = set(self.collection.get()["ids"])
        except:
            existing_ids = set()
        
        for chunk in chunks:
            chunk_id = chunk.chunk_id
            
            # Skip if already indexed
            if chunk_id in existing_ids:
                skipped_count += 1
                continue
            
            # Prepare data for Chroma
            documents.append(chunk.to_text())
            ids.append(chunk_id)
            metadatas.append({
                "conversation_id": chunk.conversation_id,
                "start_round": chunk.start_round,
                "end_round": chunk.end_round,
                "created_at": chunk.created_at,
                "chunk_metadata": json.dumps(chunk.metadata) if chunk.metadata else "{}"
            })
        
        # Get embeddings and add to collection
        if documents:
            embeddings = self.get_embeddings_batch(documents)
            
            self.collection.add(
                documents=documents,
                embeddings=embeddings,
                ids=ids,
                metadatas=metadatas
            )
            indexed_count = len(documents)
        
        result = {
            "indexed": indexed_count,
            "skipped": skipped_count,
            "total": len(chunks),
            "errors": errors
        }
        
        logger.info(f"Indexed {indexed_count} chunks to Chroma")
        return result
    
    def search(self, query: str, top_k: Optional[int] = None) -> List[SearchResult]:
        """Search for relevant chunks in Chroma"""
        top_k = top_k or self.config.top_k
        
        # Get query embedding
        query_embedding = self.get_embedding(query)
        
        # Search in Chroma
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=top_k
        )
        
        search_results = []
        if results and results["ids"]:
            for i, chunk_id in enumerate(results["ids"][0]):
                metadata = results["metadatas"][0][i]
                
                result = SearchResult(
                    chunk_id=chunk_id,
                    conversation_id=metadata["conversation_id"],
                    text=results["documents"][0][i],
                    score=1.0 - results["distances"][0][i],  # Convert distance to similarity
                    start_round=metadata["start_round"],
                    end_round=metadata["end_round"],
                    metadata=json.loads(metadata.get("chunk_metadata", "{}"))
                )
                
                if result.score >= self.config.similarity_threshold:
                    search_results.append(result)
        
        logger.info(f"Found {len(search_results)} results in Chroma")
        return search_results
    
    def clear_index(self):
        """Clear the Chroma collection"""
        self.chroma_client.delete_collection(self.config.collection_name)
        self.collection = self.chroma_client.create_collection(
            name=self.config.collection_name,
            metadata={"description": "User conversation chunks for RAG"}
        )
        logger.info("Chroma collection cleared")


class RAGIndexerFactory:
    """Factory for creating RAG indexers"""
    
    @staticmethod
    def create(config: RAGConfig, llm_config: Optional[LLMConfig] = None) -> BaseRAGIndexer:
        """Create a RAG indexer based on configuration"""
        if config.kb_type == KnowledgeBaseType.LOCAL:
            return LocalRAGIndexer(config, llm_config)
        elif config.kb_type == KnowledgeBaseType.CHROMA:
            return ChromaRAGIndexer(config, llm_config)
        elif config.kb_type == KnowledgeBaseType.FAISS:
            # FAISS implementation would go here
            raise NotImplementedError("FAISS indexer not yet implemented")
        else:
            raise ValueError(f"Unknown knowledge base type: {config.kb_type}")


import os  # Add this import at the top with other imports
