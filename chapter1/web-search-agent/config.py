"""
配置文件 - Kimi API 配置
"""

import os
from typing import Optional

class Config:
    """配置类"""
    
    # Kimi API 配置
    MOONSHOT_API_KEY: str = os.getenv("MOONSHOT_API_KEY", "")
    # 向后兼容：如果没有 MOONSHOT_API_KEY，尝试使用 KIMI_API_KEY
    if not MOONSHOT_API_KEY:
        MOONSHOT_API_KEY = os.getenv("KIMI_API_KEY", "")
    
    KIMI_BASE_URL: str = "https://api.moonshot.cn/v1"
    
    # 模型配置
    DEFAULT_MODEL: str = "kimi-k2-0905-preview"  # 使用最新的 K2 模型
    
    # 搜索配置
    MAX_SEARCH_ITERATIONS: int = 3  # 最大搜索迭代次数
    SEARCH_TIMEOUT: int = 30  # 搜索超时时间（秒）
    
    # 日志配置
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    
    @classmethod
    def validate(cls) -> bool:
        """
        验证配置是否有效
        
        Returns:
            bool: 配置是否有效
        """
        if not cls.MOONSHOT_API_KEY:
            print("错误: 未设置 MOONSHOT_API_KEY 环境变量")
            print("请设置环境变量: export MOONSHOT_API_KEY='your-api-key'")
            print("(或者使用旧的环境变量名: export KIMI_API_KEY='your-api-key')")
            return False
        return True
    
    @classmethod
    def get_api_key(cls, api_key: Optional[str] = None) -> str:
        """
        获取 API Key
        
        Args:
            api_key: 可选的 API key，如果提供则使用，否则从环境变量获取
            
        Returns:
            API key
        """
        if api_key:
            return api_key
        return cls.MOONSHOT_API_KEY
