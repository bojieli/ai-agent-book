"""
全局配置：加载环境变量、提供 OpenAI 客户端与默认模型名。

只依赖官方 OpenAI SDK，读取 OPENAI_API_KEY。
默认模型 gpt-4o-mini（便宜、够用于因子发现、结构化抽取与文案生成）。
"""
import os

from openai import OpenAI

try:
    # 可选：如果安装了 python-dotenv，则自动加载同目录 .env
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # pragma: no cover - dotenv 是可选依赖
    pass

# 默认模型，可用环境变量覆盖
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


def get_client() -> OpenAI:
    """返回一个配置好的 OpenAI 客户端（仅使用官方端点，读取 OPENAI_API_KEY）。"""
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "未找到 OPENAI_API_KEY，请先 `cp env.example .env` 并填入你的 OpenAI Key。"
        )
    # timeout + 自动重试：发现/抽取阶段要连续发几十次请求，单次瞬时错误
    # （网络抖动 / 限流 / 5xx）不应中断整条流水线。
    return OpenAI(api_key=api_key, timeout=60.0, max_retries=5)
