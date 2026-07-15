#!/usr/bin/env python3
"""
Quickstart script for the coding agent
"""

import os
from agent import CodingAgent
from config import Config


def main():
    """Run a simple coding agent interaction"""
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        print(f"Configuration error: {e}")
        print("Please set at least one API key in your .env file")
        return
    
    # Initialize agent
    provider = Config.get_provider()
    api_key = Config.get_api_key()
    base_url = Config.get_base_url()
    agent = CodingAgent(
        api_key=api_key,
        model=Config.DEFAULT_MODEL,
        base_url=base_url,
        provider=provider
    )
    
    # Example query
    user_query = """
Create a simple Python script called hello_world.py that:
1. Prints "Hello, World!"
2. Has a function that greets a person by name
3. Has a main block that demonstrates the function

After creating it, run it to verify it works.
"""
    
    print("=" * 80)
    print("CODING AGENT QUICKSTART")
    print("=" * 80)
    print(f"\nUser: {user_query.strip()}\n")
    print("-" * 80)
    print()
    
    # Run agent
    for event in agent.run(user_query):
        if event["type"] == "text_delta":
            print(event["delta"], end="", flush=True)
        
        elif event["type"] == "tool_call":
            print(f"\n\n🔧 Calling tool: {event['tool']}")
            print(f"   Input: {event['input']}")
        
        elif event["type"] == "tool_execution_complete":
            result = event["result"]
            metadata = result.get("_metadata", {})
            print(f"   ✓ {metadata.get('tool')} call #{metadata.get('call_number')} completed")
            
            # Show important results
            if "error" in result:
                print(f"   ⚠️  Error: {result['error']}")
            elif "output" in result:
                output = result["output"][:200]
                print(f"   Output: {output}...")
            
            # Show lint check results
            if "lint_check" in result:
                lint = result["lint_check"]
                if lint.get("has_errors"):
                    print(f"   ⚠️  Lint errors found: {lint.get('errors')}")
                else:
                    print(f"   ✓ No lint errors detected")
        
        elif event["type"] == "done":
            print("\n\n" + "=" * 80)
            print("✅ Agent completed successfully!")
            print("=" * 80)
        
        elif event["type"] == "error":
            print(f"\n\n❌ Error: {event['error']}")
        
        elif event["type"] == "max_iterations_reached":
            print(f"\n\n⚠️  Reached maximum iterations ({event['max_iterations']})")


if __name__ == "__main__":
    main()

