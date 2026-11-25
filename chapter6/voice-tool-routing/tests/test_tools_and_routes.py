"""Offline tests: simulated tools, latency schedule and route wiring (no network)."""

import hashlib
import json
from pathlib import Path

import pytest

import tools_sim
from routes import ROUTES, back_instructions, front_instructions, front_tools

ROOT = Path(__file__).resolve().parents[1]


def test_fixed_latencies_match_the_design():
    assert tools_sim.latency_for("get_weather", "weather", 0, 0) == 0.2
    assert tools_sim.latency_for("memory_lookup", "memory", 3, 0) == 0.02
    assert tools_sim.latency_for("web_search", "web_search", 9, 0) == 3.0


def test_sampled_latencies_are_seeded_bounded_and_route_independent():
    values = [tools_sim.latency_for("search_flights", "flight_search", run, 0) for run in range(50)]
    assert all(2.0 <= v <= 5.0 for v in values)
    assert len(set(values)) > 40
    # The key has no route component, so every route replays the same sequence.
    assert values == [tools_sim.latency_for("search_flights", "flight_search", run, 0) for run in range(50)]
    assert tools_sim.latency_for("book_flight", "booking", 0, 0) != tools_sim.latency_for("book_flight", "booking", 0, 1)


def test_flight_search_returns_speak_and_display():
    result = tools_sim.execute("search_flights", {"origin": "北京", "destination": "上海", "date": "2026-12-03"})
    assert "680" in result["speak"] and len(result["display"]) == 6
    row = next(r for r in result["display"] if r["depart"] == "09:00")
    assert row["offer_id"] == "OFR-1203-MU5103-7K2Q"
    assert {"cabin": "economy", "fare_rule": "flexible", "price_cny": 910}.items() <= row["fares"][1].items()
    assert "error" in tools_sim.execute("search_flights", {"origin": "北京市", "destination": "上海", "date": "2026-12-03"})


def test_booking_is_lenient_so_wrong_orders_are_visible():
    receipt = tools_sim.execute("book_flight", {"offer_id": "WRONG"})
    assert receipt["status"] == "confirmed" and receipt["order_id"].startswith("ORD-")


def test_routes_expose_the_agreed_tool_sets():
    names = lambda route: [t["name"] for t in front_tools(ROUTES[route])]
    assert names("all_front") == ["get_weather", "memory_lookup", "web_search", "search_flights", "book_flight"]
    assert names("all_back") == ["delegate"]
    assert names("by_property_flight_front") == ["get_weather", "search_flights", "delegate"]
    assert names("by_property_flight_back") == ["get_weather", "delegate"]
    for route in ROUTES.values():
        assert ("EK3927461" in front_instructions(route)) == route.inject_memory
        if route.delegates:
            assert "book_flight" in back_instructions(route)
    assert "memory_lookup" not in ROUTES["by_property_flight_front"].back_tools


def test_audio_fixtures_match_manifest():
    manifest = json.loads((ROOT / "fixtures/audio/manifest.json").read_text(encoding="utf-8"))
    paths = {name: ROOT / "fixtures/audio" / clip["file"] for name, clip in manifest["clips"].items()}
    if not any(path.is_file() for path in paths.values()):
        pytest.skip("WAV fixtures are not committed; run prepare_fixtures.py to regenerate them")
    for name, clip in manifest["clips"].items():
        path = paths[name]
        assert hashlib.sha256(path.read_bytes()).hexdigest() == clip["sha256"], name
