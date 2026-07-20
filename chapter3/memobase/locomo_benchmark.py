"""
LOCOMO Benchmark Implementation for Memobase Agent
Evaluates agent performance on long-context and memory-intensive tasks
"""

import json
import time
import logging
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from collections import defaultdict
import random

from config import LOCOMO_CONFIG, LOG_LEVEL, LOG_FORMAT

# Configure logging
logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)
logger = logging.getLogger(__name__)


@dataclass
class BenchmarkTask:
    """Represents a single benchmark task"""
    id: str
    category: str  # multi_turn_reasoning, long_context_qa, etc.
    query: str
    context: Optional[str] = None
    expected_capabilities: List[str] = field(default_factory=list)
    ground_truth: Optional[Any] = None
    max_turns: int = 1
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TaskResult:
    """Result of executing a benchmark task"""
    task_id: str
    response: str
    execution_time: float
    memory_usage: Dict[str, int]
    success: bool
    score: float
    turns_used: int
    errors: List[str] = field(default_factory=list)


class LOCOMOBenchmark:
    """
    LOCOMO (Long Context and Memory Optimization) Benchmark
    Evaluates agent capabilities in handling long contexts and memory management
    """
    
    def __init__(self, benchmark_path: Optional[Path] = None):
        """Initialize the benchmark suite"""
        self.benchmark_path = benchmark_path or LOCOMO_CONFIG["benchmark_path"]
        self.tasks: List[BenchmarkTask] = []
        self.results: List[TaskResult] = []
        self.metrics: Dict[str, Any] = defaultdict(list)
        
        # Load or generate benchmark tasks
        self._initialize_tasks()
        logger.info(f"Initialized LOCOMO benchmark with {len(self.tasks)} tasks")
    
    def _initialize_tasks(self):
        """Initialize benchmark tasks"""
        # Try to load from file
        if self.benchmark_path and (self.benchmark_path / "tasks.json").exists():
            self._load_tasks_from_file()
        else:
            # Generate default benchmark tasks
            self._generate_default_tasks()
    
    def _load_tasks_from_file(self):
        """Load tasks from JSON file"""
        try:
            with open(self.benchmark_path / "tasks.json", 'r') as f:
                tasks_data = json.load(f)
                for task_dict in tasks_data:
                    self.tasks.append(BenchmarkTask(**task_dict))
            logger.info(f"Loaded {len(self.tasks)} tasks from file")
        except Exception as e:
            logger.error(f"Failed to load tasks: {e}")
            self._generate_default_tasks()
    
    def _generate_default_tasks(self):
        """Generate default benchmark tasks for each category"""
        
        # Multi-turn reasoning tasks
        self.tasks.extend([
            BenchmarkTask(
                id="mtr_001",
                category="multi_turn_reasoning",
                query="Let's solve a complex problem step by step. First, calculate the compound interest on $10,000 at 5% annual rate for 3 years.",
                expected_capabilities=["mathematical_reasoning", "multi_step_problem_solving"],
                max_turns=5,
                ground_truth=11576.25
            ),
            BenchmarkTask(
                id="mtr_002",
                category="multi_turn_reasoning",
                query="Plan a detailed itinerary for a 7-day trip to Japan, considering budget constraints of $3000.",
                expected_capabilities=["planning", "constraint_satisfaction", "cultural_knowledge"],
                max_turns=8
            ),
            BenchmarkTask(
                id="mtr_003",
                category="multi_turn_reasoning",
                query="Debug this code issue: A recursive function is causing a stack overflow. Help me identify and fix it step by step.",
                expected_capabilities=["code_analysis", "debugging", "iterative_refinement"],
                max_turns=6
            )
        ])
        
        # Long context Q&A tasks
        self.tasks.extend([
            BenchmarkTask(
                id="lcqa_001",
                category="long_context_qa",
                query="Based on the provided research papers, summarize the key findings about climate change impacts on ocean acidification.",
                context=self._generate_long_context("climate_research", 50000),
                expected_capabilities=["information_extraction", "summarization", "scientific_reasoning"]
            ),
            BenchmarkTask(
                id="lcqa_002",
                category="long_context_qa",
                query="Analyze the financial statements and identify the top 3 risk factors for the company.",
                context=self._generate_long_context("financial_report", 30000),
                expected_capabilities=["financial_analysis", "risk_assessment", "data_interpretation"]
            ),
            BenchmarkTask(
                id="lcqa_003",
                category="long_context_qa",
                query="Review the legal documents and identify any potential conflicts or inconsistencies.",
                context=self._generate_long_context("legal_document", 40000),
                expected_capabilities=["legal_reasoning", "contradiction_detection", "document_analysis"]
            )
        ])
        
        # Task planning tasks
        self.tasks.extend([
            BenchmarkTask(
                id="tp_001",
                category="task_planning",
                query="Create a detailed project plan for developing a mobile app, including timeline, resources, and milestones.",
                expected_capabilities=["project_management", "resource_allocation", "timeline_planning"]
            ),
            BenchmarkTask(
                id="tp_002",
                category="task_planning",
                query="Design an optimal study plan for learning machine learning in 3 months with 2 hours daily.",
                expected_capabilities=["curriculum_design", "learning_optimization", "scheduling"]
            )
        ])
        
        # Knowledge integration tasks
        self.tasks.extend([
            BenchmarkTask(
                id="ki_001",
                category="knowledge_integration",
                query="Combine insights from psychology, neuroscience, and education to explain how humans learn languages.",
                expected_capabilities=["interdisciplinary_thinking", "knowledge_synthesis", "conceptual_integration"]
            ),
            BenchmarkTask(
                id="ki_002",
                category="knowledge_integration",
                query="Integrate historical events, economic theories, and sociological concepts to analyze the 2008 financial crisis.",
                expected_capabilities=["historical_analysis", "economic_reasoning", "systemic_thinking"]
            )
        ])
        
        # Tool usage tasks
        self.tasks.extend([
            BenchmarkTask(
                id="tu_001",
                category="tool_usage",
                query="Use available tools to gather real-time weather data and create a 5-day forecast analysis.",
                expected_capabilities=["tool_selection", "data_gathering", "predictive_analysis"]
            ),
            BenchmarkTask(
                id="tu_002",
                category="tool_usage",
                query="Research and compare the top 5 programming languages for web development using current data.",
                expected_capabilities=["web_search", "comparative_analysis", "technology_assessment"]
            )
        ])
        
        logger.info(f"Generated {len(self.tasks)} default benchmark tasks")
    
    def _generate_long_context(self, context_type: str, char_count: int) -> str:
        """Generate synthetic long context for testing"""
        templates = {
            "climate_research": [
                "Recent studies on ocean acidification show significant changes in pH levels. ",
                "The correlation between CO2 emissions and marine ecosystem degradation is evident. ",
                "Temperature variations in deep ocean currents affect global climate patterns. ",
                "Coral reef bleaching events have increased by 40% in the last decade. ",
                "Phytoplankton populations show remarkable adaptation to changing conditions. "
            ],
            "financial_report": [
                "Revenue increased by 15% year-over-year, driven by strong product demand. ",
                "Operating expenses rose due to increased R&D investments. ",
                "Market volatility poses risks to future earnings projections. ",
                "Cash flow remains strong with $2.3B in liquid assets. ",
                "Debt-to-equity ratio improved to 0.8 from previous 1.2. "
            ],
            "legal_document": [
                "The party of the first part agrees to the terms specified in Section 3.2. ",
                "Notwithstanding the above, exceptions may apply under force majeure. ",
                "Intellectual property rights remain with the original creator as per Article 7. ",
                "Dispute resolution shall follow binding arbitration procedures. ",
                "Confidentiality clauses extend for 5 years post-termination. "
            ]
        }
        
        sentences = templates.get(context_type, templates["climate_research"])
        context = ""
        
        while len(context) < char_count:
            context += random.choice(sentences)
            # Add some variation
            if random.random() > 0.7:
                context += f"In {random.randint(2020, 2024)}, researchers found that "
        
        return context[:char_count]
    
    def evaluate_response(self, task: BenchmarkTask, response: str,
                         execution_time: float, memory_usage: Dict[str, int]) -> TaskResult:
        """
        Evaluate agent response for a task
        
        Args:
            task: The benchmark task
            response: Agent's response
            execution_time: Time taken to generate response
            memory_usage: Memory statistics
            
        Returns:
            TaskResult with evaluation metrics
        """
        score = 0.0
        success = False
        errors = []
        
        # Basic response validation
        if not response or len(response) < 10:
            errors.append("Response too short or empty")
            score = 0.0
        else:
            # Category-specific evaluation
            if task.category == "multi_turn_reasoning":
                score = self._evaluate_reasoning(task, response)
            elif task.category == "long_context_qa":
                score = self._evaluate_context_qa(task, response)
            elif task.category == "task_planning":
                score = self._evaluate_planning(task, response)
            elif task.category == "knowledge_integration":
                score = self._evaluate_integration(task, response)
            elif task.category == "tool_usage":
                score = self._evaluate_tool_usage(task, response)
            else:
                score = self._evaluate_generic(task, response)
            
            success = score >= 0.6  # 60% threshold for success
        
        # Bonus for efficiency
        if execution_time < 5.0:
            score += 0.05
        if sum(memory_usage.values()) < 100:
            score += 0.05
        
        score = min(1.0, score)  # Cap at 1.0
        
        return TaskResult(
            task_id=task.id,
            response=response,
            execution_time=execution_time,
            memory_usage=memory_usage,
            success=success,
            score=score,
            turns_used=1,  # Will be updated for multi-turn tasks
            errors=errors
        )
    
    def _evaluate_reasoning(self, task: BenchmarkTask, response: str) -> float:
        """Evaluate multi-turn reasoning response"""
        score = 0.0
        
        # Check for step-by-step reasoning
        if any(marker in response.lower() for marker in ["step 1", "first", "then", "finally"]):
            score += 0.3
        
        # Check for mathematical accuracy (if applicable)
        if task.ground_truth and str(task.ground_truth) in response:
            score += 0.4
        
        # Check for logical flow
        if len(response.split('\n')) > 3:
            score += 0.2
        
        # Check for conclusion
        if any(word in response.lower() for word in ["therefore", "conclusion", "result"]):
            score += 0.1
        
        return score
    
    def _evaluate_context_qa(self, task: BenchmarkTask, response: str) -> float:
        """Evaluate long context Q&A response"""
        score = 0.0
        
        # Check for relevant content extraction
        keywords = ["finding", "summary", "key point", "important", "significant"]
        keyword_matches = sum(1 for kw in keywords if kw in response.lower())
        score += min(0.3, keyword_matches * 0.1)
        
        # Check for structured response
        if any(marker in response for marker in ["1.", "•", "-", "*"]):
            score += 0.2
        
        # Check response length (should be comprehensive but concise)
        optimal_length = 500
        length_ratio = min(len(response), optimal_length) / optimal_length
        score += length_ratio * 0.3
        
        # Check for citations or references to context
        if any(phrase in response.lower() for phrase in ["according to", "based on", "the document states"]):
            score += 0.2
        
        return score
    
    def _evaluate_planning(self, task: BenchmarkTask, response: str) -> float:
        """Evaluate task planning response"""
        score = 0.0
        
        # Check for timeline/schedule
        if any(word in response.lower() for word in ["timeline", "schedule", "deadline", "milestone"]):
            score += 0.25
        
        # Check for resource consideration
        if any(word in response.lower() for word in ["resource", "budget", "cost", "team"]):
            score += 0.25
        
        # Check for structured plan
        if any(marker in response for marker in ["phase", "stage", "step"]):
            score += 0.25
        
        # Check for risk/contingency consideration
        if any(word in response.lower() for word in ["risk", "contingency", "backup", "alternative"]):
            score += 0.25
        
        return score
    
    def _evaluate_integration(self, task: BenchmarkTask, response: str) -> float:
        """Evaluate knowledge integration response"""
        score = 0.0
        
        # Check for multiple domain references
        domains = ["psychology", "neuroscience", "education", "history", "economics", "sociology"]
        domain_count = sum(1 for domain in domains if domain in response.lower())
        score += min(0.4, domain_count * 0.2)
        
        # Check for synthesis language
        synthesis_words = ["integrate", "combine", "together", "relationship", "connection"]
        if any(word in response.lower() for word in synthesis_words):
            score += 0.3
        
        # Check for depth of analysis
        if len(response) > 300:
            score += 0.3
        
        return score
    
    def _evaluate_tool_usage(self, task: BenchmarkTask, response: str) -> float:
        """Evaluate tool usage response"""
        score = 0.0
        
        # Check for tool mentions
        if any(word in response.lower() for word in ["search", "query", "fetch", "retrieve", "analyze"]):
            score += 0.3
        
        # Check for data presentation
        if any(marker in response for marker in ["data", "result", "finding", "information"]):
            score += 0.3
        
        # Check for analysis/interpretation
        if any(word in response.lower() for word in ["analysis", "comparison", "trend", "pattern"]):
            score += 0.4
        
        return score
    
    def _evaluate_generic(self, task: BenchmarkTask, response: str) -> float:
        """Generic evaluation for unspecified task types"""
        score = 0.0
        
        # Response length
        if len(response) > 100:
            score += 0.3
        
        # Coherence (simple check)
        if response.count('.') > 2:
            score += 0.3
        
        # Relevance (keyword matching)
        query_words = task.query.lower().split()
        if query_words:
            matching_words = sum(1 for word in query_words if word in response.lower())
            score += min(0.4, matching_words / len(query_words))
        
        return score
    
    def run_benchmark(self, agent, tasks: Optional[List[BenchmarkTask]] = None,
                      verbose: bool = True) -> Dict[str, Any]:
        """
        Run benchmark evaluation on an agent
        
        Args:
            agent: The agent to evaluate (must have execute_task method)
            tasks: Optional list of tasks (uses all if None)
            verbose: Print progress information
            
        Returns:
            Benchmark results and metrics
        """
        tasks_to_run = tasks or self.tasks
        self.results = []
        
        if verbose:
            print(f"\n{'='*60}")
            print(f"Running LOCOMO Benchmark: {len(tasks_to_run)} tasks")
            print(f"{'='*60}\n")
        
        for i, task in enumerate(tasks_to_run, 1):
            if verbose:
                print(f"[{i}/{len(tasks_to_run)}] Running task {task.id} ({task.category})...")
            
            try:
                # Execute task
                start_time = time.time()
                result = agent.execute_task({
                    "id": task.id,
                    "type": task.category,
                    "query": task.query,
                    "context": task.context
                })
                execution_time = time.time() - start_time
                
                # Evaluate response
                task_result = self.evaluate_response(
                    task=task,
                    response=result.get("response", ""),
                    execution_time=execution_time,
                    memory_usage=result.get("memory_stats", {})
                )
                
                self.results.append(task_result)
                
                if verbose:
                    print(f"    ✓ Score: {task_result.score:.2f} | Time: {execution_time:.2f}s | Success: {task_result.success}")
                
            except Exception as e:
                logger.error(f"Error running task {task.id}: {e}")
                self.results.append(TaskResult(
                    task_id=task.id,
                    response="",
                    execution_time=0,
                    memory_usage={},
                    success=False,
                    score=0.0,
                    turns_used=0,
                    errors=[str(e)]
                ))
                
                if verbose:
                    print(f"    ✗ Error: {str(e)}")
        
        # Calculate metrics
        metrics = self._calculate_metrics()
        
        if verbose:
            self._print_summary(metrics)
        
        return metrics
    
    def _calculate_metrics(self) -> Dict[str, Any]:
        """Calculate benchmark metrics from results"""
        if not self.results:
            return {"error": "No results to calculate metrics"}
        
        # Overall metrics
        total_tasks = len(self.results)
        successful_tasks = sum(1 for r in self.results if r.success)
        avg_score = sum(r.score for r in self.results) / total_tasks
        avg_time = sum(r.execution_time for r in self.results) / total_tasks
        
        # Category-specific metrics
        category_scores = defaultdict(list)
        category_times = defaultdict(list)
        
        for task, result in zip(self.tasks, self.results):
            category_scores[task.category].append(result.score)
            category_times[task.category].append(result.execution_time)
        
        category_metrics = {}
        for category in category_scores:
            category_metrics[category] = {
                "avg_score": sum(category_scores[category]) / len(category_scores[category]),
                "avg_time": sum(category_times[category]) / len(category_times[category]),
                "task_count": len(category_scores[category])
            }
        
        # Memory efficiency
        total_memory = {}
        for result in self.results:
            for mem_type, count in result.memory_usage.items():
                total_memory[mem_type] = total_memory.get(mem_type, 0) + count
        
        return {
            "overall": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": successful_tasks / total_tasks,
                "average_score": avg_score,
                "average_time": avg_time
            },
            "categories": category_metrics,
            "memory_usage": total_memory,
            "detailed_results": [
                {
                    "task_id": r.task_id,
                    "score": r.score,
                    "success": r.success,
                    "time": r.execution_time,
                    "errors": r.errors
                }
                for r in self.results
            ]
        }
    
    def _print_summary(self, metrics: Dict[str, Any]):
        """Print benchmark summary"""
        print(f"\n{'='*60}")
        print("BENCHMARK SUMMARY")
        print(f"{'='*60}")
        
        overall = metrics["overall"]
        print(f"\nOverall Performance:")
        print(f"  • Success Rate: {overall['success_rate']:.1%}")
        print(f"  • Average Score: {overall['average_score']:.2f}/1.00")
        print(f"  • Average Time: {overall['average_time']:.2f}s")
        print(f"  • Tasks Completed: {overall['successful_tasks']}/{overall['total_tasks']}")
        
        print(f"\nCategory Breakdown:")
        for category, cat_metrics in metrics["categories"].items():
            print(f"  {category}:")
            print(f"    - Score: {cat_metrics['avg_score']:.2f}")
            print(f"    - Time: {cat_metrics['avg_time']:.2f}s")
            print(f"    - Tasks: {cat_metrics['task_count']}")
        
        print(f"\nMemory Usage:")
        for mem_type, count in metrics["memory_usage"].items():
            print(f"  • {mem_type}: {count} entries")
        
        print(f"\n{'='*60}\n")
    
    def save_results(self, filepath: Path):
        """Save benchmark results to file"""
        results_data = {
            "timestamp": datetime.now().isoformat(),
            "tasks": [
                {
                    "id": task.id,
                    "category": task.category,
                    "query": task.query[:100]  # Truncate for storage
                }
                for task in self.tasks
            ],
            "results": [
                {
                    "task_id": r.task_id,
                    "score": r.score,
                    "success": r.success,
                    "execution_time": r.execution_time,
                    "memory_usage": r.memory_usage,
                    "turns_used": r.turns_used,
                    "errors": r.errors
                }
                for r in self.results
            ],
            "metrics": self._calculate_metrics()
        }
        
        with open(filepath, 'w') as f:
            json.dump(results_data, f, indent=2)
        
        logger.info(f"Saved benchmark results to {filepath}")
