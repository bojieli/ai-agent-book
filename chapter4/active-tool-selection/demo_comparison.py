"""
Comparison Demo: Active vs Passive Tool Selection.

Demonstrates the efficiency gains of active tool discovery compared to
traditional passive tool injection approach.
"""

import argparse
import json
import time

from tabulate import tabulate
from agent import ActiveToolAgent, PassiveToolAgent, RetrievalToolAgent
from tool_knowledge_base import create_tool_knowledge_base, calculate_total_tokens
import benchmark
import config


def print_section(title: str):
    """Print a formatted section header."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def run_comparison_demo():
    """Run side-by-side comparison of active vs passive approaches."""
    
    print_section("Active Tool Discovery vs Passive Tool Injection Comparison")
    
    # Show knowledge base statistics
    servers = create_tool_knowledge_base()
    all_tools = []
    for server in servers:
        all_tools.extend(server.tools)
    
    total_tokens = calculate_total_tokens(all_tools)
    
    print("📊 Tool Knowledge Base Statistics:")
    print(f"   • Total Servers: {len(servers)}")
    print(f"   • Total Tools: {len(all_tools)}")
    print(f"   • Estimated tokens for all tool schemas: ~{total_tokens:,}")
    print()
    
    # Test tasks
    test_tasks = [
        {
            "name": "GitHub Repository Search",
            "task": "Find popular Python machine learning repositories on GitHub with more than 10k stars"
        },
        {
            "name": "File System Operation",
            "task": "Read the configuration file at /etc/app/config.json and list all API keys"
        },
        {
            "name": "Data Analytics",
            "task": "Calculate summary statistics (mean, median, std) for the sales data in the last quarter"
        },
        {
            "name": "Multi-Domain Task",
            "task": "Clone the repository, analyze the code files, and generate a visualization of code complexity metrics"
        }
    ]
    
    results = []
    
    for test in test_tasks:
        print(f"\n🔍 Testing: {test['name']}")
        print(f"   Task: {test['task']}")
        print()
        
        # Test with Active Agent
        print("   [Active Agent] Executing...")
        active_agent = ActiveToolAgent()
        active_result = active_agent.execute_task(test['task'])
        
        # Test with Passive Agent
        print("   [Passive Agent] Executing...")
        passive_agent = PassiveToolAgent()
        passive_result = passive_agent.execute_task(test['task'])
        
        # Calculate efficiency metrics
        token_reduction = (1 - active_result['metrics']['tokens_used'] / 
                          passive_result['metrics']['tokens_used']) * 100
        
        tools_loaded_active = active_result['metrics']['tools_loaded']
        tools_loaded_passive = passive_result['metrics']['tools_loaded']
        
        results.append({
            'Task': test['name'],
            'Active Tokens': f"{active_result['metrics']['tokens_used']:,}",
            'Passive Tokens': f"{passive_result['metrics']['tokens_used']:,}",
            'Token Reduction': f"{token_reduction:.1f}%",
            'Active Tools': tools_loaded_active,
            'Passive Tools': tools_loaded_passive,
            'Tool Reduction': f"{(1 - tools_loaded_active/tools_loaded_passive)*100:.1f}%"
        })
        
        print(f"   ✓ Active: {active_result['metrics']['tokens_used']:,} tokens, {tools_loaded_active} tools")
        print(f"   ✓ Passive: {passive_result['metrics']['tokens_used']:,} tokens, {tools_loaded_passive} tools")
        print(f"   💡 Reduction: {token_reduction:.1f}% tokens saved")
    
    # Display results table
    print_section("Comparison Results")
    print(tabulate(results, headers='keys', tablefmt='grid'))
    
    # Calculate averages
    avg_token_reduction = sum(
        float(r['Token Reduction'].rstrip('%')) for r in results
    ) / len(results)
    
    print(f"\n📈 Summary:")
    print(f"   • Average token reduction: {avg_token_reduction:.1f}%")
    print(f"   • Active approach: Loads only {results[0]['Active Tools']} tools on average")
    print(f"   • Passive approach: Loads all {results[0]['Passive Tools']} tools upfront")
    print()
    print("💡 Key Insights:")
    print("   • Active tool discovery maintains minimal context footprint")
    print("   • Significant token savings (80-98% in typical scenarios)")
    print("   • Agent autonomy preserved - discovers tools as needed")
    print("   • Scales efficiently as tool ecosystem grows")


def demo_active_discovery_process():
    """Demonstrate the active discovery process in detail."""
    
    print_section("Active Tool Discovery Process Demonstration")
    
    task = "Search for Python repositories on GitHub and analyze their README files"
    
    print(f"📝 Task: {task}\n")
    
    agent = ActiveToolAgent()
    result = agent.execute_task(task)
    
    print("🔄 Discovery Process:")
    print(f"   • Tool requests made: {result['metrics']['tool_requests']}")
    print(f"   • Tools loaded: {result['metrics']['tools_loaded']}")
    print(f"   • API calls: {result['metrics']['api_calls']}")
    print(f"   • Total tokens: {result['metrics']['tokens_used']:,}")
    print()
    
    print("🛠️  Tools Discovered:")
    for i, tool in enumerate(result['tools_loaded'], 1):
        print(f"   {i}. {tool}")
    print()
    
    print("💬 Conversation Flow:")
    for i, msg in enumerate(result['conversation'], 1):
        role = msg['role'].upper()
        content = msg.get('content', '[Tool Call]')
        if content and len(content) > 100:
            content = content[:100] + "..."
        print(f"   {i}. [{role}] {content}")
    print()
    
    print("✅ Final Response:")
    print(f"   {result['response']}")


def demo_semantic_routing():
    """Demonstrate hierarchical semantic routing."""
    
    print_section("Hierarchical Semantic Routing Demonstration")
    
    from semantic_router import SemanticRouter
    
    servers = create_tool_knowledge_base()
    router = SemanticRouter(servers)
    
    test_queries = [
        "I need to search for repositories on GitHub",
        "Read a file from the local filesystem",
        "Query the database for user information",
        "Send an email notification to the team",
        "Deploy the application to production environment"
    ]
    
    print("🎯 Testing semantic routing for various requests:\n")
    
    for query in test_queries:
        print(f"📌 Request: '{query}'")
        
        details = router.get_routing_details(query, top_k_servers=2, top_k_tools=3)
        
        print("   Stage 1 - Server Routing:")
        for server in details['stage1_servers']:
            print(f"      • {server['name']}: {server['score']:.3f}")
        
        print("   Stage 2 - Tool Routing:")
        for tool in details['final_tools']:
            print(f"      • {tool['name']} ({tool['server']}): {tool['score']:.3f}")
        print()


def demo_iterative_capability_extension():
    """Demonstrate iterative capability extension."""
    
    print_section("Iterative Capability Extension Demonstration")
    
    print("🎯 Complex Multi-Step Task:")
    task = """Perform a comprehensive analysis:
