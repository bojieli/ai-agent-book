"""
Tool-selection benchmark and offline evaluation.

Provides a small labeled benchmark (task -> ground-truth tool) and utilities to
quantify, *without any API calls*, the core claim of the chapter: when a tool
ecosystem grows to hundreds of tools, retrieving the few relevant tools on demand
keeps the right tool reachable while slashing the token cost of dumping every tool
schema into context.

Two things are measured here deterministically:
  1. Retrieval recall@k  — is the ground-truth tool among the tools a strategy
     places in the model's context?
  2. Context schema tokens — how many tokens the injected tool schemas cost.

End-to-end accuracy/latency (whether the model actually *calls* the right tool)
requires an API key and lives in demo_comparison.py.
"""

from typing import List, Dict

from tool_knowledge_base import (
    ToolDefinition,
    ServerDefinition,
    create_tool_knowledge_base,
    get_all_tools,
    calculate_total_tokens,
)
from semantic_router import SemanticRouter


# Labeled benchmark: each task has one (or a few acceptable) ground-truth tool(s).
# Queries are in English to match the English tool descriptions used by the
# TF-IDF router (see tool_knowledge_base.py).
BENCHMARK_TASKS: List[Dict] = [
    {
        "name": "GitHub repo search",
        "task": "Search GitHub for popular Python machine learning repositories with more than 10000 stars",
        "gold_tools": ["github_search_repos"],
    },
    {
        "name": "Read config file",
        "task": "Read the contents of the local configuration file at /etc/app/config.json",
        "gold_tools": ["fs_read_file"],
    },
    {
        "name": "List directory",
        "task": "List all files and subdirectories under the /var/log directory",
        "gold_tools": ["fs_list_directory"],
    },
    {
        "name": "Summary statistics",
        "task": "Calculate the mean, median and standard deviation of last quarter's sales figures",
        "gold_tools": ["analytics_summarize"],
    },
    {
        "name": "Send email",
        "task": "Send the quarterly performance summary email to the team members",
        "gold_tools": ["comm_send_email"],
    },
    {
        "name": "Deploy to production",
        "task": "Deploy version 2.3.0 of the application to the production environment",
        "gold_tools": ["devops_deploy"],
    },
    {
        "name": "SQL query",
        "task": "Run a SQL query on the database to count the number of active users per region",
        "gold_tools": ["db_query"],
    },
    {
        "name": "Upload to cloud",
        "task": "Upload the local report file to the cloud storage bucket",
        "gold_tools": ["cloud_upload_storage"],
    },
    {
        "name": "Scrape prices",
        "task": "Scrape the prices of all products listed on the given web page",
        "gold_tools": ["web_scrape"],
    },
    {
        "name": "Monitor service",
        "task": "Get the current CPU and memory monitoring metrics for the staging service",
        "gold_tools": ["devops_monitor"],
    },
]


def make_distractor_servers(num_tools: int, start_index: int = 1,
                            tools_per_server: int = 5) -> List[ServerDefinition]:
    """
    Generate synthetic *distractor* servers/tools to inflate the catalog size.

    These are deliberately generic "internal service" operations. They add real
    schema tokens and act as retrieval noise, so we can study how each strategy
    scales as the ecosystem grows to hundreds of tools — without hand-writing
    hundreds of realistic tools. They are clearly named ``svcN_opM`` so nobody
    mistakes them for the real catalog.
    """
    servers: List[ServerDefinition] = []
    created = 0
    server_idx = start_index
    while created < num_tools:
        n = min(tools_per_server, num_tools - created)
        tools = []
        for j in range(1, n + 1):
            op = created + j
            tools.append(ToolDefinition(
                name=f"svc{server_idx}_op{j}",
                description=(
                    f"Auxiliary internal-service operation {op} for background "
                    f"housekeeping on internal resource group {server_idx}"
                ),
                parameters={
                    "type": "object",
                    "properties": {
                        "resource_id": {"type": "string", "description": "Internal resource identifier"},
                        "options": {"type": "object", "description": "Operation options"},
                    },
                    "required": ["resource_id"],
                },
                server=f"internal_service_{server_idx}",
            ))
        servers.append(ServerDefinition(
            name=f"internal_service_{server_idx}",
            description=f"Internal auxiliary service {server_idx} for background housekeeping operations",
            tools=tools,
        ))
        created += n
        server_idx += 1
    return servers


def build_catalog(num_tools: int = 0) -> List[ServerDefinition]:
    """
    Build the tool catalog, optionally padded with distractor tools.

    Args:
        num_tools: Target total number of tools. 0 (default) keeps the real
            catalog untouched. Values below the real catalog size are ignored
            (we never drop real tools); larger values pad with distractors.
    """
    servers = create_tool_knowledge_base()
    real_count = len(get_all_tools(servers))
    if num_tools and num_tools > real_count:
        servers = servers + make_distractor_servers(num_tools - real_count)
    return servers


def evaluate_offline(servers: List[ServerDefinition], top_k: int,
                     tasks: List[Dict] = None) -> Dict:
    """
    Deterministically compare tool-selection strategies (no API calls).

    Returns a dict with per-strategy aggregate metrics and per-task retrieval
    details. Two strategies are directly comparable offline:

      * ``all-tools``  — inject every tool schema. Recall is 1.0 by construction
        (the gold tool is always present) but token cost grows with the catalog.
      * ``retrieval``  — inject only the top-k retrieved tools. Recall is measured;
        token cost stays roughly flat as the catalog grows.

    (The ``active`` MCP-Zero strategy needs the model in the loop, so it is only
    evaluated in the online benchmark.)
    """
    tasks = tasks or BENCHMARK_TASKS
    router = SemanticRouter(servers)
    all_tools = get_all_tools(servers)
    all_tools_tokens = calculate_total_tokens(all_tools)

    per_task = []
    retrieval_hits = 0
    retrieval_tokens_sum = 0
    for t in tasks:
        retrieved = router.retrieve(t["task"], top_k)
        retrieved_names = [tool.name for tool in retrieved]
        hit = any(g in retrieved_names for g in t["gold_tools"])
        retrieval_hits += int(hit)
        retrieval_tokens_sum += calculate_total_tokens(retrieved)
        per_task.append({
            "name": t["name"],
            "gold_tools": t["gold_tools"],
            "retrieved": retrieved_names,
            "hit": hit,
        })

    n = len(tasks)
    return {
        "num_tools": len(all_tools),
        "top_k": top_k,
        "per_task": per_task,
        "strategies": {
            "all-tools": {
                "tools_in_context": len(all_tools),
                "avg_schema_tokens": all_tools_tokens,
                "recall": 1.0,
            },
            "retrieval": {
                "tools_in_context": top_k,
                "avg_schema_tokens": retrieval_tokens_sum / n,
                "recall": retrieval_hits / n,
            },
        },
    }
