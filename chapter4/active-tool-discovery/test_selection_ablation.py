import asyncio
import gzip
import json

import httpx
import pytest

import selection_ablation as ablation


@pytest.mark.parametrize("task", ablation.TASKS, ids=lambda task: task["id"])
def test_replay_preserves_retrieved_choices_and_adds_only_distractors(task):
    campaign = ablation.VALIDATION_ROOT / "rerun_20260825"
    with gzip.open(campaign / "catalog.schemas.json.gz", "rt") as source:
        catalog = json.load(source)
    receipt = json.loads((campaign / "treatment" / task["id"] / "receipt.json").read_text())
    groups = ablation.candidates(catalog, receipt, task, 41)
    names = {key: {item["name"] for item in group} for key, group in groups.items()}
    assert names["retrieved"] == {m["name"] for m in receipt["discoveries"][0]["matches"]}
    assert names["retrieved"] < names["expanded"]
    assert not (names["expanded"] - names["retrieved"]) & task["slots"][0]
    assert len(names["retrieved"]) == len(names["random"])


def test_length_calibration_uses_fresh_messages_and_scores_only_final_reply():
    task = ablation.TASKS[0]
    calls = []

    def respond(request):
        messages = json.loads(request.content)["messages"]
        calls.append(messages)
        return httpx.Response(200, json={
            "model": ablation.MODEL, "prompt_eval_count": 100 + messages[0]["content"].count(" pad"),
            "message": {"content": json.dumps({"tool": "stock_price" if len(calls) == 2 else "other"})},
        })

    async def run():
        async with httpx.AsyncClient(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
            return await ablation.decision(client, task, [{"name": "stock_price"}], "user", 150, 41)

    row = asyncio.run(run())
    assert row["prompt_tokens"] == 150 and row["correct"]
    assert [len(messages) for messages in calls] == [2, 2]
    assert calls[0][1] == calls[1][1]


def test_truncated_reply_cannot_be_recorded_as_a_selection():
    def respond(request):
        return httpx.Response(200, json={
            "model": ablation.MODEL, "prompt_eval_count": 100, "done_reason": "length",
            "message": {"content": '{"tool":"stock_price"}'},
        })

    async def run():
        async with httpx.AsyncClient(base_url="http://test", transport=httpx.MockTransport(respond)) as client:
            await ablation.decision(client, ablation.TASKS[0], [{"name": "stock_price"}], "user", None, 41)

    with pytest.raises(ValueError, match="Incomplete"):
        asyncio.run(run())
