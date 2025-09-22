"""Configuration module for the vector similarity search service."""

import os
from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field


class IndexType(str, Enum):
    """Supported index types for vector similarity search."""
    ANNOY = "annoy"
    HNSW = "hnsw"


class ServiceConfig(BaseModel):
    """Service configuration settings."""
    
    # Model settings
    model_name: str = Field(default="BAAI/bge-m3", description="BGE-M3 model name")
    use_fp16: bool = Field(default=True, description="Use FP16 for model inference")
    max_seq_length: int = Field(default=512, description="Maximum sequence length for embeddings")
    embedding_dim: int = Field(default=1024, description="BGE-M3 embedding dimension")
    
    # Index settings
    index_type: IndexType = Field(default=IndexType.HNSW, description="Type of index to use")
    max_documents: int = Field(default=100000, description="Maximum number of documents in index")
    
    # ANNOY specific settings
    annoy_n_trees: int = Field(default=50, description="Number of trees for ANNOY index")
    annoy_metric: str = Field(default="angular", description="Distance metric for ANNOY")
    
    # HNSW specific settings
    hnsw_ef_construction: int = Field(default=200, description="HNSW ef parameter during construction")
    hnsw_M: int = Field(default=32, description="HNSW M parameter (number of connections)")
    hnsw_ef_search: int = Field(default=100, description="HNSW ef parameter during search")
    hnsw_space: str = Field(default="cosine", description="Distance metric for HNSW")
    
    # Server settings
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    debug: bool = Field(default=True, description="Enable debug mode")
    
    # Logging settings
    log_level: str = Field(default="DEBUG", description="Logging level")
    show_embeddings: bool = Field(default=False, description="Show embedding vectors in logs")
    
    @classmethod
    def from_env(cls) -> "ServiceConfig":
        """Load configuration from environment variables."""
        config_dict = {}
        
        # Load from environment variables with PREFIX "VEC_"
        prefix = "VEC_"
        for field_name, field_info in cls.model_fields.items():
            env_var = f"{prefix}{field_name.upper()}"
            if env_var in os.environ:
                value = os.environ[env_var]
                # Convert to appropriate type
                if field_info.annotation == bool:
                    value = value.lower() in ("true", "1", "yes")
                elif field_info.annotation == int:
                    value = int(value)
                elif field_info.annotation == IndexType:
                    value = IndexType(value.lower())
                config_dict[field_name] = value
        
        return cls(**config_dict)
