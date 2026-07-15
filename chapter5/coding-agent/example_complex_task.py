#!/usr/bin/env python3
"""
Example of a complex coding task with the agent
"""

from agent import CodingAgent
from config import Config


def run_complex_task():
    """Run a complex multi-step task"""
    
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
    
    # Complex task that requires multiple steps
    user_query = """
I need you to create a simple web scraper project:

1. Create a directory called 'web_scraper'
2. Inside it, create:
   - requirements.txt with requests and beautifulsoup4
   - scraper.py with a function that:
     * Takes a URL as input
     * Fetches the page
     * Extracts all links
     * Returns them as a list
   - test_scraper.py with basic unit tests
   - README.md with usage instructions

3. After creating everything, check if there are any syntax errors in the Python files

Please implement this step by step, using the TODO list to track your progress.
"""
    
    print("=" * 80)
    print("COMPLEX CODING TASK EXAMPLE")
    print("=" * 80)
    print(f"\nUser: {user_query.strip()}\n")
    print("-" * 80)
    
    # Track statistics
    tool_calls = 0
    iterations = 0
    
    for event in agent.run(user_query, max_iterations=30):
        if event["type"] == "iteration_start":
            iterations = event["iteration"]
            print(f"\n[Iteration {iterations}]")
        
        elif event["type"] == "text_delta":
            print(event["delta"], end="", flush=True)
        
        elif event["type"] == "tool_call":
            tool_calls += 1
            print(f"\n\n🔧 Tool #{tool_calls}: {event['tool']}")
        
        elif event["type"] == "tool_execution_complete":
            result = event["result"]
            
            # Show TODO updates
            if event["tool"] == "TodoWrite":
                print(f"   ✓ TODO list updated:")
                print(f"      - Total: {result.get('total_todos', 0)}")
                print(f"      - In Progress: {result.get('in_progress', 0)}")
                print(f"      - Completed: {result.get('completed', 0)}")
            
            # Show file operations
            elif event["tool"] in ["Write", "Edit", "MultiEdit"]:
                print(f"   ✓ File: {result.get('file_path', 'unknown')}")
                if "lint_check" in result:
                    lint = result["lint_check"]
                    if lint.get("has_errors"):
                        print(f"   ⚠️  Lint errors detected!")
                    else:
                        print(f"   ✓ No lint errors")
            
            # Show bash results
            elif event["tool"] == "Bash":
                exit_code = result.get("exit_code", -1)
                if exit_code == 0:
                    print(f"   ✓ Command executed successfully")
                else:
                    print(f"   ⚠️  Command failed with exit code {exit_code}")
        
        elif event["type"] == "done":
            print("\n\n" + "=" * 80)
            print("✅ TASK COMPLETED!")
            print(f"   Total iterations: {iterations}")
            print(f"   Total tool calls: {tool_calls}")
            print("=" * 80)
        
        elif event["type"] == "error":
            print(f"\n\n❌ Error: {event['error']}")
        
        elif event["type"] == "max_iterations_reached":
            print(f"\n\n⚠️  Reached maximum iterations")


if __name__ == "__main__":
    run_complex_task()

