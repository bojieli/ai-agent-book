"""Test file system tools."""

import asyncio
import tempfile
from pathlib import Path
from llm_helper import LLMHelper
from file_tools import FileTools
from config import Config


async def test_file_write():
    """Test file write functionality."""
    print("Testing file write...")
    
    llm_helper = LLMHelper()
    file_tools = FileTools(llm_helper)
    
    # Test writing valid Python code
    result = await file_tools.write_file(
        path="test_output.py",
        content='print("Hello, World!")\n',
        overwrite=True
    )
    
    assert result["success"], f"File write failed: {result.get('error')}"
    assert result["verification"] in ["passed", "skipped"]
    print(f"✓ File write successful: {result}")
    
    # Test syntax error detection
    result = await file_tools.write_file(
        path="test_syntax_error.py",
        content='print("Unclosed string\n',
        overwrite=True
    )
    
    if Config.AUTO_VERIFY_CODE:
        assert not result["success"], "Should detect syntax error"
        print(f"✓ Syntax error detected: {result['error']}")
    else:
        print("✓ Verification skipped (AUTO_VERIFY_CODE=False)")


async def test_file_edit():
    """Test file edit functionality."""
    print("\nTesting file edit...")
    
    llm_helper = LLMHelper()
    file_tools = FileTools(llm_helper)
    
    # Create a test file first
    await file_tools.write_file(
        path="test_edit.py",
        content='message = "Hello"\nprint(message)\n',
        overwrite=True
    )
    
    # Edit the file
    result = await file_tools.edit_file(
        path="test_edit.py",
        search='message = "Hello"',
        replace='message = "Hi there"'
    )
    
    assert result["success"], f"File edit failed: {result.get('error')}"
    assert "diff_preview" in result
    print(f"✓ File edit successful: {result}")


async def test_safety_checks():
    """Test safety checks for file operations."""
    print("\nTesting safety checks...")
    
    llm_helper = LLMHelper()
    file_tools = FileTools(llm_helper)
    
    # Test path outside workspace
    result = await file_tools.write_file(
        path="/tmp/outside_workspace.txt",
        content="test"
    )
    
    # This should fail unless /tmp is in workspace
    print(f"Path safety check result: {result}")


async def main():
    """Run all tests."""
    print("=== File Tools Tests ===\n")
    
    try:
        await test_file_write()
        await test_file_edit()
        await test_safety_checks()
        
        print("\n✓ All file tools tests passed!")
        
    except AssertionError as e:
        print(f"\n✗ Test failed: {e}")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
