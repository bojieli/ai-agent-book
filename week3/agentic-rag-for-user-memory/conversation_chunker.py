"""
Conversation Chunking Module

Chunks conversation histories into segments of N rounds for RAG indexing.
A round is defined as a user message followed by an assistant response.
"""

import json
import hashlib
import logging
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, asdict

from config import ChunkingConfig


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class ConversationRound:
    """Represents a single conversation round"""
    round_number: int
    user_message: str
    assistant_message: str
    timestamp: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_text(self) -> str:
        """Convert round to text format for indexing"""
        return f"User: {self.user_message}\nAssistant: {self.assistant_message}"


@dataclass
class ConversationChunk:
    """Represents a chunk of conversation"""
    chunk_id: str
    conversation_id: str
    chunk_index: int
    rounds: List[ConversationRound]
    start_round: int
    end_round: int
    created_at: str
    metadata: Optional[Dict[str, Any]] = None
    
    def to_text(self) -> str:
        """Convert chunk to text for indexing"""
        text_parts = [f"Conversation {self.conversation_id}, Rounds {self.start_round}-{self.end_round}:\n"]
        for round in self.rounds:
            text_parts.append(round.to_text())
            text_parts.append("")  # Add empty line between rounds
        return "\n".join(text_parts)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            "chunk_id": self.chunk_id,
            "conversation_id": self.conversation_id,
            "chunk_index": self.chunk_index,
            "start_round": self.start_round,
            "end_round": self.end_round,
            "created_at": self.created_at,
            "text": self.to_text(),
            "rounds": [
                {
                    "round_number": r.round_number,
                    "user_message": r.user_message,
                    "assistant_message": r.assistant_message,
                    "timestamp": r.timestamp,
                    "metadata": r.metadata
                }
                for r in self.rounds
            ],
            "metadata": self.metadata
        }


