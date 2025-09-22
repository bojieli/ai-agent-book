"""
Modified GAIA Runner with Learning from Experience
This script extends the original GAIA runner with experience learning capabilities.
"""

import argparse
import json
import logging
import os
import re
import traceback
from pathlib import Path
from typing import Any, Dict, List
from dotenv import load_dotenv

# Import AWorld components
from AWorld.aworld.config.conf import AgentConfig, TaskConfig
from AWorld.aworld.core.task import Task
from AWorld.aworld.runner import Runners
from AWorld.examples.gaia.prompt import system_prompt
from AWorld.examples.gaia.utils import (
    add_file_path,
    load_dataset_meta,
    question_scorer,
    report_results,
)

# Import our experience learning components
from experience_agent import ExperienceAgent
from knowledge_base import KnowledgeBase
from trajectory_summarizer import TrajectorySummarizer

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Run GAIA tasks with experience learning capabilities"
    )
    
    # Original GAIA arguments
    parser.add_argument(
        "--start",
        type=int,
        default=0,
        help="Start index of the dataset",
    )
    parser.add_argument(
        "--end",
        type=int,
        default=20,
        help="End index of the dataset",
    )
    parser.add_argument(
        "--q",
        type=str,
        help="Question Index or task_id. Highest priority: override other arguments if provided.",
    )
    parser.add_argument(
        "--skip",
        action="store_true",
        help="Skip the question if it has been processed before.",
    )
    parser.add_argument(
        "--split",
        type=str,
        default="validation",
        help="Split of the dataset, e.g., validation, test",
    )
    parser.add_argument(
        "--blacklist_file_path",
        type=str,
        nargs="?",
        help="Blacklist file path, e.g., blacklist.txt",
    )
    
    # Experience learning arguments
    parser.add_argument(
        "--learning-mode",
        action="store_true",
        help="Enable learning mode to capture and summarize successful trajectories"
    )
    parser.add_argument(
        "--apply-experience",
        action="store_true",
        help="Apply learned experiences to new tasks"
    )
    parser.add_argument(
        "--preload-kb",
        action="store_true",
        help="Preload knowledge base from gaia-validation.jsonl"
    )
    parser.add_argument(
        "--kb-path",
        type=str,
        default="./kb_index",
        help="Path to store knowledge base index"
    )
    parser.add_argument(
        "--experience-db",
        type=str,
        default="./learned_experiences.json",
        help="Path to store learned experiences"
    )
    parser.add_argument(
        "--validation-file",
        type=str,
        default="gaia-validation.jsonl",
        help="Path to gaia-validation.jsonl for preloading"
    )
    parser.add_argument(
        "--embedding-model",
        type=str,
        default="all-MiniLM-L6-v2",
        help="Sentence transformer model for embeddings"
    )
    parser.add_argument(
        "--summary-model",
        type=str,
        default="gpt-4o-mini",
        help="Model to use for trajectory summarization"
    )
    
    return parser.parse_args()


def setup_logging(args):
    """Setup logging configuration."""
    workspace = os.getenv("AWORLD_WORKSPACE", ".")
    os.makedirs(workspace, exist_ok=True)
    
    log_file_name = f"experience_agent_{args.q}.log" if args.q else f"experience_agent_{args.start}_{args.end}.log"
    file_handler = logging.FileHandler(
        os.path.join(workspace, log_file_name),
        mode="a",
        encoding="utf-8",
    )
    file_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")
    file_handler.setFormatter(formatter)
    
    logging.getLogger().addHandler(file_handler)


def load_mcp_config(config_path: Path) -> Dict[str, Any]:
    """Load MCP configuration."""
    mcp_config = {}
    available_servers = []
    
    try:
        if config_path.exists():
            with open(config_path, mode="r", encoding="utf-8") as f:
                mcp_config = json.loads(f.read())
                available_servers = list(mcp_config.get("mcpServers", {}).keys())
                logger.info(f"🔧 MCP Available Servers: {available_servers}")
    except json.JSONDecodeError as e:
        logger.error(f"Error loading mcp_collections.json: {e}")
    
    return mcp_config, available_servers


