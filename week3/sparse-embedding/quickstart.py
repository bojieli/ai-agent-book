#!/usr/bin/env python3
"""
Quick start script for the Educational Sparse Vector Search Engine
Demonstrates basic usage in a simple, interactive way
"""

import logging
from bm25_engine import SparseSearchEngine

# Configure logging to show educational information
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s'
)
logger = logging.getLogger(__name__)


def main():
    print("\n" + "="*60)
    print(" Educational Sparse Vector Search Engine - Quick Start")
    print("="*60)
    print("\nThis demo shows the core functionality of BM25 search.\n")
    
    # Initialize the search engine
    print("Initializing search engine...")
    engine = SparseSearchEngine()
    
    # Sample documents about different programming topics
    documents = [
        {
            "text": "Python is a versatile programming language widely used for web development, data science, machine learning, and automation. Its simple syntax makes it ideal for beginners.",
            "title": "Python Overview"
        },
        {
            "text": "JavaScript powers the interactive web. It runs in browsers and on servers with Node.js. Modern JavaScript includes features like async/await, arrow functions, and destructuring.",
            "title": "JavaScript Essentials"
        },
        {
            "text": "Machine learning algorithms enable computers to learn from data. Popular algorithms include linear regression, decision trees, neural networks, and support vector machines.",
            "title": "ML Algorithms"
        },
        {
            "text": "Web development involves HTML for structure, CSS for styling, and JavaScript for interactivity. Modern frameworks like React, Vue, and Angular simplify complex applications.",
            "title": "Web Development"
        },
        {
            "text": "Data structures organize information efficiently. Arrays provide fast access, linked lists enable dynamic sizing, trees support hierarchical data, and hash tables offer constant-time lookups.",
            "title": "Data Structures"
        },
        {
            "text": "Databases store and manage data persistently. SQL databases like PostgreSQL use structured tables, while NoSQL databases like MongoDB store flexible documents.",
            "title": "Database Systems"
        },
        {
            "text": "Cloud computing provides scalable infrastructure on demand. AWS, Google Cloud, and Azure offer services for compute, storage, networking, and machine learning.",
            "title": "Cloud Computing"
        },
        {
            "text": "Software testing ensures code quality. Unit tests verify individual functions, integration tests check component interactions, and end-to-end tests validate entire workflows.",
            "title": "Software Testing"
        },
        {
            "text": "Version control systems track code changes over time. Git is the most popular system, enabling collaboration through branches, commits, and pull requests.",
            "title": "Version Control"
        },
        {
            "text": "APIs (Application Programming Interfaces) enable communication between software systems. REST APIs use HTTP methods, while GraphQL provides flexible data querying.",
            "title": "APIs and Integration"
        }
    ]
    
    # Index documents
    print(f"\nIndexing {len(documents)} documents...")
    print("-" * 40)
    
    for i, doc in enumerate(documents):
        doc_id = engine.index_document(doc["text"], {"title": doc["title"]})
        print(f"  [{doc_id}] {doc['title']}")
    
    print(f"\n✓ Indexed {len(documents)} documents successfully!")
    
    # Show index statistics
    stats = engine.index.get_statistics()
    print(f"\nIndex Statistics:")
    print(f"  • Total documents: {stats['total_documents']}")
    print(f"  • Unique terms: {stats['unique_terms']}")
    print(f"  • Average document length: {stats['average_document_length']:.1f} terms")
    
    # Demonstrate searches
    print("\n" + "="*60)
    print(" Demonstration Searches")
    print("="*60)
    
    queries = [
        "machine learning algorithms",
        "web development JavaScript",
        "database SQL NoSQL",
        "cloud computing AWS",
        "Python programming"
    ]
    
    for query in queries:
        print(f"\n🔍 Query: '{query}'")
        print("-" * 40)
        
        results = engine.search(query, top_k=3)
        
        if results:
            for rank, result in enumerate(results, 1):
                title = result['metadata'].get('title', 'Unknown')
                score = result['score']
                matched = result['debug']['matched_terms']
                
                print(f"\n  #{rank} {title} (Score: {score:.3f})")
                print(f"     Matched terms: {', '.join(matched)}")
                print(f"     Preview: {result['text'][:100]}...")
        else:
            print("  No results found")
    
    # Interactive search
    print("\n" + "="*60)
    print(" Interactive Search")
    print("="*60)
    print("\nNow you can try your own searches!")
    print("Type 'quit' to exit, 'stats' for statistics, or enter a search query.\n")
    
    while True:
        try:
            query = input("Enter search query: ").strip()
            
            if query.lower() == 'quit':
                print("\nThank you for using the Educational Sparse Vector Search Engine!")
                break
            
            if query.lower() == 'stats':
                stats = engine.index.get_statistics()
                print(f"\nCurrent Index Statistics:")
                print(f"  • Documents: {stats['total_documents']}")
                print(f"  • Unique terms: {stats['unique_terms']}")
                print(f"  • Total terms: {stats['total_terms']}")
                print(f"  • Top terms: {', '.join([t[0] for t in stats['terms_by_frequency'][:5]])}")
                print()
                continue
            
            if not query:
                continue
            
            # Perform search
            results = engine.search(query, top_k=5)
            
            if results:
                print(f"\nFound {len(results)} results for '{query}':\n")
                for rank, result in enumerate(results, 1):
                    title = result['metadata'].get('title', 'Unknown')
                    score = result['score']
                    matched = result['debug']['matched_terms']
                    
                    print(f"  #{rank} {title}")
                    print(f"     Score: {score:.4f}")
                    print(f"     Matched: {', '.join(matched) if matched else 'None'}")
                    print(f"     Text: {result['text'][:150]}...")
                    print()
            else:
                print(f"\nNo results found for '{query}'")
                print("Try different keywords or check your spelling.\n")
                
        except KeyboardInterrupt:
            print("\n\nExiting...")
            break
        except Exception as e:
            print(f"Error: {e}")
            continue
    
    print("\n" + "="*60)
    print("\nTo learn more:")
    print("  • Run 'python test_engine.py' to see comprehensive tests")
    print("  • Run 'python server.py' to start the HTTP API server")
    print("  • Run 'python demo.py' for a full demonstration")
    print("  • Check the README.md for detailed documentation")
    print("\n" + "="*60)


if __name__ == "__main__":
    main()
