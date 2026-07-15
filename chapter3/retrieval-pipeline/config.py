"""Configuration for the retrieval pipeline."""

import os
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional

class SearchMode(str, Enum):
    """Search mode for retrieval."""
    DENSE = "dense"
    SPARSE = "sparse"
    HYBRID = "hybrid"  # Both dense and sparse

@dataclass
class ServiceConfig:
    """Configuration for external services."""
    dense_service_url: str = "http://localhost:4240"  # Port 4240 for dense service
    sparse_service_url: str = "http://localhost:4241"  # Port 4241 for sparse service
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        dense_url = os.getenv("DENSE_SERVICE_URL", "http://localhost:4240")
        sparse_url = os.getenv("SPARSE_SERVICE_URL", "http://localhost:4241")
        return cls(dense_service_url=dense_url, sparse_service_url=sparse_url)
    
@dataclass
class RerankerConfig:
    """Configuration for the reranker model."""
    model_name: str = "BAAI/bge-reranker-v2-m3"
    device: str = "mps"  # Use MPS for Mac M1/M2
    batch_size: int = 32
    max_length: int = 8192  # Increased to match HARD_LIMIT in chunking
    use_fp16: bool = True  # Use half precision for faster inference on Mac
    
@dataclass
class PipelineConfig:
    """Configuration for the retrieval pipeline."""
    services: ServiceConfig = field(default_factory=ServiceConfig)
    reranker: RerankerConfig = field(default_factory=RerankerConfig)
    
    # Retrieval settings
    default_top_k: int = 20  # Number of candidates to retrieve from each service
    rerank_top_k: int = 10  # Number of results after reranking
    
    # Logging
    debug: bool = True
    show_scores: bool = True  # Show all scores in response for educational purposes
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 4242  # Default port for retrieval pipeline
    
    @classmethod
    def from_env(cls):
        """Create config from environment variables."""
        config = cls()
        if os.getenv("PIPELINE_PORT"):
            config.port = int(os.getenv("PIPELINE_PORT"))
        if os.getenv("PIPELINE_HOST"):
            config.host = os.getenv("PIPELINE_HOST")
        if os.getenv("DEBUG"):
            config.debug = os.getenv("DEBUG").lower() == "true"
        return config
