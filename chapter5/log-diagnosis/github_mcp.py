"""
github_mcp.py —— GitHub Issue 创建（默认 mock，可选真实 MCP）

- mock（默认）：把"创建 Issue"渲染成将要提交的 Issue 结构，打印并写入本地文件，
  不联网、不需要 token。
- 真实（mock=False，需 GITHUB_TOKEN + GITHUB_REPO）：通过 MCP 协议连接官方
  GitHub MCP Server（stdio），调用其 `create_issue` 工具在真实仓库创建 Issue。
  出于安全，真实创建须由 demo.py 的 --create-issue 显式开启。
"""

import json
import os
import shlex
from datetime import datetime
from typing import Dict, Any, List

_OUT = os.path.join(os.path.dirname(__file__), "output", "github_issues.json")

# 官方 GitHub MCP Server 的默认启动命令（可用 GITHUB_MCP_COMMAND 覆盖）。
# 默认用 Docker 运行官方镜像；也可换成任何暴露 create_issue 工具的 MCP Server。
_DEFAULT_MCP_COMMAND = (
    "docker run -i --rm -e GITHUB_PERSONAL_ACCESS_TOKEN ghcr.io/github/github-mcp-server")

# 优先级 -> GitHub label 的映射
_PRIORITY_LABEL = {"P0": "priority:critical", "P1": "priority:high",
                   "P2": "priority:medium", "P3": "priority:low"}


def build_issue(problem: Dict[str, Any], test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
    """把一条诊断问题 + 关联回归测试用例，渲染成 GitHub Issue 结构。"""
    prio = problem.get("priority", "P2")
    module = problem.get("module", "unknown")
    related = [tc for tc in test_cases
               if tc.get("trajectory_id") in problem.get("trajectory_ids", [])]

    body_lines = [
        f"## 问题描述\n{problem.get('description', '')}",
        f"\n## 涉及模块\n`{module}`",
        f"\n## 优先级\n{prio}",
        f"\n## 改进建议\n{problem.get('suggestion', '')}",
        f"\n## 相关生产轨迹\n" + ", ".join(problem.get("trajectory_ids", []) or ["(无)"]),
    ]
    if related:
        body_lines.append("\n## 关联回归测试用例")
        for tc in related:
            body_lines.append(
                f"- `{tc.get('test_id')}` (轨迹 {tc.get('trajectory_id')} "
                f"第 {tc.get('focus_turn')} 轮): {tc.get('description', '')}")

    return {
        "title": f"[{prio}][{module}] {problem.get('title', problem.get('description', ''))[:60]}",
        "body": "\n".join(body_lines),
        "labels": [f"module:{module}", _PRIORITY_LABEL.get(prio, "priority:medium"),
                   "auto-diagnosis"],
        "assignees": [problem.get("suggested_assignee", "")] if problem.get("suggested_assignee") else [],
    }


def create_issues(problems: List[Dict[str, Any]], test_cases: List[Dict[str, Any]],
                  mock: bool = True, out_path: str = _OUT,
                  repo: str = None, token: str = None) -> List[Dict[str, Any]]:
    """为每条问题创建 Issue。

    mock=True（默认）：打印 + 落盘到 out_path，不联网。
    mock=False：通过 GitHub MCP Server 在 repo（owner/repo）真实创建 Issue，需 token。
    """
    issues = [build_issue(p, test_cases) for p in problems]

    if mock:
        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        payload = {"created_at": datetime.now().isoformat(),
                   "mode": "mock", "issues": issues}
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(payload, f, ensure_ascii=False, indent=2)
        print(f"\n[github_mcp:mock] 已将 {len(issues)} 个 Issue 写入 {out_path}")
        for i, iss in enumerate(issues, 1):
            print(f"\n----- Mock GitHub Issue #{i} -----")
            print(f"title  : {iss['title']}")
            print(f"labels : {iss['labels']}")
            print("body   :")
            for ln in iss["body"].splitlines():
                print("  " + ln)
    else:
        if not token or not repo:
            raise RuntimeError(
                "真实创建需 GITHUB_TOKEN 与 GITHUB_REPO(owner/repo)，见 README。")
        created = _create_issues_via_mcp(issues, repo=repo, token=token)
        print(f"\n[github_mcp] 通过 MCP 在 {repo} 创建了 {len(created)} 个 Issue：")
        for url in created:
            print(f"    {url}")

    return issues


def _create_issues_via_mcp(issues: List[Dict[str, Any]], repo: str, token: str) -> List[str]:
    """通过 stdio 连接官方 GitHub MCP Server，逐个调用 create_issue 工具。

    返回创建成功的 Issue URL 列表。需要已安装 `mcp` Python SDK 与可用的
    GitHub MCP Server（默认 Docker 镜像，可用 GITHUB_MCP_COMMAND 覆盖启动命令）。
    """
    import asyncio

    try:
        from mcp import ClientSession, StdioServerParameters
        from mcp.client.stdio import stdio_client
    except ImportError as e:  # pragma: no cover - 依赖缺失时给出清晰指引
        raise RuntimeError(
            "缺少 MCP 客户端：pip install mcp（并确保 GitHub MCP Server 可启动）") from e

    owner, _, name = repo.partition("/")
    if not owner or not name:
        raise RuntimeError(f"GITHUB_REPO 需形如 owner/repo，收到：{repo!r}")

    cmd = shlex.split(os.getenv("GITHUB_MCP_COMMAND", _DEFAULT_MCP_COMMAND))
    params = StdioServerParameters(
        command=cmd[0], args=cmd[1:],
        env={**os.environ, "GITHUB_PERSONAL_ACCESS_TOKEN": token})

    async def _run() -> List[str]:
        urls: List[str] = []
        async with stdio_client(params) as (read, write):
            async with ClientSession(read, write) as session:
                await session.initialize()
                for iss in issues:
                    result = await session.call_tool("create_issue", {
                        "owner": owner, "repo": name,
                        "title": iss["title"], "body": iss["body"],
                        "labels": iss["labels"],
                        "assignees": iss["assignees"],
                    })
                    # MCP 工具返回文本内容；尽力提取 Issue URL，否则回退为原始文本。
                    text = "".join(getattr(c, "text", "") for c in result.content)
                    url = text
                    try:
                        url = json.loads(text).get("html_url", text)
                    except Exception:
                        pass
                    urls.append(url)
        return urls

    return asyncio.run(_run())
