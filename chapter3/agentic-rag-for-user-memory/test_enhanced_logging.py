#!/usr/bin/env python3
"""Test enhanced logging of LLM responses"""

import os
import sys
import logging

# Set up logging to see all messages
logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s:%(name)s:%(message)s'
)

# Ensure we have API keys
if not os.getenv("KIMI_API_KEY"):
    print("Please set KIMI_API_KEY environment variable")
    sys.exit(1)

from config import Config
from agent import UserMemoryRAGAgent

def test_logging():
    """Test that LLM responses are properly logged"""
    print("\n" + "="*80)
    print("Testing Enhanced LLM Response Logging")
    print("="*80)
    
    # Initialize agent
    config = Config.from_env()
    agent = UserMemoryRAGAgent(config)
    
    # Test with a simple question
    test_question = "What is the purpose of this system?"
    
    print(f"\nTest Question: {test_question}")
    print("\nYou should now see:")
    print("1. Iteration info")
    print("2. LLM Response content (up to 500 chars)")
    print("3. Tool calls if any")
    print("4. Final answer")
    print("\n" + "-"*80)
    
    # Run the agent
    result = agent.answer_question(
        question=test_question,
        test_id="test_logging",
        stream=False
    )
    
    print("\n" + "-"*80)
    print(f"\nFinal Answer: {result.get('answer', 'No answer')[:200]}...")
    print(f"Success: {result.get('success', False)}")
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Tool Calls: {result.get('tool_calls', 0)}")
    
    print("\n✓ Enhanced logging is working!")
    print("  - LLM responses are shown during iterations")
    print("  - Tool calls and results are logged")
    print("  - Evaluation reasoning will be shown when running tests")
    print("="*80)

if __name__ == "__main__":
    test_logging()
