#!/usr/bin/env python3
"""Derive every reported metric from the saved session traces.

Definitions (also restated in README.md):

* ``speech_end``     the moment the last 20 ms frame of the user's recording left the client.
* substantive answer the model's speech that follows a tool/delegate result.  Its text starts at the
                     first ``response.output_text.delta`` that arrives after the result of the last
                     function call the front model emitted in that turn was uploaded; its audio
                     starts at the first ``response.output_audio.delta`` at or after that text delta.
                     When the front model made no function call in the turn, the first text/audio
                     after ``speech_end`` is the answer.
* filler             any audio that arrives after ``speech_end`` but before the answer text starts
                     (for example "好的，我查一下").
* LLM calls          front: one per ``response.function_call_arguments.done`` event plus one for the
                     spoken continuation after the results (or one for a turn answered without a
                     tool); back: one per chat completion.
"""

from __future__ import annotations

import argparse
import json
import re
import statistics
from collections import defaultdict
from pathlib import Path
from typing import Any

from tools_sim import FREQUENT_FLYER_DIGITS, PROFILE, cheapest_price, flight_rows, flight_speak, offer_id

HERE = Path(__file__).resolve().parent
OUTPUT_BYTES_PER_SECOND = 48000

EXPECTED_CALL = {
    "weather": ("get_weather", {"city": "杭州", "date": "2026-11-26"}),
    "memory": ("memory_lookup", {"topic": "frequent_flyer"}),
    "web_search": ("web_search", None),  # free text: scored by required keywords
    "flight_search": ("search_flights", {"origin": "北京", "destination": "上海", "date": "2026-12-03"}),
    "self_correction": ("search_flights", {"origin": "北京", "destination": "上海", "date": "2026-12-03"}),
}
WEB_QUERY_KEYWORDS = ("虹桥", "会展中心")
EXPECTED_BOOKING = {
    "offer_id": "OFR-1203-MU5103-7K2Q",
    "cabin": "economy",
    "fare_rule": "flexible",
    "quoted_price_cny": 910,
    "baggage": {"extra_checked_pieces": 1, "weight_kg": 23},
    "passengers": [{"name": PROFILE["name"], "id_type": PROFILE["id_type"], "id_number": PROFILE["id_number"], "phone": PROFILE["phone"]}],
    "contact": {"name": PROFILE["name"], "phone": PROFILE["phone"], "email": PROFILE["email"]},
}
# field -> (where its value comes from, getter)
BOOKING_FIELDS: dict[str, tuple[str, Any]] = {
    "offer_id": ("search_result", lambda a: a.get("offer_id")),
    "quoted_price_cny": ("search_result", lambda a: a.get("quoted_price_cny")),
    "cabin": ("heard", lambda a: a.get("cabin")),
    "fare_rule": ("heard", lambda a: a.get("fare_rule")),
    "baggage.extra_checked_pieces": ("heard", lambda a: (a.get("baggage") or {}).get("extra_checked_pieces")),
    "baggage.weight_kg": ("heard", lambda a: (a.get("baggage") or {}).get("weight_kg")),
    "passengers[0].name": ("memory", lambda a: _first(a.get("passengers")).get("name")),
    "passengers[0].id_type": ("memory", lambda a: _first(a.get("passengers")).get("id_type")),
    "passengers[0].id_number": ("memory", lambda a: _first(a.get("passengers")).get("id_number")),
    "passengers[0].phone": ("memory", lambda a: _first(a.get("passengers")).get("phone")),
    "contact.name": ("memory", lambda a: (a.get("contact") or {}).get("name")),
    "contact.phone": ("memory", lambda a: (a.get("contact") or {}).get("phone")),
    "contact.email": ("memory", lambda a: (a.get("contact") or {}).get("email")),
}
# Extension scenario: passenger details are dictated by voice (fictional colleague); contact stays the user.
DICTATED_PASSENGER = {"name": "陈嘉怡", "id_type": "passport", "id_number": "E58307194", "phone": "13900007246"}
EXPECTED_BOOKING_DICTATED = {**EXPECTED_BOOKING, "passengers": [DICTATED_PASSENGER]}
BOOKING_VARIANTS = {
    "booking": (EXPECTED_BOOKING, {}),
    "booking_dictated": (
        EXPECTED_BOOKING_DICTATED,
        {f"passengers[0].{k}": "heard_dictated" for k in ("name", "id_type", "id_number", "phone")},
    ),
}
_CN_DIGITS = str.maketrans("零〇一二三四五六七八九两", "001234567892")


