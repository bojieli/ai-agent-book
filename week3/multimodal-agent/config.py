"""
Configuration for Multimodal Agent
Supports multiple providers and extraction modes
"""
import os
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class ExtractionMode(Enum):
    """Modes for multimodal content extraction"""
    NATIVE = "native"  # Use model's native multimodal capabilities
    EXTRACT_TO_TEXT = "extract_to_text"  # Convert multimodal to text first
    

class Provider(Enum):
    """Supported model providers"""
    GEMINI = "gemini"
    OPENAI = "openai"
    DOUBAO = "doubao"
    

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    provider: Provider
    model_name: str
    api_key: str
    base_url: Optional[str] = None
    supports_native_multimodal: bool = True
    

class Config:
    """Main configuration class for multimodal agent"""
    
    def __init__(self):
        # Load API keys from environment
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY", "")
        self.openai_api_key = os.getenv("OPENAI_API_KEY", "")
        self.doubao_api_key = os.getenv("DOUBAO_API_KEY", "")
        
        # Model configurations
        self.models = {
            "gemini-2.5-pro": ModelConfig(
                provider=Provider.GEMINI,
                model_name="gemini-2.5-pro",
                api_key=self.gemini_api_key,
                supports_native_multimodal=True
            ),
            "gpt-5": ModelConfig(
                provider=Provider.OPENAI,
                model_name="gpt-5",
                api_key=self.openai_api_key,
                supports_native_multimodal=True
            ),
            "gpt-4o": ModelConfig(
                provider=Provider.OPENAI,
                model_name="gpt-4o",
                api_key=self.openai_api_key,
                supports_native_multimodal=True
            ),
            "doubao-1.6": ModelConfig(
                provider=Provider.DOUBAO,
                model_name="Doubao-1.6",
                api_key=self.doubao_api_key,
                base_url="https://ark.cn-beijing.volces.com/api/v3",
                supports_native_multimodal=True
            )
        }
        
        # Default settings
        self.default_model = "gemini-2.5-pro"
        self.default_mode = ExtractionMode.NATIVE
        self.enable_multimodal_tools = False
        
        # File size limits (in MB)
        self.max_pdf_size_mb = 20
        self.max_image_size_mb = 20
        self.max_audio_size_mb = 25
        
        # Whisper settings for audio transcription
        self.whisper_model = "whisper-1"
        
        # Temperature settings
        self.temperature = 0.7
        self.max_tokens = 4096
        
    def get_model_config(self, model_name: str) -> ModelConfig:
        """Get configuration for a specific model"""
        if model_name not in self.models:
            raise ValueError(f"Unknown model: {model_name}")
        return self.models[model_name]
        
    def validate_api_keys(self) -> Dict[str, bool]:
        """Check which API keys are configured"""
        return {
            "gemini": bool(self.gemini_api_key),
            "openai": bool(self.openai_api_key),
            "doubao": bool(self.doubao_api_key)
        }
