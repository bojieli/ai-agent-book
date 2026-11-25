#!/usr/bin/env python3
"""Capability probes for the Doubao realtime voice model 3.0 (Seeduplex).

These answer three questions with real calls instead of documentation:

1. function calling in pure end-to-end mode (``fc_basic``);
2. what happens while a function call is pending (``pending_*``): does the model keep
   listening, does it speak, is a late result still delivered;
3. how text can be injected into the model's context (``inject_*``).

Tools are simulated (tools_sim.py).  Evidence goes to validation/probes/<run-id>/.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import json
import os
from pathlib import Path
from typing import Any

from analyze import compact, digits_only
from realtime_front import FRONT_MODEL, FrontSession
from run_experiment import load_clip
from tools_sim import CALENDAR_HINT, FREQUENT_FLYER_DIGITS, MEMORY, TOOL_SCHEMAS, execute

HERE = Path(__file__).resolve().parent
BASE = "你是一位中文语音出行助理，正在和用户通电话。" + CALENDAR_HINT + "需要查询时调用工具，不要编造。"
MEMORY_TEXT = "\n【运行时自动检索到的用户记忆，可直接使用】" + MEMORY["frequent_flyer"]
MEMORY_PAIR = [
    {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "记一下，" + MEMORY["frequent_flyer"].replace("用户的", "我的")}]},
    {"type": "message", "role": "assistant", "content": [{"type": "input_text", "text": "好的，记住了。"}]},
]


async def session(name: str, out: Path, *, instructions: str, tools: list[str], tool_delay: float | None, script) -> dict[str, Any]:
    front = FrontSession(
        os.environ["DOUBAO_VOICE_API_KEY"],
        instructions=instructions,
        tools=[TOOL_SCHEMAS[t] for t in tools],
        trace_path=out / f"{name}.jsonl",
    )
    state: dict[str, Any] = {"calls": [], "uploads": [], "asr": [], "spoken": [], "audio_after": {}}
    tasks: set[asyncio.Task] = set()

    def on_event(event: dict[str, Any], t: float) -> None:
        kind = event.get("type")
        if kind == "response.function_call_arguments.done":
            for item in event.get("items") or []:
                args = json.loads(item.get("arguments") or "{}")
                state["calls"].append({"t": t, "name": item["name"], "args": args})

                async def answer(item=item, args=args) -> None:
                    await asyncio.sleep(tool_delay if tool_delay is not None else 0.2)
                    result = execute(item["name"], args)
                    result.pop("display", None)
                    await front.send_tool_results([(item["call_id"], json.dumps(result, ensure_ascii=False))])
                    state["uploads"].append({"t": front.now(), "name": item["name"], "args": args})

                task = asyncio.create_task(answer())
                tasks.add(task)
                task.add_done_callback(tasks.discard)
        elif kind == "conversation.item.input_audio_transcription.completed":
            state["asr"].append({"t": t, "text": event.get("text")})
        elif kind == "response.output_text.done":
            state["spoken"].append({"t": t, "text": event.get("text")})

    front.handlers.append(on_event)
    await front.start()
    try:
        await script(front, state)
    finally:
        for task in list(tasks):
            task.cancel()
        await front.close()
    state["error"] = front.error
    state["audio_deltas"] = [e["t"] for e in front.events if e.get("type") == "response.output_audio.delta"]
    state["clips"] = [{"clip": e["clip"], "type": e["type"], "t": e["t"]} for e in front.events if e.get("type", "").startswith("user_audio.")]
    return state


async def say(front: FrontSession, clip: str) -> None:
    front.queue_clip(clip, load_clip(clip))
    await asyncio.sleep(0.05)
    while front.speaking:
        await asyncio.sleep(0.02)


def spoken(state: dict[str, Any], after: float = 0.0) -> str:
    return compact("".join(s["text"] or "" for s in state["spoken"] if s["t"] >= after))


# ------------------------------------------------------------------- probes
async def fc_basic(out: Path, rep: int) -> dict[str, Any]:
    async def script(front, state):
        await asyncio.sleep(1)
        await say(front, "weather")
        await asyncio.sleep(12)

    s = await session(f"fc_basic-{rep}", out, instructions=BASE, tools=["get_weather"], tool_delay=0.2, script=script)
    return {"function_call_emitted": bool(s["calls"]), "args": [c["args"] for c in s["calls"]], "result_spoken": "17" in spoken(s)}


async def pending_silent(out: Path, rep: int, delay: float = 8.0, suffix: str = "") -> dict[str, Any]:
    """No filler instruction, slow tool, user stays silent: does the model say anything while waiting?"""

    async def script(front, state):
        await asyncio.sleep(1)
        await say(front, "flight_search")
        await asyncio.sleep(delay + 16)

    s = await session(f"pending_silent{suffix}-{rep}", out, instructions=BASE, tools=["search_flights"], tool_delay=delay, script=script)
    call_t = s["calls"][0]["t"] if s["calls"] else None
    upload_t = s["uploads"][0]["t"] if s["uploads"] else None
    during = [t for t in s["audio_deltas"] if call_t is not None and upload_t is not None and call_t <= t < upload_t]
    spurious = [
        e["t"]
        for e in load_probe_events(out / f"pending_silent{suffix}-{rep}.jsonl")
        if e.get("type") == "conversation.item.input_audio_transcription.started" and call_t is not None and e["t"] > call_t
    ]
    return {
        "tool_delay_s": delay,
        "function_call_emitted": call_t is not None,
        "audio_while_pending": bool(during),
        "result_spoken_after_upload": upload_t is not None and "680" in spoken(s, upload_t),
        # The client only sends digital silence after the request, so any new ASR round is server-initiated.
        "new_round_started_without_user_speech_s_after_call": round(spurious[0] - call_t, 2) if spurious else None,
    }


def load_probe_events(path: Path) -> list[dict[str, Any]]:
    return [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]


def make_pending_silent(delay: float):
    async def probe(out: Path, rep: int) -> dict[str, Any]:
        return await pending_silent(out, rep, delay, suffix=f"_{int(delay)}s")

    return probe


async def pending_change(out: Path, rep: int, delay: float = 8.0) -> dict[str, Any]:
    """User changes the request while the first call is pending."""

    async def script(front, state):
        await asyncio.sleep(1)
        await say(front, "flight_search")
        for _ in range(200):
            if state["calls"]:
                break
            await asyncio.sleep(0.1)
        await asyncio.sleep(1.0)
        await say(front, "barge_change_date")
        await asyncio.sleep(delay + 20)

    s = await session(f"pending_change-{rep}", out, instructions=BASE, tools=["search_flights"], tool_delay=delay, script=script)
    barge_start = next((c["t"] for c in s["clips"] if c["clip"] == "barge_change_date" and c["type"] == "user_audio.start"), None)
    first_upload = s["uploads"][0]["t"] if s["uploads"] else None
    text = spoken(s, barge_start or 0)
    return {
        "tool_delay_s": delay,
        "barge_started_while_pending": barge_start is not None and first_upload is not None and barge_start < first_upload,
        "barge_heard_by_asr": any(barge_start is not None and a["t"] > barge_start for a in s["asr"]),
        "new_call_with_dec4": any(c["args"].get("date") == "2026-12-04" for c in s["calls"][1:]),
        "stale_dec3_result_spoken": "680" in text,
        "dec4_result_spoken": "650" in text,
        "calls": [c["args"] for c in s["calls"]],
    }


async def pending_aside(out: Path, rep: int, delay: float = 14.0) -> dict[str, Any]:
    """User asks something unrelated (answerable from the instructions) while the call is pending;
    the tool result is uploaded only after that aside has been answered."""
    front_tools = ["search_flights"]

    async def script(front, state):
        await asyncio.sleep(1)
        await say(front, "flight_search")
        for _ in range(200):
            if state["calls"]:
                break
            await asyncio.sleep(0.1)
        await asyncio.sleep(1.0)
        await say(front, "memory")
        await asyncio.sleep(delay + 16)

    s = await session(
        f"pending_aside-{rep}",
        out,
        instructions=BASE + MEMORY_TEXT,
        tools=front_tools,
        tool_delay=delay,
        script=script,
    )
    aside_start = next((c["t"] for c in s["clips"] if c["clip"] == "memory" and c["type"] == "user_audio.start"), None)
    upload_t = s["uploads"][0]["t"] if s["uploads"] else None
    return {
        "tool_delay_s": delay,
        "aside_started_while_pending": aside_start is not None and upload_t is not None and aside_start < upload_t,
        "aside_heard_by_asr": any(aside_start is not None and a["t"] > aside_start for a in s["asr"]),
        "aside_answered_while_pending": any(
            aside_start is not None and upload_t is not None and aside_start < x["t"] < upload_t and FREQUENT_FLYER_DIGITS in digits_only(x["text"] or "")
            for x in s["spoken"]
        ),
        "audio_while_pending_after_aside": any(aside_start is not None and upload_t is not None and aside_start < t < upload_t for t in s["audio_deltas"]),
        "late_result_spoken": upload_t is not None and "680" in spoken(s, upload_t),
        "any_speech_after_late_result": upload_t is not None and bool(spoken(s, upload_t)),
        "calls": [c["args"] for c in s["calls"]],
    }


async def pending_aside_reask(out: Path, rep: int, delay: float = 14.0) -> dict[str, Any]:
    """After a late result was dropped: is it at least in the context when the user asks again?"""

    async def script(front, state):
        await asyncio.sleep(1)
        await say(front, "flight_search")
        for _ in range(200):
            if state["calls"]:
                break
            await asyncio.sleep(0.1)
        await asyncio.sleep(1.0)
        await say(front, "memory")
        await asyncio.sleep(delay + 6)
        state["reask_at"] = front.now()
        await say(front, "flight_search")
        await asyncio.sleep(delay + 14)

    s = await session(f"pending_aside_reask-{rep}", out, instructions=BASE + MEMORY_TEXT, tools=["search_flights"], tool_delay=delay, script=script)
    reask = s.get("reask_at", 1e9)
    first_upload = s["uploads"][0]["t"] if s["uploads"] else None
    return {
        "tool_delay_s": delay,
        "late_result_uploaded_before_reask": first_upload is not None and first_upload < reask,
        "late_result_spoken_before_reask": first_upload is not None and any(first_upload <= x["t"] < reask and "680" in compact(x["text"] or "") for x in s["spoken"]),
        "new_call_after_reask": any(c["t"] > reask for c in s["calls"]),
        "result_spoken_after_reask": "680" in spoken(s, reask),
        "calls": [c["args"] for c in s["calls"]],
    }


async def push_speech(out: Path, rep: int) -> dict[str, Any]:
    """Can the runtime make the model's voice say a given text without a user turn (speech_text_buffer.commit)?"""
    text = "久等了，航班查到了：12月3日北京到上海经济舱最低680元。"

    async def script(front, state):
        await asyncio.sleep(1)
        await say(front, "weather")
        await asyncio.sleep(10)
        state["push_at"] = front.now()
        await front.send({"type": "speech_text_buffer.commit", "text": text})
        await asyncio.sleep(10)

    s = await session(f"push_speech-{rep}", out, instructions=BASE, tools=["get_weather"], tool_delay=0.2, script=script)
    push = s.get("push_at", 1e9)
    audio = [t for t in s["audio_deltas"] if t > push]
    return {
        "audio_after_push": bool(audio),
        "first_audio_after_push_s": round(audio[0] - push, 3) if audio else None,
        "text_event_after_push": [x["text"] for x in s["spoken"] if x["t"] > push],
    }


