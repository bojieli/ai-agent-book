#!/usr/bin/env python3
"""Fail-closed validation of a retained voice tool-routing run.

It checks that the evidence is complete and self-consistent; it does NOT require any
hypothesis about routing to come out a particular way.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path

from analyze import analyse_run

HERE = Path(__file__).resolve().parent
# Files that determine what was sent to the models.  Analysis code may change after a run.
RUNTIME_FILES = ("realtime_front.py", "run_experiment.py", "routes.py", "tools_sim.py", "back_agent.py")
SECRET_ENVS = ("DOUBAO_VOICE_API_KEY", "VOLCENGINE_API_KEY", "VOLC_WEB_SEARCH_KEY", "ARK_API_KEY", "MIFY_API_KEY")
FORBIDDEN = ("X-Api-Key", "Authorization", "Bearer ")


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def validate(run_dir: Path) -> dict:
    manifest = json.loads((run_dir / "manifest.json").read_text(encoding="utf-8"))
    sessions = [json.loads(line) for line in (run_dir / "sessions.jsonl").read_text(encoding="utf-8").splitlines()]
    ok = [s for s in sessions if s["status"] == "ok"]
    requested = manifest["requested"]
    counts: dict[tuple[str, str], set[int]] = {}
    for s in ok:
        counts.setdefault((s["route"], s["scenario"]), set()).add(s["run"])
    secrets = [os.environ[name] for name in SECRET_ENVS if os.environ.get(name)]
    files = [p for p in run_dir.rglob("*") if p.is_file() and p.suffix in (".json", ".jsonl", ".md")]
    leaked = False
    audio_payload = False
    local_path = False
    for path in files:
        text = path.read_text(encoding="utf-8", errors="ignore")
        if any(token in text for token in FORBIDDEN) or any(secret in text for secret in secrets):
            leaked = True
        if "/Users/" in text or "/home/" in text:
            local_path = True
        if path.suffix == ".jsonl" and '"type": "input_audio_buffer.append"' in text:
            audio_payload = True
    traces_ok = True
    for s in ok:
        trace = run_dir / s["trace"]
        if not trace.is_file():
            traces_ok = False
            continue
        head = trace.read_text(encoding="utf-8")
        if '"type": "session.created"' not in head or '"type": "user_audio.end"' not in head:
            traces_ok = False
    fixtures = manifest["fixtures"]["clips"]
    stored_summary = json.loads((run_dir / "summary.json").read_text(encoding="utf-8")) if (run_dir / "summary.json").exists() else None
    _, recomputed = analyse_run(run_dir)
    checks = {
        "experiment_name": manifest.get("experiment") == "voice-tool-routing",
        "front_is_seeduplex": manifest["front"]["session_model"] == "1.2.6.1" and "duplex/realtime/dialogue" in manifest["front"]["endpoint"],
        # A run whose requested routes never delegate (e.g. the all-front serial control) has no back model.
        "back_model_recorded": bool((manifest.get("back") or {}).get("model"))
        or not any(manifest["routes"][route].get("delegate") for route in requested["routes"]),
        "tools_declared_simulated": manifest["tools"]["simulated"] is True,
        "every_cell_has_requested_runs": all(
            len(counts.get((route, scenario), ())) >= requested["runs"] for route in requested["routes"] for scenario in requested["scenarios"]
        ),
        "traces_present_and_real": traces_ok,
        "no_credentials_in_evidence": not leaked,
        "secret_scan_had_keys_to_compare": bool(secrets),
        "no_raw_audio_in_traces": not audio_payload,
        "runtime_code_matches_run": all(
            (HERE / name).is_file() and sha256_file(HERE / name) == manifest["implementation_sha256"].get(name) for name in RUNTIME_FILES
        ),
        "summary_reproducible_from_traces": stored_summary is not None and stored_summary["cells"] == recomputed["cells"],
        "no_hidden_back_llm_retries_in_counted_sessions": not recomputed["sessions_with_suspected_back_retry"],
        "no_local_paths_in_evidence": not local_path,
    }
    # The WAV fixtures are not committed (regenerate with prepare_fixtures.py); their SHA-256 values in the
    # run manifest pin the inputs. Compare them when present, and report the check as skipped otherwise.
    skipped = []
    fixture_paths = [HERE / "fixtures" / "audio" / clip["file"] for clip in fixtures.values()]
    if any(path.is_file() for path in fixture_paths):
        checks["audio_fixtures_match_manifest"] = all(
            path.is_file() and sha256_file(path) == clip["sha256"] for path, clip in zip(fixture_paths, fixtures.values())
        )
    else:
        skipped.append("audio_fixtures_match_manifest")
    return {
        "passed": all(checks.values()),
        "checks": checks,
        "skipped_checks": skipped,
        "sessions_ok": len(ok),
        "sessions_failed": len(sessions) - len(ok),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("run_dir", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = validate(args.run_dir)
    output = args.output or args.run_dir / "acceptance.json"
    output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
    return 0 if result["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
