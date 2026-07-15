"""Configuration management for the execution tools MCP server."""

import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Config:
    """Configuration for the MCP server."""
    
    # LLM Configuration
    PROVIDER: str = os.getenv("PROVIDER", "kimi")
    
    # API Keys
    SILICONFLOW_API_KEY: Optional[str] = os.getenv("SILICONFLOW_API_KEY")
    DOUBAO_API_KEY: Optional[str] = os.getenv("DOUBAO_API_KEY")
    KIMI_API_KEY: Optional[str] = os.getenv("KIMI_API_KEY")
    MOONSHOT_API_KEY: Optional[str] = os.getenv("MOONSHOT_API_KEY")
    OPENROUTER_API_KEY: Optional[str] = os.getenv("OPENROUTER_API_KEY")
    
    # Model names (optional, defaults to provider defaults)
    MODEL: Optional[str] = os.getenv("MODEL")
    
    # Model parameters
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS: int = int(os.getenv("MAX_TOKENS", "4096"))
    
    # External Services
    GOOGLE_CALENDAR_CREDENTIALS_FILE: str = os.getenv(
        "GOOGLE_CALENDAR_CREDENTIALS_FILE", 
        "credentials.json"
    )
    GITHUB_TOKEN: Optional[str] = os.getenv("GITHUB_TOKEN")
    
    # Safety Settings
    REQUIRE_APPROVAL_FOR_DANGEROUS_OPS: bool = (
        os.getenv("REQUIRE_APPROVAL_FOR_DANGEROUS_OPS", "true").lower() == "true"
    )
    AUTO_SUMMARIZE_COMPLEX_OUTPUT: bool = (
        os.getenv("AUTO_SUMMARIZE_COMPLEX_OUTPUT", "true").lower() == "true"
    )
    AUTO_VERIFY_CODE: bool = (
        os.getenv("AUTO_VERIFY_CODE", "true").lower() == "true"
    )
    MAX_OUTPUT_LENGTH: int = int(os.getenv("MAX_OUTPUT_LENGTH", "1000"))
    
    # Workspace Configuration
    WORKSPACE_DIR: Path = Path(os.getenv("WORKSPACE_DIR", os.getcwd()))
    
    @classmethod
    def get_api_key(cls, provider: str) -> Optional[str]:
        """Get API key for the specified provider."""
        provider = provider.lower()
        if provider == "siliconflow":
            return cls.SILICONFLOW_API_KEY
        elif provider == "doubao":
            return cls.DOUBAO_API_KEY
        elif provider in ["kimi", "moonshot"]:
            return cls.KIMI_API_KEY or cls.MOONSHOT_API_KEY
        elif provider == "openrouter":
            return cls.OPENROUTER_API_KEY
        return None
    
    @classmethod
    def validate(cls) -> None:
        """Validate the configuration."""
        provider = cls.PROVIDER.lower()
        api_key = cls.get_api_key(provider)
        
        if not api_key:
            raise ValueError(
                f"API key required for provider '{provider}'. "
                f"Set {provider.upper()}_API_KEY environment variable."
            )
    
    @classmethod
    def get_llm_config(cls) -> dict:
        """Get LLM configuration based on provider."""
        provider = cls.PROVIDER.lower()
        api_key = cls.get_api_key(provider)
        
        if not api_key:
            raise ValueError(f"API key not found for provider: {provider}")
        
        if provider == "siliconflow":
            return {
                "provider": "siliconflow",
                "api_key": api_key,
                "base_url": "https://api.siliconflow.cn/v1",
                "model": cls.MODEL or "Qwen/Qwen3-235B-A22B-Thinking-2507"
            }
        elif provider == "doubao":
            return {
                "provider": "doubao",
                "api_key": api_key,
                "base_url": "https://ark.cn-beijing.volces.com/api/v3",
                "model": cls.MODEL or "doubao-seed-1-6-thinking-250715"
            }
        elif provider in ["kimi", "moonshot"]:
            return {
                "provider": "kimi",
                "api_key": api_key,
                "base_url": "https://api.moonshot.cn/v1",
                "model": cls.MODEL or "kimi-k2-0905-preview"
            }
        elif provider == "openrouter":
            return {
                "provider": "openrouter",
                "api_key": api_key,
                "base_url": "https://openrouter.ai/api/v1",
                "model": cls.MODEL or "google/gemini-2.5-pro"
            }
        else:
            raise ValueError(
                f"Unsupported provider: {provider}. "
                f"Use 'siliconflow', 'doubao', 'kimi', 'moonshot', or 'openrouter'"
            )


# Validate configuration on import
Config.validate()
