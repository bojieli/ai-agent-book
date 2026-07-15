#!/usr/bin/env python3
"""
Quick test with Doubao as default
"""

import os
import sys
import time

# Set a very simple task to test quickly
task = "What is 10 + 5? Provide FINAL ANSWER with just the number."

print("="*60)
print("QUICK TEST - Doubao Default Provider")
print("="*60)

ark_key = os.getenv("ARK_API_KEY")
if not ark_key:
    print("❌ ARK_API_KEY not set")
    sys.exit(1)

from agent import ContextAwareAgent, ContextMode

# Create agent with default Doubao
agent = ContextAwareAgent(ark_key, ContextMode.FULL, provider="doubao")
print(f"✅ Using: {agent.provider} / {agent.model}")
print(f"\n📝 Task: {task}")
print("-"*40)

start = time.time()
print("Processing...")

try:
    result = agent.execute_task(task, max_iterations=2)
    elapsed = time.time() - start
    
    print(f"\n✅ Completed in {elapsed:.2f} seconds")
    
    if result.get('success'):
        print(f"Success: True")
        if result.get('final_answer'):
            print(f"Answer: {result['final_answer']}")
    else:
        print(f"Success: False")
        if result.get('error'):
            print(f"Error: {result['error']}")
    
    print(f"Iterations: {result.get('iterations', 0)}")
    print(f"Tool calls: {len(result['trajectory'].tool_calls)}")
    
except KeyboardInterrupt:
    print("\n⚠️ Interrupted")
except Exception as e:
    print(f"\n❌ Error: {str(e)}")

print("="*60)
