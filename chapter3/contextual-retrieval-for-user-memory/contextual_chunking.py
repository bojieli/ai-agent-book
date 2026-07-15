"""Contextual Chunking for User Memory Conversations

This module implements Anthropic's Contextual Retrieval approach specifically
for conversation histories. Each conversation chunk gets contextualized with
information about its position and meaning within the full conversation.
"""

import json
import hashlib
import logging
import time
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from openai import OpenAI

from config import ChunkingConfig, LLMConfig
from chunker import ConversationChunk, ConversationMessage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class ContextualConversationChunk:
    """Enhanced conversation chunk with contextual information"""
    chunk_id: str
    conversation_id: str
    test_id: str
    chunk_index: int
    start_round: int
    end_round: int
    messages: List[ConversationMessage]
    original_text: str  # Original conversation text
    context: str  # Generated contextual description
    contextualized_text: str  # Context + original text
    context_tokens: int = 0  # Track token usage
    generation_time: float = 0.0  # Track generation time
    metadata: Dict[str, Any] = field(default_factory=dict)
    context_before: Optional[str] = None
    context_after: Optional[str] = None
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
            "original_text": self.original_text,
            "context": self.context,
            "contextualized_text": self.contextualized_text,
            "context_tokens": self.context_tokens,
            "generation_time": self.generation_time,
            "metadata": self.metadata,
            "context_before": self.context_before,
            "context_after": self.context_after,
            "created_at": self.created_at
        }
    
    @classmethod
    def from_basic_chunk(cls, chunk: ConversationChunk, context: str = "",
                        contextualized_text: str = "", context_tokens: int = 0,
                        generation_time: float = 0.0) -> 'ContextualConversationChunk':
        """Create from a basic ConversationChunk"""
        original_text = chunk.to_text()
        if not contextualized_text:
            contextualized_text = f"{context}\n\n{original_text}" if context else original_text
        
        return cls(
            chunk_id=chunk.chunk_id,
            conversation_id=chunk.conversation_id,
            test_id=chunk.test_id,
            chunk_index=chunk.chunk_index,
            start_round=chunk.start_round,
            end_round=chunk.end_round,
            messages=chunk.messages,
            original_text=original_text,
            context=context,
            contextualized_text=contextualized_text,
            context_tokens=context_tokens,
            generation_time=generation_time,
            metadata=chunk.metadata,
            context_before=chunk.context_before,
            context_after=chunk.context_after,
            created_at=chunk.created_at
        )


