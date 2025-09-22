"""
Configuration module for Agentic RAG with User Memory
"""

import os
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path


class KnowledgeBaseType(str, Enum):
    """Knowledge base backend types"""
    LOCAL = "local"
    CHROMA = "chroma"
    FAISS = "faiss"


class MemoryMode(str, Enum):
    """Memory storage and retrieval modes"""
    SIMPLE_NOTES = "simple_notes"
    ENHANCED_NOTES = "enhanced_notes"
    JSON_CARDS = "json_cards"
    ADVANCED_JSON_CARDS = "advanced_json_cards"


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "openai"  # openai, kimi, doubao, moonshot
    model: str = "gpt-4o-mini"
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4000
    timeout: int = 60
    
    def __post_init__(self):
        """Load API keys from environment"""
        if not self.api_key:
            if self.provider == "openai":
                self.api_key = os.getenv("OPENAI_API_KEY")
                self.base_url = self.base_url or "https://api.openai.com/v1"
            elif self.provider in ["kimi", "moonshot"]:
                self.api_key = os.getenv("MOONSHOT_API_KEY")
                self.base_url = self.base_url or "https://api.moonshot.cn/v1"
                self.model = "moonshot-v1-8k"
            elif self.provider == "doubao":
                self.api_key = os.getenv("ARK_API_KEY")
                self.base_url = self.base_url or "https://ark.cn-beijing.volcanicengineapi.com/api/v3"
                

@dataclass
class ChunkingConfig:
    """Configuration for conversation chunking"""
    rounds_per_chunk: int = 20  # Number of conversation rounds per chunk
    min_rounds_per_chunk: int = 10  # Minimum rounds to create a chunk
    overlap_rounds: int = 2  # Number of overlapping rounds between chunks
    include_system_messages: bool = False  # Whether to include system messages
    preserve_context: bool = True  # Preserve context flow in chunks


@dataclass
class RAGConfig:
    """RAG system configuration"""
    kb_type: KnowledgeBaseType = KnowledgeBaseType.LOCAL
    embedding_model: str = "text-embedding-3-small"
    embedding_dim: int = 1536
    top_k: int = 5  # Number of top results to retrieve
    similarity_threshold: float = 0.7
    index_path: str = "./rag_index"
    chunk_metadata: bool = True  # Store metadata with chunks
    
    # Local storage settings
    local_store_path: str = "./conversation_chunks.json"
    
    # Vector DB settings (if using Chroma/FAISS)
    collection_name: str = "user_conversations"
    persist_directory: str = "./chroma_db"


@dataclass
class MemoryConfig:
    """User memory configuration"""
    mode: MemoryMode = MemoryMode.ADVANCED_JSON_CARDS
    memory_dir: str = "./memories"
    conversation_dir: str = "./conversations"
    max_memory_items: int = 100
    memory_update_threshold: int = 5  # Update memory after N rounds
    auto_consolidate: bool = True  # Auto-consolidate similar memories
    
    def __post_init__(self):
        """Ensure directories exist"""
        Path(self.memory_dir).mkdir(parents=True, exist_ok=True)
        Path(self.conversation_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class AgentConfig:
    """Agent behavior configuration"""
    max_iterations: int = 10  # Max ReAct iterations
    enable_reflection: bool = True  # Enable agent self-reflection
    verbose: bool = True  # Verbose logging
    stream_response: bool = True  # Stream agent responses
    use_tools: bool = True  # Enable tool usage
    tool_timeout: int = 30  # Tool execution timeout
    
    # Memory-specific settings
    memory_query_on_start: bool = True  # Query memories at conversation start
    memory_update_frequency: str = "auto"  # auto, manual, periodic


@dataclass
class EvaluationConfig:
    """Evaluation configuration"""
    test_cases_dir: str = "./test_cases"
    results_dir: str = "./evaluation_results"
    metrics: List[str] = field(default_factory=lambda: [
        "retrieval_accuracy",
        "memory_consistency",
        "response_relevance",
        "factual_accuracy"
    ])
    save_trajectories: bool = True  # Save agent reasoning trajectories
    
    def __post_init__(self):
        """Ensure directories exist"""
        Path(self.results_dir).mkdir(parents=True, exist_ok=True)


@dataclass
class Config:
    """Main configuration container"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    chunking: ChunkingConfig = field(default_factory=ChunkingConfig)
    rag: RAGConfig = field(default_factory=RAGConfig)
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    
    @classmethod
    def from_env(cls) -> 'Config':
        """Create config from environment variables"""
        config = cls()
        
        # Override from environment
        if provider := os.getenv("LLM_PROVIDER"):
            config.llm.provider = provider
        if model := os.getenv("LLM_MODEL"):
            config.llm.model = model
        if kb_type := os.getenv("KB_TYPE"):
            config.rag.kb_type = KnowledgeBaseType(kb_type)
        if memory_mode := os.getenv("MEMORY_MODE"):
            config.memory.mode = MemoryMode(memory_mode)
            
        return config
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary"""
        return {
            "llm": {
                "provider": self.llm.provider,
                "model": self.llm.model,
                "temperature": self.llm.temperature,
                "max_tokens": self.llm.max_tokens
            },
            "chunking": {
                "rounds_per_chunk": self.chunking.rounds_per_chunk,
                "overlap_rounds": self.chunking.overlap_rounds
            },
            "rag": {
                "kb_type": self.rag.kb_type.value,
                "top_k": self.rag.top_k,
                "similarity_threshold": self.rag.similarity_threshold
            },
            "memory": {
                "mode": self.memory.mode.value,
                "max_memory_items": self.memory.max_memory_items
            },
            "agent": {
                "max_iterations": self.agent.max_iterations,
                "enable_reflection": self.agent.enable_reflection
            }
        }
