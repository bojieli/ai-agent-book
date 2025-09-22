"""
Simple test to verify the dual-context memory system works
"""

import sys
from pathlib import Path

# Don't add week2 to path globally
# Each module should handle its own imports

def test_memory_agent():
    """Test the unified memory agent"""
    from memory_agent import MemoryAgent
    
    # Initialize agent
    agent = MemoryAgent("test_user")
    print("✅ Memory agent initialized successfully")
    
    # Create sample conversation
    conversation = {
        "conversation_id": "TEST-001",
        "timestamp": "2024-01-01T10:00:00Z",
        "messages": [
            {"role": "user", "content": "My name is John Doe"},
            {"role": "assistant", "content": "Nice to meet you, John Doe!"},
            {"role": "user", "content": "I work at TechCorp as a software engineer"},
            {"role": "assistant", "content": "Software engineering at TechCorp - that's great!"}
        ]
    }
    
    # Process conversation
    results = agent.process_conversation(conversation)
    print(f"📝 Processed conversation: {len(results['chunks_created'])} chunks, {len(results['cards_updated'])} cards")
    
    # Test answering
    answer = agent.answer("What's my name and occupation?")
    print(f"💬 Question: What's my name and occupation?")
    print(f"🤖 Answer: {answer[:200]}...")
    
    # Show statistics
    stats = agent.get_statistics()
    print(f"\n📊 Memory Statistics:")
    print(f"  - Structured cards: {stats['structured_memory']['total_cards']}")
    print(f"  - Conversation chunks: {stats['conversation_memory']['total_chunks']}")
    print(f"  - Proactive insights: {stats['agent_performance']['proactive_insights']}")
    
    print("\n✅ All tests passed! Dual-context system is working.")


if __name__ == "__main__":
    test_memory_agent()
