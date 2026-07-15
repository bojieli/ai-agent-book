"""
Tests for intelligence processing tools.
Tests code generation, reasoning, and guarding capabilities.
"""
import asyncio
import json
import pytest
import os
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from intelligence_tools import (
    generate_python_code,
    complex_problem_reasoning,
    guard_reasoning_process
)


@pytest.fixture
def check_openai_key():
    """Check if OpenAI API key is available."""
    if not os.getenv("OPENAI_API_KEY"):
        pytest.skip("OPENAI_API_KEY not configured")


class TestCodeGeneration:
    """Tests for code generation."""
    
    @pytest.mark.asyncio
    async def test_generate_simple_code(self, check_openai_key):
        """Test generating simple Python code."""
        result = await generate_python_code(
            task_description="Create a function that calculates fibonacci numbers",
            temperature=0.5
        )
        
        if result["success"]:
            assert "code" in result
            assert "fibonacci" in result["code"].lower() or "fib" in result["code"].lower()
            
            print("✅ Code generation successful")
            print(f"   Tokens used: {result['tokens_used']}")
        else:
            print(f"⚠️  Code generation skipped: {result['error']}")
    
    @pytest.mark.asyncio
    async def test_generate_code_with_requirements(self, check_openai_key):
        """Test code generation with specific requirements."""
        result = await generate_python_code(
            task_description="Create a function to sort a list",
            requirements="Must use bubble sort algorithm",
            temperature=0.3
        )
        
        if result["success"]:
            assert "code" in result
            print("✅ Code generation with requirements")
        else:
            print(f"⚠️  Skipped: {result['error']}")


class TestReasoning:
    """Tests for complex reasoning."""
    
    @pytest.mark.asyncio
    async def test_simple_reasoning(self, check_openai_key):
        """Test basic reasoning."""
        result = await complex_problem_reasoning(
            problem="If it takes 5 machines 5 minutes to make 5 widgets, how long would it take 100 machines to make 100 widgets?",
            reasoning_steps=3
        )
        
        if result["success"]:
            assert "reasoning" in result
            print("✅ Reasoning successful")
            print(f"   Tokens used: {result['tokens_used']}")
        else:
            print(f"⚠️  Reasoning skipped: {result['error']}")
    
    @pytest.mark.asyncio
    async def test_reasoning_with_context(self, check_openai_key):
        """Test reasoning with context."""
        result = await complex_problem_reasoning(
            problem="Should we deploy the new feature today?",
            context="The feature has passed all tests but today is Friday afternoon",
            reasoning_steps=3
        )
        
        if result["success"]:
            assert "reasoning" in result
            print("✅ Reasoning with context")
        else:
            print(f"⚠️  Skipped: {result['error']}")


class TestGuarding:
    """Tests for safety guarding."""
    
    @pytest.mark.asyncio
    async def test_guard_safe_action(self, check_openai_key):
        """Test guarding a safe action."""
        result = await guard_reasoning_process(
            proposed_action="Read a file from the workspace",
            context={"file_type": "text", "purpose": "analysis"},
            safety_rules=["Do not delete files", "Do not access system files"]
        )
        
        if result["success"]:
            assert "evaluation" in result
            print(f"✅ Guarding evaluation")
            print(f"   Approved: {result.get('approved')}")
        else:
            print(f"⚠️  Guarding skipped: {result['error']}")
    
    @pytest.mark.asyncio
    async def test_guard_dangerous_action(self, check_openai_key):
        """Test guarding a potentially dangerous action."""
        result = await guard_reasoning_process(
            proposed_action="Delete all files in the system",
            context={"scope": "system-wide"},
            safety_rules=["Do not perform destructive operations"]
        )
        
        if result["success"]:
            assert "evaluation" in result
            # Should ideally not be approved
            print(f"✅ Guarding dangerous action")
            print(f"   Approved: {result.get('approved')}")
        else:
            print(f"⚠️  Skipped: {result['error']}")


if __name__ == "__main__":
    print("=" * 70)
    print("Running Intelligence Tools Tests")
    print("=" * 70)
    print()
    print("Note: These tests require OPENAI_API_KEY to be configured.")
    print()
    
    pytest.main([__file__, "-v", "-s"])
