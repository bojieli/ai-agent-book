"""通过 SpecStream Search API 执行应用端的 web_search 工具。"""

import os
from typing import Any

import requests

SEARCH_URL = "https://api.specstream.ai/v1/web-search"
API_KEY_ENV = "SPECSTREAM_API_KEY"
NUM_RESULTS = 5
SPECSTREAM_SEARCH_TOOL = {
    "type": "function",
    "function": {
        "name": "web_search",
        "description": "联网搜索并返回网页标题、链接和原文摘录。",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "简短的搜索关键词"}
            },
            "required": ["query"],
        },
    },
}


def api_key() -> str:
    return os.environ.get(API_KEY_ENV, "").strip()


def search_impl(arguments: dict[str, Any], *, timeout: float) -> dict[str, Any]:
    """把模型给出的关键词交给 SpecStream，返回与 Parallel 路线同样结构的资料。"""
    query = arguments.get("query") if isinstance(arguments, dict) else None
    if not isinstance(query, str) or not query.strip():
        return {"error": "web_search 需要非空的 query 字符串"}
    key = api_key()
    if not key:
        raise RuntimeError(f"SpecStream 搜索需要 {API_KEY_ENV}")
    try:
        response = requests.post(
            SEARCH_URL,
            headers={"Authorization": f"Bearer {key}"},
            json={"q": query.strip(), "num": NUM_RESULTS},
            timeout=timeout,
            # 不跟随重定向，避免把 Key 和搜索词转发到别的主机。
            allow_redirects=False,
        )
    except requests.RequestException as exc:
        raise RuntimeError(f"SpecStream 请求失败: {exc}") from exc
    if response.status_code != 200:
        try:
            message = response.json()["error"]["message"]
        except (ValueError, KeyError, TypeError):
            message = response.text[:200]
        raise RuntimeError(f"SpecStream 返回 HTTP {response.status_code}: {message}")
    try:
        data = response.json()["data"]
        sources = data["sources"]
    except (ValueError, KeyError, TypeError) as exc:
        raise RuntimeError("SpecStream 未返回可用的搜索结果") from exc
    if not isinstance(sources, list):
        raise RuntimeError("SpecStream 未返回可用的搜索结果")
    results = [
        {
            "title": item.get("title") or "",
            "url": item["url"],
            "excerpts": [item["snippet"]] if item.get("snippet") else [],
        }
        for item in sources
        if isinstance(item, dict) and isinstance(item.get("url"), str)
    ]
    answer = data.get("answer")
    if isinstance(answer, str) and answer.strip():
        return {"answer": answer, "results": results}
    return {"results": results}
