#!/usr/bin/env python3
"""Run the voice tool-routing matrix against the real Doubao realtime API and a real back LLM.

Front model : Doubao realtime voice model 3.0 (Seeduplex), ``session.model = 1.2.6.1``
Back model  : OpenAI-compatible chat model configured through ``VTR_BACK_*`` (see back_agent.py)
Tools       : SIMULATED (tools_sim.py) with injected latency

Each session writes one JSONL trace (every upstream/downstream protocol event, audio replaced by
byte counts, plus local ``tool.*`` / ``back.*`` / ``user_audio.*`` records).  ``analyze.py`` derives
every reported number from those traces.
"""

from __future__ import annotations

import argparse
import asyncio
import datetime as dt
import hashlib
import json
import os
import platform
import subprocess
import sys
import traceback
import wave
from pathlib import Path
from typing import Any

import websockets

from back_agent import BackClient, run_back_agent
from realtime_front import DEFAULT_VOICE, ENDPOINT, FRONT_MODEL, OUTPUT_RATE, FrontSession
from routes import ROUTES, Route, back_instructions, front_instructions, front_tools
from tools_sim import LATENCY_SEED, TODAY, latency_for, memory_block, run_tool

HERE = Path(__file__).resolve().parent
AUDIO = HERE / "fixtures" / "audio"

# step = (kind, clip, seconds)
#   say          queue the clip, then wait until the assistant's turn is over
#   say_nowait   queue the clip and continue as soon as it has been sent
#   say_pending  wait for the front model's next function call, wait `seconds`, queue the clip,
#                then wait until the assistant's turn is over
SCENARIOS: dict[str, list[tuple[str, str, float]]] = {
    "weather": [("say", "weather", 0)],
    "memory": [("say", "memory", 0)],
    "web_search": [("say", "web_search", 0)],
    "flight_search": [("say", "flight_search", 0)],
    "self_correction": [("say", "self_correction", 0)],
    "pending_change": [("say_nowait", "flight_search", 0), ("say_pending", "barge_change_date", 1.0)],
    "pending_aside": [("say_nowait", "flight_search", 0), ("say_pending", "weather", 1.0)],
    "booking": [("say", "flight_search", 0), ("say", "booking_select", 0), ("say", "booking_confirm", 0)],
}


def load_clip(name: str) -> bytes:
    with wave.open(str(AUDIO / f"{name}.wav")) as wav:
        assert wav.getframerate() == 16000 and wav.getnchannels() == 1 and wav.getsampwidth() == 2
        return wav.readframes(wav.getnframes())


