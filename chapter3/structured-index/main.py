"""
Main script for building and querying structured indexes.
"""

import argparse
import asyncio
from pathlib import Path
from loguru import logger
import sys

from config import get_raptor_config, get_graphrag_config
from raptor_indexer import RaptorIndexer
from graphrag_indexer import GraphRAGIndexer
from document_processor import DocumentProcessor
from api_service import run_server


async def build_indexes(file_path: Path, index_type: str = "both"):
    """Build RAPTOR and/or GraphRAG indexes from a document."""
    logger.info(f"Building {index_type} index(es) from {file_path}")
    
    # Process document
    processor = DocumentProcessor()
    text = await processor.process_file(file_path)
    logger.info(f"Processed document: {len(text)} characters")
    
    # Build RAPTOR index
    if index_type in ["raptor", "both"]:
        logger.info("Building RAPTOR tree index...")
        raptor_config = get_raptor_config()
        raptor = RaptorIndexer(raptor_config)
        raptor.build_index(text)
        raptor.save_index()
        stats = raptor.get_tree_statistics()
        logger.info(f"RAPTOR index built: {stats}")
    
    # Build GraphRAG index
    if index_type in ["graphrag", "both"]:
        logger.info("Building GraphRAG knowledge graph...")
        graphrag_config = get_graphrag_config()
        graphrag = GraphRAGIndexer(graphrag_config)
        graphrag.build_knowledge_graph(text)
        graphrag.detect_communities()
        graphrag.hierarchical_summarization()
        graphrag.save_index()
        stats = graphrag.get_graph_statistics()
        logger.info(f"GraphRAG index built: {stats}")
    
    logger.info("Indexing complete!")


async def query_indexes(query: str, index_type: str = "both", top_k: int = 5):
    """Query RAPTOR and/or GraphRAG indexes."""
    results = {}
    
    # Query RAPTOR
    if index_type in ["raptor", "both"]:
        try:
            raptor_config = get_raptor_config()
            raptor = RaptorIndexer(raptor_config)
            raptor.load_index()
            raptor_results = raptor.search(query, top_k)
            results["raptor"] = raptor_results
            logger.info(f"RAPTOR returned {len(raptor_results)} results")
        except Exception as e:
            logger.error(f"Error querying RAPTOR: {e}")
    
    # Query GraphRAG
    if index_type in ["graphrag", "both"]:
        try:
            graphrag_config = get_graphrag_config()
            graphrag = GraphRAGIndexer(graphrag_config)
            graphrag.load_index()
            graphrag_results = graphrag.search(query, top_k)
            results["graphrag"] = graphrag_results
            logger.info(f"GraphRAG returned {len(graphrag_results)} results")
        except Exception as e:
            logger.error(f"Error querying GraphRAG: {e}")
    
    return results


def main():
    parser = argparse.ArgumentParser(description="Structured Index Tool")
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Build command
    build_parser = subparsers.add_parser("build", help="Build index from document")
    build_parser.add_argument("file", type=str, help="Path to document file")
    build_parser.add_argument("--type", choices=["raptor", "graphrag", "both"], 
                            default="both", help="Type of index to build")
    
    # Query command
    query_parser = subparsers.add_parser("query", help="Query the index")
    query_parser.add_argument("query", type=str, help="Search query")
    query_parser.add_argument("--type", choices=["raptor", "graphrag", "both"],
                            default="both", help="Index to query")
    query_parser.add_argument("--top-k", type=int, default=5, 
                            help="Number of results to return")
    
    # Server command
    server_parser = subparsers.add_parser("serve", help="Run API server")
    
    args = parser.parse_args()
    
    if args.command == "build":
        asyncio.run(build_indexes(Path(args.file), args.type))
    elif args.command == "query":
        results = asyncio.run(query_indexes(args.query, args.type, args.top_k))
        
        # Display results
        for index_type, index_results in results.items():
            print(f"\n{index_type.upper()} Results:")
            print("-" * 50)
            for i, result in enumerate(index_results, 1):
                print(f"\n{i}. Score: {result.get('score', 'N/A'):.3f}")
                if 'summary' in result:
                    print(f"   Summary: {result['summary'][:200]}...")
                elif 'description' in result:
                    print(f"   Description: {result['description'][:200]}...")
                if 'level' in result:
                    print(f"   Level: {result['level']}")
    elif args.command == "serve":
        run_server()
    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
