"""Null optional num_results must use default 6."""
import base_tools


def test_null_num_results_like_omit(monkeypatch):
    seen = {}

    def fake_parse(endpoint, html, num_results):
        seen["n"] = num_results
        return [{"title": "t", "url": "https://example.com", "snippet": ""}]

    class Resp:
        status_code = 200
        text = "<html></html>"
        def raise_for_status(self):
            return None

    monkeypatch.setattr(base_tools.requests, "post", lambda *a, **k: Resp())
    monkeypatch.setattr(base_tools, "_parse_ddg", fake_parse)
    monkeypatch.setattr(base_tools.time, "sleep", lambda *_: None)
    out = base_tools.web_search("python", num_results=None)
    assert out["success"] is True
    assert seen["n"] == 6
