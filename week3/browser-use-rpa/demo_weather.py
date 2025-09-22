"""
Demo: Weather checking with learning capability

This demo shows how the agent learns to check weather and reuses the learned workflow.
"""

import asyncio
import logging
from dotenv import load_dotenv

from browser_use import ChatOpenAI
from learning_agent import LearningAgent


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

load_dotenv()


async def demo_weather_learning():
    """Demonstrate weather checking with learning."""
    
    print("=" * 60)
    print("WEATHER CHECKING DEMO - LEARNING AGENT")
    print("=" * 60)
    
    # First task - agent will learn
    print("\n📚 PHASE 1: LEARNING - First weather check (Beijing)")
    print("-" * 40)
    
    task1 = "Check the weather in Beijing"
    
    agent1 = LearningAgent(
        task=task1,
        llm=ChatOpenAI(model="gpt-4o-mini"),
        knowledge_base_path="./weather_knowledge",
        headless=False  # Show browser for demo
    )
    
    print(f"Task: {task1}")
    print("The agent will use browser-use to complete this task from scratch...")
    
    result1 = await agent1.run(max_steps=10)
    
    print(f"\n✅ Task completed!")
    print(f"  - Success: {result1['success']}")
    print(f"  - Execution time: {result1['execution_time']:.2f}s")
    print(f"  - LLM calls made: {result1['llm_calls']}")
    print(f"  - Workflow learned: {'Yes' if result1['success'] else 'No'}")
    
    # Wait a bit before second task
    await asyncio.sleep(3)
    
    # Second task - agent should reuse learned workflow
    print("\n🚀 PHASE 2: REPLAY - Second weather check (Shanghai)")
    print("-" * 40)
    
    task2 = "Check the weather in Shanghai"
    
    agent2 = LearningAgent(
        task=task2,
        llm=ChatOpenAI(model="gpt-4o-mini"),
        knowledge_base_path="./weather_knowledge",
        headless=False
    )
    
    print(f"Task: {task2}")
    print("The agent will try to reuse the learned workflow...")
    
    result2 = await agent2.run(max_steps=10)
    
    print(f"\n✅ Task completed!")
    print(f"  - Success: {result2['success']}")
    print(f"  - Execution time: {result2['execution_time']:.2f}s")
    print(f"  - Replay used: {result2['replay_used']}")
    
    if result2['replay_used']:
        print(f"  - LLM calls saved: {result1['llm_calls']}")
        speedup = result1['execution_time'] / result2['execution_time']
        print(f"  - Speed improvement: {speedup:.1f}x faster")
    else:
        print(f"  - LLM calls made: {result2['llm_calls']}")
    
    # Show knowledge base statistics
    print("\n📊 KNOWLEDGE BASE STATISTICS")
    print("-" * 40)
    
    kb = agent2.knowledge_base
    stats = kb.get_statistics()
    
    for key, value in stats.items():
        print(f"  - {key.replace('_', ' ').title()}: {value}")
    
    print("\n" + "=" * 60)
    print("DEMO COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(demo_weather_learning())
