"""
Configuration for structured index project.
"""

import os
from pathlib import Path
from typing import Optional
from dataclasses import dataclass
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


@dataclass
class RaptorConfig:
    """Configuration for RAPTOR tree-based indexing."""
    openai_api_key: str
    model_name: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    max_tokens: int = 2048
    temperature: float = 0.1
    chunk_size: int = 1000
    chunk_overlap: int = 200
    tree_depth: int = 3
    summarization_length: int = 200
    index_dir: Path = Path("indexes/raptor")


@dataclass
class GraphRAGConfig:
    """Configuration for GraphRAG graph-based indexing."""
    llm_api_key: str
    llm_model: str = "gpt-4o-mini"
    embedding_model: str = "text-embedding-3-small"
    chunk_size: int = 1200
    chunk_overlap: int = 100
    max_knowledge_triples: int = 10
    community_detection_algorithm: str = "leiden"
    summarization_model: str = "gpt-4o-mini"
    index_dir: Path = Path("indexes/graphrag")
    cache_dir: Path = Path("cache/graphrag")


@dataclass
class APIConfig:
    """Configuration for HTTP API service."""
    host: str = "127.0.0.1"
    port: int = 4242
    reload: bool = True
    max_results: int = 10
    timeout_seconds: int = 30


def get_raptor_config() -> RaptorConfig:
    """Get RAPTOR configuration from environment."""
    return RaptorConfig(
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        model_name=os.getenv("RAPTOR_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("RAPTOR_EMBEDDING_MODEL", "text-embedding-3-small"),
        max_tokens=int(os.getenv("RAPTOR_MAX_TOKENS", "2048")),
        temperature=float(os.getenv("RAPTOR_TEMPERATURE", "0.1")),
        chunk_size=int(os.getenv("RAPTOR_CHUNK_SIZE", "1000")),
        chunk_overlap=int(os.getenv("RAPTOR_CHUNK_OVERLAP", "200")),
        tree_depth=int(os.getenv("RAPTOR_TREE_DEPTH", "3")),
        summarization_length=int(os.getenv("RAPTOR_SUMMARY_LENGTH", "200"))
    )


def get_graphrag_config() -> GraphRAGConfig:
    """Get GraphRAG configuration from environment."""
    return GraphRAGConfig(
        llm_api_key=os.getenv("OPENAI_API_KEY", ""),
        llm_model=os.getenv("GRAPHRAG_MODEL", "gpt-4o-mini"),
        embedding_model=os.getenv("GRAPHRAG_EMBEDDING_MODEL", "text-embedding-3-small"),
        chunk_size=int(os.getenv("GRAPHRAG_CHUNK_SIZE", "1200")),
        chunk_overlap=int(os.getenv("GRAPHRAG_CHUNK_OVERLAP", "100")),
        max_knowledge_triples=int(os.getenv("GRAPHRAG_MAX_TRIPLES", "10")),
        community_detection_algorithm=os.getenv("GRAPHRAG_COMMUNITY_ALG", "leiden"),
        summarization_model=os.getenv("GRAPHRAG_SUMMARY_MODEL", "gpt-4o-mini")
    )


def get_api_config() -> APIConfig:
    """Get API configuration from environment."""
    return APIConfig(
        host=os.getenv("API_HOST", "127.0.0.1"),
        port=int(os.getenv("API_PORT", "4242")),
        reload=os.getenv("API_RELOAD", "true").lower() == "true",
        max_results=int(os.getenv("API_MAX_RESULTS", "10")),
        timeout_seconds=int(os.getenv("API_TIMEOUT", "30"))
    )
