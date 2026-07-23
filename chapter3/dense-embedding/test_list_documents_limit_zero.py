"""list_documents(limit=0) must return an empty page, not all documents."""
import sys
from pathlib import Path
from unittest.mock import MagicMock

# logger.py imports colorlog at module import time.
sys.modules.setdefault("colorlog", MagicMock())

HERE = Path(__file__).resolve().parent
if str(HERE) not in sys.path:
    sys.path.insert(0, str(HERE))

from document_store import DocumentStore


def test_list_documents_limit_zero():
    store = DocumentStore()
    for i in range(3):
        store.add_document(f"content {i}", doc_id=f"id-{i}", metadata={"n": i})
    assert store.list_documents(0) == []
    assert len(store.list_documents(1)) == 1
    assert len(store.list_documents()) == 3
    assert len(store.list_documents(None)) == 3
