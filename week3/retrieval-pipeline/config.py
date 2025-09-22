"""Configuration for the retrieval pipeline."""

from dataclasses import dataclass
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
    dense_service_url: str = "http://localhost:8000"
    sparse_service_url: str = "http://localhost:8001"
    
@dataclass
class RerankerConfig:
    """Configuration for the reranker model."""
    model_name: str = "BAAI/bge-reranker-v2-m3"
    device: str = "mps"  # Use MPS for Mac M1/M2
    batch_size: int = 32
    max_length: int = 512
    use_fp16: bool = True  # Use half precision for faster inference on Mac
    
@dataclass
class PipelineConfig:
    """Configuration for the retrieval pipeline."""
    services: ServiceConfig = ServiceConfig()
    reranker: RerankerConfig = RerankerConfig()
    
    # Retrieval settings
    default_top_k: int = 20  # Number of candidates to retrieve from each service
    rerank_top_k: int = 10  # Number of results after reranking
    
    # Logging
    debug: bool = True
    show_scores: bool = True  # Show all scores in response for educational purposes
    
    # Server settings
    host: str = "0.0.0.0"
    port: int = 8002
