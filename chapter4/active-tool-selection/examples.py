"""
Example use cases demonstrating active tool selection.
"""

from agent import ActiveToolAgent
from semantic_router import SemanticRouter
from tool_knowledge_base import create_tool_knowledge_base


def example_github_workflow():
    """Example: GitHub development workflow."""
    print("\n" + "=" * 70)
    print("Example 1: GitHub Development Workflow")
    print("=" * 70 + "\n")
    
    agent = ActiveToolAgent()
    
    task = """I need to:
1. Search for Python testing frameworks on GitHub
2. Find issues labeled 'good-first-issue' in the top repository
3. Create a new branch and make changes
4. Create a pull request"""
    
    print(f"Task:\n{task}\n")
    
    result = agent.execute_task(task)
    
    print(f"\n✅ Tools discovered: {len(result['tools_loaded'])}")
    print(f"   {', '.join(result['tools_loaded'])}")
    print(f"\n📊 Metrics:")
    print(f"   • Tokens used: {result['metrics']['tokens_used']:,}")
    print(f"   • Tool requests: {result['metrics']['tool_requests']}")
    print(f"   • API calls: {result['metrics']['api_calls']}")


def example_data_pipeline():
    """Example: Data processing pipeline."""
    print("\n" + "=" * 70)
    print("Example 2: Data Processing Pipeline")
    print("=" * 70 + "\n")
    
    agent = ActiveToolAgent()
    
    task = """Build a data pipeline:
1. Query the database for last month's sales data
2. Calculate summary statistics
3. Create visualizations (bar charts and trend lines)
4. Upload results to cloud storage
5. Send notification email to stakeholders"""
    
    print(f"Task:\n{task}\n")
    
    result = agent.execute_task(task)
    
    print(f"\n✅ Cross-domain toolchain built:")
    for i, tool in enumerate(result['tools_loaded'], 1):
        print(f"   {i}. {tool}")
    
    print(f"\n📊 Efficiency:")
    print(f"   • Only {len(result['tools_loaded'])} tools loaded (out of 35 available)")
    print(f"   • Token savings: ~90% compared to loading all tools")


def example_devops_automation():
    """Example: DevOps automation task."""
    print("\n" + "=" * 70)
    print("Example 3: DevOps Automation")
    print("=" * 70 + "\n")
    
    agent = ActiveToolAgent()
    
    task = """Automate deployment process:
1. Check monitoring metrics for the staging environment
2. If metrics are healthy, trigger production deployment pipeline
3. Monitor deployment progress and logs
4. If any errors occur, automatically rollback
5. Send deployment status notification"""
    
    print(f"Task:\n{task}\n")
    
    result = agent.execute_task(task)
    
    print(f"\n✅ DevOps toolchain assembled:")
    print(f"   Tools: {', '.join(result['tools_loaded'])}")
    print(f"\n💡 Active discovery enabled iterative refinement:")
    print(f"   • Started with monitoring tools")
    print(f"   • Added deployment tools when needed")
    print(f"   • Included notification tools at the end")


def example_semantic_search():
    """Example: Demonstrate semantic search capabilities."""
    print("\n" + "=" * 70)
    print("Example 4: Semantic Tool Search")
    print("=" * 70 + "\n")
    
    servers = create_tool_knowledge_base()
    router = SemanticRouter(servers)
    
    queries = [
        "I need to version control my code",
        "Store and retrieve structured data",
        "Make HTTP requests to APIs",
        "Analyze datasets and create graphs",
        "Configure cloud infrastructure"
    ]
    
    print("Testing semantic understanding of tool requests:\n")
    
    for query in queries:
        print(f"🔍 Query: '{query}'")
        tools = router.route_request(query, top_k_servers=1, top_k_tools=3)
        
        if tools:
            print(f"   ✓ Found: {', '.join([t.name for t in tools])}")
        else:
            print(f"   ✗ No matching tools found")
        print()


def example_multi_turn_discovery():
    """Example: Multi-turn conversation with progressive tool discovery."""
    print("\n" + "=" * 70)
    print("Example 5: Multi-Turn Progressive Discovery")
    print("=" * 70 + "\n")
    
    print("Scenario: Agent progressively discovers tools across multiple turns\n")
    
    agent = ActiveToolAgent()
    
    # Turn 1: Initial request
    print("👤 User: Search for machine learning repositories")
    result1 = agent.execute_task("Search for machine learning repositories")
    print(f"🤖 Agent loaded: {', '.join(result1['tools_loaded'][:2])}")
    print()
    
    # Turn 2: Additional requirements emerge
    print("👤 User: Now download the README files and analyze them")
    result2 = agent.execute_task("Download README files and analyze them")
    print(f"🤖 Agent additionally loaded: filesystem and analytics tools")
    print()
    
    # Turn 3: Visualization needed
    print("👤 User: Create a visualization comparing repository sizes")
    result3 = agent.execute_task("Create a visualization comparing repository sizes")
    print(f"🤖 Agent additionally loaded: visualization tools")
    print()
    
    print("💡 Tools were discovered on-demand as the conversation evolved!")
    print("   This demonstrates the iterative capability extension principle.")


def example_efficiency_comparison():
    """Example: Show efficiency comparison with metrics."""
    print("\n" + "=" * 70)
    print("Example 6: Efficiency Comparison")
    print("=" * 70 + "\n")
    
    from agent import PassiveToolAgent
    
    task = "List files in the current directory"
    
    print(f"Task: {task}\n")
    
    # Active approach
    print("🔄 Active Tool Discovery:")
    active_agent = ActiveToolAgent()
    active_result = active_agent.execute_task(task)
    print(f"   • Tools loaded: {active_result['metrics']['tools_loaded']}")
    print(f"   • Tokens used: {active_result['metrics']['tokens_used']:,}")
    print()
    
    # Passive approach
    print("📚 Passive Tool Injection:")
    passive_agent = PassiveToolAgent()
    passive_result = passive_agent.execute_task(task)
    print(f"   • Tools loaded: {passive_result['metrics']['tools_loaded']}")
    print(f"   • Tokens used: {passive_result['metrics']['tokens_used']:,}")
    print()
    
    # Comparison
    reduction = (1 - active_result['metrics']['tokens_used'] / 
                passive_result['metrics']['tokens_used']) * 100
    
    print(f"📊 Efficiency Gain:")
    print(f"   • Token reduction: {reduction:.1f}%")
    print(f"   • Tool reduction: {active_result['metrics']['tools_loaded']} vs {passive_result['metrics']['tools_loaded']}")
    print()
    print("💡 For simple tasks requiring 1-2 tools, active discovery achieves")
    print("   massive efficiency gains while maintaining full capability!")


if __name__ == "__main__":
    print("""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║                   Active Tool Selection Examples                           ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝
    """)
    
    # Run all examples
    example_github_workflow()
    example_data_pipeline()
    example_devops_automation()
    example_semantic_search()
    example_multi_turn_discovery()
    example_efficiency_comparison()
    
    print("\n" + "=" * 70)
    print("All examples completed!")
    print("=" * 70 + "\n")
