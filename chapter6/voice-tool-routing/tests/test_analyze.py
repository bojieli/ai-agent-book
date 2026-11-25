"""Offline tests for the metric definitions, using a hand-written trace."""

import json

import analyze

ROUTES_META = {"all_front": {"front_tools": ["get_weather", "search_flights", "book_flight"], "back_tools": []}}


def ev(t, kind, direction="down", **body):
    return {"t": t, "dir": direction, "type": kind, **body}


def fc(t, name, args, call_id):
    return ev(t, "response.function_call_arguments.done", items=[{"name": name, "arguments": json.dumps(args), "call_id": call_id}])


def upload(t, call_id):
    return ev(t, "conversation.item.create", "up", items=[{"role": "tool", "call_id": call_id}])


def filler_then_answer_trace():
    args = {"origin": "北京", "destination": "上海", "date": "2026-12-03"}
    return [
        ev(1.0, "user_audio.start", "local", clip="flight_search"),
        ev(5.0, "user_audio.end", "local", clip="flight_search"),
        ev(5.8, "conversation.item.input_audio_transcription.completed", text="帮我查航班"),
        ev(5.9, "response.output_text.delta", delta="好的，我查一下。"),
        ev(6.6, "response.output_audio.delta", audio_bytes=48000),
        fc(7.0, "search_flights", args, "c1"),
        ev(7.0, "tool.call", "local", origin="front", name="search_flights", args=args, latency_s=3.0),
        ev(10.0, "tool.result", "local", origin="front", name="search_flights", result={}),
        upload(10.0, "c1"),
        ev(10.2, "response.output_audio.delta", audio_bytes=4800),  # tail of the filler: before any post-result text
        ev(10.6, "response.output_text.delta", delta="最低680元，是东航MU5103。"),
        ev(11.5, "response.output_audio.delta", audio_bytes=96000),
        ev(12.0, "response.output_text.done", text="好的，我查一下。最低680元，是东航MU5103。"),
    ]


def test_filler_is_separated_from_the_substantive_answer():
    record = analyze.analyse_session("all_front", "flight_search", filler_then_answer_trace(), ROUTES_META)
    w = record["windows"][0]
    assert w["filler"] and w["filler_audio_s"] == 1.6
    assert w["answer_text_s"] == 5.6 and w["answer_audio_s"] == 6.5
    assert w["answer_after_result_s"] == 1.5
    assert w["filler_text"] == "好的，我查一下。" and w["answer_text"].startswith("最低680元")
    assert w["front_llm_calls"] == 2 and w["back_llm_calls"] == 0
    assert record["call"]["first_call_exact"] is True and record["key_fact_in_answer"] is True
    assert record["readout"]["flight_numbers_spoken"] == 1 and record["readout"]["read_table_aloud"] is False


def test_answer_without_tool_counts_one_front_call():
    events = [
        ev(1.0, "user_audio.start", "local", clip="memory"),
        ev(3.0, "user_audio.end", "local", clip="memory"),
        ev(4.0, "response.output_text.delta", delta="卡号是CA 8839 2201 57。"),
        ev(4.4, "response.output_audio.delta", audio_bytes=48000),
    ]
    record = analyze.analyse_session("all_front", "memory", events, ROUTES_META)
    w = record["windows"][0]
    assert w["answer_audio_s"] == 1.4 and not w["filler"] and w["llm_calls"] == 1
    assert record["call"]["tool_called"] is False and record["key_fact_in_answer"] is True


def test_exact_match_is_strict_about_types_and_extra_keys():
    assert analyze.exact({"city": " 杭州 ", "date": "2026-11-26"}, {"city": "杭州", "date": "2026-11-26"})
    assert not analyze.exact({"city": "杭州市", "date": "2026-11-26"}, {"city": "杭州", "date": "2026-11-26"})
    assert not analyze.exact({"n": "23"}, {"n": 23})
    assert not analyze.exact({"n": 23, "extra": 1}, {"n": 23})


def test_booking_scoring_by_source_and_confirmation_order():
    good = json.loads(json.dumps(analyze.EXPECTED_BOOKING))
    bad = json.loads(json.dumps(analyze.EXPECTED_BOOKING))
    bad["offer_id"] = "OFR-1203-MU5103-7K2O"
    bad["contact"]["email"] = "zhoumingyuan@example.com"
    events = [
        ev(1.0, "user_audio.start", "local", clip="booking_select"),
        ev(9.0, "user_audio.end", "local", clip="booking_select"),
        ev(12.0, "tool.call", "local", origin="front", name="book_flight", args=bad, latency_s=2.0),
        ev(30.0, "user_audio.start", "local", clip="booking_confirm"),
        ev(31.0, "user_audio.end", "local", clip="booking_confirm"),
        ev(33.0, "tool.call", "local", origin="front", name="book_flight", args=good, latency_s=2.0),
    ]
    booking = analyze.score_booking(analyze.Session(events))
    assert booking["book_calls"] == 2 and booking["booked_before_confirmation"] == 1 and booking["wrong_bookings"] == 1
    assert booking["correct_booking_after_confirmation"] is False  # a duplicate booking is not a clean success
    wrong = [k for k, v in booking["calls"][0]["fields"].items() if not v]
    assert wrong == ["offer_id", "contact.email"]
    assert booking["calls"][1]["whole_args_exact"] is True


def test_percentile_uses_linear_interpolation():
    assert analyze.percentile([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 0.9) == 9.1
    assert analyze.percentile([], 0.9) is None
