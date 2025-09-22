"""
Memory Integration Module

Integrates the user-memory system from week2 with the RAG system.
Provides unified interface for memory operations with RAG-enhanced retrieval.
"""

import json
import logging
import sys
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from datetime import datetime
from dataclasses import dataclass, asdict

# Add week2 user-memory to path
sys.path.append(str(Path(__file__).parent.parent.parent / "week2" / "user-memory"))

try:
    from memory_manager import MemoryManager, MemoryNote, MemoryCard
    from config import MemoryMode
except ImportError:
    # Fallback implementations if import fails
    logging.warning("Could not import from week2/user-memory, using local definitions")
    
    from enum import Enum
    
    class MemoryMode(str, Enum):
        SIMPLE_NOTES = "simple_notes"
        ENHANCED_NOTES = "enhanced_notes"
        JSON_CARDS = "json_cards"
        ADVANCED_JSON_CARDS = "advanced_json_cards"
    
    @dataclass
    class MemoryNote:
        note_id: str
        content: str
        session_id: str
        created_at: str
        updated_at: str
        tags: List[str] = None
    
    @dataclass
    class MemoryCard:
        category: str
        subcategory: str
        key: str
        value: Any
        session_id: str
        created_at: str
        updated_at: str


from config import MemoryConfig, RAGConfig
from rag_indexer import RAGIndexerFactory, SearchResult


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass 
class MemorySearchResult:
    """Enhanced memory search result with RAG context"""
    memory_type: str  # "note" or "card"
    memory_id: str
    content: str
    relevance_score: float
    conversation_context: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class MemoryRAGIntegration:
    """Integrates user memory with RAG for enhanced retrieval"""
    
    def __init__(self, 
                 memory_config: Optional[MemoryConfig] = None,
                 rag_config: Optional[RAGConfig] = None):
        """Initialize memory-RAG integration"""
        self.memory_config = memory_config or MemoryConfig()
        self.rag_config = rag_config or RAGConfig()
        
        # Initialize RAG indexer
        self.rag_indexer = RAGIndexerFactory.create(self.rag_config)
        
        # Initialize memory manager
        self._init_memory_manager()
        
        # Memory cache for quick access
        self.memory_cache = {}
        self._load_memory_cache()
    
    def _init_memory_manager(self):
        """Initialize the memory manager"""
        try:
            # Try to use the actual MemoryManager from week2
            self.memory_manager = MemoryManager(
                mode=self.memory_config.mode,
                storage_dir=self.memory_config.memory_dir
            )
            logger.info("Initialized MemoryManager from week2/user-memory")
        except:
            # Fallback to simple local storage
            self.memory_manager = None
            logger.warning("Using fallback memory storage")
    
    def _load_memory_cache(self):
        """Load existing memories into cache"""
        memory_file = Path(self.memory_config.memory_dir) / "memories.json"
        if memory_file.exists():
            with open(memory_file, 'r', encoding='utf-8') as f:
                self.memory_cache = json.load(f)
                logger.info(f"Loaded {len(self.memory_cache)} memories from cache")
    
    def _save_memory_cache(self):
        """Save memory cache to disk"""
        memory_file = Path(self.memory_config.memory_dir) / "memories.json"
        memory_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(memory_file, 'w', encoding='utf-8') as f:
            json.dump(self.memory_cache, f, ensure_ascii=False, indent=2)
    
    def add_memory_from_conversation(self, 
                                    conversation: Dict[str, Any],
                                    memory_type: str = "auto") -> List[str]:
        """
        Extract and add memories from a conversation.
        
        Args:
            conversation: Conversation data
            memory_type: Type of memory to create (auto, note, card)
            
        Returns:
            List of created memory IDs
        """
        memories_created = []
        
        # Extract key information from conversation
        extracted_info = self._extract_key_information(conversation)
        
        for info in extracted_info:
            if memory_type == "auto":
                # Automatically determine memory type based on content
                if self._should_use_card(info):
                    memory_id = self._create_memory_card(info)
                else:
                    memory_id = self._create_memory_note(info)
            elif memory_type == "note":
                memory_id = self._create_memory_note(info)
            else:  # card
                memory_id = self._create_memory_card(info)
            
            if memory_id:
                memories_created.append(memory_id)
        
        # Save cache
        self._save_memory_cache()
        
        logger.info(f"Created {len(memories_created)} memories from conversation")
        return memories_created
    
    def search_memories_with_context(self, 
                                    query: str,
                                    include_conversation_context: bool = True,
                                    top_k: int = 5) -> List[MemorySearchResult]:
        """
        Search memories with RAG-enhanced context.
        
        Args:
            query: Search query
            include_conversation_context: Whether to include conversation context
            top_k: Number of results to return
            
        Returns:
            List of memory search results
        """
        results = []
        
        # Search in memory cache
        memory_results = self._search_memory_cache(query, top_k)
        
        # Search in RAG index for conversation context
        conversation_results = []
        if include_conversation_context:
            conversation_results = self.rag_indexer.search(query, top_k)
        
        # Combine and rank results
        for mem_id, memory_data, score in memory_results:
            # Find related conversation context
            context = []
            if conversation_results:
                # Find conversations that mention similar topics
                for conv_result in conversation_results:
                    if self._is_related_context(memory_data, conv_result):
                        context.append({
                            "conversation_id": conv_result.conversation_id,
                            "rounds": f"{conv_result.start_round}-{conv_result.end_round}",
                            "relevance": conv_result.score,
                            "text_preview": conv_result.text[:200] + "..."
                        })
            
            result = MemorySearchResult(
                memory_type=memory_data.get("type", "note"),
                memory_id=mem_id,
                content=memory_data.get("content", ""),
                relevance_score=score,
                conversation_context=context[:3] if context else None,
                metadata=memory_data.get("metadata")
            )
            results.append(result)
        
        # Sort by relevance score
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        
        return results[:top_k]
    
    def update_memory_from_query(self,
                                query_result: MemorySearchResult,
                                update_content: str) -> bool:
        """
        Update a memory based on search result.
        
        Args:
            query_result: Memory search result
            update_content: New content for the memory
            
        Returns:
            True if update successful
        """
        memory_id = query_result.memory_id
        
        if memory_id in self.memory_cache:
            # Update memory
            self.memory_cache[memory_id]["content"] = update_content
            self.memory_cache[memory_id]["updated_at"] = datetime.now().isoformat()
            
            # Add update history
            if "history" not in self.memory_cache[memory_id]:
                self.memory_cache[memory_id]["history"] = []
            
            self.memory_cache[memory_id]["history"].append({
                "timestamp": datetime.now().isoformat(),
                "previous_content": query_result.content,
                "action": "update"
            })
            
            # Save cache
            self._save_memory_cache()
            
            logger.info(f"Updated memory {memory_id}")
            return True
        
        return False
    
    def consolidate_memories(self, similarity_threshold: float = 0.8) -> Dict[str, Any]:
        """
        Consolidate similar memories to reduce redundancy.
        
        Args:
            similarity_threshold: Threshold for considering memories similar
            
        Returns:
            Consolidation report
        """
        consolidated_count = 0
        groups = []
        
        # Group similar memories
        memory_embeddings = {}
        for mem_id, memory_data in self.memory_cache.items():
            content = memory_data.get("content", "")
            embedding = self.rag_indexer.get_embedding(content)
            memory_embeddings[mem_id] = embedding
        
        # Find similar memories
        processed = set()
        for mem_id1, emb1 in memory_embeddings.items():
            if mem_id1 in processed:
                continue
            
            similar_group = [mem_id1]
            for mem_id2, emb2 in memory_embeddings.items():
                if mem_id2 != mem_id1 and mem_id2 not in processed:
                    similarity = self.rag_indexer.cosine_similarity(emb1, emb2)
                    if similarity >= similarity_threshold:
                        similar_group.append(mem_id2)
                        processed.add(mem_id2)
            
            if len(similar_group) > 1:
                groups.append(similar_group)
                # Merge memories in group
                self._merge_memory_group(similar_group)
                consolidated_count += len(similar_group) - 1
            
            processed.add(mem_id1)
        
        # Save updated cache
        self._save_memory_cache()
        
        report = {
            "consolidated_count": consolidated_count,
            "groups_found": len(groups),
            "total_memories": len(self.memory_cache),
            "consolidation_details": [
                {"group_size": len(group), "memory_ids": group}
                for group in groups
            ]
        }
        
        logger.info(f"Consolidated {consolidated_count} memories into {len(groups)} groups")
        return report
    
    def _extract_key_information(self, conversation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract key information from conversation for memory creation"""
        extracted = []
        messages = conversation.get("messages", [])
        
        # Simple extraction logic - can be enhanced with NLP
        key_phrases = ["remember", "important", "note that", "don't forget", 
                      "keep in mind", "preference", "always", "never"]
        
        for i, msg in enumerate(messages):
            if msg.get("role") == "user":
                content = msg.get("content", "").lower()
                
                # Check for key phrases
                for phrase in key_phrases:
                    if phrase in content:
                        # Look for assistant's response
                        if i + 1 < len(messages) and messages[i + 1].get("role") == "assistant":
                            extracted.append({
                                "user_request": msg.get("content"),
                                "assistant_response": messages[i + 1].get("content"),
                                "timestamp": msg.get("timestamp", datetime.now().isoformat()),
                                "type": "extracted"
                            })
                        break
        
        return extracted
    
    def _should_use_card(self, info: Dict[str, Any]) -> bool:
        """Determine if information should be stored as a card"""
        # Simple heuristic - can be enhanced
        content = info.get("user_request", "").lower()
        
        # Check for structured information patterns
        structured_patterns = ["email", "phone", "address", "name", "preference",
                              "setting", "configuration", "account", "id"]
        
        for pattern in structured_patterns:
            if pattern in content:
                return True
        
        return False
    
    def _create_memory_note(self, info: Dict[str, Any]) -> str:
        """Create a memory note"""
        import uuid
        
        note_id = str(uuid.uuid4())[:8]
        memory = {
            "type": "note",
            "content": f"{info.get('user_request', '')} - {info.get('assistant_response', '')}",
            "created_at": info.get("timestamp", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "source": "conversation",
                "extraction_type": info.get("type", "manual")
            }
        }
        
        self.memory_cache[note_id] = memory
        return note_id
    
    def _create_memory_card(self, info: Dict[str, Any]) -> str:
        """Create a memory card"""
        import uuid
        
        card_id = str(uuid.uuid4())[:8]
        
        # Parse content to extract structure
        content = info.get("user_request", "")
        
        # Simple parsing - can be enhanced
        memory = {
            "type": "card",
            "category": "user_info",
            "subcategory": "preference",
            "key": "extracted_info",
            "value": info.get("assistant_response", ""),
            "content": content,
            "created_at": info.get("timestamp", datetime.now().isoformat()),
            "updated_at": datetime.now().isoformat(),
            "metadata": {
                "source": "conversation",
                "extraction_type": info.get("type", "manual")
            }
        }
        
        self.memory_cache[card_id] = memory
        return card_id
    
    def _search_memory_cache(self, query: str, top_k: int) -> List[Tuple[str, Dict, float]]:
        """Search in memory cache"""
        results = []
        
        # Get query embedding
        query_embedding = self.rag_indexer.get_embedding(query)
        
        for mem_id, memory_data in self.memory_cache.items():
            content = memory_data.get("content", "")
            if not content:
                # For cards, combine key-value
                content = f"{memory_data.get('key', '')} {memory_data.get('value', '')}"
            
            # Get memory embedding
            memory_embedding = self.rag_indexer.get_embedding(content)
            
            # Calculate similarity
            similarity = self.rag_indexer.cosine_similarity(query_embedding, memory_embedding)
            
            results.append((mem_id, memory_data, similarity))
        
        # Sort by similarity
        results.sort(key=lambda x: x[2], reverse=True)
        
        return results[:top_k]
    
    def _is_related_context(self, memory_data: Dict, conv_result: SearchResult) -> bool:
        """Check if conversation result is related to memory"""
        # Simple keyword matching - can be enhanced
        memory_content = memory_data.get("content", "").lower()
        conv_text = conv_result.text.lower()
        
        # Extract keywords from memory
        import re
        words = re.findall(r'\w+', memory_content)
        important_words = [w for w in words if len(w) > 4]  # Filter short words
        
        # Check overlap
        overlap_count = sum(1 for word in important_words if word in conv_text)
        
        return overlap_count >= min(3, len(important_words) // 2)
    
    def _merge_memory_group(self, memory_ids: List[str]):
        """Merge a group of similar memories"""
        if len(memory_ids) < 2:
            return
        
        # Keep the most recent memory as primary
        memories = [(mid, self.memory_cache[mid]) for mid in memory_ids if mid in self.memory_cache]
        memories.sort(key=lambda x: x[1].get("updated_at", ""), reverse=True)
        
        if not memories:
            return
        
        primary_id, primary_memory = memories[0]
        
        # Merge content from other memories
        merged_content = [primary_memory.get("content", "")]
        for mid, memory in memories[1:]:
            content = memory.get("content", "")
            if content and content not in merged_content:
                merged_content.append(content)
        
        # Update primary memory
        primary_memory["content"] = " | ".join(merged_content)
        primary_memory["updated_at"] = datetime.now().isoformat()
        primary_memory["merged_from"] = memory_ids[1:]
        
        # Remove merged memories
        for mid in memory_ids[1:]:
            if mid in self.memory_cache:
                del self.memory_cache[mid]
