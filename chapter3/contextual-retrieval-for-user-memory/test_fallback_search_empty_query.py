"""Regression test: the fallback local search in search_with_context must not
raise ZeroDivisionError on an empty query or on chunks whose contextualized_text
is empty (e.g. loaded from disk with a missing field)."""
import os
import sys
import types

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from contextual_chunking import ContextualConversationChunk
from contextual_indexer import ContextualMemoryIndexer


def _make_indexer(chunks):
    """Build an indexer without __init__; force the retrieval-pipeline call to
    fail so the local-search fallback runs."""
    indexer = ContextualMemoryIndexer.__new__(ContextualMemoryIndexer)
    indexer.retrieval_url = "http://127.0.0.1:1"  # nothing listening -> fallback
    indexer.contextual_chunks = {c.chunk_id: c for c in chunks}
    indexer.memory_manager = types.SimpleNamespace(search_cards=lambda q: [])
    return indexer


def _chunk(chunk_id, contextualized_text):
    return ContextualConversationChunk(
        chunk_id=chunk_id,
        conversation_id="conv1",
        test_id="t1",
        chunk_index=0,
        start_round=0,
        end_round=1,
        messages=[],
        original_text="",
        context="",
        contextualized_text=contextualized_text,
    )


def test_fallback_search_empty_query_and_empty_chunk_text():
    indexer = _make_indexer([_chunk("c1", "")])
    results = indexer.search_with_context("", top_k=3)  # must not raise
    assert results["chunk_results"] == []


def test_fallback_search_normal_query_still_matches():
    indexer = _make_indexer([_chunk("c1", "the user likes blue shoes")])
    results = indexer.search_with_context("blue", top_k=3)
    assert len(results["chunk_results"]) == 1
    assert results["chunk_results"][0]["chunk_id"] == "c1"
