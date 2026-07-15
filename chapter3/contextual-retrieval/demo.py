#!/usr/bin/env python3
"""Interactive demo of the Contextual Retrieval System

This script provides an interactive demonstration showing:
1. How chunks lose context in traditional RAG
2. How contextual retrieval solves this problem
3. Side-by-side comparison of retrieval quality
"""

import json
import logging
from pathlib import Path
from typing import List
import time
from datetime import datetime

from config import Config
from contextual_chunking import ContextualChunker
from contextual_tools import ContextualKnowledgeBaseTools

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'  # Simple format for demo
)
logger = logging.getLogger(__name__)


def print_header(title: str, char: str = "=", width: int = 80):
    """Print a formatted header"""
    logger.info(f"\n{char * width}")
    logger.info(f"{title.center(width)}")
    logger.info(f"{char * width}\n")


def print_section(title: str, char: str = "-", width: int = 60):
    """Print a section header"""
    logger.info(f"\n{char * width}")
    logger.info(f"{title}")
    logger.info(f"{char * width}\n")


class ContextualRetrievalDemo:
    """Interactive demo class"""
    
    def __init__(self):
        self.config = Config.from_env()
        self.documents = {}
        self.contextual_kb = None
        self.non_contextual_kb = None
    
    def run(self):
        """Run the interactive demo"""
        print_header("CONTEXTUAL RETRIEVAL SYSTEM - INTERACTIVE DEMO")
        
        logger.info("Welcome! This demo will show you how contextual retrieval")
        logger.info("improves RAG systems by preserving context when chunking.\n")
        
        while True:
            self.show_menu()
            choice = input("\nYour choice: ").strip()
            
            if choice == "1":
                self.demo_problem()
            elif choice == "2":
                self.demo_solution()
            elif choice == "3":
                self.demo_comparison()
            elif choice == "4":
                self.demo_real_example()
            elif choice == "5":
                self.show_statistics()
            elif choice == "q":
                logger.info("\nThank you for using the Contextual Retrieval Demo!")
                break
            else:
                logger.info("Invalid choice. Please try again.")
    
    def show_menu(self):
        """Show main menu"""
        print_section("MAIN MENU")
        logger.info("1. Demonstrate the Context Loss Problem")
        logger.info("2. Show the Contextual Retrieval Solution")
        logger.info("3. Compare Search Results (Side-by-Side)")
        logger.info("4. Real-World Example (Financial Report)")
        logger.info("5. Show Performance Statistics")
        logger.info("q. Quit")
    
    def demo_problem(self):
        """Demonstrate the context loss problem"""
        print_header("THE CONTEXT LOSS PROBLEM", char="*")
        
        # Example document
        document = """
ACME Corporation Annual Report 2023

Financial Highlights:
ACME Corporation achieved record performance in 2023. The company's revenue 
grew by 15% compared to the previous year, reaching $2.5 billion. This growth 
was driven by strong demand in the technology sector.

TechStart Inc. Performance:
Meanwhile, TechStart Inc. faced challenges in 2023. The company's revenue 
declined by 8% due to supply chain disruptions. Management has implemented 
cost-cutting measures to improve profitability.

Global Industries Update:
Global Industries maintained steady performance. The company's revenue 
remained flat at $1.8 billion, but profit margins improved by 2 percentage 
points through operational efficiency gains.
        """.strip()
        
        logger.info("Consider this document:\n")
        logger.info("=" * 60)
        logger.info(document)
        logger.info("=" * 60)
        
        logger.info("\nNow imagine we chunk this document and get:\n")
        
        # Show problematic chunks
        chunks = [
            "The company's revenue grew by 15% compared to the previous year, reaching $2.5 billion.",
            "The company's revenue declined by 8% due to supply chain disruptions.",
            "The company's revenue remained flat at $1.8 billion, but profit margins improved."
        ]
        
        for i, chunk in enumerate(chunks, 1):
            logger.info(f"CHUNK {i}:")
            logger.info(f"  '{chunk}'")
            logger.info("")
        
        logger.info("❌ PROBLEM: All chunks say 'The company' but refer to different companies!")
        logger.info("❌ A search for 'company revenue growth' might return the wrong chunk!")
        logger.info("❌ Without context, we can't tell which company each chunk refers to!\n")
        
        input("\nPress Enter to continue...")
    
    def demo_solution(self):
        """Demonstrate the contextual retrieval solution"""
        print_header("THE CONTEXTUAL RETRIEVAL SOLUTION", char="*")
        
        logger.info("Contextual Retrieval solves this by adding context to each chunk:\n")
        
        # Show contextualized chunks
        contextual_chunks = [
            {
                "context": "This chunk is from ACME Corporation's 2023 annual report financial highlights section.",
                "text": "The company's revenue grew by 15% compared to the previous year, reaching $2.5 billion."
            },
            {
                "context": "This chunk discusses TechStart Inc.'s 2023 performance challenges.",
                "text": "The company's revenue declined by 8% due to supply chain disruptions."
            },
            {
                "context": "This chunk covers Global Industries' steady 2023 performance.",
                "text": "The company's revenue remained flat at $1.8 billion, but profit margins improved."
            }
        ]
        
        for i, chunk in enumerate(contextual_chunks, 1):
            logger.info(f"CONTEXTUAL CHUNK {i}:")
            logger.info(f"  Context: {chunk['context']}")
            logger.info(f"  Text: {chunk['text']}")
            logger.info(f"  Combined: {chunk['context']} {chunk['text']}\n")
        
        logger.info("✅ SOLUTION: Each chunk now has context!")
        logger.info("✅ Searching for 'ACME revenue growth' will correctly find chunk 1!")
        logger.info("✅ The context preserves crucial information lost in traditional chunking!\n")
        
        input("\nPress Enter to continue...")
    
    def demo_comparison(self):
        """Run a side-by-side comparison"""
        print_header("SIDE-BY-SIDE COMPARISON", char="*")
        
        # Create test document
        test_doc = """
Artificial Intelligence in Healthcare

Introduction:
Artificial intelligence is transforming healthcare delivery. Machine learning 
models are being used for disease diagnosis, drug discovery, and patient care 
optimization. The technology has shown remarkable results in early detection 
of diseases.

Diagnostic Applications:
In radiology, AI systems can detect cancer with 95% accuracy. The systems 
analyze medical images faster than human radiologists. This reduces diagnosis 
time from hours to minutes.

Drug Discovery:
Pharmaceutical companies use AI to identify potential drug compounds. The 
technology can predict drug interactions and side effects. This accelerates 
the drug development process by years.
        """.strip()
        
        logger.info("Test Document:")
        logger.info("=" * 60)
        logger.info(test_doc[:300] + "..." if len(test_doc) > 300 else test_doc)
        logger.info("=" * 60)
        
        # Initialize systems
        logger.info("\nInitializing systems...")
        
        # Create contextual system
        contextual_chunker = ContextualChunker(
            chunking_config=self.config.chunking,
            llm_config=self.config.llm,
            use_contextual=True
        )
        self.contextual_kb = ContextualKnowledgeBaseTools(
            config=self.config.knowledge_base,
            use_contextual=True
        )
        
        # Create non-contextual system  
        non_contextual_chunker = ContextualChunker(
            chunking_config=self.config.chunking,
            llm_config=self.config.llm,
            use_contextual=False
        )
        self.non_contextual_kb = ContextualKnowledgeBaseTools(
            config=self.config.knowledge_base,
            use_contextual=False
        )
        
        # Process document
        logger.info("\nProcessing document...")
        
        # Contextual chunks
        contextual_chunks = contextual_chunker.chunk_document(
            text=test_doc,
            doc_id="healthcare_ai"
        )
        self.contextual_kb.index_contextual_chunks(contextual_chunks)
        
        # Non-contextual chunks
        non_contextual_chunks = non_contextual_chunker.chunk_document(
            text=test_doc,
            doc_id="healthcare_ai"
        )
        self.non_contextual_kb.index_contextual_chunks(non_contextual_chunks)
        
        # Test queries
        test_queries = [
            "How accurate is the AI system?",
            "What technology reduces diagnosis time?",
            "What can the technology predict?"
        ]
        
        logger.info("\nRunning comparison...")
        
        for query in test_queries:
            print_section(f"Query: {query}")
            
            # Contextual search
            contextual_results = self.contextual_kb.contextual_search(
                query=query,
                method="hybrid",
                top_k=3
            )
            
            # Non-contextual search
            non_contextual_results = self.non_contextual_kb.contextual_search(
                query=query,
                method="hybrid",
                top_k=3
            )
            
            logger.info("CONTEXTUAL RESULTS:")
            if contextual_results:
                result = contextual_results[0]
                logger.info(f"  Score: {result.score:.4f}")
                logger.info(f"  Context: {result.context_text[:100]}..." if result.context_text else "  Context: None")
                logger.info(f"  Match: {result.text[:100]}...\n")
            else:
                logger.info("  No results found\n")
            
            logger.info("NON-CONTEXTUAL RESULTS:")
            if non_contextual_results:
                result = non_contextual_results[0]
                logger.info(f"  Score: {result.score:.4f}")
                logger.info(f"  Match: {result.text[:100]}...\n")
            else:
                logger.info("  No results found\n")
            
            # Score comparison
            if contextual_results and non_contextual_results:
                improvement = ((contextual_results[0].score - non_contextual_results[0].score) 
                             / non_contextual_results[0].score * 100)
                logger.info(f"📊 Score Improvement: {improvement:.1f}%\n")
        
        input("\nPress Enter to continue...")
    
    def demo_real_example(self):
        """Demonstrate with a real-world example"""
        print_header("REAL-WORLD EXAMPLE: FINANCIAL REPORT", char="*")
        
        # Create a realistic financial report
        report = """
Q2 2023 Earnings Report - TechCorp International

Executive Summary:
TechCorp International reported strong second quarter results for 2023, 
with revenue of $850 million, representing a 12% year-over-year growth. 
The company's cloud services division was the primary growth driver.

Revenue Breakdown:
Cloud Services: Revenue increased by 25% to $400 million, driven by 
enterprise adoption of our AI-powered analytics platform. Operating margin 
improved to 35% from 30% in the prior year.

Hardware Division: Revenue declined by 5% to $300 million due to supply 
chain constraints. However, the new product pipeline remains strong with 
three launches planned for Q3.

Software Licensing: Revenue grew by 8% to $150 million. The company added 
200 new enterprise customers during the quarter, bringing the total to 
5,000 active licenses.

Competitive Analysis:
Compared to DataSoft Corp, our main competitor, we maintained market share 
leadership. DataSoft reported 8% revenue growth in their latest quarter, 
while our 12% growth demonstrates strong execution. Their cloud division 
grew 15% compared to our 25% growth.

Future Outlook:
Management expects continued momentum in Q3 2023. The company raised 
full-year guidance to $3.5 billion in revenue, representing 15% annual 
growth. Investment in R&D will increase by 20% to accelerate AI 
product development.
        """.strip()
        
        logger.info("Processing a realistic financial report...")
        logger.info("=" * 60)
        logger.info(report[:400] + "..." if len(report) > 400 else report)
        logger.info("=" * 60)
        
        # Process with contextual system
        logger.info("\nGenerating contextual chunks (this may take a moment)...\n")
        
        chunker = ContextualChunker(
            chunking_config=self.config.chunking,
            llm_config=self.config.llm,
            use_contextual=True
        )
        
        chunks = chunker.chunk_document(
            text=report,
            doc_id="techcorp_q2_2023"
        )
        
        # Show examples of contextualized chunks
        logger.info("Example Contextual Chunks:\n")
        
        for chunk in chunks[:3]:
            logger.info(f"Original: {chunk.text[:100]}...")
            logger.info(f"Context: {chunk.context}")
            logger.info("")
        
        # Show how this helps with ambiguous queries
        logger.info("Why this matters:\n")
        logger.info("Query: 'What was the revenue growth?'")
        logger.info("  - Without context: Could match TechCorp's 12%, Cloud's 25%, or Software's 8%")
        logger.info("  - With context: Correctly identifies which growth figure you want\n")
        
        logger.info("Query: 'How did the company perform vs competition?'")
        logger.info("  - Without context: Might return DataSoft's results")
        logger.info("  - With context: Returns TechCorp's performance comparison\n")
        
        input("\nPress Enter to continue...")
    
    def show_statistics(self):
        """Show performance statistics"""
        print_header("PERFORMANCE STATISTICS", char="*")
        
        if not self.contextual_kb:
            logger.info("No searches performed yet. Run a comparison first!\n")
            input("\nPress Enter to continue...")
            return
        
        # Get statistics
        stats = self.contextual_kb.get_statistics()
        
        logger.info("Search Statistics:")
        logger.info(f"  Total searches: {stats['search_stats']['total_searches']}")
        logger.info(f"  Average retrieval time: {stats['search_stats']['avg_retrieval_time']:.3f}s")
        logger.info(f"  Contextual searches: {stats['search_stats']['contextual_searches']}")
        logger.info(f"  Non-contextual searches: {stats['search_stats']['non_contextual_searches']}")
        
        logger.info("\nIndex Statistics:")
        logger.info(f"  Contextual chunks indexed: {stats['index_stats']['contextual_chunks']}")
        logger.info(f"  Non-contextual chunks indexed: {stats['index_stats']['non_contextual_chunks']}")
        
        logger.info("\nBased on Anthropic's Research:")
        logger.info("  Standard RAG: 5.7% retrieval failure rate")
        logger.info("  Contextual RAG: 2.9% failure rate (49% improvement)")
        logger.info("  + Reranking: 1.9% failure rate (67% improvement)")
        
        input("\nPress Enter to continue...")


def main():
    """Run the interactive demo"""
    demo = ContextualRetrievalDemo()
    demo.run()


if __name__ == "__main__":
    main()
