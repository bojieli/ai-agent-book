"""Build a pair of tool-selection prompts from one archived discovery result."""

import argparse
import gzip
import json
from pathlib import Path


ARCHIVE = Path(__file__).resolve().parent / "validation/experiment_4_1/rerun_20260825"


def build_pair(task):
    receipt = json.loads((ARCHIVE / "treatment" / task / "receipt.json").read_text())
    with gzip.open(ARCHIVE / "catalog.schemas.json.gz", "rt", encoding="utf-8") as catalog:
        by_name = {schema["name"]: schema for schema in json.load(catalog)}

    discovery = receipt["discoveries"][0]
    names = [match["name"] for match in discovery["matches"]]
    if len(names) < 2 or len(set(names)) != len(names):
        raise ValueError("Expected at least two distinct archived candidates")

    # One complete schema per physical line, so moving a line never alters a field.
    lines = [json.dumps(by_name[name], ensure_ascii=False, separators=(",", ":")) for name in names]
    prefix = f"Task: {receipt['prompt']}\nCurrent need: {discovery['need']}\nCandidate schemas:\n"
    requests = []
    for ordered in (lines, lines[1:] + lines[:1]):
        requests.append({
            "model": receipt["model"],
            "options": receipt["runtime"]["options"],
            "messages": [
                {"role": "system", "content": "Select one candidate for the current need. Reply with its name."},
                {"role": "user", "content": prefix + "\n".join(ordered)},
            ],
            "stream": False,
        })

    candidates = []
    for request in requests:
        content = request["messages"][1]["content"]
        candidates.append(content.removeprefix(prefix).splitlines())
    if candidates[1] != candidates[0][1:] + candidates[0][:1]:
        raise ValueError("Candidate lines do not form the intended pair")
    return names, requests


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    tasks = sorted(p.parent.name for p in (ARCHIVE / "treatment").glob("*/receipt.json"))
    parser.add_argument("--task", choices=tasks, default="apple_stock_news")
    parser.add_argument("--json", action="store_true", help="Print both complete Ollama requests")
    args = parser.parse_args()
    names, requests = build_pair(args.task)
    if args.json:
        print(json.dumps(requests, ensure_ascii=False, indent=2))
    else:
        print(f"任务: {args.task}")
        print("A:", ", ".join(names))
        print("B:", ", ".join(names[1:] + names[:1]))
        print("用户消息 UTF-8 字节数:", *[len(r["messages"][1]["content"].encode()) for r in requests])


if __name__ == "__main__":
    main()