class ContextualConversationChunker:
    """
    Implements contextual chunking specifically for conversation histories.
    
    Key Educational Points:
    1. Conversation Context: Each chunk gets context about what was discussed before and after
    2. Topic Continuity: Context helps maintain topic understanding across chunk boundaries
    3. Temporal Information: Context includes temporal relationships between conversations
    4. Semantic Enrichment: Context adds semantic meaning to isolated conversation fragments
    """
    
    def __init__(self,
                 chunking_config: Optional[ChunkingConfig] = None,
                 llm_config: Optional[LLMConfig] = None,
                 use_contextual: bool = True):
        """
        Initialize the contextual conversation chunker.
        
        Args:
            chunking_config: Configuration for chunking parameters
            llm_config: LLM configuration for context generation
            use_contextual: Whether to generate contextual chunks (for comparison)
        """
        self.chunking_config = chunking_config or ChunkingConfig()
        self.llm_config = llm_config or LLMConfig()
        self.use_contextual = use_contextual
        
        # Initialize LLM client for context generation
        if self.use_contextual:
            self._init_llm_client()
        
        # Statistics tracking
        self.stats = {
            "total_chunks": 0,
            "contextual_chunks": 0,
            "total_context_tokens": 0,
            "total_generation_time": 0.0,
            "cache_hits": 0,
            "cache_misses": 0
        }
        
        # Context cache to avoid regenerating for similar chunks
        self.context_cache = {}
        
        logger.info(f"Initialized ContextualConversationChunker (contextual={use_contextual})")
    
    def _init_llm_client(self):
        """Initialize LLM client for context generation"""
        client_config, model = self.llm_config.get_client_config()
        base_url = client_config.pop("base_url", None)
        
        if base_url:
            self.client = OpenAI(base_url=base_url, **client_config)
        else:
            self.client = OpenAI(**client_config)
        
        self.model = model
        logger.info(f"Using {self.llm_config.provider} ({self.model}) for context generation")
    
    def contextualize_chunks(self,
                            chunks: List[ConversationChunk],
                            full_conversation_history: Optional[str] = None,
                            on_chunk_ready: Optional[callable] = None) -> List[ContextualConversationChunk]:
        """
        Add contextual information to conversation chunks.
        
        Args:
            chunks: List of basic conversation chunks
            full_conversation_history: Optional full conversation text for better context
            on_chunk_ready: Callback for when each chunk is ready
            
        Returns:
            List of contextualized conversation chunks
        """
        if not self.use_contextual:
            # Return non-contextual chunks for comparison
            return [
                ContextualConversationChunk.from_basic_chunk(chunk)
                for chunk in chunks
            ]
        
        contextual_chunks = []
        logger.info(f"Contextualizing {len(chunks)} conversation chunks")
        
        # Build full conversation if not provided
        if full_conversation_history is None:
            full_conversation_history = self._build_full_conversation(chunks)
        
        for i, chunk in enumerate(chunks):
            logger.info(f"Generating context for chunk {i+1}/{len(chunks)}")
            
            # Generate context for this chunk
            chunk_hash = hashlib.md5(chunk.to_text().encode()).hexdigest()
            
            if chunk_hash in self.context_cache:
                context = self.context_cache[chunk_hash]
                generation_time = 0.0
                context_tokens = 0
                self.stats["cache_hits"] += 1
                logger.debug(f"Cache hit for chunk {chunk.chunk_id}")
            else:
                # Generate new context using Anthropic's approach
                context, context_tokens, generation_time = self._generate_chunk_context(
                    chunk,
                    full_conversation_history,
                )
                
                # Cache the context
                self.context_cache[chunk_hash] = context
                self.stats["cache_misses"] += 1
                self.stats["total_context_tokens"] += context_tokens
                self.stats["total_generation_time"] += generation_time
            
            # Create contextual chunk
            contextual_chunk = ContextualConversationChunk.from_basic_chunk(
                chunk,
                context=context,
                context_tokens=context_tokens,
                generation_time=generation_time
            )
            
            contextual_chunks.append(contextual_chunk)
            
            # Log the full contextualized chunk
            logger.info(f"\n{'='*80}")
            logger.info(f"📝 CONTEXTUAL CHUNK {i}/{len(chunks)} CREATED")
            logger.info(f"{'='*80}")
            logger.info(f"Chunk ID: {contextual_chunk.chunk_id}")
            logger.info(f"Rounds: {contextual_chunk.start_round}-{contextual_chunk.end_round}")
            logger.info(f"Context Generated:\n{context}")
            logger.info(f"Original Text Preview (first 500 chars):\n{contextual_chunk.original_text[:500]}...")
            logger.info(f"Context Tokens: {context_tokens}")
            logger.info(f"Generation Time: {generation_time:.2f}s")
            logger.info(f"{'='*80}\n")
            
            # Call callback if provided
            if on_chunk_ready:
                try:
                    on_chunk_ready(contextual_chunk)
                except Exception as e:
                    logger.error(f"Error in on_chunk_ready callback: {e}")
            
            # Log progress
            if (i + 1) % 5 == 0:
                avg_time = self.stats["total_generation_time"] / (i + 1) if i > 0 else 0
                logger.info(f"Progress: {i+1}/{len(chunks)} chunks, avg time: {avg_time:.2f}s")
        
        # Update statistics
        self.stats["total_chunks"] += len(contextual_chunks)
        self.stats["contextual_chunks"] += len(contextual_chunks)
        
        logger.info(f"Contextualization complete. Statistics: {json.dumps(self.stats, indent=2)}")
        
        return contextual_chunks
    
    def _build_full_conversation(self, chunks: List[ConversationChunk]) -> str:
        """Build full conversation text from chunks"""
        all_messages = []
        for chunk in chunks:
            all_messages.extend([chunk.to_text()])
        return "\n\n---\n\n".join(all_messages)
    
    def _generate_chunk_context(self,
                               chunk: ConversationChunk,
                               full_conversation: str,
                               ) -> Tuple[str, int, float]:
        """
        Generate contextual description for a conversation chunk.
        
        This follows Anthropic's Contextual Retrieval approach adapted for conversations:
        1. Provide the full conversation history
        2. Show the specific chunk
        3. Ask for concise context about what's being discussed
        
        Returns:
            Tuple of (context, token_count, generation_time)
        """
        start_time = time.time()
        
        try:
            # Build context about surrounding conversation
            chunk_text = chunk.to_text()

            # Create prompt following Anthropic's template with conversation-specific adaptations
            prompt = f"""<full_conversation>
{full_conversation}
</full_conversation>

Here is a specific conversation chunk we want to situate within the whole conversation history:

<chunk>
Conversation rounds {chunk.start_round} to {chunk.end_round}:
{chunk_text}
</chunk>

Additional context:
- This is chunk {chunk.chunk_index + 1} from conversation {chunk.conversation_id}

Please provide a brief context (2-3 sentences) that describes:
1. What main topics or issues are being discussed in this chunk
2. Any key decisions, facts, or preferences mentioned
3. How this relates to the overall conversation flow

Write the context in a way that would help someone quickly understand what this conversation segment is about when searching through conversation history. Use the same language as the conversation."""

            # Generate context
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,  # Low temperature for consistency
                max_tokens=150  # Slightly more tokens for conversation context
            )
            
            context = response.choices[0].message.content.strip()
            
            # Estimate token count (rough approximation)
            token_count = len(prompt.split()) + len(context.split())
            generation_time = time.time() - start_time
            
            # Add structured prefix to context
            context_prefix = f"[Conversation {chunk.conversation_id}, Rounds {chunk.start_round}-{chunk.end_round}] "
            context = context_prefix + context
            
            logger.debug(f"Generated context in {generation_time:.2f}s: {context}")
            
            return context, token_count, generation_time
            
        except Exception as e:
            logger.error(f"Error generating chunk context: {e}")
            # Return a basic context on error
            basic_context = f"[Conversation chunk {chunk.chunk_index + 1}, Rounds {chunk.start_round}-{chunk.end_round}]"
            return basic_context, 0, time.time() - start_time
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get chunking statistics"""
        stats = self.stats.copy()
        
        # Calculate averages
        if stats["contextual_chunks"] > 0:
            stats["avg_context_tokens"] = stats["total_context_tokens"] / stats["contextual_chunks"]
            stats["avg_generation_time"] = stats["total_generation_time"] / stats["contextual_chunks"]
        else:
            stats["avg_context_tokens"] = 0
            stats["avg_generation_time"] = 0
        
        # Cache efficiency
        total_cache_ops = stats["cache_hits"] + stats["cache_misses"]
        if total_cache_ops > 0:
            stats["cache_hit_rate"] = stats["cache_hits"] / total_cache_ops
        else:
            stats["cache_hit_rate"] = 0
        
        # Cost estimation (rough)
        if self.llm_config.provider == "openai":
            cost_per_1k = 0.03
        else:
            cost_per_1k = 0.01
        
        stats["estimated_cost"] = (stats["total_context_tokens"] / 1000) * cost_per_1k
        
        return stats
