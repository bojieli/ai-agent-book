"""
Evaluation Framework for Contextual Memory Retrieval
Integrates with user-memory-evaluation test cases
"""

import json
import logging
import yaml
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path
import time
from collections import defaultdict
import numpy as np

from config import Config, RetrievalMode, EvaluationConfig
from memory_agent import MemoryAgent

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass 
class EvaluationMetrics:
    """Metrics for a single evaluation run"""
    test_id: str
    mode: str
    
    # Retrieval metrics
    chunks_retrieved: int = 0
    relevant_chunks_found: int = 0
    precision: float = 0.0
    recall: float = 0.0
    f1_score: float = 0.0
    mrr: float = 0.0  # Mean Reciprocal Rank
    
    # Answer quality metrics
    answer_accuracy: float = 0.0
    completeness: float = 0.0
    coherence: float = 0.0
    
    # Performance metrics
    tool_calls: int = 0
    iterations: int = 0
    total_tokens: int = 0
    latency_ms: int = 0
    
    # Error tracking
    errors: List[str] = field(default_factory=list)
    
    def calculate_f1(self):
        """Calculate F1 score from precision and recall"""
        if self.precision + self.recall == 0:
            self.f1_score = 0.0
        else:
            self.f1_score = 2 * (self.precision * self.recall) / (self.precision + self.recall)


@dataclass
class TestCase:
    """Represents a user memory evaluation test case"""
    test_id: str
    category: str  # layer1, layer2, layer3
    title: str
    description: str
    conversation_histories: List[Dict[str, Any]]
    user_question: str
    evaluation_criteria: str
    expected_behavior: Optional[str] = None
    
    @classmethod
    def from_yaml(cls, yaml_path: Path) -> "TestCase":
        """Load test case from YAML file"""
        with open(yaml_path, 'r', encoding='utf-8') as f:
            data = yaml.safe_load(f)
        
        return cls(
            test_id=data['test_id'],
            category=data['category'],
            title=data['title'],
            description=data['description'],
            conversation_histories=data['conversation_histories'],
            user_question=data['user_question'],
            evaluation_criteria=data.get('evaluation_criteria', ''),
            expected_behavior=data.get('expected_behavior')
        )


