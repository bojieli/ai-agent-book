"""Test execution tools."""

import asyncio
from llm_helper import LLMHelper
from execution_tools import ExecutionTools


async def test_code_interpreter():
    """Test code interpreter functionality."""
    print("Testing code interpreter...")
    
    llm_helper = LLMHelper()
    execution_tools = ExecutionTools(llm_helper)
    
    # Test valid code
    result = await execution_tools.code_interpreter(
        code='print("Test successful")\nresult = 2 + 2\nprint(f"2 + 2 = {result}")'
    )
    
    assert result["success"], f"Code execution failed: {result.get('error')}"
    assert "Test successful" in result["stdout"]
    print(f"✓ Code execution successful: {result}")
    
    # Test error handling
    result = await execution_tools.code_interpreter(
        code='x = 1 / 0'
    )
    
    assert not result["success"], "Should fail with division by zero"
    assert "error_analysis" in result
    print(f"✓ Error handling works: {result['error'][:100]}...")


async def test_virtual_terminal():
    """Test virtual terminal functionality."""
    print("\nTesting virtual terminal...")
    
    llm_helper = LLMHelper()
    execution_tools = ExecutionTools(llm_helper)
    
    # Test successful command
    result = await execution_tools.virtual_terminal(
        command='echo "Terminal test"'
    )
    
    assert result["success"], f"Command failed: {result.get('error')}"
    assert "Terminal test" in result["stdout"]
    print(f"✓ Command execution successful: {result}")
    
    # Test failed command
    result = await execution_tools.virtual_terminal(
        command='ls /nonexistent_directory_12345'
    )
    
    assert not result["success"], "Should fail with non-existent directory"
    assert "error_analysis" in result
    print(f"✓ Error handling works: returncode={result['returncode']}")


async def test_syntax_verification():
    """Test syntax verification."""
    print("\nTesting syntax verification...")
    
    llm_helper = LLMHelper()
    execution_tools = ExecutionTools(llm_helper)
    
    # Test syntax error detection
    result = await execution_tools.code_interpreter(
        code='print("Unclosed string'
    )
    
    assert not result["success"], "Should detect syntax error"
    print(f"✓ Syntax verification works: {result['error'][:100]}...")


async def main():
    """Run all tests."""
    print("=== Execution Tools Tests ===\n")
    
    try:
        await test_code_interpreter()
        await test_virtual_terminal()
        await test_syntax_verification()
        
        print("\n✓ All execution tools tests passed!")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
