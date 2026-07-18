"""
agent.py —— 代码生成 Agent（自愈闭环的“大脑”）

职责：拿到无法解析的失败样本 + 报错，调用 OpenAI，生成一个能正确解析该格式的
Python 解析函数 `def parse(line: str) -> dict | None`。支持把上一轮自动测试的
失败报告作为反馈再次生成（迭代修复）。
"""

from __future__ import annotations

import os
import re
from typing import List, Optional

from openai import OpenAI

# .env 加载（可选依赖）
try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:
    pass


SYSTEM_PROMPT = """你是一个"日志解析器代码生成器"。用户会给你一批**同一种未知格式**的日志样本，
以及现有系统解析失败的报错。你的任务：编写一个 Python 函数，把这种格式的每一行解析成结构化字段。

严格要求：
1. 只输出一个 Python 代码块（```python ... ```），不要任何解释文字。
2. 代码块里必须定义一个函数：def parse(line: str) -> dict | None
   - 输入是一行日志（字符串）。
   - 如果这行符合你要解析的格式，返回一个 dict，键为字段名（英文小写下划线），值为解析出的内容。
   - 如果这行**不符合**这种格式，必须返回 None（不要抛异常，把机会让给其它解析器）。
3. 只能使用 Python 标准库（re、json、datetime 等），不要 import 第三方库。
4. 不要有任何 print、input、文件读写、网络访问等副作用。
5. 必须解析出用户指定的**所有必需字段**（required_keys），字段值不能为空。
6. 尽量健壮：用正则/分隔符解析，容忍字段顺序内的空格。
"""


def _build_user_prompt(
    samples: List[str],
    required_keys: List[str],
    error_report: str,
    feedback: Optional[str],
) -> str:
    sample_block = "\n".join(samples)
    parts = [
        "现有系统无法解析下面这种格式的日志，请生成解析函数。",
        "",
        "【失败样本（同一种新格式）】",
        sample_block,
        "",
        f"【系统报错】\n{error_report}",
        "",
        f"【必需解析出的字段 required_keys】\n{required_keys}",
    ]
    if feedback:
        parts += [
            "",
            "【上一版代码没通过自动测试，请修复后重新生成】",
            feedback,
        ]
    return "\n".join(parts)


def _extract_code(text: str) -> str:
    """从模型回复中抽取 Python 代码块；没有围栏时退回整段文本。"""
    m = re.search(r"```(?:python)?\s*(.*?)```", text, re.DOTALL)
    return (m.group(1) if m else text).strip()


OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"


def _map_to_openrouter_model(model: str) -> str:
    """把直连模型名映射为 OpenRouter 上的 id（非可映射 id 统一兜底到当前廉价旗舰）。"""
    if not model or "/" in model:
        return model or "openai/gpt-5.6-luna"
    m = model.lower()
    if m.startswith(("gpt-", "o1", "o3", "o4")):
        return "openai/" + model
    if m.startswith("claude"):
        if "haiku" in m:
            return "anthropic/claude-haiku-4.5"
        if "sonnet" in m:
            return "anthropic/claude-sonnet-4.6"
        return "anthropic/claude-opus-4.8"
    if m.startswith("gemini"):
        return "google/" + model
    return "openai/gpt-5.6-luna"


