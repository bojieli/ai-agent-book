"""Case-insensitive ASCII retrieval with and without jieba."""

import builtins

import pytest

from offline_retriever import OfflineRetriever


@pytest.mark.parametrize("use_jieba", [True, False])
def test_english_query_matches_document_regardless_of_case(tmp_path, monkeypatch, use_jieba):
    if use_jieba:
        pytest.importorskip("jieba")
    else:
        original_import = builtins.__import__

        def import_without_jieba(name, *args, **kwargs):
            if name == "jieba":
                raise ImportError("simulate optional dependency being unavailable")
            return original_import(name, *args, **kwargs)

        monkeypatch.setattr(builtins, "__import__", import_without_jieba)

    (tmp_path / "guide.md").write_text(
        "HTTP error troubleshooting guide", encoding="utf-8"
    )
    retriever = OfflineRetriever(str(tmp_path))
    assert [r["text"] for r in retriever.search("http")] == [
        "HTTP error troubleshooting guide"
    ]
    assert [r["text"] for r in retriever.search("HTTP")] == [
        "HTTP error troubleshooting guide"
    ]