WEATHER_FACT = "杭州11月26日多云转晴，9到17度，东北风3级，降水概率10%。"
WEATHER_BLOCK = "\n【运行时刚查到的信息，可直接使用】" + WEATHER_FACT
WEATHER_PAIR = [
    {"type": "message", "role": "user", "content": [{"type": "input_text", "text": "杭州明天的天气预报是什么？"}]},
    {"type": "message", "role": "assistant", "content": [{"type": "input_text", "text": WEATHER_FACT}]},
]
PLAIN_BASE = "你是出行助理。今天是2026年11月25日，星期三。"


def make_inject(mode: str):
    """Inject one fact as text, then ask about it by voice.

    The fact is the simulated Hangzhou forecast and the question is the ``weather`` recording.  No
    tool is declared, so without the fact the model can only refuse or invent numbers; the
    ``control`` mode measures that baseline.  ``fact_used`` requires both "东北风" and "17".
    The ``*_after_turn`` modes first complete one unrelated voice turn (the ``memory`` recording).
    """

    async def probe(out: Path, rep: int) -> dict[str, Any]:
        base = PLAIN_BASE if mode.endswith("_plain") else BASE
        kind = mode.replace("_plain", "")

        async def script(front, state):
            await asyncio.sleep(0.5)
            if kind in ("update_after_turn", "item_after_turn"):
                await say(front, "memory")
                await asyncio.sleep(9)
            if kind in ("update_before_first_turn", "update_after_turn"):
                await front.update_instructions(base + WEATHER_BLOCK)
            if kind in ("item_before_first_turn", "item_after_turn"):
                await front.send({"type": "conversation.item.create", "items": WEATHER_PAIR})
            await asyncio.sleep(1.0)
            state["question_at"] = front.now()
            await say(front, "weather")
            await asyncio.sleep(10)

        instructions = base + (WEATHER_BLOCK if kind == "instructions_at_create" else "")
        s = await session(f"inject_{mode}-{rep}", out, instructions=instructions, tools=[], tool_delay=None, script=script)
        answer = "".join(x["text"] or "" for x in s["spoken"] if x["t"] >= s.get("question_at", 0))
        return {"fact_used": "东北风" in answer and "17" in answer, "answer": answer}

    return probe


