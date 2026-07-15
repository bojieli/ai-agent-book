#!/usr/bin/env python3
"""
Example demonstrating system hints features
"""

from agent import CodingAgent
from config import Config


def demo_system_hints():
    """Demonstrate system hint features like timestamps, tool counting, and TODO tracking"""
    
    Config.validate()
    
    provider = Config.get_provider()
    api_key = Config.get_api_key()
    base_url = Config.get_base_url()
    agent = CodingAgent(
        api_key=api_key,
        model=Config.DEFAULT_MODEL,
        base_url=base_url,
        provider=provider
    )
    
    user_query = """
Let's test the system hint features:

1. Create 3 simple Python files (test1.py, test2.py, test3.py)
2. Each should just print a different message
3. Use a TODO list to track your progress
4. After creating them, read each one back to verify

This will help demonstrate:
- Timestamps on each operation
- Tool call counting
- TODO list tracking
- Working directory persistence across commands
"""
    
    print("=" * 80)
    print("SYSTEM HINTS DEMONSTRATION")
    print("=" * 80)
    print("\nThis example will show:")
    print("  • Timestamps on all operations")
    print("  • Tool call counters (watch for warnings after 3+ calls)")
    print("  • TODO list tracking")
    print("  • Persistent shell session")
    print("  • Automatic lint checking")
    print("=" * 80)
    print(f"\nUser: {user_query.strip()}\n")
    print("-" * 80)
    
    for event in agent.run(user_query, max_iterations=30):
        if event["type"] == "user_message":
            print(f"\n[{event['timestamp']}] User message received")
        
        elif event["type"] == "iteration_start":
            print(f"\n{'='*60}")
            print(f"ITERATION {event['iteration']}")
            
            # Show current system state
            state = agent.system_state
            print(f"System State:")
            print(f"  Working Directory: {state.current_directory}")
            print(f"  Tool Calls: {sum(state.tool_call_counts.values())}")
            if state.todos:
                print(f"  TODOs: {len(state.todos)} total")
            print('='*60)
        
        elif event["type"] == "text_delta":
            print(event["delta"], end="", flush=True)
        
        elif event["type"] == "tool_call":
            print(f"\n\n🔧 Calling: {event['tool']}")
        
        elif event["type"] == "tool_execution_complete":
            result = event["result"]
            metadata = result.get("_metadata", {})
            
            print(f"   [{metadata.get('timestamp')}] Call #{metadata.get('call_number')}")
            
            # Highlight repeated tool calls
            if metadata.get('call_number', 0) >= 3:
                print(f"   ⚠️  This tool has been called {metadata.get('call_number')} times!")
            
            # Show TODO updates
            if event["tool"] == "TodoWrite":
                print(f"   📋 TODO List:")
                print(f"      Pending: {result.get('pending', 0)}")
                print(f"      In Progress: {result.get('in_progress', 0)}")
                print(f"      Completed: {result.get('completed', 0)}")
                
                # Show actual TODOs
                if agent.system_state.todos:
                    for todo in agent.system_state.todos:
                        status = todo['status']
                        icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}[status]
                        print(f"      {icon} {todo['content']}")
            
            elif event["tool"] == "Write":
                print(f"   📝 Created: {result.get('file_path')}")
                if "lint_check" in result:
                    lint = result["lint_check"]
                    if lint.get("has_errors"):
                        print(f"      ❌ Lint errors found!")
                    else:
                        print(f"      ✅ No syntax errors")
            
            elif event["tool"] == "Bash":
                wd = result.get("working_directory", "unknown")
                print(f"   💻 Working directory: {wd}")
                print(f"   Exit code: {result.get('exit_code', 'unknown')}")
        
        elif event["type"] == "done":
            print("\n\n" + "=" * 80)
            print("✅ DEMONSTRATION COMPLETE!")
            print("\nFinal System State:")
            state = agent.system_state
            print(f"  • Total tool calls: {sum(state.tool_call_counts.values())}")
            print(f"  • Tool breakdown:")
            for tool, count in sorted(state.tool_call_counts.items()):
                print(f"    - {tool}: {count}")
            if state.todos:
                completed = sum(1 for t in state.todos if t['status'] == 'completed')
                print(f"  • TODOs: {completed}/{len(state.todos)} completed")
            print("=" * 80)
        
        elif event["type"] == "error":
            print(f"\n\n❌ Error: {event['error']}")


if __name__ == "__main__":
    demo_system_hints()

