"""
Main entry point for Contextual Retrieval User Memory System
"""

import argparse
import logging
from pathlib import Path
import json
import sys
import os

# Add parent directories to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "week2" / "user-memory"))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "week2" / "user-memory-evaluation"))

from config import Config, RetrievalMode
from memory_agent import MemoryAgent
from evaluation import MemoryEvaluator, TestCase

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def run_evaluation(args):
    """Run evaluation on test cases"""
    config = Config.from_env()
    
    if args.verbose:
        config.verbose = True
        config.evaluation.enable_verbose = True
    
    evaluator = MemoryEvaluator(config)
    
    if args.test_case:
        # Evaluate single test case
        test_path = Path(args.test_case)
        if not test_path.exists():
            # Try relative to test_cases directory
            test_path = Path(config.evaluation.test_cases_dir) / args.test_case
        
        if not test_path.exists():
            logger.error(f"Test case not found: {args.test_case}")
            return
        
        test_case = TestCase.from_yaml(test_path)
        
        # Determine modes to compare
        modes = []
        if args.mode == "compare":
            modes = [RetrievalMode.CONTEXTUAL, RetrievalMode.NON_CONTEXTUAL]
        else:
            mode_map = {
                "contextual": RetrievalMode.CONTEXTUAL,
                "non-contextual": RetrievalMode.NON_CONTEXTUAL,
                "baseline": RetrievalMode.NON_CONTEXTUAL
            }
            modes = [mode_map.get(args.mode, RetrievalMode.CONTEXTUAL)]
        
        results = evaluator.evaluate_test_case(test_case, modes, verbose=True)
        
        # Save results if requested
        if args.output:
            output_file = Path(args.output)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Convert to serializable format
            output_data = {}
            for mode, metrics in results.items():
                output_data[mode] = {
                    "test_id": metrics.test_id,
                    "chunks_retrieved": metrics.chunks_retrieved,
                    "answer_accuracy": metrics.answer_accuracy,
                    "completeness": metrics.completeness,
                    "tool_calls": metrics.tool_calls,
                    "latency_ms": metrics.latency_ms,
                    "total_tokens": metrics.total_tokens
                }
            
            with open(output_file, 'w') as f:
                json.dump(output_data, f, indent=2)
            
            logger.info(f"Results saved to {output_file}")
    
    else:
        # Run full test suite
        categories = args.categories.split(',') if args.categories else None
        sample_size = args.sample_size
        
        summary = evaluator.evaluate_test_suite(
            test_cases_dir=args.test_dir,
            categories=categories,
            sample_size=sample_size
        )
        
        # Print final summary
        if summary.get("improvements"):
            logger.info("\n" + "="*60)
            logger.info("OVERALL IMPROVEMENTS WITH CONTEXTUAL RETRIEVAL:")
            logger.info("="*60)
            
            for category, improvements in summary["improvements"].items():
                logger.info(f"\n{category}:")
                logger.info(f"  Answer Accuracy: {improvements['accuracy_improvement']:+.1f}%")
                logger.info(f"  Completeness: {improvements['completeness_improvement']:+.1f}%")


