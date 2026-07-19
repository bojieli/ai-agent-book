"""
实验 8-6 配置模块：统一读取 API Key、构造 OpenAI 客户端。

支持以下 OpenAI 兼容服务（按 PROVIDER 选择）：
- openai   （默认，读 OPENAI_API_KEY，默认模型 gpt-5.6-luna）
- moonshot （读 MOONSHOT_API_KEY，Kimi，默认 kimi-k3）
- ark      （读 ARK_API_KEY，火山方舟）

统一的 OpenRouter 兜底（fallback）：
    若所选 provider 自己的 Key 缺失，但设置了 OPENROUTER_API_KEY，则自动改走
    OpenRouter（https://openrouter.ai/api/v1），并把模型名映射到 OpenRouter 命名：
        gpt-*     -> openai/gpt-*
        claude-*  -> anthropic/claude-opus-4.8
        含 "/"    -> 原样透传
        其它      -> openai/gpt-5.6-luna
    这样在没有 OpenAI 直连 Key 时也能一键跑通。
"""

import os
from typing import Optional

from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


# 各 provider 的 base_url 与默认模型
_PROVIDERS = {
    "openai": {
        "key_env": "OPENAI_API_KEY",
        "base_url": None,  # OpenAI 官方默认地址
        "default_model": "gpt-5.6-luna",
    },
    "moonshot": {
        "key_env": "MOONSHOT_API_KEY",
        "base_url": "https://api.moonshot.cn/v1",
        "default_model": "kimi-k3",
    },
    "ark": {
        "key_env": "ARK_API_KEY",
        "base_url": "https://ark.cn-beijing.volces.com/api/v3",
        "default_model": "doubao-seed-1-6-250615",
    },
}


def _to_openrouter_model(model: str) -> str:
    """把常见模型名映射到 OpenRouter 命名空间。"""
    if not model:
        return "openai/gpt-5.6-luna"
    if "/" in model:
        return model
    if model.startswith("gpt-"):
        return "openai/" + model
    if model.startswith("claude-"):
        return "anthropic/claude-opus-4.8"
    return "openai/gpt-5.6-luna"


class Config:
    # 被测 Agent（工具创造）默认模型
    PROVIDER: str = os.getenv("PROVIDER", "openai").lower()
    AGENT_MODEL: str = os.getenv("AGENT_MODEL", "gpt-5.6-luna")
    # LLM-as-a-Judge 使用的模型（第 3 层工具创造质量打分）
    JUDGE_MODEL: str = os.getenv("JUDGE_MODEL", "gpt-5.6-luna")
    TEMPERATURE: float = float(os.getenv("TEMPERATURE", "0.2"))

    @classmethod
    def provider_meta(cls) -> dict:
        if cls.PROVIDER not in _PROVIDERS:
            raise ValueError(
                f"未知 PROVIDER={cls.PROVIDER}，可选：{list(_PROVIDERS)}"
            )
        return _PROVIDERS[cls.PROVIDER]

    @classmethod
    def _use_openrouter(cls) -> bool:
        """所选 provider 的 Key 缺失、但有 OPENROUTER_API_KEY 时，走 OpenRouter 兜底。"""
        meta = cls.provider_meta()
        return (not os.getenv(meta["key_env"])) and bool(os.getenv("OPENROUTER_API_KEY"))

    @classmethod
    def map_model(cls, model: str) -> str:
        """在 OpenRouter 兜底路径下，把模型名映射到 OpenRouter 命名；否则原样返回。"""
        return _to_openrouter_model(model) if cls._use_openrouter() else model

    @classmethod
    def get_client(cls) -> OpenAI:
        """构造并返回 OpenAI 兼容客户端（优先直连，缺 Key 时走 OpenRouter 兜底）。"""
        meta = cls.provider_meta()
        if cls._use_openrouter():
            return OpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url=OPENROUTER_BASE_URL,
            )
        api_key = os.getenv(meta["key_env"], "")
        if not api_key:
            raise RuntimeError(
                f"未找到 {meta['key_env']}，也未设置 OPENROUTER_API_KEY。"
                f"请在 .env 中配置其一（OpenRouter 可作为统一兜底）。"
            )
        kwargs = {"api_key": api_key}
        if meta["base_url"]:
            kwargs["base_url"] = meta["base_url"]
        return OpenAI(**kwargs)

    @classmethod
    def resolve_default_model(cls, override: Optional[str] = None) -> str:
        """解析被测 Agent 的模型：处理 provider 默认回退与 OpenRouter 命名映射。"""
        meta = cls.provider_meta()
        model = override or cls.AGENT_MODEL
        # 非 openai provider 下若仍是 gpt-* 默认值，则回退到该 provider 的默认模型
        if not override and cls.PROVIDER != "openai" and model.startswith("gpt-"):
            model = meta["default_model"]
        return cls.map_model(model)
