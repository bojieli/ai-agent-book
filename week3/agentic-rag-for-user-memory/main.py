#!/usr/bin/env python3
"""
Main entry point for the Agentic RAG User Memory System
"""

import argparse
import json
import logging
from pathlib import Path

from config import Config
from agent import UserMemoryRAGAgent
from conversation_chunker import ConversationChunker


logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def build_index(args):
    """Build index from conversation history"""
    config = Config.from_env()
    
    # Override chunking settings if provided
    if args.rounds_per_chunk:
        config.chunking.rounds_per_chunk = args.rounds_per_chunk
    
    agent = UserMemoryRAGAgent(config)
    
    # Build index
    report = agent.build_index_from_history(
        args.history_file,
        save_chunks=args.save_chunks
    )
    
    # Print report
    print("\n=== Indexing Report ===")
    print(f"Chunks created: {report['chunks_created']}")
    print(f"Chunks indexed: {report['chunks_indexed']}")
    print(f"Memories extracted: {report['memories_extracted']}")
    print(f"\nMetadata:")
    print(json.dumps(report['metadata'], indent=2))
    
    if args.output:
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        print(f"\nReport saved to: {args.output}")


def query_interactive(args):
    """Interactive query mode"""
    config = Config.from_env()
    agent = UserMemoryRAGAgent(config)
    
    print("\n=== Agentic RAG User Memory System ===")
    print("Type 'exit' or 'quit' to end the session")
    print("Type 'reset' to clear conversation history")
    print("Type 'help' for available commands\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['exit', 'quit']:
                print("Goodbye!")
                break
            
            elif user_input.lower() == 'reset':
                agent.reset()
                print("Conversation history cleared.\n")
                continue
            
            elif user_input.lower() == 'help':
                print("\nAvailable commands:")
                print("  - Type your question to query the system")
                print("  - 'reset': Clear conversation history")
                print("  - 'exit'/'quit': End the session")
                print("\nThe agent can search conversations and memories to answer your questions.\n")
                continue
            
            elif not user_input:
                continue
            
            # Process query
            print("\nAssistant: ", end="", flush=True)
            
            if args.stream:
                for chunk in agent.query(user_input, stream=True):
                    print(chunk, end="", flush=True)
                print("\n")
            else:
                response = next(agent.query(user_input, stream=False))
                print(response)
                print()
                
        except KeyboardInterrupt:
            print("\n\nInterrupted. Type 'exit' to quit.\n")
        except Exception as e:
            logger.error(f"Error: {e}")
            print(f"\nError: {e}\n")


def query_single(args):
    """Process a single query"""
    config = Config.from_env()
    agent = UserMemoryRAGAgent(config)
    
    print(f"Query: {args.query}\n")
    print("Response: ", end="", flush=True)
    
    if args.stream:
        for chunk in agent.query(args.query, stream=True):
            print(chunk, end="", flush=True)
        print()
    else:
        response = next(agent.query(args.query, stream=False))
        print(response)
    
    if args.output:
        result = {
            "query": args.query,
            "response": response if not args.stream else "[streamed response]",
            "config": config.to_dict()
        }
        with open(args.output, 'w') as f:
            json.dump(result, f, indent=2)
        print(f"\nResult saved to: {args.output}")


def chunk_history(args):
    """Chunk conversation history without indexing"""
    config = Config.from_env()
    
    if args.rounds_per_chunk:
        config.chunking.rounds_per_chunk = args.rounds_per_chunk
    
    chunker = ConversationChunker(config.chunking)
    
    # Chunk the history
    chunks, metadata = chunker.chunk_conversation_history(args.history_file)
    
    print(f"\nCreated {len(chunks)} chunks from {metadata['total_conversations']} conversations")
    print(f"Total rounds: {metadata['total_rounds']}")
    
    # Save chunks
    output_file = args.output or "conversation_chunks.json"
    chunker.save_chunks(chunks, output_file)
    print(f"Chunks saved to: {output_file}")
    
    # Print sample chunk
    if chunks and args.verbose:
        print("\nSample chunk:")
        print(json.dumps(chunks[0].to_dict(), indent=2, ensure_ascii=False)[:1000] + "...")


def main():
    parser = argparse.ArgumentParser(
        description="Agentic RAG System for User Memory Evaluation"
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Build index command
    build_parser = subparsers.add_parser("build", help="Build index from conversation history")
    build_parser.add_argument("history_file", help="Path to conversation history JSON file")
    build_parser.add_argument("--rounds-per-chunk", type=int, help="Number of rounds per chunk")
    build_parser.add_argument("--save-chunks", action="store_true", help="Save chunks to file")
    build_parser.add_argument("-o", "--output", help="Output file for report")
    
    # Query commands
    query_parser = subparsers.add_parser("query", help="Query the indexed conversations")
    query_parser.add_argument("query", nargs="?", help="Query string (if not provided, enters interactive mode)")
    query_parser.add_argument("--stream", action="store_true", help="Stream the response")
    query_parser.add_argument("-o", "--output", help="Output file for results")
    
    # Chunk command
    chunk_parser = subparsers.add_parser("chunk", help="Chunk conversation history")
    chunk_parser.add_argument("history_file", help="Path to conversation history JSON file")
    chunk_parser.add_argument("--rounds-per-chunk", type=int, help="Number of rounds per chunk")
    chunk_parser.add_argument("-o", "--output", help="Output file for chunks")
    chunk_parser.add_argument("-v", "--verbose", action="store_true", help="Show sample chunk")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    if args.command == "build":
        build_index(args)
    elif args.command == "query":
        if args.query:
            query_single(args)
        else:
            query_interactive(args)
    elif args.command == "chunk":
        chunk_history(args)


if __name__ == "__main__":
    main()
