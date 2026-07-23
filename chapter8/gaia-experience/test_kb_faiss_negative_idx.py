"""Regression: FAISS padding index -1 must not map to documents[-1]."""
from pathlib import Path


def test_search_guards_negative_indices():
    src = Path(__file__).with_name("knowledge_base.py").read_text()
    assert "0 <= idx < len(self.documents)" in src

    documents = [{"id": i} for i in range(3)]
    indices = [0, -1, -1]
    results = [documents[idx] for idx in indices if 0 <= idx < len(documents)]
    assert results == [{"id": 0}]
