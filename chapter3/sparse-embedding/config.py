"""Configuration for the sparse embedding service."""

import os

# Server configuration
SPARSE_PORT = int(os.getenv("SPARSE_PORT", "4241"))  # Port 4241 to avoid conflicts
SPARSE_HOST = os.getenv("SPARSE_HOST", "0.0.0.0")

# Logging
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