class VoiceRuntime:
    """One phone call: front session + simulated tools + optional back agent."""

    def __init__(
        self,
        *,
        route: Route,
        scenario: str,
        run_index: int,
        front_key: str,
        back: BackClient | None,
        trace_path: Path,
        save_audio: Path | None = None,
    ) -> None:
        self.route = route
        self.scenario = scenario
        self.run_index = run_index
        self.back = back
        self.save_audio = save_audio
        self.front = FrontSession(
            front_key,
            instructions=front_instructions(route),
            tools=front_tools(route),
            trace_path=trace_path,
            keep_output_audio=save_audio is not None,
        )
        self.front.handlers.append(self.on_event)
        self.pending: set[str] = set()
        self.playback_end = 0.0
        self.last_activity = 0.0
        self.responses_done = 0
        self.transcript: list[dict[str, str]] = []
        self.tool_log: list[dict[str, Any]] = []
        self.tool_counts: dict[str, int] = {}
        self.fc_event = asyncio.Event()
        self.tasks: set[asyncio.Task] = set()
        self.notes: list[str] = []

    # ------------------------------------------------------------- events
    def on_event(self, event: dict[str, Any], t: float) -> None:
        kind = event.get("type")
        self.last_activity = t
        if kind == "response.output_audio.delta":
            # Model the client's speaker: audio arrives faster than real time and plays back at 1x.
            import base64

            seconds = len(base64.b64decode(event.get("delta") or "")) / (OUTPUT_RATE * 2)
            self.playback_end = max(self.playback_end, t) + seconds
        elif kind == "conversation.item.input_audio_transcription.started":
            # The user started talking: a real client flushes its playback queue (as the vendor demo does).
            self.playback_end = t
        elif kind == "conversation.item.input_audio_transcription.completed":
            text = event.get("text") or event.get("transcript") or ""
            self.transcript.append({"role": "user", "text": text})
        elif kind == "response.output_text.done":
            self.responses_done += 1
            self.transcript.append({"role": "assistant", "text": event.get("text") or ""})
        elif kind == "response.function_call_arguments.done":
            items = event.get("items") or []
            for item in items:
                self.pending.add(item.get("call_id", ""))
            self.fc_event.set()
            task = asyncio.create_task(self.handle_function_calls(items))
            self.tasks.add(task)
            task.add_done_callback(self.tasks.discard)

    # -------------------------------------------------------------- tools
    async def exec_tool(self, origin: str, name: str, args: dict[str, Any]) -> dict[str, Any]:
        nth = self.tool_counts.get(name, 0)
        self.tool_counts[name] = nth + 1
        latency = latency_for(name, self.scenario, self.run_index, nth)
        self.front.log("local", {"type": "tool.call", "origin": origin, "name": name, "args": args, "nth": nth, "latency_s": latency, "simulated": True})
        result = await run_tool(name, args, latency)
        self.front.log("local", {"type": "tool.result", "origin": origin, "name": name, "nth": nth, "result": result})
        if isinstance(result.get("display"), list) and result["display"]:
            self.front.log("local", {"type": "screen.display", "origin": origin, "rows": len(result["display"])})
        self.tool_log.append({"origin": origin, "name": name, "args": args, "result": result})
        return result

    async def handle_function_calls(self, items: list[dict[str, Any]]) -> None:
        async def one(item: dict[str, Any]) -> tuple[str, str]:
            name = item.get("name", "")
            call_id = item.get("call_id", "")
            try:
                args = json.loads(item.get("arguments") or "{}")
            except json.JSONDecodeError:
                return call_id, json.dumps({"error": "arguments are not valid JSON"})
            if name == "delegate":
                if self.back is None or not self.route.delegates:
                    return call_id, json.dumps({"error": "delegate is not available"})
                self.front.log("local", {"type": "delegate.start", "call_id": call_id, "task": args.get("task")})
                text = await run_back_agent(
                    self.back,
                    system=back_instructions(self.route),
                    tool_names=self.route.back_tools,
                    transcript=list(self.transcript),
                    tool_log=list(self.tool_log),
                    task=str(args.get("task", "")),
                    run_tool=lambda n, a: self.exec_tool("back", n, a),
                    log=lambda record: self.front.log("local", {**record, "call_id": call_id}),
                )
                self.front.log("local", {"type": "delegate.end", "call_id": call_id, "speak": text})
                return call_id, json.dumps({"speak": text}, ensure_ascii=False)
            if name not in self.route.front_tools:
                return call_id, json.dumps({"error": f"tool {name} is not available"}, ensure_ascii=False)
            return call_id, json.dumps(await self.exec_tool("front", name, args), ensure_ascii=False)

        try:
            results = await asyncio.gather(*(one(item) for item in items))
            # The API pairs outputs by call_id and wants all outputs of one event in one upload.
            await self.front.send_tool_results(list(results))
        except (websockets.ConnectionClosed, asyncio.CancelledError):
            raise
        except Exception as exc:  # noqa: BLE001 - recorded, the session is marked failed
            self.notes.append(f"tool handler error: {exc!r}")
            self.front.log("local", {"type": "runtime.error", "error": repr(exc), "trace": traceback.format_exc()[-800:]})
        finally:
            for item in items:
                self.pending.discard(item.get("call_id", ""))
            self.last_activity = self.front.now()

    # -------------------------------------------------------------- steps
    async def wait_clip_sent(self) -> None:
        while self.front.speaking:
            await asyncio.sleep(0.02)

    async def wait_turn_done(self, timeout: float = 75.0) -> bool:
        start = self.front.now()
        baseline = self.responses_done
        while self.front.now() - start < timeout:
            await asyncio.sleep(0.1)
            now = self.front.now()
            if self.front.error is not None:
                return False
            if self.pending or self.responses_done == baseline:
                continue
            if now > self.playback_end + 0.8 and now - self.last_activity > 2.5:
                return True
        self.front.log("local", {"type": "turn.timeout", "pending": len(self.pending), "responses": self.responses_done - baseline})
        return False

    async def refresh_memory(self) -> None:
        """By-property route: the runtime re-runs retrieval and refreshes the injected block."""
        if not self.route.inject_memory:
            return
        await asyncio.sleep(latency_for("memory_lookup", self.scenario, self.run_index, 0))
        self.front.log("local", {"type": "memory.inject", "via": "session.update", "block": memory_block()})
        await self.front.update_instructions(front_instructions(self.route))

    async def run(self) -> None:
        if self.route.inject_memory:
            await asyncio.sleep(latency_for("memory_lookup", self.scenario, self.run_index, 0))
        await self.front.start()
        if self.route.inject_memory:
            self.front.log("local", {"type": "memory.inject", "via": "session.create", "block": memory_block()})
        await asyncio.sleep(1.0)
        try:
            for index, (kind, clip, seconds) in enumerate(SCENARIOS[self.scenario]):
                self.front.log("local", {"type": "step", "index": index, "kind": kind, "clip": clip})
                if kind == "say_pending":
                    try:
                        await asyncio.wait_for(self.fc_event.wait(), timeout=25)
                    except asyncio.TimeoutError:
                        self.front.log("local", {"type": "step.no_pending_window", "clip": clip})
                        break
                    await asyncio.sleep(seconds)
                    self.front.log("local", {"type": "pending_at_barge", "pending": len(self.pending)})
                self.fc_event.clear()
                baseline_wait = kind != "say_nowait"
                self.front.queue_clip(clip, load_clip(clip))
                await asyncio.sleep(0.05)
                await self.wait_clip_sent()
                if baseline_wait:
                    await self.wait_turn_done()
                    if kind == "say" and index < len(SCENARIOS[self.scenario]) - 1:
                        await self.refresh_memory()
                        await asyncio.sleep(0.6)
            await asyncio.sleep(0.5)
        finally:
            for task in list(self.tasks):
                task.cancel()
            await self.front.close()
            if self.save_audio is not None and self.front.output_audio:
                with wave.open(str(self.save_audio), "wb") as wav:
                    wav.setnchannels(1)
                    wav.setsampwidth(2)
                    wav.setframerate(OUTPUT_RATE)
                    wav.writeframes(bytes(self.front.output_audio))