class ConversationChunker:
    """Chunks conversation histories for RAG indexing"""
    
    def __init__(self, config: Optional[ChunkingConfig] = None):
        """Initialize the chunker"""
        self.config = config or ChunkingConfig()
        
    def chunk_conversation(self, 
                         conversation: Dict[str, Any],
                         conversation_id: Optional[str] = None) -> List[ConversationChunk]:
        """
        Chunk a single conversation into segments.
        
        Args:
            conversation: Conversation data with 'messages' list
            conversation_id: Optional conversation identifier
            
        Returns:
            List of conversation chunks
        """
        # Extract messages
        messages = conversation.get("messages", [])
        if not messages:
            logger.warning("No messages found in conversation")
            return []
        
        # Generate conversation ID if not provided
        if not conversation_id:
            conversation_id = self._generate_conversation_id(messages)
        
        # Extract rounds (user-assistant pairs)
        rounds = self._extract_rounds(messages)
        
        if not rounds:
            logger.warning(f"No valid rounds found in conversation {conversation_id}")
            return []
        
        # Create chunks
        chunks = self._create_chunks(rounds, conversation_id)
        
        logger.info(f"Created {len(chunks)} chunks from {len(rounds)} rounds for conversation {conversation_id}")
        return chunks
    
    def chunk_conversation_history(self,
                                 history_file: str) -> Tuple[List[ConversationChunk], Dict[str, Any]]:
        """
        Chunk conversation history from a file.
        
        Args:
            history_file: Path to conversation history JSON file
            
        Returns:
            Tuple of (chunks, metadata)
        """
        history_path = Path(history_file)
        if not history_path.exists():
            raise FileNotFoundError(f"History file not found: {history_file}")
        
        with open(history_path, 'r', encoding='utf-8') as f:
            history_data = json.load(f)
        
        all_chunks = []
        metadata = {
            "total_conversations": 0,
            "total_rounds": 0,
            "total_chunks": 0,
            "chunking_config": asdict(self.config)
        }
        
        # Handle different history formats
        if isinstance(history_data, list):
            # List of conversations
            conversations = history_data
        elif isinstance(history_data, dict):
            if "conversations" in history_data:
                conversations = history_data["conversations"]
            elif "messages" in history_data:
                # Single conversation
                conversations = [history_data]
            else:
                conversations = []
        else:
            conversations = []
        
        for idx, conversation in enumerate(conversations):
            conv_id = conversation.get("conversation_id", f"conv_{idx}")
            chunks = self.chunk_conversation(conversation, conv_id)
            all_chunks.extend(chunks)
            
            # Update metadata
            metadata["total_conversations"] += 1
            if chunks:
                metadata["total_rounds"] += chunks[-1].end_round
        
        metadata["total_chunks"] = len(all_chunks)
        
        logger.info(f"Processed {metadata['total_conversations']} conversations into {metadata['total_chunks']} chunks")
        return all_chunks, metadata
    
    def _extract_rounds(self, messages: List[Dict[str, Any]]) -> List[ConversationRound]:
        """Extract conversation rounds from messages"""
        rounds = []
        round_number = 0
        
        i = 0
        while i < len(messages):
            # Skip system messages if configured
            if not self.config.include_system_messages:
                while i < len(messages) and messages[i].get("role") == "system":
                    i += 1
            
            if i >= len(messages):
                break
            
            # Look for user-assistant pairs
            if messages[i].get("role") == "user":
                user_msg = messages[i].get("content", "")
                timestamp = messages[i].get("timestamp")
                metadata = messages[i].get("metadata")
                
                # Find corresponding assistant message
                assistant_msg = ""
                j = i + 1
                while j < len(messages) and messages[j].get("role") != "user":
                    if messages[j].get("role") == "assistant":
                        assistant_msg = messages[j].get("content", "")
                        break
                    j += 1
                
                if assistant_msg:
                    round_number += 1
                    rounds.append(ConversationRound(
                        round_number=round_number,
                        user_message=user_msg,
                        assistant_message=assistant_msg,
                        timestamp=timestamp,
                        metadata=metadata
                    ))
                    i = j + 1
                else:
                    # No assistant response found
                    i += 1
            else:
                i += 1
        
        return rounds
    
    def _create_chunks(self, 
                      rounds: List[ConversationRound],
                      conversation_id: str) -> List[ConversationChunk]:
        """Create chunks from rounds"""
        chunks = []
        rounds_per_chunk = self.config.rounds_per_chunk
        overlap = self.config.overlap_rounds
        
        # Calculate chunk boundaries
        i = 0
        chunk_index = 0
        
        while i < len(rounds):
            # Determine chunk size
            chunk_size = min(rounds_per_chunk, len(rounds) - i)
            
            # Skip if chunk is too small (unless it's the last chunk)
            if chunk_size < self.config.min_rounds_per_chunk and i + chunk_size < len(rounds):
                # Merge with next chunk
                chunk_size = min(rounds_per_chunk + chunk_size, len(rounds) - i)
            
            # Extract rounds for this chunk
            chunk_rounds = rounds[i:i + chunk_size]
            
            # Add overlap from previous chunk if configured and not first chunk
            if overlap > 0 and i > 0 and self.config.preserve_context:
                overlap_start = max(0, i - overlap)
                overlap_rounds = rounds[overlap_start:i]
                chunk_rounds = overlap_rounds + chunk_rounds
                start_round = overlap_rounds[0].round_number
            else:
                start_round = chunk_rounds[0].round_number
            
            end_round = chunk_rounds[-1].round_number
            
            # Generate chunk ID
            chunk_id = self._generate_chunk_id(conversation_id, chunk_index, start_round, end_round)
            
            # Create chunk
            chunk = ConversationChunk(
                chunk_id=chunk_id,
                conversation_id=conversation_id,
                chunk_index=chunk_index,
                rounds=chunk_rounds,
                start_round=start_round,
                end_round=end_round,
                created_at=datetime.now().isoformat(),
                metadata={
                    "total_rounds": len(chunk_rounds),
                    "has_overlap": i > 0 and overlap > 0,
                    "overlap_size": min(overlap, i) if i > 0 else 0
                }
            )
            
            chunks.append(chunk)
            
            # Move to next chunk (accounting for overlap)
            i += chunk_size
            chunk_index += 1
        
        return chunks
    
    def _generate_conversation_id(self, messages: List[Dict[str, Any]]) -> str:
        """Generate a unique conversation ID"""
        content = json.dumps(messages[:3], sort_keys=True)  # Use first 3 messages
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _generate_chunk_id(self, conversation_id: str, chunk_index: int, 
                          start_round: int, end_round: int) -> str:
        """Generate a unique chunk ID"""
        id_string = f"{conversation_id}_chunk_{chunk_index}_r{start_round}-{end_round}"
        return hashlib.md5(id_string.encode()).hexdigest()[:16]
    
    def save_chunks(self, chunks: List[ConversationChunk], output_file: str):
        """Save chunks to a JSON file"""
        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        data = {
            "chunks": [chunk.to_dict() for chunk in chunks],
            "metadata": {
                "total_chunks": len(chunks),
                "created_at": datetime.now().isoformat(),
                "config": asdict(self.config)
            }
        }
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Saved {len(chunks)} chunks to {output_file}")
    
    def load_chunks(self, chunks_file: str) -> List[ConversationChunk]:
        """Load chunks from a JSON file"""
        with open(chunks_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        chunks = []
        for chunk_data in data.get("chunks", []):
            # Reconstruct rounds
            rounds = []
            for round_data in chunk_data.get("rounds", []):
                rounds.append(ConversationRound(
                    round_number=round_data["round_number"],
                    user_message=round_data["user_message"],
                    assistant_message=round_data["assistant_message"],
                    timestamp=round_data.get("timestamp"),
                    metadata=round_data.get("metadata")
                ))
            
            # Reconstruct chunk
            chunk = ConversationChunk(
                chunk_id=chunk_data["chunk_id"],
                conversation_id=chunk_data["conversation_id"],
                chunk_index=chunk_data["chunk_index"],
                rounds=rounds,
                start_round=chunk_data["start_round"],
                end_round=chunk_data["end_round"],
                created_at=chunk_data["created_at"],
                metadata=chunk_data.get("metadata")
            )
            chunks.append(chunk)
        
        logger.info(f"Loaded {len(chunks)} chunks from {chunks_file}")
        return chunks
