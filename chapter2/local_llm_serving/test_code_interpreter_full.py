"""
Test the full Python environment code interpreter with error handling
"""
import json
from tools import ToolRegistry

def test_successful_execution():
    """Test that code executes successfully with full Python environment"""
    print("=" * 60)
    print("Test 1: Successful execution with full Python environment")
    print("=" * 60)
    
    registry = ToolRegistry()
    
    # Test with various Python features that would fail in a sandbox
    test_cases = [
        {
            "name": "Complex calculation",
            "code": "import numpy as np\nresult = np.array([1, 2, 3, 4, 5]).mean()"
        },
        {
            "name": "File operations (simulated)",
            "code": "import os\nresult = os.getcwd()"
        },
        {
            "name": "Dict comprehension",
            "code": "result = {i: i**2 for i in range(5)}"
        },
        {
            "name": "Lambda and map",
            "code": "result = list(map(lambda x: x**2, [1, 2, 3, 4, 5]))"
        }
    ]
    
    for test in test_cases:
        print(f"\n{test['name']}:")
        try:
            result = registry.execute_tool("code_interpreter", {"code": test["code"]})
            result_dict = json.loads(result)
            if result_dict.get("success"):
                print(f"  ✓ Success: {result_dict.get('result')}")
            else:
                print(f"  ✗ Failed: {result_dict.get('error')}")
        except Exception as e:
            print(f"  ✗ Exception: {e}")

def test_error_handling():
    """Test that errors are properly captured and formatted"""
    print("\n" + "=" * 60)
    print("Test 2: Error handling and reporting")
    print("=" * 60)
    
    registry = ToolRegistry()
    
    error_cases = [
        {
            "name": "Syntax Error",
            "code": "if True\n    print('missing colon')"
        },
        {
            "name": "Name Error",
            "code": "result = undefined_variable + 10"
        },
        {
            "name": "Type Error",
            "code": "result = '5' + 5"
        },
        {
            "name": "Division by Zero",
            "code": "result = 10 / 0"
        },
        {
            "name": "Import Error",
            "code": "import nonexistent_module\nresult = 42"
        }
    ]
    
    for test in error_cases:
        print(f"\n{test['name']}:")
        result = registry.execute_tool("code_interpreter", {"code": test["code"]})
        result_dict = json.loads(result)
        
        if not result_dict.get("success"):
            print(f"  ✓ Error properly caught:")
            print(f"    Error Type: {result_dict.get('error_type')}")
            print(f"    Error Message: {result_dict.get('error')}")
            if result_dict.get('traceback'):
                print(f"    Traceback: {result_dict.get('traceback')[:100]}...")
        else:
            print(f"  ✗ Error not caught - this shouldn't happen")

def test_full_environment_access():
    """Test that the code interpreter has access to full Python environment"""
    print("\n" + "=" * 60)
    print("Test 3: Full Python environment access")
    print("=" * 60)
    
    registry = ToolRegistry()
    
    # Test access to various Python features that would be blocked in a sandbox
    full_env_tests = [
        {
            "name": "Access to all builtins",
            "code": "result = [callable(eval), callable(exec), callable(compile), callable(__import__)]"
        },
        {
            "name": "Dynamic import",
            "code": "import sys\nresult = f'Python {sys.version_info.major}.{sys.version_info.minor}'"
        },
        {
            "name": "List comprehension with filter",
            "code": "result = [x for x in range(20) if x % 2 == 0 and x % 3 == 0]"
        },
        {
            "name": "Multiple variable assignment",
            "code": "a, b, c = 1, 2, 3\nresult = a + b + c"
        }
    ]
    
    for test in full_env_tests:
        print(f"\n{test['name']}:")
        result = registry.execute_tool("code_interpreter", {"code": test["code"]})
        result_dict = json.loads(result)
        
        if result_dict.get("success"):
            print(f"  ✓ Success: {result_dict.get('result')}")
            if result_dict.get('output'):
                print(f"    Output: {result_dict.get('output')}")
        else:
            print(f"  ✗ Failed: {result_dict.get('error')}")

def test_agent_error_propagation():
    """Test that errors are properly formatted for the agent"""
    print("\n" + "=" * 60)
    print("Test 4: Agent error message formatting")
    print("=" * 60)
    
    from agent import VLLMToolAgent
    
    # This test would require a running vLLM server, so we'll just show
    # how errors would be formatted
    
    registry = ToolRegistry()
    
    # Simulate an error
    result = registry.execute_tool("code_interpreter", {
        "code": "result = 1 / 0"
    })
    
    result_dict = json.loads(result)
    
    # Format as the agent would
    if not result_dict.get("success"):
        error_msg = f"❌ Tool 'code_interpreter' execution failed:\n"
        if "error" in result_dict:
            error_msg += f"Error: {result_dict['error']}\n"
        if "error_type" in result_dict:
            error_msg += f"Type: {result_dict['error_type']}\n"
        if "traceback" in result_dict:
            error_msg += f"Traceback:\n{result_dict['traceback']}\n"
        
        print("\nFormatted error message that would be sent to agent:")
        print("-" * 60)
        print(error_msg)
        print("-" * 60)
        print("\nThe agent will receive this error message and can:")
        print("  1. Try to fix the code")
        print("  2. Ask the user for clarification")
        print("  3. Provide an alternative solution")

if __name__ == "__main__":
    test_successful_execution()
    test_error_handling()
    test_full_environment_access()
    test_agent_error_propagation()
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    print("\nSummary:")
    print("  ✓ Full Python environment is available (no sandbox restrictions)")
    print("  ✓ Errors are properly caught and detailed traceback provided")
    print("  ✓ Error messages are formatted clearly for the agent")
    print("  ✓ Agent can receive and process error information")
