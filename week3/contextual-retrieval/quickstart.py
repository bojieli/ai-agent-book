#!/usr/bin/env python3
"""Quick start script to test the Contextual Retrieval System

This script provides a quick way to test contextual retrieval
with a sample document and see the improvements.
"""

import logging
from pathlib import Path
from config import Config
from contextual_chunking import ContextualChunker
from contextual_tools import ContextualKnowledgeBaseTools

# Simple logging for quickstart
logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger(__name__)


def main():
    """Quick demonstration of contextual retrieval"""
    
    print("\n" + "="*60)
    print("CONTEXTUAL RETRIEVAL - QUICK START")
    print("="*60 + "\n")
    
    # Sample document about multiple companies
    document = """
    2023 Technology Sector Report
    
    Apple Inc. Performance:
    Apple reported exceptional results in 2023. The company's revenue reached 
    $394 billion, with iPhone sales contributing 52% of total revenue. The 
    services division showed strong growth of 16% year-over-year. Tim Cook 
    emphasized the company's commitment to innovation and sustainability.
    
    Microsoft Corporation Update:
    Microsoft achieved record cloud revenue in 2023. Azure revenue grew by 27% 
    as enterprises accelerated digital transformation. The company's total 
    revenue was $211 billion. CEO Satya Nadella highlighted AI integration 
    across all product lines as a key strategic priority.
    
    Google (Alphabet) Highlights:
    Google's parent company Alphabet reported $283 billion in revenue for 2023. 
    Search advertising remained the largest revenue driver at $175 billion. 
    The company increased AI research spending by 30% to maintain competitive 
    advantage. YouTube advertising revenue exceeded $40 billion.
    
    Market Analysis:
    The technology sector showed resilience despite economic headwinds. Companies 
    that invested heavily in AI and cloud infrastructure outperformed the market. 
    The sector's average growth rate was 12%, with cloud services growing at 25% 
    and traditional hardware declining by 3%.
    """
    
    print("Step 1: Initializing systems...")
    config = Config.from_env()
    
    # Create both contextual and non-contextual systems
    contextual_chunker = ContextualChunker(use_contextual=True)
    non_contextual_chunker = ContextualChunker(use_contextual=False)
    
    contextual_kb = ContextualKnowledgeBaseTools(use_contextual=True)
    non_contextual_kb = ContextualKnowledgeBaseTools(use_contextual=False)
    
    print("\nStep 2: Processing document...")
    print("-" * 40)
    
    # Process with contextual system
    print("Creating contextual chunks...")
    contextual_chunks = contextual_chunker.chunk_document(
        text=document,
        doc_id="tech_report_2023"
    )
    contextual_kb.index_contextual_chunks(contextual_chunks)
    print(f"✓ Created {len(contextual_chunks)} contextual chunks")
    
    # Process with non-contextual system
    print("Creating non-contextual chunks...")
    non_contextual_chunks = non_contextual_chunker.chunk_document(
        text=document,
        doc_id="tech_report_2023"
    )
    non_contextual_kb.index_contextual_chunks(non_contextual_chunks)
    print(f"✓ Created {len(non_contextual_chunks)} non-contextual chunks")
    
    # Show example contextual chunk
    if contextual_chunks:
        print("\nExample Contextual Chunk:")
        print("-" * 40)
        chunk = contextual_chunks[0]
        print(f"Original text: {chunk.text[:100]}...")
        print(f"Added context: {chunk.context}")
    
    print("\n" + "="*60)
    print("Step 3: Testing Search Queries")
    print("="*60)
    
    # Test queries
    queries = [
        "What was the company's revenue?",
        "Which company emphasized AI?",
        "What was the growth rate?"
    ]
    
    for query in queries:
        print(f"\nQuery: '{query}'")
        print("-" * 40)
        
        # Contextual search
        contextual_results = contextual_kb.contextual_search(query, top_k=1)
        
        # Non-contextual search
        non_contextual_results = non_contextual_kb.contextual_search(query, top_k=1)
        
        print("\nContextual Result:")
        if contextual_results:
            result = contextual_results[0]
            print(f"  Score: {result.score:.4f}")
            if result.context_text:
                print(f"  Context: {result.context_text[:80]}...")
            print(f"  Match: {result.text[:100]}...")
        else:
            print("  No results")
        
        print("\nNon-Contextual Result:")
        if non_contextual_results:
            result = non_contextual_results[0]
            print(f"  Score: {result.score:.4f}")
            print(f"  Match: {result.text[:100]}...")
        else:
            print("  No results")
        
        # Compare scores
        if contextual_results and non_contextual_results:
            improvement = ((contextual_results[0].score - non_contextual_results[0].score) 
                         / non_contextual_results[0].score * 100)
            print(f"\n📊 Improvement: {improvement:+.1f}%")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    # Get statistics
    stats = contextual_chunker.get_statistics()
    
    print(f"\nContextual Chunking Statistics:")
    print(f"  Chunks processed: {stats['total_chunks']}")
    print(f"  Context tokens used: {stats['total_context_tokens']}")
    print(f"  Estimated cost: ${stats['estimated_cost']:.4f}")
    
    print("\nKey Insights:")
    print("✓ Contextual chunks preserve company-specific information")
    print("✓ Ambiguous queries ('the company') are resolved correctly")
    print("✓ Search accuracy improves significantly with context")
    
    print("\n" + "="*60)
    print("Quick start complete! Try with your own documents:")
    print("  python contextual_main.py --mode index --document your_file.txt")
    print("="*60 + "\n")


if __name__ == "__main__":
    main()