# --------------------------------------------------------------------- matrix
def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def build_manifest(args: argparse.Namespace, back: BackClient | None) -> dict[str, Any]:
    try:
        commit = subprocess.run(["git", "-C", str(HERE), "rev-parse", "HEAD"], capture_output=True, text=True, check=True).stdout.strip()
    except Exception:  # noqa: BLE001
        commit = None
    return {
        "experiment": "voice-tool-routing",
        "run_id": args.run_id,
        "started_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
        "front": {"model": "豆包实时语音模型 3.0 (Seeduplex)", "session_model": FRONT_MODEL, "endpoint": ENDPOINT, "voice": DEFAULT_VOICE, "credential_env": "DOUBAO_VOICE_API_KEY"},
        "back": back.describe() if back else None,
        "tools": {"simulated": True, "latency_seed": LATENCY_SEED, "fixed_today": TODAY},
        "routes": {name: {"front_tools": list(r.front_tools), "delegate": r.delegates, "back_tools": list(r.back_tools), "inject_memory": r.inject_memory, "front_instructions": front_instructions(r), "back_instructions": back_instructions(r) if r.delegates else None, "front_tool_schemas": front_tools(r)} for name, r in ROUTES.items()},
        "scenarios": {name: [list(step) for step in steps] for name, steps in SCENARIOS.items()},
        "fixtures": json.loads((AUDIO / "manifest.json").read_text(encoding="utf-8")),
        "implementation_sha256": {p.name: sha256_file(p) for p in sorted(HERE.glob("*.py"))},
        "git_commit_at_run": commit,
        "python": platform.python_version(),
        "websockets": websockets.__version__,
        "requested": {"routes": args.routes, "scenarios": args.scenarios, "runs": args.runs, "concurrency": args.concurrency},
    }