def _first(value: Any) -> dict[str, Any]:
    return value[0] if isinstance(value, list) and value and isinstance(value[0], dict) else {}


def _strip(value: Any) -> Any:
    if isinstance(value, str):
        return value.strip()
    if isinstance(value, dict):
        return {k: _strip(v) for k, v in value.items()}
    if isinstance(value, list):
        return [_strip(v) for v in value]
    return value


def exact(args: Any, expected: Any) -> bool:
    """Exact match after trimming surrounding whitespace of strings; types must match (23 != "23")."""
    a, e = _strip(args), _strip(expected)
    if isinstance(e, dict):
        return isinstance(a, dict) and set(a) == set(e) and all(exact(a[k], e[k]) for k in e)
    if isinstance(e, list):
        return isinstance(a, list) and len(a) == len(e) and all(exact(x, y) for x, y in zip(a, e))
    return type(a) is type(e) and a == e


def digits_only(text: str) -> str:
    return re.sub(r"\D", "", text.translate(_CN_DIGITS))


def compact(text: str) -> str:
    return re.sub(r"\s+", "", text)


def percentile(values: list[float], q: float) -> float | None:
    """Linear interpolation between closest ranks (the numpy default)."""
    if not values:
        return None
    data = sorted(values)
    pos = (len(data) - 1) * q
    low = int(pos)
    high = min(low + 1, len(data) - 1)
    return data[low] + (data[high] - data[low]) * (pos - low)


