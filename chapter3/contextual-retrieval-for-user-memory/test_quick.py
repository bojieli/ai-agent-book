#!/usr/bin/env python3
"""Quick test to verify the fixes work"""

from config import Config
from contextual_evaluator import ContextualMemoryEvaluator

# Test configuration loading
config = Config.from_env()
print(f"✓ Config loaded successfully")
print(f"  - EvaluationConfig.use_llm_judge: {config.evaluation.use_llm_judge}")
print(f"  - AgentConfig.verbose: {config.agent.verbose}")

# Test evaluator initialization
evaluator = ContextualMemoryEvaluator(config)
print(f"✓ Evaluator initialized successfully")

# Load test cases
test_cases = evaluator.load_test_cases("layer1")
print(f"✓ Loaded {len(test_cases)} test cases")

if test_cases:
    test_id = test_cases[0]
    print(f"\nWill test with: {test_id}")
    print("Attempting evaluation...")
    
    try:
        result = evaluator.evaluate_test_case(test_id)
        print(f"✓ Evaluation completed!")
        print(f"  Success: {result.success}")
        print(f"  Iterations: {result.iterations}")
        print(f"  Processing time: {result.processing_time:.2f}s")
    except Exception as e:
        print(f"✗ Evaluation failed: {e}")
        import traceback
        traceback.print_exc()
else:
    print("No test cases found")