async def run_one(route: Route, scenario: str, run_index: int, out: Path, front_key: str, back: BackClient | None, save_audio: bool) -> dict[str, Any]:
    folder = out / "traces" / route.name / scenario
    folder.mkdir(parents=True, exist_ok=True)
    attempt = len(list(folder.glob(f"run-{run_index:02d}.attempt-*.jsonl")))
    trace = folder / f"run-{run_index:02d}.attempt-{attempt}.jsonl"
    runtime = VoiceRuntime(
        route=route,
        scenario=scenario,
        run_index=run_index,
        front_key=front_key,
        back=back,
        trace_path=trace,
        save_audio=(folder / f"run-{run_index:02d}.wav") if save_audio else None,
    )
    status, error = "ok", None
    try:
        await runtime.run()
        if runtime.front.error is not None:
            status, error = "error", json.dumps({k: v for k, v in runtime.front.error.items() if k != "_t"}, ensure_ascii=False)[:500]
        elif runtime.notes:
            status, error = "error", "; ".join(runtime.notes)[:500]
    except Exception as exc:  # noqa: BLE001 - a failed session is recorded, never replaced
        status, error = "error", repr(exc)[:500]
    record = {"route": route.name, "scenario": scenario, "run": run_index, "attempt": attempt, "status": status, "error": error, "trace": str(trace.relative_to(out)), "logid": runtime.front.logid}
    with (out / "sessions.jsonl").open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(record, ensure_ascii=False) + "\n")
    print(f"[{status}] {route.name}/{scenario}/run-{run_index:02d} attempt {attempt}" + (f" :: {error}" if error else ""), flush=True)
    return record


def completed(out: Path) -> set[tuple[str, str, int]]:
    done: set[tuple[str, str, int]] = set()
    path = out / "sessions.jsonl"
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            record = json.loads(line)
            if record["status"] == "ok":
                done.add((record["route"], record["scenario"], record["run"]))
    return done


async def main_async(args: argparse.Namespace) -> int:
    front_key = os.environ.get("DOUBAO_VOICE_API_KEY")
    if not front_key:
        raise SystemExit("DOUBAO_VOICE_API_KEY is not set")
    routes = [ROUTES[name] for name in args.routes]
    back = BackClient() if any(r.delegates for r in routes) else None
    out = HERE / "validation" / "runs" / args.run_id
    out.mkdir(parents=True, exist_ok=True)
    manifest_path = out / "manifest.json"
    if not manifest_path.exists():
        manifest_path.write_text(json.dumps(build_manifest(args, back), ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    done = completed(out)
    jobs = [
        (route, scenario, run)
        for run in range(args.runs)
        for scenario in args.scenarios
        for route in routes
        if (route.name, scenario, run) not in done
    ]
    print(f"{len(jobs)} sessions to run ({len(done)} already complete)", flush=True)
    semaphore = asyncio.Semaphore(args.concurrency)

    async def guarded(job: tuple[Route, str, int]) -> dict[str, Any]:
        async with semaphore:
            return await run_one(*job, out, front_key, back, args.save_audio)

    results = await asyncio.gather(*(guarded(job) for job in jobs))
    if back:
        await back.close()
    failed = sum(1 for r in results if r["status"] != "ok")
    print(f"done: {len(results) - failed} ok, {failed} failed -> {out}")
    return 0 if failed == 0 else 2


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--run-id", required=True, help="directory name under validation/runs/")
    parser.add_argument("--routes", nargs="+", default=list(ROUTES), choices=list(ROUTES))
    parser.add_argument("--scenarios", nargs="+", default=list(SCENARIOS), choices=list(SCENARIOS))
    parser.add_argument("--runs", type=int, default=10, help="runs per route x scenario")
    parser.add_argument("--concurrency", type=int, default=4, help="parallel phone calls")
    parser.add_argument("--save-audio", action="store_true", help="also keep the model's output audio as WAV")
    return asyncio.run(main_async(parser.parse_args()))


if __name__ == "__main__":
    sys.exit(main())
