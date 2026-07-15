"""
Configuration for the coding agent
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration class for the coding agent"""
    
    # API Configuration
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    # Provider selection (anthropic, openai, or openrouter)
    PROVIDER = os.getenv("PROVIDER", "anthropic").lower()
    
    # Default model
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "claude-sonnet-4-20250514")
    
    # OpenRouter configuration
    OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"
    
    # Agent configuration
    MAX_ITERATIONS = int(os.getenv("MAX_ITERATIONS", "50"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "8192"))
    
    # System configuration
    WORKING_DIRECTORY = os.getenv("WORKING_DIRECTORY", os.getcwd())
    
    @classmethod
    def get_provider(cls) -> str:
        """Get the configured provider"""
        return cls.PROVIDER
    
    @classmethod
    def get_api_key(cls, provider: str = None) -> str:
        """Get API key for specified provider (or configured provider if not specified)"""
        if provider is None:
            provider = cls.PROVIDER
        
        if provider == "anthropic":
            if not cls.ANTHROPIC_API_KEY:
                raise ValueError("ANTHROPIC_API_KEY not set in .env file")
            return cls.ANTHROPIC_API_KEY
        elif provider == "openai":
            if not cls.OPENAI_API_KEY:
                raise ValueError("OPENAI_API_KEY not set in .env file")
            return cls.OPENAI_API_KEY
        elif provider == "openrouter":
            if not cls.OPENROUTER_API_KEY:
                raise ValueError("OPENROUTER_API_KEY not set in .env file")
            return cls.OPENROUTER_API_KEY
        else:
            raise ValueError(f"Unknown provider: {provider}. Must be one of: anthropic, openai, openrouter")
    
    @classmethod
    def get_base_url(cls) -> str:
        """Get base URL for the configured provider"""
        if cls.PROVIDER == "openrouter":
            return cls.OPENROUTER_BASE_URL
        return None  # Use default for anthropic/openai
    
    @classmethod
    def validate(cls):
        """Validate configuration"""
        # Check that the configured provider has an API key
        provider = cls.get_provider()
        try:
            cls.get_api_key(provider)
        except ValueError as e:
            raise ValueError(f"Configuration error: {str(e)}")
        
        # Validate model name based on provider
        if provider == "anthropic" and not cls.DEFAULT_MODEL.startswith("claude"):
            raise ValueError(f"Model '{cls.DEFAULT_MODEL}' is not valid for Anthropic. Use a model starting with 'claude-'")
        elif provider == "openai" and not any(cls.DEFAULT_MODEL.startswith(p) for p in ["gpt-", "o1-"]):
            raise ValueError(f"Model '{cls.DEFAULT_MODEL}' is not valid for OpenAI. Use a model starting with 'gpt-' or 'o1-'")
        # OpenRouter accepts any model name, so no validation needed