INJECT_MODES = (
    "control",
    "instructions_at_create",
    "update_before_first_turn",
    "item_before_first_turn",
    "update_after_turn",
    "item_after_turn",
    "update_after_turn_plain",
    "item_after_turn_plain",
)

PROBES = {
    "fc_basic": fc_basic,
    "pending_silent": pending_silent,
    **{f"pending_silent_{d}s": make_pending_silent(float(d)) for d in (10, 12, 14, 16, 20)},
    "pending_change": pending_change,
    "pending_aside": pending_aside,
    "pending_aside_reask": pending_aside_reask,
    "push_speech": push_speech,
    **{f"inject_{m}": make_inject(m) for m in INJECT_MODES},
}


async def main_async(args: argparse.Namespace) -> int:
    out = HERE / "validation" / "probes" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    semaphore = asyncio.Semaphore(args.concurrency)
    results: dict[str, list[dict[str, Any]]] = {name: [] for name in args.probes}

    async def one(name: str, rep: int) -> None:
        async with semaphore:
            try:
                outcome = await PROBES[name](out, rep)
            except Exception as exc:  # noqa: BLE001 - recorded as a failed probe
                outcome = {"probe_error": repr(exc)[:300]}
            outcome["rep"] = rep
            outcome["trace"] = f"{name}-{rep}.jsonl"
            results[name].append(outcome)
            print(name, rep, json.dumps({k: v for k, v in outcome.items() if k not in ("answer", "calls")}, ensure_ascii=False), flush=True)

    await asyncio.gather(*(one(name, rep) for name in args.probes for rep in range(args.reps)))
    report = {
        "run_id": args.run_id,
        "date": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "front": {"session_model": FRONT_MODEL},
        "tools_simulated": True,
        "reps_per_probe": args.reps,
        "results": {name: sorted(rows, key=lambda r: r["rep"]) for name, rows in results.items()},
    }
    (out / "probes.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(out / "probes.json")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--probes", nargs="+", default=list(PROBES), choices=list(PROBES))
    parser.add_argument("--reps", type=int, default=5)
    parser.add_argument("--concurrency", type=int, default=4)
    return asyncio.run(main_async(parser.parse_args()))


if __name__ == "__main__":
    raise SystemExit(main())
