import asyncio
import json
import os
import sys
import types

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

# Optional runtime deps for importing the chapter module in unit tests.
sys.modules.setdefault("wikipedia", types.ModuleType("wikipedia"))
sys.modules.setdefault("dotenv", types.SimpleNamespace(load_dotenv=lambda: None))
mcp = types.ModuleType("mcp")
mcp_types = types.ModuleType("mcp.types")

class TextContent:
    def __init__(self, **kwargs):
        self.__dict__.update(kwargs)

mcp_types.TextContent = TextContent
sys.modules["mcp"] = mcp
sys.modules["mcp.types"] = mcp_types

from wiki_enhanced import get_article_history


def test_year_only_date_returns_error_payload():
    result = asyncio.run(get_article_history("Python", "2025"))
    payload = json.loads(result.text)
    assert payload["success"] is False
    msg = str(payload["message"])
    assert "date must be" in msg or "Failed" in msg