def run_interactive(args):
    """Run interactive mode for testing"""
    config = Config.from_env()
    
    logger.info(f"Starting interactive mode with dual-context memory system")
    logger.info("Type 'exit' to quit, 'stats' for statistics")
    logger.info("="*60)
    
    # Initialize unified memory agent (always uses dual context)
    user_id = args.user_id or "interactive_user"
    agent = MemoryAgent(
        user_id=user_id,
        config=config
    )
    
    # Check if we need to index any test data
    if args.index_test_case:
        test_path = Path(args.index_test_case)
        if test_path.exists():
            logger.info(f"Indexing test case: {test_path}")
            test_case = TestCase.from_yaml(test_path)
            
            # Process conversation histories (updates both memory systems)
            for conv in test_case.conversation_histories:
                results = agent.process_conversation(conv)
                logger.info(f"  Processed {conv.get('conversation_id')}: "
                          f"{len(results['chunks_created'])} chunks, "
                          f"{len(results['cards_updated'])} cards")
            
            logger.info(f"Indexed {len(test_case.conversation_histories)} conversations")
            stats = agent.get_statistics()
            logger.info(f"Memory statistics: {stats}")
    
    last_query = None
    
    while True:
        try:
            query = input("\nYour question: ").strip()
            
            if query.lower() == 'exit':
                break
            
            if query.lower() == 'stats':
                # Show comprehensive statistics
                stats = agent.get_statistics()
                
                logger.info("\n" + "="*60)
                logger.info("MEMORY SYSTEM STATISTICS:")
                logger.info("="*60)
                
                # Structured memory stats
                logger.info("\nStructured Memory (JSON Cards):")
                sm = stats['structured_memory']
                logger.info(f"  Total cards: {sm['total_cards']}")
                logger.info(f"  Categories: {', '.join(sm['categories']) if sm['categories'] else 'None'}")
                
                # Conversation memory stats
                logger.info("\nConversation Memory (Contextual Chunks):")
                cm = stats['conversation_memory']
                for key, value in cm.items():
                    logger.info(f"  {key}: {value}")
                
                # Agent performance stats
                logger.info("\nAgent Performance:")
                ap = stats['agent_performance']
                for key, value in ap.items():
                    if isinstance(value, float):
                        logger.info(f"  {key}: {value:.2f}")
                    else:
                        logger.info(f"  {key}: {value}")
                
                continue
            
            # Answer the query
            last_query = query
            logger.info("\nSearching memories and generating response...")
            
            answer = agent.answer(query)
            
            logger.info("\n" + "="*60)
            logger.info("ANSWER:")
            logger.info("="*60)
            logger.info(answer)
            
            # Show trajectory if verbose
            if args.verbose and agent.trajectories:
                trajectory = agent.trajectories[-1]
                logger.info("\n" + "-"*40)
                logger.info("Processing Details:")
                logger.info(f"  Memory cards used: {trajectory.cards_used}")
                logger.info(f"  Chunks retrieved: {trajectory.chunks_retrieved}")
                logger.info(f"  Tool calls: {len(trajectory.tool_calls)}")
                logger.info(f"  Proactive insights: {trajectory.insights_generated}")
                logger.info(f"  Latency: {trajectory.latency_ms}ms")
                logger.info(f"  Total tokens: {trajectory.total_tokens}")
                
                if trajectory.tool_calls:
                    logger.info(f"\n  Tool sequence:")
                    for tc in trajectory.tool_calls[:5]:  # Show first 5 tools
                        logger.info(f"    - {tc.tool_name}: {str(tc.arguments)[:50]}...")
        
        except KeyboardInterrupt:
            logger.info("\nInterrupted by user")
            break
        except Exception as e:
            logger.error(f"Error: {e}")


def run_demo(args):
    """Run demonstration with dual-context system"""
    if args.basic:
        # Run basic demo without JSON Cards
        from demo import run_demo as demo_func
        demo_func()
    else:
        # Run full demo with dual-context system
        from demo_advanced import demonstrate_dual_context_system
        demonstrate_dual_context_system()


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Contextual Retrieval for User Memory Evaluation"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Evaluate command
    eval_parser = subparsers.add_parser("evaluate", help="Run evaluation")
    eval_parser.add_argument(
        "--test-case",
        help="Single test case to evaluate (e.g., layer1/01_bank_account.yaml)"
    )
    eval_parser.add_argument(
        "--test-dir",
        default="test_cases",
        help="Directory containing test cases"
    )
    eval_parser.add_argument(
        "--categories",
        help="Categories to test (comma-separated: layer1,layer2,layer3)"
    )
    eval_parser.add_argument(
        "--sample-size",
        type=int,
        help="Number of tests to sample per category"
    )
    eval_parser.add_argument(
        "--mode",
        choices=["contextual", "non-contextual", "baseline", "compare"],
        default="compare",
        help="Retrieval mode to test"
    )
    eval_parser.add_argument(
        "--output",
        help="Output file for results"
    )
    eval_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose output"
    )
    
    # Interactive command
    interactive_parser = subparsers.add_parser("interactive", help="Run interactive mode")
    interactive_parser.add_argument(
        "--user-id",
        default="interactive_user",
        help="User ID for the session"
    )
    interactive_parser.add_argument(
        "--index-test-case",
        help="Test case to pre-index for interactive testing"
    )
    interactive_parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed search trajectory"
    )
    
    # Demo command
    demo_parser = subparsers.add_parser("demo", help="Run demonstration")
    demo_parser.add_argument(
        "--basic",
        action="store_true",
        help="Run basic demo without JSON Cards (contextual retrieval only)"
    )
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    # Run appropriate command
    if args.command == "evaluate":
        run_evaluation(args)
    elif args.command == "interactive":
        run_interactive(args)
    elif args.command == "demo":
        run_demo(args)


if __name__ == "__main__":
    main()
