"""Main entry point for the Contextual Retrieval System

Educational implementation demonstrating the power of contextual chunking
for improving retrieval accuracy in RAG systems.
"""

import json
import logging
import argparse
from pathlib import Path
from typing import List, Dict, Any, Optional
import time
from datetime import datetime
import sys

from config import Config, KnowledgeBaseType
from agent import AgenticRAG
from contextual_chunking import ContextualChunker, ContextualChunk
from contextual_tools import ContextualKnowledgeBaseTools
from contextual_agent import ContextualAgenticRAG

# Configure detailed logging for educational purposes
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('contextual_retrieval.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)


class ContextualRetrievalDemo:
    """
    Main demo class for contextual retrieval system.
    
    Educational Features:
    1. Side-by-side comparison of contextual vs non-contextual
    2. Detailed logging of each step
    3. Performance metrics and analysis
    4. Visual comparison of results
    """
    
    def __init__(self, config: Optional[Config] = None):
        """Initialize the demo system"""
        self.config = config or Config.from_env()
        
        # Initialize components
        self.contextual_chunker = None
        self.non_contextual_chunker = None
        self.contextual_kb = None
        self.non_contextual_kb = None
        self.contextual_agent = None
        self.non_contextual_agent = None
        
        # Results storage
        self.comparison_results = []
        
        logger.info("="*80)
        logger.info("CONTEXTUAL RETRIEVAL SYSTEM - EDUCATIONAL DEMO")
        logger.info("="*80)
        logger.info("This system demonstrates how contextual chunking improves retrieval:")
        logger.info("1. Traditional RAG loses context when chunking documents")
        logger.info("2. Contextual RAG prepends context to chunks before indexing")
        logger.info("3. This improves both BM25 (lexical) and embedding (semantic) search")
        logger.info("="*80)
    
    def initialize_systems(self):
        """Initialize both contextual and non-contextual systems"""
        logger.info("\n" + "="*60)
        logger.info("INITIALIZING RETRIEVAL SYSTEMS")
        logger.info("="*60)
        
        # Initialize contextual system
        logger.info("\n[CONTEXTUAL SYSTEM] Initializing...")
        self.contextual_chunker = ContextualChunker(
            chunking_config=self.config.chunking,
            llm_config=self.config.llm,
            use_contextual=True
        )
        
        self.contextual_kb = ContextualKnowledgeBaseTools(
            config=self.config.knowledge_base,
            use_contextual=True,
            enable_comparison=True
        )
        
        self.contextual_agent = ContextualAgenticRAG(
            config=self.config,
            kb_tools=self.contextual_kb,
            use_contextual=True
        )
        logger.info("[CONTEXTUAL SYSTEM] ✓ Initialized successfully")
        
        # Initialize non-contextual system
        logger.info("\n[NON-CONTEXTUAL SYSTEM] Initializing...")
        self.non_contextual_chunker = ContextualChunker(
            chunking_config=self.config.chunking,
            llm_config=self.config.llm,
            use_contextual=False
        )
        
        self.non_contextual_kb = ContextualKnowledgeBaseTools(
            config=self.config.knowledge_base,
            use_contextual=False,
            enable_comparison=False
        )
        
        self.non_contextual_agent = ContextualAgenticRAG(
            config=self.config,
            kb_tools=self.non_contextual_kb,
            use_contextual=False
        )
        logger.info("[NON-CONTEXTUAL SYSTEM] ✓ Initialized successfully")
        
        logger.info("\n" + "="*60)
        logger.info("INITIALIZATION COMPLETE")
        logger.info("="*60)
    
    def index_document(self, file_path: str):
        """
        Index a document in both systems for comparison.
        
        Educational Note:
        This method shows the difference in indexing:
        - Contextual: Generates context for each chunk using LLM
        - Non-contextual: Standard chunking without context
        """
        logger.info("\n" + "="*60)
        logger.info("DOCUMENT INDEXING")
        logger.info("="*60)
        logger.info(f"Document: {file_path}")
        
        # Read document
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        doc_id = Path(file_path).stem
        logger.info(f"Document ID: {doc_id}")
        logger.info(f"Document size: {len(content)} characters")
        
        # Preview document
        preview = content[:500] + "..." if len(content) > 500 else content
        logger.info(f"\nDocument preview:\n{preview}\n")
        
        # Contextual indexing
        logger.info("\n" + "-"*40)
        logger.info("[CONTEXTUAL INDEXING]")
        logger.info("-"*40)
        logger.info("Generating contextual chunks...")
        logger.info("This process:")
        logger.info("1. Chunks the document normally")
        logger.info("2. For each chunk, uses LLM to generate context")
        logger.info("3. Prepends context to chunk before indexing")
        
        start_time = time.time()
        contextual_chunks = self.contextual_chunker.chunk_document(
            text=content,
            doc_id=doc_id,
            doc_metadata={"source": file_path}
        )
        contextual_time = time.time() - start_time
        
        logger.info(f"\nCreated {len(contextual_chunks)} contextual chunks")
        logger.info(f"Time taken: {contextual_time:.2f} seconds")
        
        # Show example contextual chunk
        if contextual_chunks:
            example = contextual_chunks[0]
            logger.info("\n[EXAMPLE CONTEXTUAL CHUNK]")
            logger.info(f"Chunk ID: {example.chunk_id}")
            logger.info(f"Original text ({len(example.text)} chars):")
            logger.info(f"  {example.text[:200]}...")
            logger.info(f"\nGenerated context ({len(example.context)} chars):")
            logger.info(f"  {example.context}")
            logger.info(f"\nContextualized text ({len(example.contextualized_text)} chars):")
            logger.info(f"  {example.contextualized_text[:300]}...")
        
        # Index contextual chunks
        self.contextual_kb.index_contextual_chunks(contextual_chunks)
        
        # Non-contextual indexing
        logger.info("\n" + "-"*40)
        logger.info("[NON-CONTEXTUAL INDEXING]")
        logger.info("-"*40)
        logger.info("Creating standard chunks...")
        
        start_time = time.time()
        non_contextual_chunks = self.non_contextual_chunker.chunk_document(
            text=content,
            doc_id=doc_id,
            doc_metadata={"source": file_path}
        )
        non_contextual_time = time.time() - start_time
        
        logger.info(f"\nCreated {len(non_contextual_chunks)} non-contextual chunks")
        logger.info(f"Time taken: {non_contextual_time:.2f} seconds")
        
        # Show example non-contextual chunk
        if non_contextual_chunks:
            example = non_contextual_chunks[0]
            logger.info("\n[EXAMPLE NON-CONTEXTUAL CHUNK]")
            logger.info(f"Chunk ID: {example.chunk_id}")
            logger.info(f"Text ({len(example.text)} chars):")
            logger.info(f"  {example.text[:200]}...")
        
        # Index non-contextual chunks
        self.non_contextual_kb.index_contextual_chunks(non_contextual_chunks)
        
        # Show statistics
        logger.info("\n" + "-"*40)
        logger.info("[INDEXING STATISTICS]")
        logger.info("-"*40)
        
        contextual_stats = self.contextual_chunker.get_statistics()
        logger.info("\nContextual Chunking Stats:")
        logger.info(json.dumps(contextual_stats, indent=2))
        
        logger.info(f"\nSpeed comparison:")
        logger.info(f"  Contextual: {contextual_time:.2f}s ({contextual_time/len(contextual_chunks):.3f}s per chunk)")
        logger.info(f"  Non-contextual: {non_contextual_time:.2f}s ({non_contextual_time/len(non_contextual_chunks):.3f}s per chunk)")
        logger.info(f"  Overhead: {contextual_time - non_contextual_time:.2f}s for context generation")
        
        logger.info("\n" + "="*60)
        logger.info("INDEXING COMPLETE")
        logger.info("="*60)
    
    def compare_search(self, query: str, top_k: int = 10):
        """
        Compare search results between contextual and non-contextual.
        
        Educational Note:
        This shows how context improves retrieval:
        - Better semantic understanding
        - Improved lexical matching
        - Higher quality results
        """
        logger.info("\n" + "="*60)
        logger.info("SEARCH COMPARISON")
        logger.info("="*60)
        logger.info(f"Query: {query}")
        logger.info(f"Top-K: {top_k}")
        
        # Contextual search
        logger.info("\n" + "-"*40)
        logger.info("[CONTEXTUAL SEARCH]")
        logger.info("-"*40)
        
        start_time = time.time()
        contextual_results = self.contextual_kb.contextual_search(
            query=query,
            method="hybrid",
            top_k=top_k
        )
        contextual_time = time.time() - start_time
        
        logger.info(f"Found {len(contextual_results)} results in {contextual_time:.3f}s")
        
        # Show top contextual results
        logger.info("\nTop 3 Contextual Results:")
        for i, result in enumerate(contextual_results[:3], 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Chunk ID: {result.chunk_id}")
            logger.info(f"    Score: {result.score:.4f}")
            logger.info(f"    BM25: {result.bm25_score:.4f}, Embedding: {result.embedding_score:.4f}")
            logger.info(f"    Context: {result.context_text[:150]}..." if result.context_text else "    Context: None")
            logger.info(f"    Text: {result.text[:150]}...")
        
        # Non-contextual search
        logger.info("\n" + "-"*40)
        logger.info("[NON-CONTEXTUAL SEARCH]")
        logger.info("-"*40)
        
        start_time = time.time()
        non_contextual_results = self.non_contextual_kb.contextual_search(
            query=query,
            method="hybrid",
            top_k=top_k
        )
        non_contextual_time = time.time() - start_time
        
        logger.info(f"Found {len(non_contextual_results)} results in {non_contextual_time:.3f}s")
        
        # Show top non-contextual results
        logger.info("\nTop 3 Non-Contextual Results:")
        for i, result in enumerate(non_contextual_results[:3], 1):
            logger.info(f"\n  Result {i}:")
            logger.info(f"    Chunk ID: {result.chunk_id}")
            logger.info(f"    Score: {result.score:.4f}")
            logger.info(f"    BM25: {result.bm25_score:.4f}, Embedding: {result.embedding_score:.4f}")
            logger.info(f"    Text: {result.text[:150]}...")
        
        # Analysis
        logger.info("\n" + "-"*40)
        logger.info("[SEARCH ANALYSIS]")
        logger.info("-"*40)
        
        # Score comparison
        contextual_avg_score = sum(r.score for r in contextual_results) / len(contextual_results) if contextual_results else 0
        non_contextual_avg_score = sum(r.score for r in non_contextual_results) / len(non_contextual_results) if non_contextual_results else 0
        
        improvement = ((contextual_avg_score - non_contextual_avg_score) / non_contextual_avg_score * 100) if non_contextual_avg_score > 0 else 0
        
        logger.info(f"\nAverage Scores:")
        logger.info(f"  Contextual: {contextual_avg_score:.4f}")
        logger.info(f"  Non-contextual: {non_contextual_avg_score:.4f}")
        logger.info(f"  Improvement: {improvement:.1f}%")
        
        logger.info(f"\nSpeed:")
        logger.info(f"  Contextual: {contextual_time:.3f}s")
        logger.info(f"  Non-contextual: {non_contextual_time:.3f}s")
        
        # Store comparison results
        self.comparison_results.append({
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "contextual": {
                "avg_score": contextual_avg_score,
                "time": contextual_time,
                "num_results": len(contextual_results)
            },
            "non_contextual": {
                "avg_score": non_contextual_avg_score,
                "time": non_contextual_time,
                "num_results": len(non_contextual_results)
            },
            "improvement_pct": improvement
        })
        
        logger.info("\n" + "="*60)
        logger.info("SEARCH COMPARISON COMPLETE")
        logger.info("="*60)
        
        return contextual_results, non_contextual_results
    
    def compare_agent_responses(self, query: str):
        """
        Compare agent responses using contextual vs non-contextual retrieval.
        
        Educational Note:
        This shows the end-to-end impact on answer quality:
        - Contextual: More accurate and complete answers
        - Non-contextual: May miss important context
        """
        logger.info("\n" + "="*60)
        logger.info("AGENT RESPONSE COMPARISON")
        logger.info("="*60)
        logger.info(f"Query: {query}")
        
        # Contextual agent response
        logger.info("\n" + "-"*40)
        logger.info("[CONTEXTUAL AGENT]")
        logger.info("-"*40)
        
        start_time = time.time()
        contextual_response = self.contextual_agent.query(query, stream=False)
        contextual_time = time.time() - start_time
        
        logger.info(f"\nResponse ({contextual_time:.2f}s):")
        logger.info(contextual_response)
        
        # Non-contextual agent response
        logger.info("\n" + "-"*40)
        logger.info("[NON-CONTEXTUAL AGENT]")
        logger.info("-"*40)
        
        start_time = time.time()
        non_contextual_response = self.non_contextual_agent.query(query, stream=False)
        non_contextual_time = time.time() - start_time
        
        logger.info(f"\nResponse ({non_contextual_time:.2f}s):")
        logger.info(non_contextual_response)
        
        # Analysis
        logger.info("\n" + "-"*40)
        logger.info("[RESPONSE ANALYSIS]")
        logger.info("-"*40)
        
        logger.info(f"\nResponse Length:")
        logger.info(f"  Contextual: {len(contextual_response)} characters")
        logger.info(f"  Non-contextual: {len(non_contextual_response)} characters")
        
        logger.info(f"\nResponse Time:")
        logger.info(f"  Contextual: {contextual_time:.2f}s")
        logger.info(f"  Non-contextual: {non_contextual_time:.2f}s")
        
        logger.info("\n" + "="*60)
        logger.info("AGENT COMPARISON COMPLETE")
        logger.info("="*60)
        
        return contextual_response, non_contextual_response
    
    def run_comprehensive_comparison(self, 
                                    document_path: str,
                                    test_queries: List[str]):
        """
        Run a comprehensive comparison with multiple queries.
        
        Educational Note:
        This demonstrates the consistent improvement across
        different types of queries and use cases.
        """
        logger.info("\n" + "="*80)
        logger.info("COMPREHENSIVE COMPARISON")
        logger.info("="*80)
        
        # Index document
        self.index_document(document_path)
        
        # Test each query
        for i, query in enumerate(test_queries, 1):
            logger.info(f"\n\n{'='*80}")
            logger.info(f"TEST QUERY {i}/{len(test_queries)}")
            logger.info(f"{'='*80}")
            
            # Compare search
            self.compare_search(query)
            
            # Compare agent responses
            if self.config.agent.enabled:
                self.compare_agent_responses(query)
        
        # Final summary
        self.print_summary()
    
    def print_summary(self):
        """Print comprehensive summary of all comparisons"""
        logger.info("\n" + "="*80)
        logger.info("FINAL SUMMARY")
        logger.info("="*80)
        
        if not self.comparison_results:
            logger.info("No comparison results available")
            return
        
        # Calculate overall statistics
        total_improvement = sum(r["improvement_pct"] for r in self.comparison_results)
        avg_improvement = total_improvement / len(self.comparison_results)
        
        logger.info(f"\nTotal queries tested: {len(self.comparison_results)}")
        logger.info(f"Average score improvement: {avg_improvement:.1f}%")
        
        # Show chunking statistics
        contextual_stats = self.contextual_chunker.get_statistics()
        logger.info(f"\nContextual Chunking Statistics:")
        logger.info(f"  Total chunks generated: {contextual_stats['total_chunks']}")
        logger.info(f"  Total context tokens: {contextual_stats['total_context_tokens']}")
        logger.info(f"  Estimated cost: ${contextual_stats['estimated_cost']:.4f}")
        logger.info(f"  Cache hit rate: {contextual_stats['cache_hit_rate']:.1%}")
        
        # Show retrieval statistics
        kb_stats = self.contextual_kb.get_statistics()
        logger.info(f"\nRetrieval Statistics:")
        logger.info(f"  Total searches: {kb_stats['search_stats']['total_searches']}")
        logger.info(f"  Average retrieval time: {kb_stats['search_stats']['avg_retrieval_time']:.3f}s")
        
        # Key insights
        logger.info("\n" + "-"*40)
        logger.info("KEY INSIGHTS:")
        logger.info("-"*40)
        
        if avg_improvement > 20:
            logger.info("✓ Contextual retrieval shows SIGNIFICANT improvement (>20%)")
            logger.info("  Recommendation: Use contextual retrieval for production")
        elif avg_improvement > 10:
            logger.info("✓ Contextual retrieval shows MODERATE improvement (10-20%)")
            logger.info("  Recommendation: Consider contextual retrieval for important queries")
        else:
            logger.info("✓ Contextual retrieval shows MINOR improvement (<10%)")
            logger.info("  Recommendation: Evaluate cost-benefit for your use case")
        
        logger.info("\n" + "="*80)
        logger.info("DEMONSTRATION COMPLETE")
        logger.info("="*80)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Contextual Retrieval System - Educational Demo"
    )
    
    # Mode selection
    parser.add_argument(
        "--mode",
        choices=["index", "search", "compare", "demo"],
        default="demo",
        help="Operation mode"
    )
    
    # Document indexing
    parser.add_argument(
        "--document",
        type=str,
        help="Path to document to index"
    )
    
    # Search parameters
    parser.add_argument(
        "--query",
        type=str,
        help="Search query"
    )
    
    parser.add_argument(
        "--top-k",
        type=int,
        default=10,
        help="Number of results to retrieve"
    )
    
    # System configuration
    parser.add_argument(
        "--contextual",
        action="store_true",
        default=True,
        help="Use contextual retrieval"
    )
    
    parser.add_argument(
        "--no-contextual",
        dest="contextual",
        action="store_false",
        help="Disable contextual retrieval"
    )
    
    parser.add_argument(
        "--provider",
        type=str,
        help="LLM provider for context generation"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Enable verbose logging"
    )
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Initialize configuration
    config = Config.from_env()
    if args.provider:
        config.llm.provider = args.provider
    
    # Create demo system
    demo = ContextualRetrievalDemo(config)
    demo.initialize_systems()
    
    # Execute based on mode
    if args.mode == "demo":
        # Run full demo with example document and queries
        logger.info("Running demonstration with example data...")
        
        # Create example document if it doesn't exist
        example_doc = Path("example_document.txt")
        if not example_doc.exists():
            with open(example_doc, "w") as f:
                f.write("""
Artificial Intelligence and Machine Learning

Artificial Intelligence (AI) is a broad field of computer science focused on creating intelligent machines that can perform tasks typically requiring human intelligence. Machine learning (ML), a subset of AI, enables systems to learn and improve from experience without being explicitly programmed.

Deep Learning and Neural Networks

Deep learning is a specialized subset of machine learning that uses multi-layered neural networks. These networks are inspired by the human brain's structure and can process vast amounts of data to identify patterns and make decisions. Convolutional Neural Networks (CNNs) are particularly effective for image recognition, while Recurrent Neural Networks (RNNs) excel at sequential data processing.

Natural Language Processing

Natural Language Processing (NLP) is another crucial area of AI that focuses on the interaction between computers and human language. Modern NLP systems use transformer architectures, such as BERT and GPT, which have revolutionized tasks like translation, sentiment analysis, and text generation. These models use attention mechanisms to understand context and relationships between words.

Applications in Industry

AI and ML are transforming various industries. In healthcare, machine learning models assist in disease diagnosis and drug discovery. Financial services use AI for fraud detection and algorithmic trading. Autonomous vehicles rely on computer vision and reinforcement learning to navigate safely.

Challenges and Future Directions

Despite significant progress, AI faces challenges including bias in algorithms, lack of explainability, and ethical concerns. Researchers are working on explainable AI (XAI) to make models more transparent. The field is also exploring quantum computing's potential to accelerate AI computations and solve previously intractable problems.
""")
        
        # Run comprehensive comparison
        test_queries = [
            "What is deep learning and how does it relate to neural networks?",
            "What are the applications of AI in healthcare?",
            "How do transformer architectures work in NLP?",
            "What are CNNs and RNNs?",
            "What are the main challenges facing AI?"
        ]
        
        demo.run_comprehensive_comparison(str(example_doc), test_queries)
    
    elif args.mode == "index":
        if not args.document:
            logger.error("Please provide a document path with --document")
            return
        
        demo.index_document(args.document)
    
    elif args.mode == "search":
        if not args.query:
            logger.error("Please provide a search query with --query")
            return
        
        demo.compare_search(args.query, args.top_k)
    
    elif args.mode == "compare":
        if not args.query:
            logger.error("Please provide a query with --query")
            return
        
        demo.compare_agent_responses(args.query)


if __name__ == "__main__":
    main()
