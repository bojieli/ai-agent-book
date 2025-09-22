"""
Configuration for Contextual Retrieval User Memory System
"""

import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from enum import Enum
from pathlib import Path


class RetrievalMode(Enum):
    """Retrieval mode for memory search"""
    CONTEXTUAL = "contextual"
    NON_CONTEXTUAL = "non_contextual"
    BASELINE = "baseline"
    COMPARE = "compare"


class SearchStrategy(Enum):
    """Search strategy for hybrid retrieval"""
    BM25_ONLY = "bm25"
    EMBEDDING_ONLY = "embedding"
    HYBRID = "hybrid"
    HYBRID_RRF = "hybrid_rrf"  # Reciprocal Rank Fusion


@dataclass
class LLMConfig:
    """LLM configuration"""
    provider: str = "kimi"  # kimi, doubao, openai, siliconflow
    model: Optional[str] = None
    api_key: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096
    
    def get_api_key(self) -> str:
        """Get API key from config or environment"""
        if self.api_key:
            return self.api_key
        
        # Map provider to environment variable
        env_map = {
            "kimi": "MOONSHOT_API_KEY",
            "moonshot": "MOONSHOT_API_KEY",
            "doubao": "ARK_API_KEY",
            "openai": "OPENAI_API_KEY",
            "siliconflow": "SILICONFLOW_API_KEY",
            "anthropic": "ANTHROPIC_API_KEY"
        }
        
        env_var = env_map.get(self.provider.lower())
        if env_var:
            return os.getenv(env_var, "")
        return ""
    
    def get_base_url(self) -> Optional[str]:
        """Get base URL for provider"""
        url_map = {
            "kimi": "https://api.moonshot.cn/v1",
            "moonshot": "https://api.moonshot.cn/v1",
            "doubao": "https://ark.cn-beijing.volces.com/api/v3",
            "siliconflow": "https://api.siliconflow.cn/v1"
        }
        return url_map.get(self.provider.lower())
    
    def get_model_name(self) -> str:
        """Get model name with defaults"""
        if self.model:
            return self.model
        
        # Default models for each provider
        defaults = {
            "kimi": "kimi-k2-0905-preview",
            "moonshot": "kimi-k2-0905-preview",
            "doubao": "doubao-seed-1-6-thinking-250715",
            "openai": "gpt-4o-mini",
            "siliconflow": "Qwen/Qwen3-235B-A22B-Thinking-2507",
            "anthropic": "claude-3-haiku-20240307"
        }
        return defaults.get(self.provider.lower(), "gpt-4o-mini")


@dataclass
class IndexingConfig:
    """Configuration for memory indexing"""
    chunk_size: int = 20  # Number of conversation rounds per chunk
    chunk_overlap: int = 2  # Overlapping rounds between chunks
    min_chunk_size: int = 5  # Minimum rounds for a chunk
    
    # Context generation
    enable_contextual: bool = True
    context_window_size: int = 50  # Rounds to consider for context
    context_model: str = "claude-3-haiku-20240307"  # Efficient model for context generation
    max_context_length: int = 150  # Max tokens for generated context
    
    # Embedding configuration
    embedding_model: str = "text-embedding-3-small"
    embedding_dimension: int = 1536
    
    # BM25 configuration
    bm25_k1: float = 1.5  # Term frequency saturation
    bm25_b: float = 0.75  # Length normalization
    
    # Storage
    index_dir: str = "memory_indexes"
    enable_persistence: bool = True


@dataclass
class AgentConfig:
    """Configuration for the agentic memory agent"""
    max_iterations: int = 5  # Max ReAct iterations
    enable_reasoning: bool = True  # Show reasoning steps
    enable_tool_calling: bool = True
    
    # Search configuration
    search_top_k: int = 10  # Number of chunks to retrieve
    rerank_top_k: int = 5  # After reranking
    enable_reranking: bool = True
    reranking_model: Optional[str] = None  # Use LLM for reranking if specified
    
    # Hybrid search weights
    bm25_weight: float = 0.4
    embedding_weight: float = 0.6
    
    # Advanced features
    use_hyde: bool = False  # Hypothetical Document Embeddings
    enable_query_expansion: bool = False
    enable_metadata_filtering: bool = True
    
    # Memory context
    max_memory_context: int = 10  # Max memory chunks in context
    include_conversation_context: bool = True


