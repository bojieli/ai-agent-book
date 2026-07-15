"""Quick start guide for the execution tools MCP server."""

import asyncio
from llm_helper import LLMHelper
from file_tools import FileTools
from execution_tools import ExecutionTools


async def quickstart():
    """Quick demonstration of the execution tools."""
    print("=== Execution Tools MCP Server - Quick Start ===\n")
    
    # Initialize
    print("Initializing tools...")
    llm_helper = LLMHelper()
    file_tools = FileTools(llm_helper)
    execution_tools = ExecutionTools(llm_helper)
    
    # 1. File operations
    print("\n1. File Operations Demo")
    print("-" * 50)
    
    print("\nWriting a Python script...")
    result = await file_tools.write_file(
        path="hello.py",
        content="""#!/usr/bin/env python3
\"\"\"A simple greeting script.\"\"\"

def main():
    name = "World"
    print(f"Hello, {name}!")

if __name__ == "__main__":
    main()
""",
        overwrite=True
    )
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    if result['success']:
        print(f"Written to: {result['path']}")
        print(f"Verification: {result['verification']}")
    
    # 2. Code execution
    print("\n2. Code Interpreter Demo")
    print("-" * 50)
    
    print("\nExecuting Python code...")
    result = await execution_tools.code_interpreter(
        code="""
# Calculate fibonacci sequence
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print("Fibonacci sequence (first 10 numbers):")
for i in range(10):
    print(f"F({i}) = {fibonacci(i)}")
"""
    )
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    if result['success']:
        print("Output:")
        print(result['stdout'][:500])  # Print first 500 chars
    
    # 3. Terminal execution
    print("\n3. Virtual Terminal Demo")
    print("-" * 50)
    
    print("\nExecuting shell command...")
    result = await execution_tools.virtual_terminal(
        command="python --version && echo 'Current directory:' && pwd"
    )
    print(f"Status: {'✓ Success' if result['success'] else '✗ Failed'}")
    if result['success']:
        print("Output:")
        print(result['stdout'])
    
    # Summary
    print("\n" + "=" * 50)
    print("Quick start completed!")
    print("\nKey Features:")
    print("  • File operations with automatic syntax verification")
    print("  • Code execution with error analysis")
    print("  • Shell commands with result summarization")
    print("  • LLM-based approval for dangerous operations")
    print("  • External integrations (Google Calendar, GitHub)")
    print("\nNext Steps:")
    print("  • Run 'python examples.py' for more examples")
    print("  • Run 'python server.py' to start the MCP server")
    print("  • See README.md for full documentation")


if __name__ == "__main__":
    asyncio.run(quickstart())
