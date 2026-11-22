"""Run a one-decision ablation alongside Experiment 4-1 (see README)."""

import argparse
import asyncio
import gzip
import json
import random
from pathlib import Path

import httpx

from run_exact_experiment import (
    MODEL, OLLAMA_URL, TASKS, VALIDATION_ROOT, canonical_json, render_schemas, sha256_bytes,
)

CONTEXT = 8192
MATCHED_TOKENS = 6144
INSTRUCTION = ("Select the first tool to call for the task from the supplied schemas. "
               "Return a JSON object with a tool field containing its exact name, or null if none is suitable.")


def candidates(catalog, receipt, task, seed):
    digest = sha256_bytes(canonical_json(catalog).encode())
    if receipt["catalog_sha256"] != digest or receipt["task"] != task["id"]:
        raise ValueError("Discovery receipt does not match task and catalog")
    retrieved = [m["name"] for m in receipt["discoveries"][0]["matches"]]
    by_name = {s["name"]: s for s in catalog}
    rng = random.Random(f"{seed}:{task['id']}")
    # Hold the correct choices fixed when adding distractors.
    pool = sorted(by_name.keys() - set(retrieved) - task["slots"][0])
    expanded = retrieved + rng.sample(pool, len(retrieved))
    random_names = rng.sample(sorted(by_name), len(retrieved))
    groups = {"retrieved": retrieved, "expanded": expanded, "random": random_names}
    return {label: [by_name[name] for name in sorted(names)] for label, names in groups.items()}


def messages(prompt, schemas, position, padding):
    block = "\n\nCandidate schemas:\n" + render_schemas(schemas)
    system = INSTRUCTION + "\nPadding:" + " pad" * padding
    user = "Task: " + prompt
    if position == "system":
        system += block
    else:
        user += block
    return [{"role": "system", "content": system}, {"role": "user", "content": user}]


async def decision(client, task, schemas, position, target, seed):
    padding = 0
    for _ in range(5):
        chat = messages(task["prompt"], schemas, position, padding)
        request = dict(model=MODEL, messages=chat, stream=False, think=False,
                       format={"type": "object", "properties": {"tool": {"type": ["string", "null"]}},
                               "required": ["tool"], "additionalProperties": False},
                       options=dict(temperature=0, seed=seed, num_ctx=CONTEXT, num_predict=64))
        response = await client.post("/api/chat", json=request)
        response.raise_for_status()
        data = response.json()
        tokens = data["prompt_eval_count"]
        if not 0 < tokens < CONTEXT - 64:
            raise ValueError("Prompt outside the context budget")
        if target is None or tokens == target:
            break
        padding += target - tokens
        if padding < 0:
            raise ValueError("Unpadded catalog exceeds the matched-length budget")
    else:
        raise ValueError(f"Could not match prompt length to {target} tokens")
    raw = data["message"]["content"]
    choice = json.loads(raw)["tool"]
    if data.get("done_reason") == "length" or not isinstance(choice, (str, type(None))):
        raise ValueError("Incomplete or invalid tool selection")
    names = [s["name"] for s in schemas]
    correct = task["slots"][0]
    return {
        "candidates": names,
        "gold_available": bool(correct.intersection(names)),
        "selected": choice,
        "correct": isinstance(choice, str) and choice in names and choice in correct,
        "raw_response": raw,
        "prompt_tokens": tokens,
        "padding_units": padding,
        "request_sha256": sha256_bytes(canonical_json(request).encode()),
        "model": data["model"],
        "done_reason": data.get("done_reason"),
    }


async def run(args):
    campaign = args.campaign
    with gzip.open(campaign / "catalog.schemas.json.gz", "rt") as source:
        catalog = json.load(source)
    rows = []
    async with httpx.AsyncClient(base_url=OLLAMA_URL, timeout=900) as client:
        for task in TASKS:
            if args.task and task["id"] != args.task:
                continue
            receipt = json.loads((campaign / "treatment" / task["id"] / "receipt.json").read_text())
            groups = candidates(catalog, receipt, task, args.seed)
            for label, group, role, target in (
                ("short", "retrieved", "system", None),
                ("long", "retrieved", "system", MATCHED_TOKENS),
                ("more_distractors", "expanded", "system", MATCHED_TOKENS),
                ("random_shortlist", "random", "system", MATCHED_TOKENS),
                ("user_schemas", "retrieved", "user", MATCHED_TOKENS),
            ):
                row = await decision(client, task, groups[group], role, target, args.seed)
                rows.append(dict(task=task["id"], arm=label, role=role, **row))
    return dict(campaign=campaign.name, catalog_sha256=sha256_bytes(canonical_json(catalog).encode()),
                seed=args.seed, context_tokens=CONTEXT, rows=rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--campaign", type=Path, default=VALIDATION_ROOT / "rerun_20260825")
    parser.add_argument("--seed", type=int, default=41)
    parser.add_argument("--task", choices=[t["id"] for t in TASKS])
    print(json.dumps(asyncio.run(run(parser.parse_args())), indent=2))