async def run_with_experience(args):
    """Main execution function with experience learning."""
    
    # Load dataset
    gaia_dataset_path = os.getenv("GAIA_DATASET_PATH", "./gaia_dataset")
    full_dataset = load_dataset_meta(gaia_dataset_path, split=args.split)
    logger.info(f"Total questions: {len(full_dataset)}")
    
    # Load MCP configuration
    mcp_config_path = Path(__file__).parent / "AWorld" / "examples" / "gaia" / "mcp.json"
    mcp_config, available_servers = load_mcp_config(mcp_config_path)
    
    # Setup agent configuration
    agent_config = AgentConfig(
        llm_provider=os.getenv("LLM_PROVIDER", "openai"),
        llm_model_name=os.getenv("LLM_MODEL_NAME", "gpt-4o"),
        llm_base_url=os.getenv("LLM_BASE_URL"),
        llm_api_key=os.getenv("LLM_API_KEY"),
        llm_temperature=float(os.getenv("LLM_TEMPERATURE", "0.0"))
    )
    
    # Initialize knowledge base
    knowledge_base = None
    if args.apply_experience or args.preload_kb:
        logger.info("Initializing knowledge base...")
        knowledge_base = KnowledgeBase(
            index_path=args.kb_path,
            model_name=args.embedding_model
        )
        
        # Preload validation data if requested
        if args.preload_kb and os.path.exists(args.validation_file):
            logger.info(f"Preloading knowledge base from {args.validation_file}")
            knowledge_base.index_gaia_validation(args.validation_file)
            stats = knowledge_base.get_statistics()
            logger.info(f"Knowledge base statistics: {stats}")
    
    # Initialize trajectory summarizer
    summarizer = None
    if args.learning_mode:
        logger.info("Initializing trajectory summarizer...")
        summarizer = TrajectorySummarizer(
            llm_config=agent_config,
            model_name=args.summary_model
        )
    
    # Create experience agent
    experience_agent = ExperienceAgent(
        conf=agent_config,
        name="gaia_experience_agent",
        system_prompt=system_prompt,
        learning_mode=args.learning_mode,
        apply_experience=args.apply_experience,
        experience_db_path=args.experience_db,
        knowledge_base=knowledge_base,
        summarizer=summarizer,
        mcp_config=mcp_config,
        mcp_servers=available_servers,
    )
    
    logger.info(f"Experience Agent initialized:")
    logger.info(f"  - Learning mode: {args.learning_mode}")
    logger.info(f"  - Apply experience: {args.apply_experience}")
    logger.info(f"  - Knowledge base: {'Yes' if knowledge_base else 'No'}")
    logger.info(f"  - Summarizer: {'Yes' if summarizer else 'No'}")
    
    # Load existing results
    results_file = os.path.join(os.getenv("AWORLD_WORKSPACE", "."), "experience_results.json")
    if os.path.exists(results_file):
        with open(results_file, "r", encoding="utf-8") as f:
            results = json.load(f)
    else:
        results = []
    
    # Load blacklist
    blacklist = set()
    if args.blacklist_file_path and os.path.exists(args.blacklist_file_path):
        with open(args.blacklist_file_path, "r", encoding="utf-8") as f:
            blacklist = set(f.read().splitlines())
    
    try:
        # Determine dataset slice
        if args.q:
            dataset_slice = [
                record for record in full_dataset 
                if record["task_id"] == args.q
            ]
        else:
            dataset_slice = full_dataset[args.start:args.end]
        
        # Process each question
        for i, dataset_i in enumerate(dataset_slice):
            # Check if should skip
            if not args.q:
                if dataset_i["task_id"] in blacklist:
                    logger.info(f"Skipping blacklisted task: {dataset_i['task_id']}")
                    continue
                
                if args.skip and any(
                    result["task_id"] == dataset_i["task_id"]
                    for result in results
                ):
                    logger.info(f"Skipping already processed task: {dataset_i['task_id']}")
                    continue
            
            try:
                # Log task details
                logger.info(f"{'='*60}")
                logger.info(f"Processing task {i+1}/{len(dataset_slice)}: {dataset_i['task_id']}")
                logger.info(f"Question: {dataset_i['Question']}")
                logger.info(f"Level: {dataset_i['Level']}")
                logger.info(f"Tools: {dataset_i['Annotator Metadata']['Tools']}")
                
                # Prepare question with file paths
                question_data = add_file_path(dataset_i, file_path=gaia_dataset_path, split=args.split)
                question = question_data["Question"]
                
                # Create and execute task
                task = Task(
                    input=question,
                    agent=experience_agent,
                    conf=TaskConfig()
                )
                
                # Execute with experience learning/application
                task_response = await experience_agent.execute_task(task)
                
                # Extract answer
                answer = None
                if task_response and task_response.answer:
                    match = re.search(r"<answer>(.*?)</answer>", task_response.answer)
                    if match:
                        answer = match.group(1)
                
                # Evaluate result
                is_correct = False
                if answer:
                    logger.info(f"Agent answer: {answer}")
                    logger.info(f"Correct answer: {dataset_i['Final answer']}")
                    is_correct = question_scorer(answer, dataset_i["Final answer"])
                    
                    if is_correct:
                        logger.info(f"✓ Question {i} Correct!")
                    else:
                        logger.info(f"✗ Incorrect!")
                else:
                    logger.warning("No answer extracted from response")
                
                # Record result
                new_result = {
                    "task_id": dataset_i["task_id"],
                    "level": dataset_i["Level"],
                    "question": question,
                    "answer": dataset_i["Final answer"],
                    "response": answer or "",
                    "is_correct": is_correct,
                    "learning_mode": args.learning_mode,
                    "applied_experience": args.apply_experience
                }
                
                # Update or append result
                existing_index = next(
                    (idx for idx, result in enumerate(results) 
                     if result["task_id"] == dataset_i["task_id"]),
                    None
                )
                
                if existing_index is not None:
                    results[existing_index] = new_result
                else:
                    results.append(new_result)
                
                # Save intermediate results
                with open(results_file, "w", encoding="utf-8") as f:
                    json.dump(results, f, indent=4, ensure_ascii=False)
                
            except Exception as e:
                logger.error(f"Error processing task {dataset_i['task_id']}: {e}")
                logger.error(traceback.format_exc())
                continue
        
    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    
    finally:
        # Report final results
        report_results(results)
        
        # Save final results
        with open(results_file, "w", encoding="utf-8") as f:
            json.dump(results, f, indent=4, ensure_ascii=False)
        
        # Log experience learning statistics if enabled
        if args.learning_mode:
            num_experiences = len(experience_agent.experiences)
            logger.info(f"\nLearning Statistics:")
            logger.info(f"  - Total experiences learned: {num_experiences}")
            logger.info(f"  - Experience database: {args.experience_db}")
        
        if args.apply_experience and knowledge_base:
            stats = knowledge_base.get_statistics()
            logger.info(f"\nKnowledge Base Statistics:")
            logger.info(f"  - Total indexed documents: {stats['total_documents']}")
            logger.info(f"  - Sources: {stats['sources']}")


def main():
    """Main entry point."""
    # Parse arguments
    args = parse_arguments()
    
    # Load environment
    load_dotenv()
    
    # Setup logging
    setup_logging(args)
    
    # Log configuration
    logger.info("Starting GAIA with Experience Learning")
    logger.info(f"Configuration:")
    logger.info(f"  - Learning mode: {args.learning_mode}")
    logger.info(f"  - Apply experience: {args.apply_experience}")
    logger.info(f"  - Preload KB: {args.preload_kb}")
    
    # Run async main
    import asyncio
    asyncio.run(run_with_experience(args))


if __name__ == "__main__":
    main()
