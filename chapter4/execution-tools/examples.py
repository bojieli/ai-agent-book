"""Example usage of the execution tools MCP server."""

import asyncio
from llm_helper import LLMHelper
from file_tools import FileTools
from execution_tools import ExecutionTools
from external_tools import ExternalTools


async def example_file_operations():
    """Example: File operations with verification."""
    print("=== File Operations Example ===\n")
    
    llm_helper = LLMHelper()
    file_tools = FileTools(llm_helper)
    
    # Write a Python file
    print("1. Writing a Python file...")
    result = await file_tools.write_file(
        path="test_script.py",
        content="""def greet(name):
    print(f"Hello, {name}!")

if __name__ == "__main__":
    greet("World")
""",
        overwrite=True
    )
    print(f"Result: {result}\n")
    
    # Edit the file
    print("2. Editing the file...")
    result = await file_tools.edit_file(
        path="test_script.py",
        search='greet("World")',
        replace='greet("MCP Server")'
    )
    print(f"Result: {result}\n")


async def example_code_interpreter():
    """Example: Code interpreter with analysis."""
    print("=== Code Interpreter Example ===\n")
    
    llm_helper = LLMHelper()
    execution_tools = ExecutionTools(llm_helper)
    
    # Execute valid code
    print("1. Executing valid code...")
    result = await execution_tools.code_interpreter(
        code="""
import math

# Calculate factorial
def factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)

print(f"Factorial of 5: {factorial(5)}")
print(f"Square root of 16: {math.sqrt(16)}")
"""
    )
    print(f"Result: {result}\n")
    
    # Execute code with error
    print("2. Executing code with error...")
    result = await execution_tools.code_interpreter(
        code="""
# This will cause an error
x = 10 / 0
"""
    )
    print(f"Result: {result}\n")


async def example_virtual_terminal():
    """Example: Virtual terminal."""
    print("=== Virtual Terminal Example ===\n")
    
    llm_helper = LLMHelper()
    execution_tools = ExecutionTools(llm_helper)
    
    # Execute simple command
    print("1. Listing current directory...")
    result = await execution_tools.virtual_terminal(
        command="ls -la"
    )
    print(f"Result: {result}\n")
    
    # Execute command with error
    print("2. Executing command that fails...")
    result = await execution_tools.virtual_terminal(
        command="cat nonexistent_file.txt"
    )
    print(f"Result: {result}\n")


async def example_google_calendar():
    """Example: Google Calendar integration."""
    print("=== Google Calendar Example ===\n")
    
    llm_helper = LLMHelper()
    external_tools = ExternalTools(llm_helper)
    
    print("Adding event to Google Calendar...")
    result = await external_tools.google_calendar_add(
        summary="Team Meeting",
        start_time="2025-10-01T10:00:00",
        end_time="2025-10-01T11:00:00",
        description="Quarterly planning meeting",
        location="Conference Room A"
    )
    print(f"Result: {result}\n")


async def example_github_pr():
    """Example: GitHub Pull Request creation."""
    print("=== GitHub PR Example ===\n")
    
    llm_helper = LLMHelper()
    external_tools = ExternalTools(llm_helper)
    
    print("Creating GitHub Pull Request...")
    result = await external_tools.github_create_pr(
        repo_name="owner/repository",
        title="Add new feature",
        body="This PR adds a new feature to improve performance.\n\n## Changes\n- Optimized algorithm\n- Added tests\n- Updated documentation",
        head_branch="feature/new-feature",
        base_branch="main"
    )
    print(f"Result: {result}\n")


async def main():
    """Run all examples."""
    try:
        # File operations
        await example_file_operations()
        
        # Code interpreter
        await example_code_interpreter()
        
        # Virtual terminal
        await example_virtual_terminal()
        
        # External tools (commented out as they require credentials)
        # await example_google_calendar()
        # await example_github_pr()
        
        print("All examples completed!")
        
    except Exception as e:
        print(f"Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
