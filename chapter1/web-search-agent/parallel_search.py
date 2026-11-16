"""通过 Parallel MCP 执行应用端的 web_search 工具。"""

import asyncio
import logging
from typing import Any


MCP_URL = "https://mcp.parallel.ai/mcp"
logger = logging.getLogger(__name__)
PARALLEL_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "联网搜索并返回网页标题、链接和原文摘录。",
        "parameters": {
            "type": "object",
            "properties": {"query": {"type": "string", "description": "简短的搜索关键词"}},
            "required": ["query"],
        },
    },
}


def search_impl(arguments: dict[str, Any], *, timeout: float) -> dict[str, Any]:
    """把模型给出的关键词交给 Parallel，返回供下一轮引用的资料。"""
    query = arguments.get("query") if isinstance(arguments, dict) else None
    if not isinstance(query, str) or not query.strip():
        return {"error": "web_search 需要非空的 query 字符串"}
    return asyncio.run(_search(query.strip(), timeout))


async def _search(query: str, timeout: float) -> dict[str, Any]:
    try:
        import httpx
        from mcp import ClientSession
        from mcp.client.streamable_http import streamable_http_client
    except ImportError as exc:
        raise RuntimeError("Parallel 搜索需要 MCP SDK，请按本实验 README 安装依赖") from exc

    async def reject_redirect(response: httpx.Response) -> None:
        # SDK 在部分请求中会显式启用重定向。先拦截响应，避免转发搜索词或会话 ID。
        if response.is_redirect:
            response.raise_for_status()

    async with httpx.AsyncClient(
        headers={"User-Agent": "ai-agent-book/1.0"},
        follow_redirects=False,
        trust_env=False,
        timeout=timeout,
        event_hooks={"response": [reject_redirect]},
    ) as client:
        get_session_id = None
        cleanup_headers = {}
        try:
            # 在 SDK 的任务组退出后关闭远端会话，避免取消搜索时跳过 DELETE。
            async with asyncio.timeout(timeout):
                async with streamable_http_client(
                    MCP_URL, http_client=client, terminate_on_close=False
                ) as (read, write, get_session_id):
                    async with ClientSession(read, write) as session:
                        init = await session.initialize()
                        cleanup_headers["Mcp-Protocol-Version"] = init.protocolVersion
                        result = await session.call_tool(
                            "web_search",
                            arguments={
                                "objective": f"Find authoritative sources and excerpts about: {query}",
                                "search_queries": [query],
                            },
                        )
        except TimeoutError as exc:
            raise RuntimeError(f"Parallel MCP 请求超过 {timeout:g} 秒") from exc
        except ExceptionGroup as exc:
            raise RuntimeError(f"Parallel MCP 请求失败: {exc.exceptions[0]}") from exc
        finally:
            session_id = get_session_id() if get_session_id else None
            if session_id:
                cleanup_headers["Mcp-Session-Id"] = session_id
                try:
                    async with asyncio.timeout(min(timeout, 2)):
                        async with client.stream(
                            "DELETE", MCP_URL, headers=cleanup_headers
                        ) as response:
                            if response.status_code != 405:
                                response.raise_for_status()
                except (TimeoutError, httpx.HTTPError) as exc:
                    logger.warning("Parallel MCP 会话关闭失败: %s", exc)

    data = result.structuredContent
    if result.isError or data is None or not isinstance(data.get("results"), list):
        raise RuntimeError("Parallel MCP 未返回可用的搜索结果")
    return data
