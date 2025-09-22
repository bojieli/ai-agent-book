"""Educational logging configuration with extensive debug information."""

import logging
import sys
import time
from typing import Optional
import colorlog
from functools import wraps


def setup_logger(name: str = "vector_search", level: str = "DEBUG") -> logging.Logger:
    """
    Set up a colorful and informative logger for educational purposes.
    
    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR)
    
    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, level))
    
    # Clear existing handlers
    logger.handlers = []
    
    # Create console handler with colors
    console_handler = colorlog.StreamHandler(sys.stdout)
    console_handler.setLevel(getattr(logging, level))
    
    # Create detailed formatter for educational purposes
    log_format = (
        "%(log_color)s%(asctime)s - %(name)s - [%(levelname)s] - "
        "%(filename)s:%(lineno)d - %(funcName)s() - %(message)s%(reset)s"
    )
    
    formatter = colorlog.ColoredFormatter(
        log_format,
        datefmt="%Y-%m-%d %H:%M:%S",
        reset=True,
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )
    
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


def log_execution_time(logger: Optional[logging.Logger] = None):
    """
    Decorator to log function execution time for educational purposes.
    
    Args:
        logger: Logger instance to use
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            nonlocal logger
            if logger is None:
                logger = logging.getLogger("vector_search")
            
            logger.debug(f"Starting execution of {func.__name__}")
            start_time = time.time()
            
            try:
                result = func(*args, **kwargs)
                execution_time = time.time() - start_time
                logger.info(
                    f"✅ {func.__name__} completed successfully in {execution_time:.4f} seconds"
                )
                return result
            except Exception as e:
                execution_time = time.time() - start_time
                logger.error(
                    f"❌ {func.__name__} failed after {execution_time:.4f} seconds: {str(e)}"
                )
                raise
        
        return wrapper
    return decorator


class VectorSearchLogger:
    """Educational logger for vector search operations with detailed debugging."""
    
    def __init__(self, logger: logging.Logger, show_embeddings: bool = False):
        self.logger = logger
        self.show_embeddings = show_embeddings
    
    def log_indexing_start(self, doc_id: str, text: str):
        """Log the start of document indexing."""
        self.logger.debug("=" * 80)
        self.logger.info(f"📝 Starting INDEXING operation")
        self.logger.debug(f"Document ID: {doc_id}")
        self.logger.debug(f"Text length: {len(text)} characters")
        self.logger.debug(f"Text preview: {text[:100]}..." if len(text) > 100 else f"Text: {text}")
    
    def log_embedding_generation(self, text: str, embedding_shape: tuple, time_taken: float):
        """Log embedding generation details."""
        self.logger.debug(f"🧮 Generating embeddings using BGE-M3 model")
        self.logger.debug(f"Input text length: {len(text)} characters")
        self.logger.debug(f"Embedding shape: {embedding_shape}")
        self.logger.debug(f"Embedding generation time: {time_taken:.4f} seconds")
    
    def log_embedding_vector(self, embedding, sample_size: int = 10):
        """Log embedding vector details for educational purposes."""
        if self.show_embeddings:
            self.logger.debug(f"Embedding vector (first {sample_size} dimensions): {embedding[:sample_size]}")
            self.logger.debug(f"Embedding statistics - Min: {embedding.min():.6f}, Max: {embedding.max():.6f}, Mean: {embedding.mean():.6f}")
    
    def log_index_update(self, index_type: str, doc_id: str, current_size: int):
        """Log index update operations."""
        self.logger.info(f"📊 Updating {index_type.upper()} index")
        self.logger.debug(f"Adding document {doc_id} to index")
        self.logger.debug(f"Current index size: {current_size} documents")
    
    def log_search_start(self, query: str, top_k: int):
        """Log the start of search operation."""
        self.logger.debug("=" * 80)
        self.logger.info(f"🔍 Starting SEARCH operation")
        self.logger.debug(f"Query: {query}")
        self.logger.debug(f"Retrieving top {top_k} results")
    
    def log_search_results(self, results: list, distances: list, time_taken: float):
        """Log search results with detailed information."""
        self.logger.info(f"✨ Search completed in {time_taken:.4f} seconds")
        self.logger.debug(f"Found {len(results)} matching documents")
        
        for i, (doc_id, distance) in enumerate(zip(results, distances), 1):
            self.logger.debug(f"  Rank {i}: Document {doc_id} (distance: {distance:.6f})")
    
    def log_deletion(self, doc_id: str):
        """Log document deletion."""
        self.logger.debug("=" * 80)
        self.logger.info(f"🗑️  Starting DELETE operation")
        self.logger.debug(f"Deleting document: {doc_id}")
    
    def log_error(self, operation: str, error: Exception):
        """Log errors with context."""
        self.logger.error(f"❌ Error during {operation}: {type(error).__name__}: {str(error)}")
        self.logger.debug(f"Full error details:", exc_info=True)
    
    def log_index_build(self, index_type: str, num_documents: int, parameters: dict):
        """Log index building process."""
        self.logger.info(f"🏗️  Building {index_type.upper()} index")
        self.logger.debug(f"Number of documents: {num_documents}")
        self.logger.debug(f"Index parameters: {parameters}")