# --------------------------------------------------------------- trace parsing
def load_trace(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


class Session:
    def __init__(self, events: list[dict[str, Any]]) -> None:
        self.events = events
        self.clips: list[dict[str, Any]] = []
        self.asr: list[tuple[float, str]] = []
        self.asr_started: list[float] = []
        self.fcs: list[dict[str, Any]] = []
        self.uploads: list[dict[str, Any]] = []
        self.text: list[tuple[float, str]] = []
        self.text_done: list[tuple[float, str]] = []
        self.audio: list[tuple[float, int]] = []
        self.tools: list[dict[str, Any]] = []
        self.tool_results: list[dict[str, Any]] = []
        self.back_calls: list[dict[str, Any]] = []
        self.delegates: list[dict[str, Any]] = []
        self.errors: list[dict[str, Any]] = []
        self.end = events[-1]["t"] if events else 0.0
        open_clip: dict[str, Any] | None = None
        for e in events:
            kind, t = e.get("type"), e["t"]
            if kind == "user_audio.start":
                open_clip = {"clip": e["clip"], "start": t, "end": None}
                self.clips.append(open_clip)
            elif kind == "user_audio.end" and open_clip is not None:
                open_clip["end"] = t
            elif kind == "conversation.item.input_audio_transcription.started":
                self.asr_started.append(t)
            elif kind == "conversation.item.input_audio_transcription.completed":
                self.asr.append((t, e.get("text") or e.get("transcript") or ""))
            elif kind == "response.function_call_arguments.done":
                items = []
                for item in e.get("items") or []:
                    try:
                        args = json.loads(item.get("arguments") or "{}")
                    except json.JSONDecodeError:
                        args = {"_invalid_json": item.get("arguments")}
                    items.append({"name": item.get("name"), "args": args, "call_id": item.get("call_id")})
                self.fcs.append({"t": t, "items": items})
            elif kind == "conversation.item.create" and e["dir"] == "up":
                ids = [i.get("call_id") for i in e.get("items") or [] if i.get("role") == "tool"]
                if ids:
                    self.uploads.append({"t": t, "call_ids": ids})
            elif kind == "response.output_text.delta":
                self.text.append((t, e.get("delta") or ""))
            elif kind == "response.output_text.done":
                self.text_done.append((t, e.get("text") or ""))
            elif kind == "response.output_audio.delta":
                self.audio.append((t, e.get("audio_bytes") or 0))
            elif kind == "tool.call":
                self.tools.append(e)
            elif kind == "tool.result":
                self.tool_results.append(e)
            elif kind == "back.llm_call":
                self.back_calls.append(e)
            elif kind == "delegate.start":
                self.delegates.append(e)
            elif kind in ("error", "runtime.error", "turn.timeout", "ws.closed"):
                self.errors.append(e)

    def pending_at(self, t: float, fcs: list[dict[str, Any]] | None = None) -> bool:
        """True if a function call (of ``fcs``, default all) emitted before ``t`` is still unanswered at ``t``."""
        answered = {cid: u["t"] for u in self.uploads for cid in u["call_ids"]}
        for fc in self.fcs if fcs is None else fcs:
            if fc["t"] > t:
                continue
            for item in fc["items"]:
                if answered.get(item["call_id"], float("inf")) > t:
                    return True
        return False

    def window(self, index: int) -> dict[str, Any]:
        """Metrics for the turn that starts with clip ``index`` and ends when the next clip starts."""
        clip = self.clips[index]
        start = clip["start"]
        stop = self.clips[index + 1]["start"] if index + 1 < len(self.clips) else self.end + 1
        speech_end = clip["end"]
        fcs = [f for f in self.fcs if start <= f["t"] < stop]
        uploads = [u for u in self.uploads if start <= u["t"] < stop]
        # The substantive answer follows the result of the LAST function call the front model emitted
        # in this turn.  Results of a superseded call from the previous turn may also be uploaded in
        # this window; they do not start the answer.
        ready_t: float | None = speech_end
        if fcs:
            last_ids = {item["call_id"] for item in fcs[-1]["items"]}
            matching = [u["t"] for u in uploads if last_ids & set(u["call_ids"])]
            ready_t = matching[0] if matching else None
        answer_text_t = next((t for t, _ in self.text if ready_t is not None and max(ready_t, speech_end) <= t < stop), None)
        answer_audio_t = next((t for t, _ in self.audio if answer_text_t is not None and answer_text_t <= t < stop), None)
        limit = answer_text_t if answer_text_t is not None else stop
        filler_audio = [(t, n) for t, n in self.audio if speech_end <= t < limit]
        filler_text = "".join(d for t, d in self.text if speech_end <= t < limit)
        answer_text = "".join(d for t, d in self.text if answer_text_t is not None and answer_text_t <= t < stop)
        answer_audio_bytes = sum(n for t, n in self.audio if answer_text_t is not None and answer_text_t <= t < stop)
        asr = [(t, text) for t, text in self.asr if start <= t < stop]
        tools = [e for e in self.tools if start <= e["t"] < stop]
        back = [e for e in self.back_calls if start <= e["t"] < stop]
        front_calls = len(fcs) + (1 if answer_text_t is not None or (not fcs and filler_text) else 0)
        return {
            "clip": clip["clip"],
            "start": start,
            "stop": stop,
            "speech_end": speech_end,
            "asr_text": " | ".join(text for _, text in asr) if asr else None,
            "asr_done_s": round(asr[-1][0] - speech_end, 3) if asr else None,
            "asr_rounds": len(asr),
            "fc": [{"t": round(f["t"] - speech_end, 3), "items": [{"name": i["name"], "args": i["args"]} for i in f["items"]]} for f in fcs],
            "text_before_last_result": bool(fcs) and ready_t is not None and any(fcs[-1]["t"] <= t < ready_t for t, d in self.text if d.strip()),
            "first_fc_s": round(fcs[0]["t"] - speech_end, 3) if fcs else None,
            "fc_after_asr_s": round(fcs[0]["t"] - asr[-1][0], 3) if fcs and asr and fcs[0]["t"] >= asr[-1][0] else None,
            "first_fc_name": fcs[0]["items"][0]["name"] if fcs and fcs[0]["items"] else None,
            "fc_before_speech_end": sum(1 for f in fcs if f["t"] < speech_end),
            "last_upload_s": round(uploads[-1]["t"] - speech_end, 3) if uploads else None,
            "filler": bool(filler_audio),
            "filler_audio_s": round(filler_audio[0][0] - speech_end, 3) if filler_audio else None,
            "filler_text": filler_text,
            "answer_text_s": round(answer_text_t - speech_end, 3) if answer_text_t is not None else None,
            "answer_audio_s": round(answer_audio_t - speech_end, 3) if answer_audio_t is not None else None,
            "answer_after_result_s": round(answer_audio_t - max(u["t"] for u in uploads if u["t"] <= answer_audio_t), 3)
            if answer_audio_t is not None and any(u["t"] <= answer_audio_t for u in uploads)
            else None,
            "answer_text": answer_text,
            "answer_audio_seconds": round(answer_audio_bytes / OUTPUT_BYTES_PER_SECOND, 2),
            "front_llm_calls": front_calls,
            "back_llm_calls": len(back),
            "back_llm_seconds": round(sum(e["seconds"] for e in back), 3),
            "llm_calls": front_calls + len(back),
            "tools": [{"t": round(e["t"] - speech_end, 3), "origin": e["origin"], "name": e["name"], "args": e["args"], "latency_s": e["latency_s"]} for e in tools],
            "tool_latency_s": round(sum(e["latency_s"] for e in tools), 3),
            "delegate_tasks": [d.get("task") for d in self.delegates if start <= d["t"] < stop],
        }


def back_unexplained_seconds(events: list[dict[str, Any]]) -> float:
    """Wall-clock time inside delegations that neither a logged back LLM call nor an injected tool
    latency explains.  The back client retries HTTP 429/5xx without logging the failed attempts, so a
    value well above zero means a retry inflated the delegated latency; such sessions are rerun."""
    worst = 0.0
    starts = {e["call_id"]: e["t"] for e in events if e.get("type") == "delegate.start"}
    for e in events:
        if e.get("type") != "delegate.end" or e.get("call_id") not in starts:
            continue
        t0, t1 = starts[e["call_id"]], e["t"]
        llm = sorted((x for x in events if x.get("type") == "back.llm_call" and x.get("call_id") == e["call_id"]), key=lambda x: x["t"])
        tools = [x for x in events if x.get("type") == "tool.call" and x.get("origin") == "back" and t0 <= x["t"] <= t1]
        tool_time = 0.0
        for i, call in enumerate(llm):
            nxt = llm[i + 1]["t"] if i + 1 < len(llm) else t1 + 1
            group = [x["latency_s"] for x in tools if call["t"] <= x["t"] < nxt]
            tool_time += max(group) if group else 0.0  # parallel tool calls of one step overlap
        worst = max(worst, (t1 - t0) - sum(x["seconds"] for x in llm) - tool_time)
    return round(worst, 3)


BACK_RETRY_THRESHOLD_S = 0.5

# ------------------------------------------------------------------- scoring
def score_expected_call(scenario: str, window: dict[str, Any], route_has_tool: bool) -> dict[str, Any]:
    name, expected = EXPECTED_CALL[scenario]
    calls = [t for t in window["tools"] if t["name"] == name]

    def ok(args: dict[str, Any]) -> bool:
        if expected is None:
            query = args.get("query")
            return isinstance(query, str) and set(args) == {"query"} and all(k in query for k in WEB_QUERY_KEYWORDS)
        return exact(args, expected)

    return {
        "expected_tool": name,
        "tool_expected_in_route": route_has_tool,
        "tool_called": bool(calls),
        "n_calls": len(calls),
        "first_call_exact": ok(calls[0]["args"]) if calls else None,
        "last_call_exact": ok(calls[-1]["args"]) if calls else None,
        "first_call_args": calls[0]["args"] if calls else None,
        "called_by": calls[0]["origin"] if calls else None,
    }


def key_fact(scenario: str, text: str) -> bool:
    flat = compact(text)
    if scenario == "weather":
        return "17" in flat or "十七" in flat
    if scenario == "memory":
        return FREQUENT_FLYER_DIGITS in digits_only(flat)
    if scenario == "web_search":
        return "2号线" in flat or "二号线" in flat
    if scenario in ("flight_search", "self_correction"):
        return str(cheapest_price("2026-12-03")) in flat
    return False


def flight_readout(text: str, date: str) -> dict[str, Any]:
    flat = compact(text).upper()
    rows = flight_rows(date)
    flights = sum(1 for r in rows if r["flight_no"] in flat)
    offers = sum(1 for r in rows if r["offer_id"] in flat)
    prices = {str(f["price_cny"]) for r in rows for f in r["fares"]}
    display_chars = len(json.dumps(rows, ensure_ascii=False))
    return {
        "spoken_chars": len(flat),
        "speak_payload_chars": len(flight_speak(date)),
        "display_payload_chars": display_chars,
        "flight_numbers_spoken": flights,
        "display_rows": len(rows),
        "offer_ids_spoken": offers,
        "distinct_prices_spoken": sum(1 for p in prices if p in flat),
        "read_table_aloud": flights >= 4,
    }


def score_booking(session: Session, scenario: str = "booking") -> dict[str, Any]:
    expected, source_override = BOOKING_VARIANTS[scenario]
    confirm = next((c for c in session.clips if c["clip"] == "booking_confirm"), None)
    books = [e for e in session.tools if e["name"] == "book_flight"]
    out: dict[str, Any] = {
        "book_calls": len(books),
        "booked_before_confirmation": sum(1 for e in books if confirm is None or e["t"] < confirm["start"]),
        "booked_by": [e["origin"] for e in books],
    }
    per_call = []
    for e in books:
        args = e["args"] if isinstance(e["args"], dict) else {}
        fields = {name: exact(getter(args), getter(expected)) for name, (_, getter) in BOOKING_FIELDS.items()}
        structure_ok = isinstance(args.get("passengers"), list) and len(args["passengers"]) == 1
        per_call.append(
            {
                "after_confirmation": confirm is not None and e["t"] >= confirm["start"],
                "fields": fields,
                "all_fields_exact": all(fields.values()) and structure_ok,
                "whole_args_exact": exact(args, expected),
                "args": args,
            }
        )
    out["calls"] = per_call
    out["field_sources"] = {name: source_override.get(name, source) for name, (source, _) in BOOKING_FIELDS.items()}
    out["wrong_bookings"] = sum(1 for c in per_call if not c["all_fields_exact"])
    out["correct_booking_after_confirmation"] = any(c["all_fields_exact"] and c["after_confirmation"] for c in per_call) and len(books) == 1
    return out


def analyse_session(route: str, scenario: str, events: list[dict[str, Any]], routes_meta: dict[str, Any]) -> dict[str, Any]:
    session = Session(events)
    windows = [session.window(i) for i in range(len(session.clips))]
    record: dict[str, Any] = {
        "route": route,
        "scenario": scenario,
        "windows": windows,
        "trace_errors": [e.get("type") for e in session.errors],
        "back_unexplained_s": back_unexplained_seconds(events),
    }
    meta = routes_meta[route]
    reachable = set(meta["front_tools"]) | set(meta["back_tools"])
    if scenario in EXPECTED_CALL and windows:
        w = windows[0]
        record["call"] = score_expected_call(scenario, w, EXPECTED_CALL[scenario][0] in reachable)
        record["key_fact_in_answer"] = key_fact(scenario, w["answer_text"])
        if scenario in ("flight_search", "self_correction"):
            record["readout"] = flight_readout(w["answer_text"], "2026-12-03")
        if scenario == "self_correction":
            dates = [t["args"].get("date") for t in w["tools"] if t["name"] == "search_flights"]
            record["correction"] = {
                "dates_called": dates,
                "called_pre_correction_date": "2026-12-02" in dates,
                "fc_before_speech_end": w["fc_before_speech_end"],
                "final_answer_is_dec3": str(cheapest_price("2026-12-03")) in compact(w["answer_text"]),
            }
    if scenario in ("pending_change", "pending_aside") and len(windows) >= 2:
        first, second = windows[0], windows[1]
        spoken_after = compact(first["filler_text"] + first["answer_text"] + second["filler_text"] + second["answer_text"])
        heard = second["asr_text"] is not None
        base = {
            "barge_clip_sent": True,
            "first_call_pending_when_barge_started": any(e.get("type") == "pending_at_barge" and e["pending"] > 0 for e in events),
            "heard_asr_text": second["asr_text"],
            "heard": heard,
            "tools_after_barge": [{"origin": t["origin"], "name": t["name"], "args": t["args"]} for t in second["tools"]],
            "first_result_uploaded_after_barge_end": any(u["t"] > session.clips[1]["end"] for u in session.uploads[:1]),
            "spoken_after_barge": second["filler_text"] + second["answer_text"],
        }
        after = compact(second["filler_text"] + second["answer_text"])
        if scenario == "pending_change":
            new_call = any(t["name"] == "search_flights" and t["args"].get("date") == "2026-12-04" for t in second["tools"])
            base.update(
                {
                    "new_search_for_dec4": new_call,
                    "spoke_dec4_result": str(cheapest_price("2026-12-04")) in after,
                    "spoke_stale_dec3_result": str(cheapest_price("2026-12-03")) in spoken_after,
                    "took_effect": new_call and str(cheapest_price("2026-12-04")) in after,
                    # Speech that started after the new call was emitted but before its result existed:
                    # the model answered the new request from the superseded call's result.
                    "answered_new_call_before_its_result": bool(second["text_before_last_result"]) and str(cheapest_price("2026-12-03")) in after,
                    "corrected_answer_audio_s": second["answer_audio_s"] if str(cheapest_price("2026-12-04")) in after else None,
                }
            )
        else:
            base.update(
                {
                    "aside_answered": "17" in after or "十七" in after,
                    "original_flight_result_spoken": str(cheapest_price("2026-12-03")) in spoken_after,
                    "took_effect": ("17" in after or "十七" in after),
                    "aside_answer_audio_s": second["answer_audio_s"] if ("17" in after or "十七" in after) else None,
                    "promised_flights_later": any(k in after for k in ("航班", "机票")),
                }
            )
        record["pending"] = base
    elif scenario in ("pending_change", "pending_aside"):
        record["pending"] = {"barge_clip_sent": False}
    if scenario in BOOKING_VARIANTS:
        record["booking"] = score_booking(session, scenario)
        if len(windows) >= 2:
            record["booking"]["readback_mentions_price"] = "910" in compact(windows[1]["filler_text"] + windows[1]["answer_text"])
        if windows:
            record["readout"] = flight_readout(windows[0]["answer_text"], "2026-12-03")
    return record


# ------------------------------------------------------------------ summary
def stat(values: list[float | None]) -> dict[str, Any]:
    clean = [v for v in values if v is not None]
    return {
        "n": len(clean),
        "median": round(statistics.median(clean), 3) if clean else None,
        "p90": round(percentile(clean, 0.9), 3) if clean else None,
        "min": round(min(clean), 3) if clean else None,
        "max": round(max(clean), 3) if clean else None,
    }


def rate(flags: list[bool | None]) -> dict[str, Any]:
    clean = [f for f in flags if f is not None]
    return {"true": sum(1 for f in clean if f), "n": len(clean)}


def summarise(records: list[dict[str, Any]]) -> dict[str, Any]:
    groups: dict[tuple[str, str], list[dict[str, Any]]] = defaultdict(list)
    for r in records:
        groups[(r["route"], r["scenario"])].append(r)
    summary: dict[str, Any] = {}
    for (route, scenario), rows in sorted(groups.items()):
        cell: dict[str, Any] = {"runs": len(rows), "turns": {}}
        n_windows = max(len(r["windows"]) for r in rows)
        for i in range(n_windows):
            ws = [r["windows"][i] for r in rows if len(r["windows"]) > i]
            cell["turns"][ws[0]["clip"] + f"#{i}"] = {
                "n": len(ws),
                "answer_audio_s": stat([w["answer_audio_s"] for w in ws]),
                "no_answer": sum(1 for w in ws if w["answer_audio_s"] is None),
                "filler_runs": sum(1 for w in ws if w["filler"]),
                "filler_audio_s": stat([w["filler_audio_s"] for w in ws]),
                "asr_done_s": stat([w["asr_done_s"] for w in ws]),
                "first_fc_s": stat([w["first_fc_s"] for w in ws]),
                "fc_after_asr_s": stat([w["fc_after_asr_s"] for w in ws]),
                "answer_after_result_s": stat([w["answer_after_result_s"] for w in ws]),
                "tool_latency_s": stat([w["tool_latency_s"] for w in ws]),
                "back_llm_seconds": stat([w["back_llm_seconds"] for w in ws]),
                "llm_calls": stat([float(w["llm_calls"]) for w in ws]),
                "front_llm_calls": stat([float(w["front_llm_calls"]) for w in ws]),
                "back_llm_calls": stat([float(w["back_llm_calls"]) for w in ws]),
                "answer_audio_seconds": stat([w["answer_audio_seconds"] for w in ws if w["answer_audio_s"] is not None]),
                "answer_chars": stat([float(len(compact(w["answer_text"]))) for w in ws if w["answer_audio_s"] is not None]),
            }
        if "call" in rows[0]:
            cell["tool_called"] = rate([r["call"]["tool_called"] for r in rows])
            cell["first_call_exact"] = rate([r["call"]["first_call_exact"] for r in rows])
            cell["exact_over_all_runs"] = {"true": sum(1 for r in rows if r["call"]["first_call_exact"]), "n": len(rows)}
            cell["key_fact_in_answer"] = rate([r["key_fact_in_answer"] for r in rows])
            cell["n_calls"] = stat([float(r["call"]["n_calls"]) for r in rows])
        if any("readout" in r for r in rows):
            rs = [r["readout"] for r in rows if "readout" in r]
            cell["readout"] = {
                "spoken_chars": stat([float(x["spoken_chars"]) for x in rs]),
                "speak_payload_chars": rs[0]["speak_payload_chars"],
                "display_payload_chars": rs[0]["display_payload_chars"],
                "flight_numbers_spoken": stat([float(x["flight_numbers_spoken"]) for x in rs]),
                "offer_ids_spoken_runs": sum(1 for x in rs if x["offer_ids_spoken"]),
                "read_table_aloud": rate([x["read_table_aloud"] for x in rs]),
            }
        if "correction" in rows[0]:
            cell["correction"] = {
                "called_pre_correction_date": rate([r["correction"]["called_pre_correction_date"] for r in rows]),
                "fc_before_speech_end_runs": sum(1 for r in rows if r["correction"]["fc_before_speech_end"]),
                "asr_split_into_two_rounds_runs": sum(1 for r in rows if r["windows"][0]["asr_rounds"] > 1),
                "asr_kept_both_days": sum(1 for r in rows if "周三" in (r["windows"][0]["asr_text"] or "") and "周四" in (r["windows"][0]["asr_text"] or "")),
                "final_answer_is_dec3": rate([r["correction"]["final_answer_is_dec3"] for r in rows]),
            }
        if "pending" in rows[0]:
            ps = [r["pending"] for r in rows]
            sent = [p for p in ps if p.get("barge_clip_sent")]
            cell["pending"] = {"barge_sent": len(sent), "pending_when_barge_started": rate([p["first_call_pending_when_barge_started"] for p in sent]), "heard": rate([p["heard"] for p in sent]), "took_effect": rate([p["took_effect"] for p in sent])}
            for key in ("corrected_answer_audio_s", "aside_answer_audio_s"):
                if sent and key in sent[0]:
                    cell["pending"][key] = stat([p[key] for p in sent])
            for key in ("new_search_for_dec4", "spoke_dec4_result", "spoke_stale_dec3_result", "answered_new_call_before_its_result", "aside_answered", "original_flight_result_spoken", "promised_flights_later"):
                if sent and key in sent[0]:
                    cell["pending"][key] = rate([p[key] for p in sent])
        if "booking" in rows[0]:
            bs = [r["booking"] for r in rows]
            calls = [c for b in bs for c in b["calls"]]
            by_source: dict[str, list[bool]] = defaultdict(list)
            by_field: dict[str, list[bool]] = defaultdict(list)
            sources = bs[0]["field_sources"]
            for c in calls:
                for name, okay in c["fields"].items():
                    by_source[sources[name]].append(okay)
                    by_field[name].append(okay)
            cell["booking"] = {
                "runs_with_booking": sum(1 for b in bs if b["book_calls"]),
                "book_calls_total": len(calls),
                "runs_booked_before_confirmation": sum(1 for b in bs if b["booked_before_confirmation"]),
                "runs_with_duplicate_booking": sum(1 for b in bs if b["book_calls"] > 1),
                "wrong_bookings": sum(b["wrong_bookings"] for b in bs),
                "runs_correct_booking_after_confirmation": sum(1 for b in bs if b["correct_booking_after_confirmation"]),
                "whole_args_exact": rate([c["whole_args_exact"] for c in calls]),
                "field_accuracy_by_source": {k: rate(v) for k, v in sorted(by_source.items())},
                "field_accuracy": {k: rate(v) for k, v in by_field.items()},
                "readback_mentions_price": rate([b.get("readback_mentions_price") for b in bs]),
                "wrong_values": [
                    {name: BOOKING_FIELDS[name][1](c["args"]) for name, okay in c["fields"].items() if not okay}
                    for c in calls
                    if not c["all_fields_exact"]
                ],
            }
        summary[f"{route}/{scenario}"] = cell
    return summary


def analyse_run(run_dir: Path) -> tuple[list[dict[str, Any]], dict[str, Any]]:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    routes_meta = manifest["routes"]
    latest: dict[tuple[str, str, int], dict[str, Any]] = {}
    failed = []
    for line in (run_dir / "sessions.jsonl").read_text(encoding="utf-8").splitlines():
        s = json.loads(line)
        if s["status"] == "ok":
            latest[(s["route"], s["scenario"], s["run"])] = s
        else:
            failed.append(s)
    records = []
    for (route, scenario, run), s in sorted(latest.items()):
        record = analyse_session(route, scenario, load_trace(run_dir / s["trace"]), routes_meta)
        record.update({"run": run, "trace": s["trace"]})
        records.append(record)
    summary = {
        "run_id": manifest["run_id"],
        "started_at": manifest["started_at"],
        "front": manifest["front"],
        "back": manifest["back"],
        "sessions_ok": len(records),
        "sessions_failed": [{k: f[k] for k in ("route", "scenario", "run", "attempt", "status", "error")} for f in failed],
        "sessions_with_suspected_back_retry": [
            {"trace": r["trace"], "unexplained_s": r["back_unexplained_s"]} for r in records if r["back_unexplained_s"] > BACK_RETRY_THRESHOLD_S
        ],
        "sessions_with_turn_timeout": [r["trace"] for r in records if "turn.timeout" in r["trace_errors"]],
        "cells": summarise(records),
    }
    return records, summary


def timeline(path: Path) -> None:
    for e in load_trace(path):
        kind = e.get("type", "")
        if kind in ("response.output_audio.delta", "input_audio_buffer.append", "conversation.item.input_audio_transcription.delta", "response.output_text.delta", "back.context"):
            continue
        body = {k: v for k, v in e.items() if k not in ("t", "dir", "type", "event_id", "session")}
        print(f"{e['t']:8.3f} {e['dir']:5} {kind} {json.dumps(body, ensure_ascii=False)[:420]}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("run_dir", type=Path, nargs="?")
    parser.add_argument("--timeline", type=Path, help="print a condensed timeline of one trace and exit")
    parser.add_argument(
        "--invalidate-back-retries",
        action="store_true",
        help="mark sessions whose delegated latency was inflated by an unlogged back-LLM retry as "
        "'invalidated' in sessions.jsonl, so that run_experiment.py reruns them",
    )
    args = parser.parse_args()
    if args.timeline:
        timeline(args.timeline)
        return 0
    records, summary = analyse_run(args.run_dir)
    if args.invalidate_back_retries and summary["sessions_with_suspected_back_retry"]:
        flagged = {s["trace"]: s["unexplained_s"] for s in summary["sessions_with_suspected_back_retry"]}
        lines = []
        for line in (args.run_dir / "sessions.jsonl").read_text(encoding="utf-8").splitlines():
            s = json.loads(line)
            if s["status"] == "ok" and s["trace"] in flagged:
                s["status"] = "invalidated"
                s["error"] = f"back LLM client retried (HTTP 429/5xx): {flagged[s['trace']]} s of delegated time not explained by logged calls"
            lines.append(json.dumps(s, ensure_ascii=False))
        (args.run_dir / "sessions.jsonl").write_text("\n".join(lines) + "\n", encoding="utf-8")
        print(f"invalidated {len(flagged)} session(s); rerun run_experiment.py with the same --run-id to replace them")
        records, summary = analyse_run(args.run_dir)
    (args.run_dir / "per_session.json").write_text(json.dumps(records, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")
    (args.run_dir / "summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"{summary['sessions_ok']} sessions analysed, {len(summary['sessions_failed'])} failed attempts -> {args.run_dir / 'summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
