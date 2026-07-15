#!/usr/bin/env python3
"""Test script to verify all fixes are working"""

import logging
from config import Config
from contextual_evaluator import ContextualMemoryEvaluator

# Set up detailed logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def test_single_evaluation():
    """Test evaluation with a single simple test case"""
    print("="*80)
    print("TESTING CONTEXTUAL RETRIEVAL SYSTEM - VERBOSE MODE")
    print("="*80)
    
    config = Config.from_env()
    evaluator = ContextualMemoryEvaluator(config)
    
    # Load only layer1 test cases
    test_cases = evaluator.load_test_cases("layer1")
    print(f"\nLoaded {len(test_cases)} test cases")
    
    if test_cases:
        # Pick the first test case
        test_id = test_cases[0]
        test_case = evaluator.test_cases[test_id]
        
        print(f"\n{'='*80}")
        print(f"EVALUATING: {test_id}")
        print(f"Title: {test_case.title}")
        print(f"Question: {test_case.user_question}")
        print(f"Conversations: {len(test_case.conversation_histories)}")
        if test_case.conversation_histories:
            first_conv = test_case.conversation_histories[0]
            print(f"First conversation has {len(first_conv.get('messages', []))} messages")
        print(f"{'='*80}\n")
        
        # Run evaluation
        try:
            result = evaluator.evaluate_test_case(test_id)
            
            print(f"\n{'='*80}")
            print("EVALUATION RESULT")
            print(f"{'='*80}")
            print(f"Success: {result.success}")
            print(f"Iterations: {result.iterations}")
            print(f"Tool Calls: {result.tool_calls}")
            print(f"Memory Cards Used: {len(result.memory_cards_used)}")
            print(f"Chunks Retrieved: {len(result.chunks_retrieved)}")
            print(f"Processing Time: {result.processing_time:.2f}s")
            
            if result.agent_answer:
                print(f"\nAgent Answer:")
                print(result.agent_answer)
            
            if result.error:
                print(f"\nError: {result.error}")
            
            print(f"{'='*80}\n")
            
        except Exception as e:
            print(f"\nERROR during evaluation: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("No test cases available")

if __name__ == "__main__":
    test_single_evaluation()
