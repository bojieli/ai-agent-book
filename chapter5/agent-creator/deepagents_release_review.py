# /// script
# requires-python = ">=3.11"
# dependencies = ["deepagents==0.7.41"]
# ///
"""Run a release review with the Deep Agents SDK and the chapter's policy tool."""

import argparse
import json

from deepagents import create_deep_agent
from langchain_core.language_models.fake_chat_models import GenericFakeChatModel
from langchain_core.messages import AIMessage, ToolMessage
from langchain_core.tools import tool

from reference_agent.domain_tools import evaluate_policy_records


@tool
def inspect_release(release_id: str) -> dict:
    """Read a sample release's test results and evaluate its required checks."""
    if release_id not in {"R17", "R18"}:
        raise ValueError(f"Unknown release: {release_id}")
    status = "failed" if release_id == "R17" else "passed"
    records = [
        {"id": "build", "required": True, "status": "passed", "evidence": "build log"},
        {"id": "smoke", "required": True, "status": status, "evidence": "smoke log"},
    ]
    return evaluate_policy_records(records)


class ReplayModel(GenericFakeChatModel):
    """Supply recorded message shapes without a model service."""

    def bind_tools(self, tools, **kwargs):
        return self


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("release_id", choices=["R17", "R18"])
    parser.add_argument("--model", help="Provider-qualified model with tool calling")
    args = parser.parse_args()
    model = args.model
    if model is None:
        call = {"name": "inspect_release", "args": {"release_id": args.release_id},
                "id": "review-1", "type": "tool_call"}
        model = ReplayModel(messages=iter([
            AIMessage(content="", tool_calls=[call]),
            AIMessage(content="回放结束，请对照上面的工具结果。"),
        ]))
    agent = create_deep_agent(
        model=model,
        tools=[inspect_release],
        system_prompt="请调用 inspect_release 核查指定版本，依据工具结果答复，并列出失败的必检项。",
    )
    result = agent.invoke({"messages": [{"role": "user", "content": f"核查 {args.release_id} 能否发布。"}]})
    reports = [m for m in result["messages"] if isinstance(m, ToolMessage) and m.name == "inspect_release"]
    if not reports:
        raise RuntimeError("本轮没有发布检查的工具回执。")
    for report in reports:
        if report.status == "error":
            raise RuntimeError(report.content)
        evidence = json.loads(report.content)
        failed = [row["id"] for row in evidence["failed_required_records"]]
        print(f"工具回执 {report.tool_call_id}: {evidence['decision']}，失败的必检项 {failed}")
    print(result["messages"][-1].content)


if __name__ == "__main__":
    main()
