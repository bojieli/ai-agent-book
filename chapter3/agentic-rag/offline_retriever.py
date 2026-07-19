"""In-process offline retriever (BM25 over the local law corpus).

This backend makes the whole experiment runnable without the external
`retrieval-pipeline` HTTP service: it reads the Markdown law files under
``laws/``, splits them into article-level chunks (每一条法条一个 chunk), and
scores queries with Okapi BM25. Retrieval therefore runs fully offline with no
API key and no server; only the LLM answer-generation step (in ``agent.py``)
still needs a provider API.

Chinese text is tokenised with ``jieba`` when available, falling back to a
character uni/bi-gram tokeniser so the module works with only the standard
library installed.
"""

import os
import re
import math
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional
from collections import Counter, defaultdict

logger = logging.getLogger(__name__)


# Article marker at the start of a line, e.g. 第二百三十五条 / 第一百三十三条之一
_ARTICLE_RE = re.compile(r"^第[一二三四五六七八九十百千零两0-9]+条(?:之[一二三四五六七八九十0-9]+)?")


def _tokenize(text: str) -> List[str]:
    """Tokenise mixed Chinese/English text.

    Prefers jieba; otherwise emits ASCII words plus Chinese character uni- and
    bi-grams, which is enough for lexical BM25 matching without extra deps.
    """
    try:
        import jieba  # type: ignore
        return [t for t in jieba.cut(text) if t.strip()]
    except Exception:
        tokens: List[str] = []
        for m in re.findall(r"[a-zA-Z0-9]+|[一-鿿]+", text):
            if m[0].isascii():
                tokens.append(m.lower())
            else:
                tokens.extend(list(m))  # unigrams
                tokens.extend(m[i:i + 2] for i in range(len(m) - 1))  # bigrams
        return tokens


class OfflineRetriever:
    """Okapi BM25 retriever over article-level chunks of the law corpus."""

    def __init__(self,
                 corpus_path: str = "laws",
                 k1: float = 1.5,
                 b: float = 0.75,
                 extensions: Optional[List[str]] = None):
        self.corpus_path = corpus_path
        self.k1 = k1
        self.b = b
        self.extensions = extensions or [".md", ".txt"]

        self.chunks: List[Dict[str, Any]] = []          # {doc_id, chunk_id, title, category, text}
        self.documents: Dict[str, Dict[str, Any]] = {}   # doc_id -> {title, category, file, content}
        self._doc_freqs: List[Counter] = []              # per-chunk term frequencies
        self._doc_lens: List[int] = []
        self._df: Dict[str, int] = defaultdict(int)      # document frequency per term
        self._idf: Dict[str, float] = {}
        self._avg_len: float = 0.0

        self._build_index()

    # ------------------------------------------------------------------ build
    def _iter_files(self):
        root = Path(self.corpus_path)
        if not root.exists():
            logger.warning(f"Offline corpus path not found: {root}")
            return
        for path in sorted(root.rglob("*")):
            if path.is_file() and path.suffix in self.extensions:
                yield path

    def _split_articles(self, content: str) -> List[str]:
        """Split a law document into article-level chunks.

        Falls back to blank-line paragraph grouping when the file has no
        ``第X条`` markers (e.g. non-statute documents).
        """
        lines = content.splitlines()
        articles: List[str] = []
        current: List[str] = []
        seen_article = False

        for line in lines:
            if _ARTICLE_RE.match(line.strip()):
                seen_article = True
                if current:
                    articles.append("\n".join(current).strip())
                current = [line]
            else:
                current.append(line)
        if current:
            articles.append("\n".join(current).strip())

        if not seen_article:
            # No article markers: group by blank lines into ~paragraph chunks.
            articles = [p.strip() for p in content.split("\n\n") if p.strip()]

        return [a for a in articles if a]

    def _build_index(self):
        for path in self._iter_files():
            try:
                content = path.read_text(encoding="utf-8")
            except Exception as e:
                logger.error(f"Error reading {path}: {e}")
                continue

            category = path.parent.name
            title = path.stem
            doc_id = f"{category}/{title}"
            self.documents[doc_id] = {
                "doc_id": doc_id,
                "title": title,
                "category": category,
                "file": str(path),
                "content": content,
            }

            for idx, article in enumerate(self._split_articles(content)):
                if len(article) < 4:
                    continue
                chunk_id = f"{doc_id}_chunk_{idx}"
                self.chunks.append({
                    "doc_id": doc_id,
                    "chunk_id": chunk_id,
                    "title": title,
                    "category": category,
                    "text": article,
                })

        # Build BM25 statistics.
        for chunk in self.chunks:
            tf = Counter(_tokenize(chunk["text"]))
            self._doc_freqs.append(tf)
            self._doc_lens.append(sum(tf.values()))
            for term in tf:
                self._df[term] += 1

        n = len(self.chunks)
        self._avg_len = (sum(self._doc_lens) / n) if n else 0.0
        for term, df in self._df.items():
            # BM25 idf with +1 to stay non-negative.
            self._idf[term] = math.log(1 + (n - df + 0.5) / (df + 0.5))

        logger.info(
            f"OfflineRetriever indexed {n} chunks from {len(self.documents)} "
            f"documents under '{self.corpus_path}'"
        )

    # ----------------------------------------------------------------- search
    def search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """Return the ``top_k`` article chunks scored by BM25 for ``query``."""
        if not self.chunks:
            return []

        q_terms = _tokenize(query)
        scored: List[tuple] = []
        for i, tf in enumerate(self._doc_freqs):
            dl = self._doc_lens[i]
            score = 0.0
            for term in q_terms:
                f = tf.get(term)
                if not f:
                    continue
                idf = self._idf.get(term, 0.0)
                denom = f + self.k1 * (1 - self.b + self.b * dl / (self._avg_len or 1))
                score += idf * (f * (self.k1 + 1)) / denom
            if score > 0:
                scored.append((score, i))

        scored.sort(reverse=True)
        results: List[Dict[str, Any]] = []
        for score, i in scored[:top_k]:
            chunk = self.chunks[i]
            results.append({
                "doc_id": chunk["doc_id"],
                "chunk_id": chunk["chunk_id"],
                "text": chunk["text"],
                "score": float(score),
                "metadata": {
                    "title": chunk["title"],
                    "category": chunk["category"],
                    "source": "offline",
                },
            })
        return results

    def get_document(self, doc_id: str) -> Dict[str, Any]:
        """Return the full source document for ``doc_id``."""
        doc = self.documents.get(doc_id)
        if not doc:
            return {"error": f"Document {doc_id} not found"}
        return {
            "doc_id": doc_id,
            "content": doc["content"],
            "metadata": {
                "title": doc["title"],
                "category": doc["category"],
                "file": doc["file"],
                "source": "offline",
            },
        }
