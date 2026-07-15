"""Evaluation Framework Integration for User Memory RAG Agent

This module integrates with the user-memory-evaluation framework to load
test cases and evaluate the agent's performance.
"""

import os
import sys
import json
import yaml
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
from dataclasses import dataclass, field
from datetime import datetime
import openai

# Import our local modules first to avoid conflicts
from config import Config
from chunker import ConversationChunker
from indexer import MemoryIndexer
from agent import UserMemoryRAGAgent

# Import modules from user-memory-evaluation project
LLMEvaluator = None
EvalTestCase = None
ConversationHistory = None
EvalMessage = None
MessageRole = None

# Import the specific modules we need from user-memory-evaluation
eval_project_path = Path(__file__).parent.parent.parent / "week2" / "user-memory-evaluation"
if eval_project_path.exists():
    import importlib.util
    try:
        # Load models module from user-memory-evaluation
        models_spec = importlib.util.spec_from_file_location(
            "user_memory_models", 
            eval_project_path / "models.py"
        )
        models_module = importlib.util.module_from_spec(models_spec)
        models_spec.loader.exec_module(models_module)
        
        # Load config module from user-memory-evaluation for the evaluator
        eval_config_spec = importlib.util.spec_from_file_location(
            "user_memory_config",
            eval_project_path / "config.py"
        )
        eval_config_module = importlib.util.module_from_spec(eval_config_spec)
        eval_config_spec.loader.exec_module(eval_config_module)
        
        # Load evaluator module from user-memory-evaluation
        eval_spec = importlib.util.spec_from_file_location(
            "user_memory_evaluator",
            eval_project_path / "evaluator.py"
        )
        eval_module = importlib.util.module_from_spec(eval_spec)
        
        # Temporarily add required modules to sys.modules for the evaluator to find
        sys.modules['models'] = models_module
        sys.modules['config'] = eval_config_module
        
        # Execute the evaluator module
        eval_spec.loader.exec_module(eval_module)
        
        # Clean up sys.modules to avoid conflicts
        del sys.modules['models']
        sys.modules['config'] = sys.modules[Config.__module__]  # Restore our own config
        
        # Extract the classes we need
        LLMEvaluator = eval_module.LLMEvaluator
        EvalTestCase = models_module.TestCase
        ConversationHistory = models_module.ConversationHistory
        EvalMessage = models_module.ConversationMessage
        MessageRole = models_module.MessageRole
        
        print(f"Successfully imported LLMEvaluator from {eval_project_path}")
            
    except Exception as e:
        print(f"Error loading LLMEvaluator: {e}")
        import traceback
        traceback.print_exc()


logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class TestCase:
    """Test case matching user-memory-evaluation framework structure"""
    test_id: str
    category: str
    title: str
    description: str
    conversation_histories: List[Dict[str, Any]]
    user_question: str
    evaluation_criteria: str  # Primary evaluation criteria (was expected_answer)
    expected_behavior: Optional[str] = None  # Optional expected behavior
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EvaluationResult:
    """Result from evaluating a test case"""
    test_id: str
    success: bool
    agent_answer: str
    evaluation_criteria: str  # Changed from expected_answer to match TestCase
    iterations: int
    tool_calls: int
    trajectory: Optional[Dict[str, Any]] = None
    processing_time: float = 0.0
    indexing_time: float = 0.0
    chunk_count: int = 0
    llm_evaluation: Optional[Dict[str, Any]] = None  # LLM evaluation details


