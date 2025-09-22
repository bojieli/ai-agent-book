#!/usr/bin/env python3
"""
Test script for evaluating the Agentic RAG User Memory system

This script demonstrates:
1. Loading test cases similar to user-memory-evaluation
2. Building indexes from conversation histories
3. Evaluating retrieval and memory consistency
"""

import json
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Tuple

from config import Config
from agent import UserMemoryRAGAgent
from conversation_chunker import ConversationChunker
from memory_integration import MemoryRAGIntegration


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class UserMemoryEvaluator:
    """Evaluates the RAG system's performance on user memory tasks"""
    
    def __init__(self, config: Config = None):
        """Initialize the evaluator"""
        self.config = config or Config.from_env()
        self.agent = UserMemoryRAGAgent(self.config)
        self.results = []
    
    def prepare_test_case(self, test_case: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepare a test case by chunking and indexing its conversation history.
        
        Args:
            test_case: Test case with conversation history and evaluation query
            
        Returns:
            Prepared test case with indexing report
        """
        # Extract conversation history
        conversations = test_case.get("conversation_histories", [])
        
        if not conversations:
            logger.warning(f"No conversation history in test case: {test_case.get('test_id')}")
            return test_case
        
        # Save conversations to temp file
        temp_file = Path("./temp_test_history.json")
        with open(temp_file, 'w', encoding='utf-8') as f:
            json.dump({"conversations": conversations}, f)
        
        # Build index
        report = self.agent.build_index_from_history(str(temp_file))
        
        # Clean up temp file
        temp_file.unlink()
        
        test_case["indexing_report"] = report
        return test_case
    
    def evaluate_query(self, 
                       query: str, 
                       expected_info: List[str] = None,
                       conversation_context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Evaluate a single query against the indexed data.
        
        Args:
            query: The query to evaluate
            expected_info: List of expected information pieces in the response
            conversation_context: Optional context about which conversations to check
            
        Returns:
            Evaluation result
        """
        # Get response from agent
        response = ""
        for chunk in self.agent.query(query, stream=False):
            response = chunk
        
        # Evaluate response
        evaluation = {
            "query": query,
            "response": response,
            "timestamp": datetime.now().isoformat(),
            "metrics": {}
        }
        
        # Check if expected information is present
        if expected_info:
            found_count = 0
            missing_info = []
            
            for info in expected_info:
                if info.lower() in response.lower():
                    found_count += 1
                else:
                    missing_info.append(info)
            
            evaluation["metrics"]["recall"] = found_count / len(expected_info)
            evaluation["metrics"]["missing_info"] = missing_info
        
        # Check response length and quality
        evaluation["metrics"]["response_length"] = len(response)
        evaluation["metrics"]["has_tool_usage"] = "search_conversations" in response or "search_memories" in response
        
        return evaluation
    
    def evaluate_memory_consistency(self) -> Dict[str, Any]:
        """
        Evaluate consistency of extracted memories.
        
        Returns:
            Consistency evaluation report
        """
        # Check for contradictions in memories
        if not hasattr(self.agent, 'memory_integration'):
            return {"error": "No memory integration available"}
        
        # Get all memories
        memories = self.agent.memory_integration.memory_cache
        
        consistency_report = {
            "total_memories": len(memories),
            "potential_contradictions": [],
            "duplicate_candidates": []
        }
        
        # Check for potential duplicates
        memory_contents = {}
        for mem_id, memory_data in memories.items():
            content = memory_data.get("content", "").lower()
            
            # Check for similar content
            for existing_id, existing_content in memory_contents.items():
                similarity = self._calculate_similarity(content, existing_content)
                if similarity > 0.8:
                    consistency_report["duplicate_candidates"].append({
                        "memory1": mem_id,
                        "memory2": existing_id,
                        "similarity": similarity
                    })
            
            memory_contents[mem_id] = content
        
        # Run consolidation
        consolidation_report = self.agent.memory_integration.consolidate_memories(0.8)
        consistency_report["consolidation_report"] = consolidation_report
        
        return consistency_report
    
    def _calculate_similarity(self, text1: str, text2: str) -> float:
        """Simple text similarity calculation"""
        words1 = set(text1.split())
        words2 = set(text2.split())
        
        if not words1 or not words2:
            return 0.0
        
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        return len(intersection) / len(union)
    
    def run_evaluation_suite(self, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run a complete evaluation suite.
        
        Args:
            test_cases: List of test cases to evaluate
            
        Returns:
            Complete evaluation report
        """
        logger.info(f"Running evaluation suite with {len(test_cases)} test cases")
        
        suite_results = {
            "test_cases": [],
            "summary": {
                "total_cases": len(test_cases),
                "successful": 0,
                "failed": 0
            },
            "timestamp": datetime.now().isoformat()
        }
        
        for test_case in test_cases:
            test_id = test_case.get("test_id", "unknown")
            logger.info(f"Evaluating test case: {test_id}")
            
            try:
                # Prepare test case
                prepared_case = self.prepare_test_case(test_case)
                
                # Evaluate main query
                user_question = test_case.get("user_question", "")
                expected_info = test_case.get("expected_information", [])
                
                result = self.evaluate_query(user_question, expected_info)
                result["test_id"] = test_id
                result["test_category"] = test_case.get("category", "unknown")
                
                # Check if successful
                if result["metrics"].get("recall", 0) >= 0.7:
                    suite_results["summary"]["successful"] += 1
                    result["status"] = "success"
                else:
                    suite_results["summary"]["failed"] += 1
                    result["status"] = "failed"
                
                suite_results["test_cases"].append(result)
                
            except Exception as e:
                logger.error(f"Error evaluating test case {test_id}: {e}")
                suite_results["test_cases"].append({
                    "test_id": test_id,
                    "status": "error",
                    "error": str(e)
                })
                suite_results["summary"]["failed"] += 1
            
            # Reset agent for next test
            self.agent.reset()
        
        # Add memory consistency check
        suite_results["memory_consistency"] = self.evaluate_memory_consistency()
        
        return suite_results


def create_sample_test_cases() -> List[Dict[str, Any]]:
    """Create sample test cases for evaluation"""
    
    test_cases = []
    
    # Test Case 1: Simple information retrieval
    test_case1 = {
        "test_id": "simple_retrieval_001",
        "category": "layer1",
        "description": "Test retrieval of specific user information",
        "conversation_histories": [{
            "conversation_id": "test_001",
            "messages": []
        }],
        "user_question": "What is my email address?",
        "expected_information": ["john.doe@example.com"]
    }
    
    # Add conversation rounds
    for i in range(25):
        test_case1["conversation_histories"][0]["messages"].extend([
            {"role": "user", "content": f"Question {i+1}"},
            {"role": "assistant", "content": f"Answer {i+1}"}
        ])
    
    # Insert the email information in round 10
    test_case1["conversation_histories"][0]["messages"][18] = {
        "role": "user", 
        "content": "My email is john.doe@example.com. Please remember this."
    }
    test_case1["conversation_histories"][0]["messages"][19] = {
        "role": "assistant",
        "content": "I've noted that your email address is john.doe@example.com. I'll remember this for future reference."
    }
    
    test_cases.append(test_case1)
    
    # Test Case 2: Multiple related facts
    test_case2 = {
        "test_id": "multiple_facts_002",
        "category": "layer2",
        "description": "Test retrieval of multiple related facts",
        "conversation_histories": [{
            "conversation_id": "test_002",
            "messages": []
        }],
        "user_question": "What are my dietary restrictions and allergies?",
        "expected_information": ["vegetarian", "peanut allergy", "lactose intolerant"]
    }
    
    # Build conversation with scattered information
    dietary_conversations = [
        ("I'm vegetarian", "Noted that you follow a vegetarian diet."),
        ("I have a severe peanut allergy", "Important: You have a severe peanut allergy. I'll keep this in mind."),
        ("I'm also lactose intolerant", "Added to your profile: lactose intolerance along with your vegetarian diet and peanut allergy."),
    ]
    
    # Create 30 rounds with dietary info scattered throughout
    for i in range(30):
        if i % 10 == 5 and i // 10 < len(dietary_conversations):
            user_msg, assistant_msg = dietary_conversations[i // 10]
        else:
            user_msg = f"General question {i+1}"
            assistant_msg = f"General response {i+1}"
        
        test_case2["conversation_histories"][0]["messages"].extend([
            {"role": "user", "content": user_msg},
            {"role": "assistant", "content": assistant_msg}
        ])
    
    test_cases.append(test_case2)
    
    return test_cases


def main():
    """Main evaluation script"""
    
    print("=" * 60)
    print("User Memory RAG Evaluation")
    print("=" * 60)
    
    # Initialize configuration
    config = Config.from_env()
    config.chunking.rounds_per_chunk = 20
    
    # Create evaluator
    evaluator = UserMemoryEvaluator(config)
    
    # Create or load test cases
    test_cases = create_sample_test_cases()
    print(f"\nLoaded {len(test_cases)} test cases")
    
    # Run evaluation
    print("\nRunning evaluation suite...")
    results = evaluator.run_evaluation_suite(test_cases)
    
    # Print results
    print("\n" + "=" * 60)
    print("EVALUATION RESULTS")
    print("=" * 60)
    
    print(f"\nSummary:")
    print(f"  Total test cases: {results['summary']['total_cases']}")
    print(f"  Successful: {results['summary']['successful']}")
    print(f"  Failed: {results['summary']['failed']}")
    print(f"  Success rate: {results['summary']['successful'] / results['summary']['total_cases'] * 100:.1f}%")
    
    print("\nDetailed Results:")
    for test_result in results["test_cases"]:
        print(f"\n  Test: {test_result.get('test_id')}")
        print(f"    Status: {test_result.get('status')}")
        if "metrics" in test_result:
            print(f"    Recall: {test_result['metrics'].get('recall', 0):.2f}")
            if test_result['metrics'].get('missing_info'):
                print(f"    Missing: {test_result['metrics']['missing_info']}")
    
    print("\nMemory Consistency:")
    consistency = results.get("memory_consistency", {})
    print(f"  Total memories: {consistency.get('total_memories', 0)}")
    print(f"  Duplicate candidates: {len(consistency.get('duplicate_candidates', []))}")
    if "consolidation_report" in consistency:
        print(f"  Consolidated: {consistency['consolidation_report'].get('consolidated_count', 0)}")
    
    # Save results
    output_file = Path("./evaluation_results.json")
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nFull results saved to: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
