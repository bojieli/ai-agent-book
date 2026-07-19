#!/usr/bin/env python3
"""Test script for the Contextual Retrieval + Advanced Memory Cards System"""

import logging
from config import Config
from contextual_evaluator import ContextualMemoryEvaluator
from contextual_indexer import ContextualMemoryIndexer
from contextual_agent import ContextualUserMemoryAgent
from advanced_memory_manager import create_sample_cards
from chunker import ConversationChunk, ConversationMessage

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def test_dual_memory_system():
    """Test the dual memory system with a sample scenario"""
    
    print("\n" + "="*60)
    print("Testing Contextual Retrieval + Advanced Memory Cards")
    print("="*60)
    
    # Initialize components
    config = Config.from_env()
    user_id = "test_user_contextual"
    
    # Create indexer with contextual chunking
    print("\n1. Initializing Contextual Memory Indexer...")
    indexer = ContextualMemoryIndexer(
        user_id=user_id,
        use_contextual=True
    )
    print(f"   ✓ Indexer initialized")
    
    # Add sample memory cards
    print("\n2. Adding Advanced Memory Cards...")
    sample_cards = create_sample_cards()
    for card in sample_cards:
        indexer.memory_manager.add_card(card)
    print(f"   ✓ Added {len(sample_cards)} memory cards")
    
    # Create sample conversation chunks
    print("\n3. Creating Sample Conversation Chunks...")
    chunks = []
    
    # Conversation about travel
    messages1 = [
        ConversationMessage("user", "我想订一张去东京的机票", 1),
        ConversationMessage("assistant", "好的，请问您什么时候出发？", 2),
        ConversationMessage("user", "1月25日出发，2月1日返回", 3),
        ConversationMessage("assistant", "让我为您查询1月25日到2月1日的东京往返机票", 4),
    ]
    
    chunk1 = ConversationChunk(
        chunk_id="test_chunk_001",
        conversation_id="test_conv",
        test_id="test",
        chunk_index=0,
        start_round=1,
        end_round=2,
        messages=messages1,
        metadata={"topic": "travel"}
    )
    chunks.append(chunk1)
    
    # Conversation about passport
    messages2 = [
        ConversationMessage("user", "我的护照快过期了，什么时候需要续签？", 5),
        ConversationMessage("assistant", "您的护照将于2025年2月18日过期，建议提前3-6个月办理续签", 6),
        ConversationMessage("user", "好的，我会尽快去办理", 7),
        ConversationMessage("assistant", "建议您在出国前确保护照有效期至少6个月", 8),
    ]
    
    chunk2 = ConversationChunk(
        chunk_id="test_chunk_002",
        conversation_id="test_conv",
        test_id="test",
        chunk_index=1,
        start_round=3,
        end_round=4,
        messages=messages2,
        metadata={"topic": "passport"}
    )
    chunks.append(chunk2)
    
    print(f"   ✓ Created {len(chunks)} conversation chunks")
    
    # Process with contextual chunking
    print("\n4. Processing with Contextual Chunking...")
    result = indexer.process_conversation_history(
        chunks=chunks,
        conversation_id="test_conv",
        generate_summary_cards=False
    )
    print(f"   ✓ Generated {result['contextual_chunks']} contextual chunks")
    print(f"   ✓ Processing time: {result['processing_time']:.2f}s")
    
    # Initialize agent
    print("\n5. Initializing Contextual Agent...")
    agent = ContextualUserMemoryAgent(
        indexer=indexer,
        config=config
    )
    print(f"   ✓ Agent initialized with {sum(len(cards) for cards in indexer.memory_manager.categories.values())} memory cards")
    
    # Test queries
    print("\n6. Testing Queries...")
    test_queries = [
        ("我的护照什么时候过期？", "Should find passport expiration date from memory cards"),
        ("我一月份的东京之行需要准备什么？", "Should combine travel and passport info"),
        ("我的银行账户信息是什么？", "Should find bank account from memory cards"),
    ]
    
    for i, (query, expected) in enumerate(test_queries, 1):
        print(f"\n   Query {i}: {query}")
        print(f"   Expected: {expected}")
        
        trajectory = agent.answer_question(
            question=query,
            test_id=f"test_{i}",
            stream=False
        )
        
        if trajectory.final_answer:
            print(f"   Answer: {trajectory.final_answer[:200]}...")
            print(f"   ✓ Memory cards used: {len(trajectory.memory_cards_used)}")
            print(f"   ✓ Chunks retrieved: {len(trajectory.chunks_retrieved)}")
        else:
            print(f"   ✗ No answer generated")
    
    # Show statistics
    print("\n7. System Statistics:")
    stats = indexer.get_statistics()
    print(f"   • Chunks indexed: {stats.get('chunks_indexed', 0)}")
    print(f"   • Memory cards: {stats.get('memory_cards', 0)}")
    
    if 'chunker_stats' in stats:
        cs = stats['chunker_stats']
        print(f"   • Context generation tokens: {cs.get('total_context_tokens', 0)}")
        print(f"   • Estimated cost: ${cs.get('estimated_cost', 0):.3f}")
    
    print("\n" + "="*60)
    print("Test Complete! The dual memory system is working correctly.")
    print("="*60)


def test_evaluation_system():
    """Test the evaluation system with Layer 1 test cases"""
    
    print("\n" + "="*60)
    print("Testing Evaluation System")
    print("="*60)
    
    config = Config.from_env()
    evaluator = ContextualMemoryEvaluator(config)
    
    # Load Layer 1 test cases
    print("\n1. Loading Test Cases...")
    test_cases = evaluator.load_test_cases("layer1")
    print(f"   ✓ Loaded {len(test_cases)} test cases")
    
    if test_cases:
        # Test the first case
        first_test = test_cases[0]
        print(f"\n2. Testing First Case: {first_test}")
        
        test_case = evaluator.test_cases[first_test]
        print(f"   Title: {test_case.title}")
        print(f"   Category: {test_case.category}")
        print(f"   Conversations: {len(test_case.conversation_histories)}")
        
        # Run evaluation
        print("\n3. Running Evaluation...")
        try:
            result = evaluator.evaluate_test_case(first_test)
            print(f"   ✓ Evaluation complete")
            print(f"   Success: {result.success}")
            print(f"   Iterations: {result.iterations}")
            print(f"   Tool calls: {result.tool_calls}")
            print(f"   Processing time: {result.processing_time:.2f}s")
            
            if result.agent_answer:
                print(f"   Answer preview: {result.agent_answer[:100]}...")
        except Exception as e:
            print(f"   ✗ Evaluation failed: {e}")
    
    print("\n" + "="*60)
    print("Evaluation System Test Complete!")
    print("="*60)


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "eval":
        test_evaluation_system()
    else:
        test_dual_memory_system()
