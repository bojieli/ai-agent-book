"""Conversation Chunker for User Memory RAG System

This module handles chunking of conversation histories into manageable segments
for indexing into the RAG database.
"""

import json
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
import hashlib

from config import ChunkingConfig, ChunkingStrategy


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationMessage:
    """Single message in a conversation"""
    role: str  # "user" or "assistant"
    content: str
    timestamp: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        return {k: v for k, v in asdict(self).items() if v is not None}


@dataclass
class ConversationChunk:
    """A chunk of conversation with metadata"""
    chunk_id: str
    conversation_id: str
    test_id: str
    chunk_index: int
    start_round: int
    end_round: int
    messages: List[ConversationMessage]
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_before: Optional[str] = None  # Summary of previous context
    context_after: Optional[str] = None   # Preview of next context
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "chunk_id": self.chunk_id,
            "conversation_id": self.conversation_id,
            "test_id": self.test_id,
            "chunk_index": self.chunk_index,
            "start_round": self.start_round,
            "end_round": self.end_round,
            "messages": [msg.to_dict() for msg in self.messages],
            "metadata": self.metadata,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "created_at": self.created_at
        }
    
    def to_text(self) -> str:
        """Convert chunk to text format for indexing"""
        lines = []
        
        # Add metadata header
        if self.metadata:
            lines.append(f"[Conversation Metadata]")
            for key, value in self.metadata.items():
                lines.append(f"  {key}: {value}")
            lines.append("")
        
        # Add context if available
        if self.context_before:
            lines.append(f"[Previous Context]\n{self.context_before}\n")
        
        # Add messages
        lines.append(f"[Conversation Rounds {self.start_round}-{self.end_round}]")
        for msg in self.messages:
            role_label = "Customer" if msg.role == "user" else "Representative"
            lines.append(f"{role_label}: {msg.content}")
        
        # Add next context preview if available
        if self.context_after:
            lines.append(f"\n[Next Context Preview]\n{self.context_after}")
        
        return "\n".join(lines)


