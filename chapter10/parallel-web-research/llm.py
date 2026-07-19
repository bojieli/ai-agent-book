"""
可选的 LLM 判断层
=================

子 Agent 抓到网页文本后，需要判断"这段内容是否回答了目标问题"。
- 默认使用 ``sources.keyword_judge`` 的可控关键词判断（无需联网、结果可复现）；
- 若设置了 ``OPENAI_API_KEY`` 且未强制离线，则调用真实 LLM 做判断，
  展示"子 Agent 用大模型做真实决策"这条路径。

协调 / 总线 / 终止 / 竞态这些机制与 LLM 无关，始终是真实实现；
LLM 只影响"单个源里是否命中答案"的判断，属于可插拔部分。
"""

from __future__ import annotations

import json
import os
from typing import Optional

from sources import keyword_judge


def _to_openrouter_model(model: str) -> str:
    """把模型名映射到 OpenRouter 命名空间（用于无 OPENAI_API_KEY 的回退路径）。"""
    if "/" in model:
        return model                      # 已是 OpenRouter 命名空间，原样使用
    if model.startswith("gpt-"):
        return "openai/" + model          # gpt-* -> openai/gpt-*
    if model.startswith("claude-"):
        return "anthropic/claude-opus-4.8"
    return "openai/gpt-5.6-luna"          # 兜底：当前便宜旗舰


def _loads_lenient(content: str):
    """容错解析 JSON：兼容个别模型把 JSON 包在 ```json ... ``` 代码围栏里的情况。"""
    s = (content or "").strip()
    if s.startswith("```"):
        s = s.split("\n", 1)[-1] if "\n" in s else s
        s = s.rsplit("```", 1)[0].strip()
        if s.lower().startswith("json"):
            s = s[4:].strip()
    return json.loads(s)


def llm_available() -> bool:
    """是否具备调用真实 LLM 的条件。

    注意：本实验的重点是"并行协调 / 消息总线 / 级联终止 / 竞态结算"这些机制，
    而不是 LLM 的检索质量。为保证演示**可复现**（只有真正包含答案的源才命中，
    从而稳定触发竞态与级联终止），默认走确定性的关键词判断。
    只有显式设置 USE_LLM=1 时才启用真实 LLM 判断（可能对 mock 源产生幻觉，仅供体验）。

    Key 解析：优先 OPENAI_API_KEY；没有则回退 OPENROUTER_API_KEY（走 OpenRouter）。
    """
    if os.getenv("USE_LLM", "").lower() not in ("1", "true", "yes"):
        return False
    return bool(os.getenv("OPENAI_API_KEY") or os.getenv("OPENROUTER_API_KEY"))


async def judge_answer(question: str, text: str) -> Optional[str]:
    """
    判断 text 是否回答了 question。命中则返回答案字符串，否则返回 None。
    优先用 LLM；不可用或出错时回退到关键词判断，保证 demo 始终可跑通。
    """
    if not llm_available():
        return keyword_judge(text)

    try:
        # 延迟导入，避免没装 openai 时影响关键词路径
        from openai import AsyncOpenAI

        model = os.getenv("OPENAI_MODEL", "gpt-5.6-luna")
        # 通用回退：优先直连 OPENAI_API_KEY；否则用 OPENROUTER_API_KEY 走 OpenRouter。
        if os.getenv("OPENAI_API_KEY"):
            client = AsyncOpenAI(
                api_key=os.getenv("OPENAI_API_KEY"),
                base_url=os.getenv("OPENAI_BASE_URL") or None,
            )
        else:
            client = AsyncOpenAI(
                api_key=os.getenv("OPENROUTER_API_KEY"),
                base_url="https://openrouter.ai/api/v1",
            )
            model = _to_openrouter_model(model)
        prompt = (
            f"问题：{question}\n\n"
            f"网页内容：{text}\n\n"
            "严格只依据上面的『网页内容』判断，**不得使用你自己的知识**。"
            "只有当网页内容里**确实出现了**问题的具体答案时，才算命中。"
            "命中则只输出 JSON：{\"found\": true, \"answer\": \"<从网页内容中摘出的答案>\"}；"
            "若网页内容没有直接给出答案（哪怕你知道答案），一律输出 {\"found\": false}。"
            "只输出 JSON，不要其它文字。"
        )
        resp = await client.chat.completions.create(
            model=model,
            messages=[{"role": "user", "content": prompt}],
            temperature=0,
            response_format={"type": "json_object"},
        )
        data = _loads_lenient(resp.choices[0].message.content)
        if data.get("found"):
            return data.get("answer") or text
        return None
    except Exception as exc:  # noqa: BLE001 —— 任何异常都回退到离线判断
        print(f"  [llm] 调用失败，回退关键词判断：{exc}")
        return keyword_judge(text)