class CodeGenAgent:
    def __init__(self, model: Optional[str] = None):
        model = model or os.getenv("MODEL", "gpt-5.6-luna")
        api_key = os.getenv("OPENAI_API_KEY")
        base_url = os.getenv("OPENAI_BASE_URL")
        orkey = os.getenv("OPENROUTER_API_KEY")
        # 通用 OpenRouter 兜底：无直连 key，或默认 gpt-5.x（直连需组织实名认证）时改走 OpenRouter。
        prefer_or = bool(orkey) and (model or "").lower().startswith("gpt-5")
        if prefer_or or (not api_key and orkey):
            api_key, base_url, model = orkey, OPENROUTER_BASE_URL, _map_to_openrouter_model(model)
        if not api_key:
            raise SystemExit("未找到 OPENAI_API_KEY（或 OPENROUTER_API_KEY 兜底），请在环境变量或 .env 中设置。")
        # timeout / max_retries：让偶发的网络/SSL 抖动自动重试，不至于整轮崩溃
        client_kwargs = {"api_key": api_key, "timeout": 60.0, "max_retries": 3}
        if base_url:
            client_kwargs["base_url"] = base_url
        self.client = OpenAI(**client_kwargs)
        self.model = model

    def generate_parser_code(
        self,
        samples: List[str],
        required_keys: List[str],
        error_report: str,
        feedback: Optional[str] = None,
    ) -> str:
        """调用 LLM 生成解析器代码，返回纯 Python 源码字符串。"""
        user_prompt = _build_user_prompt(samples, required_keys, error_report, feedback)
        # 推理模型（gpt-5 / o 系列等）不接受 temperature=0。
        _reasoning = any(k in (self.model or "").lower()
                         for k in ("gpt-5", "o1", "o3", "o4", "thinking", "reasoner", "kimi-k3"))
        resp = self.client.chat.completions.create(
            model=self.model,
            temperature=1 if _reasoning else 0,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt},
            ],
        )
        return _extract_code(resp.choices[0].message.content or "")


# ---------------------------------------------------------------------------
# 离线（无 API）代码生成 Agent
# ---------------------------------------------------------------------------
# 与 CodeGenAgent 接口完全一致，但不调用 OpenAI，而是根据必需字段返回**预置**的
# 解析器源码。它的用途是：在没有 API Key 的环境里，仍能确定性地演示与验证整条
# 机制——失败检测 → （预置）生成代码 → 自动测试 → 热加载注册 → 持久化复用。
# 注意：这里的“生成”是查表返回预写好的代码，并非真正让 LLM 现写；只有换用
# CodeGenAgent 才是真正的代码生成。
_CANNED_PARSERS = {
    # 竖线分隔格式：时间戳|级别|模块|step=N|消息
    frozenset(["timestamp", "level", "module", "step", "message"]): '''import re


def parse(line: str) -> dict | None:
    pattern = (
        r"^(?P<timestamp>\\S+)\\|(?P<level>\\S+)\\|(?P<module>\\S+)"
        r"\\|step=(?P<step>\\d+)\\|(?P<message>.+)$"
    )
    match = re.match(pattern, line.strip())
    if match:
        return match.groupdict()
    return None
''',
    # 嵌套括号格式：[时间] (级别) <tool=名字> {k=v k=v} :: 消息
    frozenset(["timestamp", "level", "tool", "message"]): '''import re


def parse(line: str) -> dict | None:
    pattern = (
        r"\\[(?P<timestamp>.*?)\\] \\((?P<level>.*?)\\) <tool=(?P<tool>.*?)> "
        r"\\{latency_ms=(?P<latency_ms>\\d+) status=(?P<status>\\w+)\\} :: (?P<message>.*)"
    )
    match = re.match(pattern, line.strip())
    if match:
        return match.groupdict()
    return None
''',
}


class OfflineCodeGenAgent:
    """离线桩：查表返回预置解析器代码，接口与 CodeGenAgent 一致（无需 API Key）。"""

    def __init__(self, model: Optional[str] = None):
        self.model = model or "offline-canned"

    def generate_parser_code(
        self,
        samples: List[str],
        required_keys: List[str],
        error_report: str,
        feedback: Optional[str] = None,
    ) -> str:
        key = frozenset(required_keys)
        code = _CANNED_PARSERS.get(key)
        if code is not None:
            return code
        # 未预置该格式：返回一个永远返回 None 的桩，让自动测试如实失败，
        # 从而演示“测试未通过 → 放弃该格式”的分支（离线模式无法真正现写代码）。
        return (
            "def parse(line: str) -> dict | None:\n"
            "    # 离线模式未预置该格式的解析器\n"
            "    return None\n"
        )