@dataclass
class EvaluationConfig:
    """Configuration for evaluation framework"""
    test_cases_dir: str = "test_cases"
    results_dir: str = "evaluation_results"
    
    # Evaluation modes
    compare_modes: List[RetrievalMode] = field(
        default_factory=lambda: [RetrievalMode.CONTEXTUAL, RetrievalMode.NON_CONTEXTUAL]
    )
    
    # Metrics to track
    track_metrics: List[str] = field(
        default_factory=lambda: [
            "precision", "recall", "f1", "mrr",  # Retrieval metrics
            "answer_accuracy", "completeness",  # Answer quality
            "tool_calls", "iterations", "latency"  # Performance metrics
        ]
    )
    
    # Evaluation settings
    enable_verbose: bool = True
    save_trajectories: bool = True
    generate_report: bool = True
    
    # Sampling for large test sets
    sample_size: Optional[int] = None  # None means use all
    random_seed: int = 42


@dataclass
class Config:
    """Main configuration class"""
    llm: LLMConfig = field(default_factory=LLMConfig)
    indexing: IndexingConfig = field(default_factory=IndexingConfig)
    agent: AgentConfig = field(default_factory=AgentConfig)
    evaluation: EvaluationConfig = field(default_factory=EvaluationConfig)
    
    # System settings
    debug: bool = False
    verbose: bool = True
    log_file: Optional[str] = "memory_agent.log"
    
    @classmethod
    def from_env(cls) -> "Config":
        """Create config from environment variables"""
        config = cls()
        
        # LLM configuration from environment
        config.llm.provider = os.getenv("LLM_PROVIDER", "kimi")
        config.llm.model = os.getenv("LLM_MODEL")
        config.llm.temperature = float(os.getenv("LLM_TEMPERATURE", "0.7"))
        
        # Indexing configuration
        config.indexing.chunk_size = int(os.getenv("CHUNK_SIZE", "20"))
        config.indexing.enable_contextual = os.getenv("ENABLE_CONTEXTUAL", "true").lower() == "true"
        config.indexing.embedding_model = os.getenv("EMBEDDING_MODEL", config.indexing.embedding_model)
        
        # Agent configuration
        config.agent.max_iterations = int(os.getenv("MAX_ITERATIONS", "5"))
        config.agent.search_top_k = int(os.getenv("SEARCH_TOP_K", "10"))
        config.agent.enable_reranking = os.getenv("ENABLE_RERANKING", "true").lower() == "true"
        
        # Debug mode
        config.debug = os.getenv("DEBUG", "false").lower() == "true"
        config.verbose = config.debug or os.getenv("VERBOSE", "false").lower() == "true"
        
        return config
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Config":
        """Create config from dictionary"""
        config = cls()
        
        # Update LLM config
        if "llm" in data:
            for key, value in data["llm"].items():
                if hasattr(config.llm, key):
                    setattr(config.llm, key, value)
        
        # Update other configs similarly
        for section in ["indexing", "agent", "evaluation"]:
            if section in data:
                section_config = getattr(config, section)
                for key, value in data[section].items():
                    if hasattr(section_config, key):
                        setattr(section_config, key, value)
        
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
            "indexing": {
                "chunk_size": self.indexing.chunk_size,
                "chunk_overlap": self.indexing.chunk_overlap,
                "enable_contextual": self.indexing.enable_contextual,
                "embedding_model": self.indexing.embedding_model
            },
            "agent": {
                "max_iterations": self.agent.max_iterations,
                "search_top_k": self.agent.search_top_k,
                "enable_reranking": self.agent.enable_reranking,
                "bm25_weight": self.agent.bm25_weight,
                "embedding_weight": self.agent.embedding_weight
            },
            "evaluation": {
                "test_cases_dir": self.evaluation.test_cases_dir,
                "results_dir": self.evaluation.results_dir,
                "compare_modes": [mode.value for mode in self.evaluation.compare_modes]
            }
        }


# Convenience function for getting default config
def get_default_config() -> Config:
    """Get default configuration, preferring environment variables"""
    return Config.from_env()