class MemoryEvaluator:
    """
    Evaluates the contextual memory retrieval system
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Initialize the evaluator
        
        Args:
            config: Configuration object
        """
        self.config = config or Config.from_env()
        self.eval_config = self.config.evaluation
        
        # Results storage
        self.results: Dict[str, List[EvaluationMetrics]] = defaultdict(list)
        self.test_cases: Dict[str, TestCase] = {}
        
        # Create results directory
        self.results_dir = Path(self.eval_config.results_dir)
        self.results_dir.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"Initialized MemoryEvaluator with results dir: {self.results_dir}")
    
    def evaluate_test_case(self,
                          test_case: TestCase,
                          modes: Optional[List[RetrievalMode]] = None,
                          verbose: bool = True) -> Dict[str, EvaluationMetrics]:
        """
        Evaluate a single test case across different modes
        
        Args:
            test_case: Test case to evaluate
            modes: Retrieval modes to test
            verbose: Show progress
            
        Returns:
            Evaluation metrics for each mode
        """
        modes = modes or self.eval_config.compare_modes
        results = {}
        
        if verbose:
            logger.info(f"\n{'='*60}")
            logger.info(f"Evaluating: {test_case.test_id} - {test_case.title}")
            logger.info(f"Category: {test_case.category}")
            logger.info(f"Question: {test_case.user_question}")
            logger.info(f"{'='*60}")
        
        # Create temporary user for this test
        user_id = f"test_user_{test_case.test_id}"
        
        for mode in modes:
            if verbose:
                logger.info(f"\nTesting {mode.value} mode...")
            
            # Evaluate with specific mode
            metrics = self._evaluate_single_mode(
                test_case, user_id, mode, verbose
            )
            
            results[mode.value] = metrics
            self.results[test_case.test_id].append(metrics)
        
        # Compare results
        if len(results) > 1 and verbose:
            self._print_comparison(results)
        
        return results
    
    def _evaluate_single_mode(self,
                             test_case: TestCase,
                             user_id: str,
                             mode: RetrievalMode,
                             verbose: bool) -> EvaluationMetrics:
        """Evaluate a test case with a specific retrieval mode"""
        metrics = EvaluationMetrics(
            test_id=test_case.test_id,
            mode=mode.value
        )
        
        try:
            # Phase 1: Learning - Process conversation histories
            start_time = time.time()
            
            # Create memory agent (always uses dual context now)
            agent = MemoryAgent(
                user_id=user_id,
                config=self.config
            )
            
            # Process all conversation histories
            total_chunks = 0
            total_cards = 0
            for conv in test_case.conversation_histories:
                results = agent.process_conversation(conv)
                total_chunks += len(results['chunks_created'])
                total_cards += len(results['cards_updated'])
            
            indexing_time = time.time() - start_time
            
            if verbose:
                logger.info(f"  Processed {total_chunks} chunks and {total_cards} cards in {indexing_time:.2f}s")
                stats = agent.get_statistics()
                logger.info(f"  Memory stats: {stats}")
            
            # Phase 2: Evaluation - Answer the question
            start_time = time.time()
            answer = agent.answer(test_case.user_question)
            answer_time = time.time() - start_time
            
            # Get trajectory for metrics
            if agent.trajectories:
                trajectory = agent.trajectories[-1]
                metrics.tool_calls = len(trajectory.tool_calls)
                metrics.iterations = len(trajectory.tool_calls)  # Each tool call is an iteration
                metrics.total_tokens = trajectory.total_tokens
                metrics.latency_ms = trajectory.latency_ms
                metrics.chunks_retrieved = trajectory.chunks_retrieved
            
            # Evaluate answer quality (simplified - in production would use LLM judge)
            metrics.answer_accuracy = self._evaluate_answer_accuracy(
                answer, test_case.evaluation_criteria
            )
            metrics.completeness = self._evaluate_completeness(
                answer, test_case.evaluation_criteria
            )
            
            # Calculate retrieval metrics
            metrics.calculate_f1()
            
            if verbose:
                logger.info(f"  Answer time: {answer_time:.2f}s")
                logger.info(f"  Tool calls: {metrics.tool_calls}")
                logger.info(f"  Chunks retrieved: {metrics.chunks_retrieved}")
                logger.info(f"  Answer preview: {answer[:200]}...")
            
        except Exception as e:
            logger.error(f"Error evaluating {test_case.test_id} with {mode.value}: {e}")
            metrics.errors.append(str(e))
        
        return metrics
    
    def _evaluate_answer_accuracy(self, answer: str, criteria: str) -> float:
        """
        Evaluate answer accuracy against criteria
        Simplified version - in production would use LLM-as-judge
        """
        # Simple heuristic: check if key terms from criteria appear in answer
        if not criteria or not answer:
            return 0.0
        
        criteria_lower = criteria.lower()
        answer_lower = answer.lower()
        
        # Extract key terms (simplified)
        key_terms = []
        for line in criteria_lower.split('\n'):
            if 'must' in line or 'should' in line or 'required' in line:
                # Extract important words
                words = line.split()
                key_terms.extend([w for w in words if len(w) > 4])
        
        if not key_terms:
            return 0.5  # No clear criteria
        
        # Calculate coverage
        found = sum(1 for term in key_terms if term in answer_lower)
        accuracy = found / len(key_terms) if key_terms else 0.0
        
        return min(accuracy, 1.0)
    
    def _evaluate_completeness(self, answer: str, criteria: str) -> float:
        """
        Evaluate answer completeness
        Simplified version
        """
        # Check if answer addresses multiple aspects
        if not answer:
            return 0.0
        
        # Simple heuristics
        indicators = {
            'comprehensive': len(answer) > 500,
            'multi_aspect': answer.count('\n') > 2,
            'specific': any(char.isdigit() for char in answer),
            'structured': any(marker in answer for marker in ['first', 'second', '1.', '2.', '•'])
        }
        
        completeness = sum(indicators.values()) / len(indicators)
        return completeness
    
    def evaluate_test_suite(self,
                           test_cases_dir: Optional[str] = None,
                           categories: Optional[List[str]] = None,
                           sample_size: Optional[int] = None) -> Dict[str, Any]:
        """
        Evaluate a full test suite
        
        Args:
            test_cases_dir: Directory containing test cases
            categories: Categories to test (layer1, layer2, layer3)
            sample_size: Number of tests to sample per category
            
        Returns:
            Aggregated evaluation results
        """
        test_cases_dir = Path(test_cases_dir or self.eval_config.test_cases_dir)
        categories = categories or ["layer1", "layer2", "layer3"]
        
        all_results = {}
        
        for category in categories:
            category_dir = test_cases_dir / category
            if not category_dir.exists():
                logger.warning(f"Category directory {category_dir} not found")
                continue
            
            # Load test cases
            test_files = list(category_dir.glob("*.yaml"))
            
            # Sample if requested
            if sample_size and len(test_files) > sample_size:
                import random
                random.seed(self.eval_config.random_seed)
                test_files = random.sample(test_files, sample_size)
            
            logger.info(f"\nEvaluating {len(test_files)} test cases from {category}")
            
            category_results = []
            
            for test_file in test_files:
                try:
                    test_case = TestCase.from_yaml(test_file)
                    self.test_cases[test_case.test_id] = test_case
                    
                    # Evaluate test case
                    results = self.evaluate_test_case(
                        test_case,
                        verbose=self.eval_config.enable_verbose
                    )
                    
                    category_results.append(results)
                    
                    # Save intermediate results
                    if self.eval_config.save_trajectories:
                        self._save_test_results(test_case.test_id, results)
                    
                except Exception as e:
                    logger.error(f"Error processing {test_file}: {e}")
            
            all_results[category] = category_results
        
        # Generate summary
        summary = self._generate_summary(all_results)
        
        # Save final report
        if self.eval_config.generate_report:
            self._generate_report(summary)
        
        return summary
    
    def _generate_summary(self, all_results: Dict[str, List[Dict]]) -> Dict[str, Any]:
        """Generate summary statistics"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "config": self.config.to_dict(),
            "categories": {}
        }
        
        for category, results_list in all_results.items():
            if not results_list:
                continue
            
            # Aggregate metrics by mode
            mode_metrics = defaultdict(list)
            
            for test_results in results_list:
                for mode, metrics in test_results.items():
                    if isinstance(metrics, EvaluationMetrics):
                        mode_metrics[mode].append(metrics)
            
            # Calculate averages
            category_summary = {}
            
            for mode, metrics_list in mode_metrics.items():
                avg_metrics = {
                    "total_tests": len(metrics_list),
                    "avg_chunks_retrieved": np.mean([m.chunks_retrieved for m in metrics_list]),
                    "avg_precision": np.mean([m.precision for m in metrics_list]),
                    "avg_recall": np.mean([m.recall for m in metrics_list]),
                    "avg_f1": np.mean([m.f1_score for m in metrics_list]),
                    "avg_accuracy": np.mean([m.answer_accuracy for m in metrics_list]),
                    "avg_completeness": np.mean([m.completeness for m in metrics_list]),
                    "avg_tool_calls": np.mean([m.tool_calls for m in metrics_list]),
                    "avg_latency_ms": np.mean([m.latency_ms for m in metrics_list]),
                    "avg_tokens": np.mean([m.total_tokens for m in metrics_list]),
                    "error_rate": sum(1 for m in metrics_list if m.errors) / len(metrics_list)
                }
                category_summary[mode] = avg_metrics
            
            summary["categories"][category] = category_summary
        
        # Calculate overall improvements
        if "contextual" in summary["categories"].get("layer1", {}) and \
           "non_contextual" in summary["categories"].get("layer1", {}):
            
            improvements = {}
            for category in summary["categories"]:
                cat_data = summary["categories"][category]
                if "contextual" in cat_data and "non_contextual" in cat_data:
                    ctx = cat_data["contextual"]
                    non_ctx = cat_data["non_contextual"]
                    
                    improvements[category] = {
                        "accuracy_improvement": (ctx["avg_accuracy"] - non_ctx["avg_accuracy"]) / non_ctx["avg_accuracy"] * 100 if non_ctx["avg_accuracy"] > 0 else 0,
                        "completeness_improvement": (ctx["avg_completeness"] - non_ctx["avg_completeness"]) / non_ctx["avg_completeness"] * 100 if non_ctx["avg_completeness"] > 0 else 0,
                        "f1_improvement": (ctx["avg_f1"] - non_ctx["avg_f1"]) / non_ctx["avg_f1"] * 100 if non_ctx["avg_f1"] > 0 else 0,
                    }
            
            summary["improvements"] = improvements
        
        return summary
    
    def _print_comparison(self, results: Dict[str, EvaluationMetrics]):
        """Print comparison between modes"""
        logger.info(f"\n{'='*60}")
        logger.info("Mode Comparison:")
        logger.info(f"{'='*60}")
        
        # Create comparison table
        modes = list(results.keys())
        metrics_names = ["chunks_retrieved", "answer_accuracy", "completeness", "tool_calls", "latency_ms"]
        
        for metric in metrics_names:
            logger.info(f"\n{metric}:")
            for mode in modes:
                value = getattr(results[mode], metric, "N/A")
                if isinstance(value, float):
                    logger.info(f"  {mode}: {value:.3f}")
                else:
                    logger.info(f"  {mode}: {value}")
    
    def _save_test_results(self, test_id: str, results: Dict[str, Any]):
        """Save individual test results"""
        results_file = self.results_dir / f"{test_id}_results.json"
        
        # Convert metrics to dict
        serializable_results = {}
        for mode, metrics in results.items():
            if isinstance(metrics, EvaluationMetrics):
                serializable_results[mode] = asdict(metrics)
            else:
                serializable_results[mode] = metrics
        
        with open(results_file, 'w') as f:
            json.dump(serializable_results, f, indent=2)
    
    def _generate_report(self, summary: Dict[str, Any]):
        """Generate evaluation report"""
        report_file = self.results_dir / f"evaluation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(report_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        logger.info(f"Evaluation report saved to {report_file}")
        
        # Print summary to console
        logger.info(f"\n{'='*60}")
        logger.info("EVALUATION SUMMARY")
        logger.info(f"{'='*60}")
        
        for category, data in summary.get("categories", {}).items():
            logger.info(f"\n{category.upper()}:")
            for mode, metrics in data.items():
                logger.info(f"  {mode}:")
                logger.info(f"    Accuracy: {metrics['avg_accuracy']:.3f}")
                logger.info(f"    Completeness: {metrics['avg_completeness']:.3f}")
                logger.info(f"    Latency: {metrics['avg_latency_ms']:.0f}ms")
        
        if "improvements" in summary:
            logger.info(f"\n{'='*60}")
            logger.info("CONTEXTUAL RETRIEVAL IMPROVEMENTS:")
            logger.info(f"{'='*60}")
            for category, improvements in summary["improvements"].items():
                logger.info(f"\n{category}:")
                for metric, value in improvements.items():
                    logger.info(f"  {metric}: {value:+.1f}%")