class ConversationChunker:
    """Chunks conversation histories into segments for RAG indexing"""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """
        Initialize the chunker
        
        Args:
            config: Chunking configuration
        """
        self.config = config or ChunkingConfig()
        logger.info(f"Initialized chunker with strategy: {self.config.strategy}")
        logger.info(f"Rounds per chunk: {self.config.rounds_per_chunk}")
        logger.info(f"Overlap rounds: {self.config.overlap_rounds}")
    
    def chunk_conversation(self,
                          conversation_id: str,
                          test_id: str,
                          messages: List[Dict[str, Any]],
                          metadata: Optional[Dict[str, Any]] = None) -> List[ConversationChunk]:
        """
        Chunk a single conversation into segments
        
        Args:
            conversation_id: Unique conversation identifier
            test_id: Test case identifier
            messages: List of messages in the conversation
            metadata: Optional conversation metadata
            
        Returns:
            List of conversation chunks
        """
        # Convert to ConversationMessage objects
        conv_messages = []
        for msg in messages:
            conv_messages.append(ConversationMessage(
                role=msg.get('role', 'user'),
                content=msg.get('content', ''),
                timestamp=msg.get('timestamp')
            ))
        
        # Calculate rounds (1 round = 1 user message + 1 assistant response)
        rounds = []
        current_round = []
        
        for msg in conv_messages:
            current_round.append(msg)
            if msg.role == "assistant" and len(current_round) >= 2:
                rounds.append(current_round)
                current_round = []
        
        # Add remaining messages as incomplete round if any
        if current_round:
            rounds.append(current_round)
        
        total_rounds = len(rounds)
        logger.info(f"Processing conversation {conversation_id} with {total_rounds} rounds")
        
        # Choose chunking strategy
        if self.config.strategy == ChunkingStrategy.FIXED_ROUNDS:
            chunks = self._chunk_fixed_rounds(
                conversation_id, test_id, rounds, metadata
            )
        elif self.config.strategy == ChunkingStrategy.SEMANTIC:
            # For now, fallback to fixed rounds
            # Semantic chunking would require more sophisticated analysis
            chunks = self._chunk_fixed_rounds(
                conversation_id, test_id, rounds, metadata
            )
        else:
            chunks = self._chunk_fixed_rounds(
                conversation_id, test_id, rounds, metadata
            )
        
        logger.info(f"Created {len(chunks)} chunks for conversation {conversation_id}")
        return chunks
    
    def _chunk_fixed_rounds(self,
                           conversation_id: str,
                           test_id: str,
                           rounds: List[List[ConversationMessage]],
                           metadata: Optional[Dict[str, Any]] = None) -> List[ConversationChunk]:
        """
        Chunk conversation using fixed number of rounds
        
        Args:
            conversation_id: Conversation identifier
            test_id: Test case identifier
            rounds: List of conversation rounds
            metadata: Optional metadata
            
        Returns:
            List of chunks
        """
        chunks = []
        total_rounds = len(rounds)
        
        # Calculate chunk boundaries with overlap
        chunk_size = self.config.rounds_per_chunk
        overlap = self.config.overlap_rounds
        step = max(1, chunk_size - overlap)
        
        chunk_index = 0
        for start_idx in range(0, total_rounds, step):
            end_idx = min(start_idx + chunk_size, total_rounds)
            
            # Skip if chunk is too small (except for the last chunk)
            if end_idx - start_idx < self.config.min_chunk_size and end_idx < total_rounds:
                continue
            
            # Flatten rounds into messages
            chunk_messages = []
            for round_idx in range(start_idx, end_idx):
                chunk_messages.extend(rounds[round_idx])
            
            # Generate chunk ID
            chunk_content = f"{conversation_id}_{chunk_index}_{start_idx}_{end_idx}"
            chunk_id = hashlib.md5(chunk_content.encode()).hexdigest()[:12]
            
            # Create context summaries if enabled
            context_before = None
            context_after = None
            
            if self.config.include_metadata:
                # Add summary of previous context
                if start_idx > 0:
                    prev_rounds = min(3, start_idx)
                    context_msgs = []
                    for i in range(max(0, start_idx - prev_rounds), start_idx):
                        for msg in rounds[i]:
                            if msg.role == "user":
                                context_msgs.append(f"User asked: {msg.content[:100]}...")
                    if context_msgs:
                        context_before = "Previous discussion: " + " | ".join(context_msgs[-2:])
                
                # Add preview of next context
                if end_idx < total_rounds:
                    next_rounds = min(2, total_rounds - end_idx)
                    context_msgs = []
                    for i in range(end_idx, min(end_idx + next_rounds, total_rounds)):
                        for msg in rounds[i]:
                            if msg.role == "user":
                                context_msgs.append(f"Next: {msg.content[:100]}...")
                    if context_msgs:
                        context_after = " | ".join(context_msgs[:2])
            
            # Create chunk
            chunk = ConversationChunk(
                chunk_id=f"{test_id}_{conversation_id}_{chunk_id}",
                conversation_id=conversation_id,
                test_id=test_id,
                chunk_index=chunk_index,
                start_round=start_idx + 1,  # 1-indexed for display
                end_round=end_idx,  # Inclusive
                messages=chunk_messages,
                metadata=metadata or {},
                context_before=context_before,
                context_after=context_after
            )
            
            chunks.append(chunk)
            chunk_index += 1
            
            # Stop if we've reached the end
            if end_idx >= total_rounds:
                break
        
        return chunks
    
    def chunk_test_case_conversations(self,
                                     test_case: Dict[str, Any]) -> List[ConversationChunk]:
        """
        Chunk all conversations in a test case
        
        Args:
            test_case: Test case containing conversation histories
            
        Returns:
            List of all chunks from all conversations
        """
        all_chunks = []
        test_id = test_case.get('test_id', 'unknown')
        
        # Process each conversation history
        for conv_history in test_case.get('conversation_histories', []):
            conv_id = conv_history.get('conversation_id', '')
            messages = conv_history.get('messages', [])
            metadata = conv_history.get('metadata', {})
            
            # Add test case information to metadata
            metadata['test_id'] = test_id
            metadata['test_title'] = test_case.get('title', '')
            metadata['test_category'] = test_case.get('category', '')
            
            # Chunk the conversation
            chunks = self.chunk_conversation(
                conversation_id=conv_id,
                test_id=test_id,
                messages=messages,
                metadata=metadata
            )
            
            all_chunks.extend(chunks)
        
        logger.info(f"Chunked test case {test_id}: {len(all_chunks)} total chunks")
        return all_chunks
    
    def save_chunks(self, chunks: List[ConversationChunk], filepath: str):
        """
        Save chunks to a JSON file
        
        Args:
            chunks: List of conversation chunks
            filepath: Path to save the chunks
        """
        chunks_data = [chunk.to_dict() for chunk in chunks]
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(chunks_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(chunks)} chunks to {filepath}")
    
    def load_chunks(self, filepath: str) -> List[ConversationChunk]:
        """
        Load chunks from a JSON file
        
        Args:
            filepath: Path to the chunks file
            
        Returns:
            List of conversation chunks
        """
        with open(filepath, 'r', encoding='utf-8') as f:
            chunks_data = json.load(f)
        
        chunks = []
        for chunk_data in chunks_data:
            # Convert messages
            messages = []
            for msg_data in chunk_data.get('messages', []):
                messages.append(ConversationMessage(**msg_data))
            
            # Create chunk
            chunk = ConversationChunk(
                chunk_id=chunk_data['chunk_id'],
                conversation_id=chunk_data['conversation_id'],
                test_id=chunk_data['test_id'],
                chunk_index=chunk_data['chunk_index'],
                start_round=chunk_data['start_round'],
                end_round=chunk_data['end_round'],
                messages=messages,
                metadata=chunk_data.get('metadata', {}),
                context_before=chunk_data.get('context_before'),
                context_after=chunk_data.get('context_after'),
                created_at=chunk_data.get('created_at', '')
            )
            chunks.append(chunk)
        
        logger.info(f"Loaded {len(chunks)} chunks from {filepath}")
        return chunks