class UserMemoryEvaluator:
    """Evaluates the RAG agent on user memory test cases"""
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the evaluator
        
        Args:
            config: Configuration object
        """
        self.config = config or Config.from_env()
        self.test_cases: Dict[str, TestCase] = {}
        self.results: Dict[str, EvaluationResult] = {}
        
        # Components
        self.chunker = ConversationChunker(self.config.chunking)
        self.indexer = None
        self.agent = None
        
        # Initialize LLM evaluator if available
        self.llm_evaluator = None
        if LLMEvaluator:
            try:
                self.llm_evaluator = LLMEvaluator()
                logger.info("LLM Evaluator initialized for automatic evaluation")
            except Exception as e:
                logger.warning(f"Could not initialize LLM evaluator: {e}")
                logger.info("Automatic LLM evaluation will be skipped")
        else:
            logger.info("LLM Evaluator not available - automatic evaluation will be skipped")
        
        # Paths
        self.test_cases_dir = Path(self.config.evaluation.test_cases_dir)
        self.results_dir = Path(self.config.evaluation.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized evaluator with test cases from: {self.test_cases_dir}")
    
    def load_test_cases(self, category: Optional[str] = None) -> List[str]:
        """
        Load test cases from YAML files
        
        Args:
            category: Optional category filter (layer1, layer2, layer3)
            
        Returns:
            List of test case IDs that were loaded
        """
        test_case_ids = []
        
        # Determine which categories to load
        if category:
            categories = [category]
        else:
            categories = ["layer1", "layer2", "layer3"]
        
        for cat in categories:
            category_dir = self.test_cases_dir / cat
            if not category_dir.exists():
                logger.warning(f"Category directory {category_dir} does not exist")
                continue
            
            # Load all YAML files in category
            for yaml_file in category_dir.glob("*.yaml"):
                try:
                    test_case = self._load_single_test_case(yaml_file)
                    if test_case:
                        test_case_ids.append(test_case.test_id)
                        self.test_cases[test_case.test_id] = test_case
                except Exception as e:
                    logger.error(f"Error loading {yaml_file}: {e}")
        
        logger.info(f"Loaded {len(test_case_ids)} test cases")
        return test_case_ids
    
    def _load_single_test_case(self, yaml_file: Path) -> Optional[TestCase]:
        """Load a single test case from YAML file"""
        with open(yaml_file, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        if not data:
            return None
        
        # Parse conversation histories
        conversation_histories = []
        for conv_data in data.get('conversation_histories', []):
            # Ensure messages are in the right format
            messages = []
            msg_list = conv_data.get('messages', [])
            for msg in msg_list:
                if isinstance(msg, dict) and 'role' in msg and 'content' in msg:
                    messages.append(msg)
            
            conversation = {
                "conversation_id": conv_data.get('conversation_id', ''),
                "timestamp": conv_data.get('timestamp', ''),
                "metadata": conv_data.get('metadata', {}),
                "messages": messages
            }
            conversation_histories.append(conversation)
        
        # Load evaluation criteria and expected behavior directly from YAML
        evaluation_criteria = data.get('evaluation_criteria', '')
        expected_behavior = data.get('expected_behavior', None)
        
        # Create test case with matching structure
        test_case = TestCase(
            test_id=data.get('test_id', ''),
            category=data.get('category', ''),
            title=data.get('title', ''),
            description=data.get('description', ''),
            conversation_histories=conversation_histories,
            user_question=data.get('user_question', ''),
            evaluation_criteria=evaluation_criteria,
            expected_behavior=expected_behavior,
            metadata=data.get('metadata', {})
        )
        
        return test_case
    
    def prepare_test_case(self, test_id: str) -> Tuple[int, float]:
        """
        Prepare a test case by chunking and indexing its conversations
        
        Args:
            test_id: The test case ID to prepare
            
        Returns:
            Tuple of (number of chunks, indexing time)
        """
        if test_id not in self.test_cases:
            raise ValueError(f"Test case {test_id} not found")
        
        test_case = self.test_cases[test_id]
        start_time = datetime.now()
        
        logger.info(f"Preparing test case: {test_id}")
        
        # Create new indexer for this test case
        self.indexer = MemoryIndexer(self.config.index)
        
        # Chunk all conversations
        all_chunks = []
        for conv_history in test_case.conversation_histories:
            chunks = self.chunker.chunk_conversation(
                conversation_id=conv_history['conversation_id'],
                test_id=test_id,
                messages=conv_history['messages'],
                metadata=conv_history.get('metadata', {})
            )
            all_chunks.extend(chunks)
        
        logger.info(f"Created {len(all_chunks)} chunks for test case {test_id}")
        
        # Index chunks
        self.indexer.add_chunks(all_chunks)
        
        # Save index if caching is enabled
        if self.config.evaluation.enable_caching:
            cache_path = self.results_dir / f"index_{test_id}"
            self.indexer.save_index(str(cache_path))
            logger.info(f"Cached index for {test_id}")
        
        # Create agent with the indexed data
        self.agent = UserMemoryRAGAgent(self.indexer, self.config)
        
        end_time = datetime.now()
        indexing_time = (end_time - start_time).total_seconds()
        
        return len(all_chunks), indexing_time
    
    def evaluate_test_case(self, test_id: str) -> EvaluationResult:
        """
        Evaluate a single test case
        
        Args:
            test_id: The test case ID to evaluate
            
        Returns:
            Evaluation result
        """
        if test_id not in self.test_cases:
            raise ValueError(f"Test case {test_id} not found")
        
        test_case = self.test_cases[test_id]
        
        logger.info(f"\n{'='*60}")
        logger.info(f"Evaluating: {test_case.title}")
        logger.info(f"Category: {test_case.category}")
        logger.info(f"Question: {test_case.user_question}")
        logger.info(f"{'='*60}")
        
        # Check if we can load cached index
        chunk_count = 0
        indexing_time = 0.0
        
        if self.config.evaluation.enable_caching:
            cache_path = self.results_dir / f"index_{test_id}"
            if Path(f"{cache_path}_chunks.json").exists():
                logger.info(f"Loading cached index for {test_id}")
                self.indexer = MemoryIndexer(self.config.index)
                self.indexer.load_index(str(cache_path))
                self.agent = UserMemoryRAGAgent(self.indexer, self.config)
                chunk_count = len(self.indexer.chunks)
            else:
                chunk_count, indexing_time = self.prepare_test_case(test_id)
        else:
            chunk_count, indexing_time = self.prepare_test_case(test_id)
        
        # Get agent's answer
        start_time = datetime.now()
        result = self.agent.answer_question(
            question=test_case.user_question,
            test_id=test_id,
            stream=False
        )
        end_time = datetime.now()
        processing_time = (end_time - start_time).total_seconds()
        
        agent_answer = result.get("answer", "")
        
        # Perform LLM evaluation if available
        llm_evaluation = None
        if self.llm_evaluator and agent_answer:
            logger.info("\n" + "="*60)
            logger.info("Running LLM Evaluation...")
            logger.info("-"*60)
            
            try:
                # Convert test case to format expected by LLM evaluator
                # Using the imported classes from user-memory-evaluation models
                
                # Build conversation histories for evaluator
                eval_histories = []
                for conv_hist in test_case.conversation_histories:
                    eval_messages = []
                    for msg in conv_hist.get('messages', []):
                        eval_messages.append(EvalMessage(
                            role=MessageRole(msg.get('role', 'user')),
                            content=msg.get('content', '')
                        ))
                    
                    # Extract timestamp from metadata or use a default
                    timestamp = conv_hist.get('timestamp', '')
                    if not timestamp and 'metadata' in conv_hist:
                        # Try to extract from metadata
                        metadata = conv_hist.get('metadata', {})
                        timestamp = metadata.get('timestamp', metadata.get('date', '2024-01-01'))
                    if not timestamp:
                        timestamp = '2024-01-01'  # Default timestamp
                    
                    eval_histories.append(ConversationHistory(
                        conversation_id=conv_hist.get('conversation_id', ''),
                        timestamp=timestamp,
                        messages=eval_messages,
                        metadata=conv_hist.get('metadata', {})
                    ))
                
                # Use the test case's evaluation_criteria directly
                eval_test_case = EvalTestCase(
                    test_id=test_case.test_id,
                    category=test_case.category,
                    title=test_case.title,
                    description=test_case.description,
                    conversation_histories=eval_histories,
                    user_question=test_case.user_question,
                    evaluation_criteria=test_case.evaluation_criteria if test_case.evaluation_criteria else "The agent should provide a relevant and accurate response based on the conversation history.",
                    expected_behavior=test_case.expected_behavior  # Pass through expected_behavior
                )
                
                # Run LLM evaluation
                llm_result = self.llm_evaluator.evaluate(
                    test_case=eval_test_case,
                    agent_response=agent_answer,
                    extracted_memory=None
                )
                
                llm_evaluation = {
                    "reward": llm_result.reward,
                    "passed": llm_result.passed if llm_result.passed is not None else llm_result.reward >= 0.6,
                    "reasoning": llm_result.reasoning,
                    "required_info_found": llm_result.required_info_found if hasattr(llm_result, 'required_info_found') else {},
                    "suggestions": llm_result.suggestions if hasattr(llm_result, 'suggestions') else None
                }
                
                # Log evaluation results with full reasoning
                logger.info("-"*60)
                logger.info(f"LLM Evaluation Reward: {llm_result.reward:.3f}/1.000")
                logger.info(f"Passed: {'Yes' if llm_evaluation['passed'] else 'No'}")
                logger.info("-"*60)
                logger.info(f"Evaluation Reasoning:")
                logger.info(llm_result.reasoning)
                logger.info("-"*60)
                
                if llm_result.required_info_found:
                    logger.info("Required Information Found:")
                    for info, found in llm_result.required_info_found.items():
                        check = "✓" if found else "✗"
                        logger.info(f"  {check} {info}")
                
                if llm_result.suggestions:
                    logger.info(f"Suggestions: {llm_result.suggestions}")
                    
                logger.info("="*60)
                
            except Exception as e:
                logger.error(f"Error during LLM evaluation: {e}")
                llm_evaluation = {"error": str(e)}
        
        # Create evaluation result
        eval_result = EvaluationResult(
            test_id=test_id,
            success=llm_evaluation.get('passed', result.get("success", False)) if llm_evaluation else result.get("success", False),
            agent_answer=agent_answer,
            evaluation_criteria=test_case.evaluation_criteria,  # Use evaluation_criteria
            iterations=result.get("iterations", 0),
            tool_calls=result.get("tool_calls", 0),
            trajectory=result.get("trajectory"),
            processing_time=processing_time,
            indexing_time=indexing_time,
            chunk_count=chunk_count
        )
        
        # Add LLM evaluation details to the result if available
        if llm_evaluation:
            eval_result.llm_evaluation = llm_evaluation
        
        # Save result
        self.results[test_id] = eval_result
        
        # Save trajectory if enabled
        if self.config.evaluation.save_trajectories and eval_result.trajectory:
            trajectory_file = self.results_dir / f"trajectory_{test_id}.json"
            with open(trajectory_file, 'w', encoding='utf-8') as f:
                json.dump(eval_result.trajectory, f, ensure_ascii=False, indent=2)
        
        # Log summary
        logger.info(f"\n{'='*60}")
        logger.info(f"Evaluation Complete for {test_id}")
        if llm_evaluation and 'reward' in llm_evaluation:
            logger.info(f"LLM Evaluation Passed: {'✓' if eval_result.success else '✗'}")
            logger.info(f"LLM Reward Score: {llm_evaluation['reward']:.3f}/1.000")
        else:
            logger.info(f"Success: {eval_result.success}")
        logger.info(f"Iterations: {eval_result.iterations}")
        logger.info(f"Tool Calls: {eval_result.tool_calls}")
        logger.info(f"Chunks: {eval_result.chunk_count}")
        logger.info(f"Processing Time: {eval_result.processing_time:.2f}s")
        logger.info(f"Indexing Time: {eval_result.indexing_time:.2f}s")
        logger.info(f"{'='*60}")
        
        return eval_result
    
    def evaluate_batch(self, 
                      test_ids: Optional[List[str]] = None,
                      category: Optional[str] = None) -> Dict[str, EvaluationResult]:
        """
        Evaluate multiple test cases
        
        Args:
            test_ids: List of test IDs to evaluate (evaluates all if None)
            category: Category filter if test_ids not provided
            
        Returns:
            Dictionary of results
        """
        # Determine which test cases to evaluate
        if test_ids:
            ids_to_evaluate = test_ids
        else:
            # Load test cases if needed
            if not self.test_cases:
                self.load_test_cases(category)
            
            if category:
                ids_to_evaluate = [
                    tid for tid, tc in self.test_cases.items() 
                    if tc.category == category
                ]
            else:
                ids_to_evaluate = list(self.test_cases.keys())
        
        logger.info(f"Evaluating {len(ids_to_evaluate)} test cases")
        
        # Evaluate each test case
        for i, test_id in enumerate(ids_to_evaluate, 1):
            logger.info(f"\n[{i}/{len(ids_to_evaluate)}] Evaluating {test_id}")
            try:
                self.evaluate_test_case(test_id)
            except Exception as e:
                logger.error(f"Error evaluating {test_id}: {e}")
                self.results[test_id] = EvaluationResult(
                    test_id=test_id,
                    success=False,
                    agent_answer=f"Error: {str(e)}",
                    evaluation_criteria="",
                    iterations=0,
                    tool_calls=0
                )
        
        return self.results
    
    def generate_report(self, output_file: Optional[str] = None) -> str:
        """
        Generate evaluation report
        
        Args:
            output_file: Optional file path to save report
            
        Returns:
            Report as string
        """
        if not self.results:
            return "No evaluation results available"
        
        lines = []
        lines.append("="*80)
        lines.append("USER MEMORY RAG EVALUATION REPORT")
        lines.append(f"Generated: {datetime.now().isoformat()}")
        lines.append("="*80)
        lines.append("")
        
        # Summary statistics
        total = len(self.results)
        successful = sum(1 for r in self.results.values() if r.success)
        
        # Calculate LLM evaluation metrics if available
        llm_evaluated = sum(1 for r in self.results.values() if r.llm_evaluation and 'reward' in r.llm_evaluation)
        avg_reward = 0.0
        if llm_evaluated > 0:
            avg_reward = sum(r.llm_evaluation['reward'] for r in self.results.values() 
                           if r.llm_evaluation and 'reward' in r.llm_evaluation) / llm_evaluated
        
        lines.append("SUMMARY")
        lines.append("-"*40)
        lines.append(f"Total Test Cases: {total}")
        lines.append(f"Successful: {successful}/{total} ({100*successful/total:.1f}%)")
        if llm_evaluated > 0:
            lines.append(f"LLM Evaluated: {llm_evaluated}/{total}")
            lines.append(f"Average LLM Reward: {avg_reward:.3f}/1.000")
        lines.append("")
        
        # Average metrics
        avg_iterations = sum(r.iterations for r in self.results.values()) / total
        avg_tool_calls = sum(r.tool_calls for r in self.results.values()) / total
        avg_chunks = sum(r.chunk_count for r in self.results.values()) / total
        avg_proc_time = sum(r.processing_time for r in self.results.values()) / total
        avg_idx_time = sum(r.indexing_time for r in self.results.values()) / total
        
        lines.append("AVERAGE METRICS")
        lines.append("-"*40)
        lines.append(f"Iterations per test: {avg_iterations:.2f}")
        lines.append(f"Tool calls per test: {avg_tool_calls:.2f}")
        lines.append(f"Chunks per test: {avg_chunks:.1f}")
        lines.append(f"Processing time: {avg_proc_time:.2f}s")
        lines.append(f"Indexing time: {avg_idx_time:.2f}s")
        lines.append("")
        
        # Results by category
        categories = {}
        for test_id, result in self.results.items():
            if test_id in self.test_cases:
                cat = self.test_cases[test_id].category
                if cat not in categories:
                    categories[cat] = {"total": 0, "successful": 0}
                categories[cat]["total"] += 1
                if result.success:
                    categories[cat]["successful"] += 1
        
        lines.append("RESULTS BY CATEGORY")
        lines.append("-"*40)
        for cat, stats in sorted(categories.items()):
            pct = 100 * stats["successful"] / stats["total"]
            lines.append(f"{cat}: {stats['successful']}/{stats['total']} ({pct:.1f}%)")
        lines.append("")
        
        # Individual test results
        lines.append("INDIVIDUAL TEST RESULTS")
        lines.append("-"*40)
        for test_id, result in sorted(self.results.items()):
            status = "✓" if result.success else "✗"
            test_title = self.test_cases.get(test_id, {}).title if test_id in self.test_cases else test_id
            lines.append(f"{status} {test_id}: {test_title}")
            lines.append(f"  Iterations: {result.iterations}, Tool calls: {result.tool_calls}")
            lines.append(f"  Processing: {result.processing_time:.2f}s, Chunks: {result.chunk_count}")
            if result.llm_evaluation and 'reward' in result.llm_evaluation:
                lines.append(f"  LLM Reward: {result.llm_evaluation['reward']:.3f}/1.000")
            lines.append("")
        
        report = "\n".join(lines)
        
        # Save report if output file provided
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report)
            logger.info(f"Report saved to {output_file}")
        
        return report
    
    def save_results(self, output_file: Optional[str] = None):
        """
        Save evaluation results to JSON
        
        Args:
            output_file: Output file path (defaults to timestamped file)
        """
        if not output_file:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_file = self.results_dir / f"results_{timestamp}.json"
        
        results_data = {}
        for test_id, result in self.results.items():
            results_data[test_id] = {
                "success": result.success,
                "agent_answer": result.agent_answer,
                "evaluation_criteria": result.evaluation_criteria,
                "iterations": result.iterations,
                "tool_calls": result.tool_calls,
                "processing_time": result.processing_time,
                "indexing_time": result.indexing_time,
                "chunk_count": result.chunk_count
            }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(results_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Results saved to {output_file}")