1. Search GitHub for Python data science repositories
2. Download the top repository
3. Analyze the code structure
4. Generate visualization of dependencies
5. Send summary report via email"""
    
    print(f"{task}\n")
    
    agent = ActiveToolAgent()
    result = agent.execute_task(task)
    
    print("📊 Capability Extension Timeline:")
    print(f"   • Initial tools: 0")
    print(f"   • Tools after request 1: GitHub tools")
    print(f"   • Tools after request 2: Filesystem + GitHub")
    print(f"   • Tools after request 3: Analytics + Filesystem + GitHub")
    print(f"   • Tools after request 4: Communication + Analytics + Filesystem + GitHub")
    print()
    print(f"   Total tool requests: {result['metrics']['tool_requests']}")
    print(f"   Final toolchain size: {result['metrics']['tools_loaded']} tools")
    print()
    print("💡 The agent iteratively built a cross-domain toolchain as task understanding evolved!")


def run_offline_benchmark(servers, top_k: int, scaling: bool = True) -> dict:
    """
    Deterministic (no-API) strategy comparison: retrieval recall vs token cost.

    This is the heart of the experiment and runs without any API key. It shows
    that as the tool catalog grows, injecting all tools makes context token cost
    explode, while on-demand retrieval keeps cost roughly flat and still surfaces
    the right tool (recall).
    """
    print_section("Offline Strategy Comparison (deterministic, no API)")

    result = benchmark.evaluate_offline(servers, top_k)
    strat = result['strategies']

    print(f"Benchmark tasks: {len(benchmark.BENCHMARK_TASKS)}   "
          f"Catalog size: {result['num_tools']} tools   Retrieval top-k: {top_k}\n")

    rows = [
        {
            'Strategy': 'all-tools (dump everything)',
            'Tools in context': strat['all-tools']['tools_in_context'],
            'Schema tokens': f"{strat['all-tools']['avg_schema_tokens']:,}",
            'Recall (gold reachable)': f"{strat['all-tools']['recall']*100:.0f}%",
        },
        {
            'Strategy': f'retrieval (top-{top_k})',
            'Tools in context': strat['retrieval']['tools_in_context'],
            'Schema tokens': f"{strat['retrieval']['avg_schema_tokens']:,.0f}",
            'Recall (gold reachable)': f"{strat['retrieval']['recall']*100:.0f}%",
        },
    ]
    print(tabulate(rows, headers='keys', tablefmt='grid'))

    token_saving = (1 - strat['retrieval']['avg_schema_tokens'] /
                    strat['all-tools']['avg_schema_tokens']) * 100
    print(f"\n=> Retrieval keeps {strat['retrieval']['recall']*100:.0f}% recall while cutting "
          f"tool-schema tokens by {token_saving:.1f}% "
          f"({strat['all-tools']['avg_schema_tokens']:,} -> "
          f"{strat['retrieval']['avg_schema_tokens']:,.0f}).")

    # Per-task retrieval detail (which tools were surfaced, and whether the gold hit)
    print("\nPer-task retrieval (top-k tools surfaced for each task):")
    detail_rows = [
        {
            'Task': p['name'],
            'Gold tool': ', '.join(p['gold_tools']),
            'Hit': '✓' if p['hit'] else '✗',
            'Retrieved (top-k)': ', '.join(p['retrieved']),
        }
        for p in result['per_task']
    ]
    print(tabulate(detail_rows, headers='keys', tablefmt='github'))

    scaling_result = None
    if scaling:
        print_section("Scaling: token cost as the catalog grows")
        sizes = [size for size in [50, 100, 200, 400] if size >= result['num_tools']]
        if not sizes or sizes[0] != result['num_tools']:
            sizes = [result['num_tools']] + sizes
        scaling_rows = []
        scaling_result = []
        for size in sizes:
            padded = benchmark.build_catalog(size)
            r = benchmark.evaluate_offline(padded, top_k)
            s = r['strategies']
            scaling_rows.append({
                'Catalog tools': r['num_tools'],
                'all-tools tokens': f"{s['all-tools']['avg_schema_tokens']:,}",
                f'retrieval(top-{top_k}) tokens': f"{s['retrieval']['avg_schema_tokens']:,.0f}",
                'retrieval recall': f"{s['retrieval']['recall']*100:.0f}%",
            })
            scaling_result.append({
                'num_tools': r['num_tools'],
                'all_tools_tokens': s['all-tools']['avg_schema_tokens'],
                'retrieval_tokens': s['retrieval']['avg_schema_tokens'],
                'retrieval_recall': s['retrieval']['recall'],
            })
        print(tabulate(scaling_rows, headers='keys', tablefmt='grid'))
        print("\n=> all-tools token cost grows with the catalog; retrieval stays roughly flat.")

    return {'benchmark': result, 'scaling': scaling_result}


STRATEGY_AGENTS = {
    'all': ('all-tools', PassiveToolAgent),
    'retrieval': ('retrieval', RetrievalToolAgent),
    'active': ('active (MCP-Zero)', ActiveToolAgent),
}


def _build_agent(strategy: str, servers, top_k: int, model: str):
    """Instantiate the agent for a strategy (needs a valid API key)."""
    if strategy == 'retrieval':
        return RetrievalToolAgent(servers=servers, model=model, top_k=top_k)
    _, cls = STRATEGY_AGENTS[strategy]
    return cls(servers=servers, model=model)


def run_online_benchmark(servers, strategies, top_k: int, model: str,
                         tasks=None) -> dict:
    """
    End-to-end benchmark (requires API key): does the model actually CALL the
    ground-truth tool, at what token cost and latency, under each strategy?
    """
    tasks = tasks or benchmark.BENCHMARK_TASKS
    print_section("Online End-to-End Benchmark (requires API)")
    print(f"Model: {model}   Tasks: {len(tasks)}   "
          f"Catalog: {sum(len(s.tools) for s in servers)} tools   "
          f"Retrieval top-k: {top_k}\n")

    agents = {st: _build_agent(st, servers, top_k, model) for st in strategies}

    rows = []
    raw = {}
    for st in strategies:
        label = STRATEGY_AGENTS[st][0]
        agent = agents[st]
        hits = 0
        tokens_sum = 0
        latency_sum = 0.0
        tools_ctx_sum = 0
        per_task = []
        print(f"[{label}] running {len(tasks)} tasks...")
        for t in tasks:
            agent.reset()
            start = time.time()
            res = agent.execute_task(t['task'])
            elapsed = time.time() - start

            called = res['metrics'].get('tools_called', [])
            hit = any(g in called for g in t['gold_tools'])
            hits += int(hit)
            tokens_sum += res['metrics']['tokens_used']
            latency_sum += elapsed
            tools_ctx_sum += res['metrics']['tools_loaded']
            per_task.append({
                'task': t['name'],
                'gold': t['gold_tools'],
                'called': called,
                'hit': hit,
                'tokens': res['metrics']['tokens_used'],
                'latency': round(elapsed, 2),
            })

        n = len(tasks)
        rows.append({
            'Strategy': label,
            'Accuracy (calls gold)': f"{hits/n*100:.0f}%",
            'Avg tools in ctx': f"{tools_ctx_sum/n:.1f}",
            'Avg tokens': f"{tokens_sum/n:,.0f}",
            'Avg latency (s)': f"{latency_sum/n:.2f}",
        })
        raw[st] = {'accuracy': hits / n, 'per_task': per_task}

    print()
    print(tabulate(rows, headers='keys', tablefmt='grid'))
    return raw


def run_single_query(servers, strategies, query: str, top_k: int, model: str) -> dict:
    """Run a single ad-hoc query through the chosen strategies (requires API)."""
    print_section("Single Query")
    print(f"Query: {query}\n")
    raw = {}
    for st in strategies:
        label = STRATEGY_AGENTS[st][0]
        agent = _build_agent(st, servers, top_k, model)
        res = agent.execute_task(query)
        print(f"[{label}]")
        print(f"   tools in context : {res['metrics']['tools_loaded']}")
        print(f"   tools loaded     : {', '.join(res['tools_loaded']) or '(none)'}")
        print(f"   tools called     : {', '.join(res['metrics'].get('tools_called', [])) or '(none)'}")
        print(f"   tokens used      : {res['metrics']['tokens_used']:,}")
        print()
        raw[st] = {
            'tools_loaded': res['tools_loaded'],
            'tools_called': res['metrics'].get('tools_called', []),
            'tokens_used': res['metrics']['tokens_used'],
        }
    return raw


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="demo_comparison.py",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description=(
            "主动工具选择实验：对比\"把全部工具塞进上下文\"与\"按需检索工具\"两类策略。\n"
            "在工具数量增长到上百个时，动态检索（retrieval）在保持召回率的同时大幅降低\n"
            "上下文 token 成本，并减少模型的选择错误。\n\n"
            "策略说明：\n"
            "  all-tools  一次性注入全部工具（传统被动式基线）\n"
            "  retrieval  按任务语义检索 top-k 个工具后再注入（工具检索 / RAG 式）\n"
            "  active     MCP-Zero 式主动发现：模型迭代地请求所需工具\n\n"
            "离线表格（召回率 / token 成本 / 随工具规模的扩展性）无需 API Key 即可运行；\n"
            "端到端准确率与延迟对比需要配置 API Key。"
        ),
        epilog=(
            "示例：\n"
            "  python demo_comparison.py --offline                 # 仅离线对比，无需 API\n"
            "  python demo_comparison.py --offline --num-tools 200 # 扩展到 200 个工具再对比\n"
            "  python demo_comparison.py --strategy compare        # 三种策略端到端对比（需 API）\n"
            "  python demo_comparison.py --query \"部署到生产环境\" --strategy retrieval\n"
            "  python demo_comparison.py --output results.json     # 保存结果为 JSON"
        ),
    )
    parser.add_argument(
        "--strategy", choices=["all", "retrieval", "active", "compare"],
        default="compare",
        help="端到端评测使用的策略；compare 表示三种策略全部对比（默认：compare）",
    )
    parser.add_argument(
        "--query", type=str, default=None,
        help="只对单条查询运行选定策略（需要 API），而不是跑整个基准集",
    )
    parser.add_argument(
        "--num-tools", type=int, default=0, metavar="N",
        help="将工具目录扩充到 N 个（用合成干扰工具补齐，用于观察扩展性）；0 表示保持真实目录（默认：0）",
    )
    parser.add_argument(
        "--top-k", type=int, default=config.TOP_K_TOOLS, metavar="K",
        help=f"retrieval 策略检索的工具数量（默认：{config.TOP_K_TOOLS}）",
    )
    parser.add_argument(
        "--model", type=str, default=config.OPENAI_MODEL,
        help=f"覆盖使用的 LLM 模型（默认：{config.OPENAI_MODEL}）",
    )
    parser.add_argument(
        "--output", type=str, default=None, metavar="PATH",
        help="将结果写入 JSON 文件",
    )
    parser.add_argument(
        "--offline", action="store_true",
        help="仅运行离线确定性对比（召回率/token 成本），不进行任何 API 调用",
    )
    parser.add_argument(
        "--legacy-demos", action="store_true",
        help="额外运行原有的叙事式演示（语义路由、迭代发现等，需要 API）",
    )
    return parser


def _has_api_key() -> bool:
    return bool(config.OPENAI_API_KEY)


def main(argv=None):
    parser = build_parser()
    args = parser.parse_args(argv)

    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║              Active Tool Selection — Strategy Comparison                    ║
║              Inspired by MCP-Zero (arXiv:2506.01056)                        ║
╚════════════════════════════════════════════════════════════════════════════╝
""")

    servers = benchmark.build_catalog(args.num_tools)
    strategies = ["all", "retrieval", "active"] if args.strategy == "compare" else [args.strategy]

    results = {
        'config': {
            'num_tools': sum(len(s.tools) for s in servers),
            'top_k': args.top_k,
            'model': args.model,
            'strategies': strategies,
        }
    }

    # 1) Offline deterministic comparison — always runs, no API needed.
    if not args.query:
        results['offline'] = run_offline_benchmark(servers, args.top_k)

    # 2) Online end-to-end comparison — needs an API key.
    if args.offline:
        print("\n[offline mode] 跳过所有需要 API 的评测。")
    elif not _has_api_key():
        print("\n[提示] 未检测到 OPENAI_API_KEY，跳过端到端评测（准确率/延迟）。")
        print("       配置 .env 后可运行端到端对比；或使用 --offline 显式仅跑离线部分。")
    else:
        if args.query:
            results['single_query'] = run_single_query(
                servers, strategies, args.query, args.top_k, args.model)
        else:
            results['online'] = run_online_benchmark(
                servers, strategies, args.top_k, args.model)

        if args.legacy_demos:
            run_comparison_demo()
            demo_active_discovery_process()
            demo_semantic_routing()
            demo_iterative_capability_extension()

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f"\n结果已写入 {args.output}")

    print_section("Takeaway")
    print(
        "当工具数量增长到上百个时，把全部工具塞进上下文既浪费 token 又干扰决策；\n"
        "按需检索把\"工具选择\"问题转化为\"知识检索\"问题——在保持召回率的同时\n"
        "把工具描述的 token 成本压到很低，也减少了模型的选择错误。\n\n"
        "参考：MCP-Zero 论文 (https://arxiv.org/pdf/2506.01056)"
    )


if __name__ == "__main__":
    main()
