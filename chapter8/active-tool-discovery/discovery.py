"""
主动工具发现的核心：用嵌入向量相似度，从 126 个工具里
按自然语言"能力需求"检索出最相关的 3-5 个候选工具。

- 工具向量：对每个工具用 "name: description" 生成 embedding，并缓存到本地
  .cache/tool_embeddings_<embedder>.json，避免每次运行都重新计算。
- discover_tools(need)：把 need 向量化，与工具向量做余弦相似度，返回 top-k。

嵌入后端是可插拔的（见 `Embedder` 协议）：
- OpenAIEmbedder：调用 OpenAI embeddings API（默认，联网，效果最好）。
- 离线模式（--offline）使用 offline_backend.LocalEmbedder（本地哈希词袋，无需 API），
  用于在没有 key 时验证整条流水线与量化 token/延迟。
"""

import hashlib
import json
import os
import re
from typing import Dict, List, Tuple

from tools_library import ALL_TOOLS

EMBED_MODEL = os.getenv("EMBED_MODEL", "text-embedding-3-small")
_CACHE_DIR = os.path.join(os.path.dirname(__file__), ".cache")


def _tool_text(tool: Dict) -> str:
    f = tool["function"]
    return f"{f['name']}: {f['description']}"


def _cosine(a: List[float], b: List[float]) -> float:
    dot = sum(x * y for x, y in zip(a, b))
    na = sum(x * x for x in a) ** 0.5
    nb = sum(y * y for y in b) ** 0.5
    return dot / (na * nb + 1e-9)


class OpenAIEmbedder:
    """基于 OpenAI embeddings API 的嵌入后端。"""

    def __init__(self, client, model: str = None):
        self.client = client
        self.model = model or EMBED_MODEL
        self.name = self.model

    def embed(self, texts: List[str]) -> List[List[float]]:
        resp = self.client.embeddings.create(model=self.model, input=texts)
        return [d.embedding for d in resp.data]


class ToolIndex:
    """工具向量索引 + 相似度检索。

    embedder: 具备 `.embed(texts) -> List[vec]` 与 `.name` 的对象；
              为向后兼容，也可直接传入 OpenAI client（会自动包装为 OpenAIEmbedder）。
    tools:    参与索引的工具子集，缺省为全部 ALL_TOOLS（配合 --tool-set-size 使用）。
    """

    def __init__(self, embedder, tools: List[Dict] = None):
        self.embedder = embedder if hasattr(embedder, "embed") else OpenAIEmbedder(embedder)
        tools = tools if tools is not None else ALL_TOOLS
        self.names = [t["function"]["name"] for t in tools]
        self.texts = [_tool_text(t) for t in tools]
        self.vectors = self._load_or_build()

    def _cache_file(self) -> str:
        safe = re.sub(r"[^A-Za-z0-9_.-]", "_", self.embedder.name)
        return os.path.join(_CACHE_DIR, f"tool_embeddings_{safe}.json")

    def _signature(self) -> str:
        h = hashlib.sha256()
        h.update(self.embedder.name.encode())
        for t in self.texts:
            h.update(t.encode())
        return h.hexdigest()[:16]

    def _load_or_build(self) -> Dict[str, List[float]]:
        sig = self._signature()
        cache_file = self._cache_file()
        if os.path.exists(cache_file):
            try:
                cached = json.load(open(cache_file, encoding="utf-8"))
                if cached.get("signature") == sig:
                    return cached["vectors"]
            except Exception:
                pass
        # 缓存缺失或失效 -> 调用嵌入后端批量生成
        print(f"[discovery] 正在用 {self.embedder.name} 为 {len(self.texts)} 个工具生成嵌入向量 ...")
        embeddings = self.embedder.embed(self.texts)
        vectors = {name: vec for name, vec in zip(self.names, embeddings)}
        os.makedirs(_CACHE_DIR, exist_ok=True)
        json.dump({"signature": sig, "vectors": vectors},
                  open(cache_file, "w", encoding="utf-8"))
        return vectors

    def search(self, need: str, top_k: int = 4) -> List[Tuple[str, float]]:
        """返回与 need 最相关的 top_k 个 (工具名, 相似度)。"""
        q = self.embedder.embed([need])[0]
        scored = [(name, _cosine(q, self.vectors[name])) for name in self.names]
        scored.sort(key=lambda x: x[1], reverse=True)
        return scored[:top_k]
