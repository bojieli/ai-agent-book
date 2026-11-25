"""Back LLM (text) agent reached through an OpenAI-compatible chat-completions API.

Configuration comes from the environment so that no credential or private
endpoint is written into the repository:

* ``VTR_BACK_BASE_URL``   default ``https://ark.cn-beijing.volces.com/api/v3``
* ``VTR_BACK_MODEL``      default ``deepseek-v4-pro-ga-260813``
* ``VTR_BACK_API_KEY_ENV`` name of the variable holding the key, default ``ARK_API_KEY``
"""

from __future__ import annotations

import asyncio
import json
import os
import ssl
import time
from typing import Any, Awaitable, Callable
from urllib.parse import urlparse

import httpx

from tools_sim import TOOL_SCHEMAS, to_openai_tool

DEFAULT_BASE_URL = "https://ark.cn-beijing.volces.com/api/v3"
DEFAULT_MODEL = "deepseek-v4-pro-ga-260813"
PUBLIC_HOSTS = {"ark.cn-beijing.volces.com", "api.deepseek.com"}
MAX_STEPS = 6

ToolRunner = Callable[[str, dict[str, Any]], Awaitable[dict[str, Any]]]
Logger = Callable[[dict[str, Any]], None]


class BackClient:
    def __init__(self) -> None:
        self.base_url = os.environ.get("VTR_BACK_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
        self.model = os.environ.get("VTR_BACK_MODEL", DEFAULT_MODEL)
        self.key_env = os.environ.get("VTR_BACK_API_KEY_ENV", "ARK_API_KEY")
        key = os.environ.get(self.key_env)
        if not key:
            raise SystemExit(f"{self.key_env} is not set (back LLM credential)")
        # The default context honours SSL_CERT_FILE, which is needed behind a TLS-inspecting proxy.
        self._http = httpx.AsyncClient(
            verify=ssl.create_default_context(),
            timeout=httpx.Timeout(90, connect=15),
            headers={"Authorization": f"Bearer {key}"},
        )
        self.thinking = os.environ.get("VTR_BACK_THINKING", "disabled")

    def describe(self) -> dict[str, Any]:
        host = urlparse(self.base_url).hostname or ""
        return {
            "model": self.model,
            "endpoint": self.base_url if host in PUBLIC_HOSTS else "<private OpenAI-compatible gateway>",
            "credential_env": self.key_env,
            "thinking": self.thinking,
            "temperature": 0,
        }

    async def close(self) -> None:
        await self._http.aclose()

    async def chat(self, messages: list[dict[str, Any]], tools: list[dict[str, Any]]) -> tuple[dict[str, Any], dict[str, Any], float]:
        body: dict[str, Any] = {"model": self.model, "messages": messages, "temperature": 0}
        if tools:
            body["tools"] = tools
        if self.thinking in ("disabled", "enabled"):
            body["thinking"] = {"type": self.thinking}
        last: Exception | None = None
        for attempt in range(3):
            started = time.monotonic()
            try:
                response = await self._http.post(f"{self.base_url}/chat/completions", json=body)
                if response.status_code >= 500 or response.status_code == 429:
                    raise httpx.HTTPStatusError(f"HTTP {response.status_code}", request=response.request, response=response)
                data = response.json()
                if "choices" not in data:
                    raise RuntimeError(f"back LLM error: {json.dumps(data, ensure_ascii=False)[:400]}")
                return data["choices"][0]["message"], data.get("usage") or {}, time.monotonic() - started
            except (httpx.TransportError, httpx.HTTPStatusError) as exc:
                last = exc
                await asyncio.sleep(0.5 * (attempt + 1))
        raise RuntimeError(f"back LLM failed after retries: {last!r}")


def render_context(transcript: list[dict[str, str]], tool_log: list[dict[str, Any]], task: str) -> str:
    lines = ["【通话记录（语音识别转写）】"]
    for turn in transcript:
        lines.append(("用户：" if turn["role"] == "user" else "助理：") + turn["text"])
    if not transcript:
        lines.append("（空）")
    lines.append("")
    lines.append("【本次通话已执行的工具调用】")
    if not tool_log:
        lines.append("（无）")
    for i, entry in enumerate(tool_log, 1):
        lines.append(
            f"{i}. {entry['name']}({json.dumps(entry['args'], ensure_ascii=False)}) -> "
            f"{json.dumps(entry['result'], ensure_ascii=False)}"
        )
    lines.append("")
    lines.append("【前台委派的任务】")
    lines.append(task)
    return "\n".join(lines)


async def run_back_agent(
    client: BackClient,
    *,
    system: str,
    tool_names: tuple[str, ...],
    transcript: list[dict[str, str]],
    tool_log: list[dict[str, Any]],
    task: str,
    run_tool: ToolRunner,
    log: Logger,
) -> str:
    """Tool loop.  Every chat completion is logged and counts as one LLM call."""
    tools = [to_openai_tool(TOOL_SCHEMAS[name]) for name in tool_names]
    messages: list[dict[str, Any]] = [
        {"role": "system", "content": system},
        {"role": "user", "content": render_context(transcript, tool_log, task)},
    ]
    log({"type": "back.context", "messages": messages})
    for step in range(MAX_STEPS):
        message, usage, seconds = await client.chat(messages, tools)
        calls = message.get("tool_calls") or []
        log(
            {
                "type": "back.llm_call",
                "step": step,
                "seconds": round(seconds, 3),
                "usage": usage,
                "content": message.get("content"),
                "tool_calls": [{"name": c["function"]["name"], "arguments": c["function"]["arguments"]} for c in calls],
            }
        )
        if not calls:
            return (message.get("content") or "").strip()
        messages.append({"role": "assistant", "content": message.get("content") or "", "tool_calls": calls})

        async def one(call: dict[str, Any]) -> dict[str, Any]:
            try:
                args = json.loads(call["function"]["arguments"] or "{}")
            except json.JSONDecodeError:
                return {"role": "tool", "tool_call_id": call["id"], "content": json.dumps({"error": "arguments are not valid JSON"})}
            result = await run_tool(call["function"]["name"], args)
            return {"role": "tool", "tool_call_id": call["id"], "content": json.dumps(result, ensure_ascii=False)}

        messages.extend(await asyncio.gather(*(one(c) for c in calls)))
    return "后台处理超出了步数上限，请稍后再试。"
