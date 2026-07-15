#!/usr/bin/env python3
"""Quick demo script to showcase the vector similarity search service."""

import time
import sys


def print_section(title):
    """Print a formatted section header."""
    print("\n" + "=" * 60)
    print(f"  {title}")
    print("=" * 60)


def main():
    """Run a quick demo of the service."""
    
    print_section("Vector Similarity Search - Quick Demo")
    
    print("""
This educational service demonstrates vector similarity search
using BGE-M3 embeddings with ANNOY/HNSW indexing.

EDUCATIONAL CONCEPTS DEMONSTRATED:
1. Text → Vector embedding generation
2. Approximate nearest neighbor search  
3. Cosine similarity for semantic matching
4. Trade-offs between index types (ANNOY vs HNSW)
    """)
    
    print("\n📚 STEP 1: Start the service")
    print("-" * 40)
    print("\nOption A - Using HNSW (high precision):")
    print("  python main.py --index-type hnsw --debug")
    
    print("\nOption B - Using ANNOY (fast, memory-efficient):")
    print("  python main.py --index-type annoy --debug")
    
    print("\nOption C - Using the startup script:")
    print("  ./start_service.sh hnsw 8000 true")
    
    print("\n📝 STEP 2: Index some documents")
    print("-" * 40)
    print("""
Example using curl:

curl -X POST http://localhost:8000/index \\
  -H "Content-Type: application/json" \\
  -d '{
    "text": "Machine learning is a subset of AI that enables systems to learn from data.",
    "metadata": {"category": "AI", "level": "beginner"}
  }'
    """)
    
    print("\n🔍 STEP 3: Search for similar documents")
    print("-" * 40)
    print("""
Example search:

curl -X POST http://localhost:8000/search \\
  -H "Content-Type: application/json" \\
  -d '{
    "query": "What is deep learning?",
    "top_k": 5
  }'
    """)
    
    print("\n🎯 STEP 4: Run the test client")
    print("-" * 40)
    print("""
The test client will:
- Index 10 sample documents about AI, programming, and DevOps
- Perform 5 different similarity searches
- Demonstrate document deletion
- Show performance metrics

Run it with:
  python test_client.py

For performance testing (100 documents):
  python test_client.py --performance
    """)
    
    print("\n📊 KEY LEARNING POINTS")
    print("-" * 40)
    print("""
1. EMBEDDINGS: BGE-M3 converts text → 1024-dimensional vectors
   - Semantic meaning is captured in vector space
   - Similar texts have similar vectors

2. INDEXING: Two algorithms for efficient similarity search
   - ANNOY: Tree-based, fast but approximate
   - HNSW: Graph-based, slower but more accurate

3. SIMILARITY: Cosine distance measures semantic similarity
   - Score close to 1.0 = very similar
   - Score close to 0.0 = not similar

4. TRADE-OFFS:
   - Speed vs Accuracy (ANNOY vs HNSW)
   - Memory vs Performance (index parameters)
   - Build time vs Search time
    """)
    
    print("\n🔗 USEFUL ENDPOINTS")
    print("-" * 40)
    print("""
- API Documentation: http://localhost:8000/docs
- Service Status: http://localhost:8000/
- Statistics: http://localhost:8000/stats
- List Documents: http://localhost:8000/documents
    """)
    
    print("\n💡 EXPERIMENT IDEAS")
    print("-" * 40)
    print("""
1. Compare ANNOY vs HNSW accuracy on same queries
2. Measure indexing time for different document sizes
3. Test multilingual search (BGE-M3 supports 100+ languages)
4. Analyze how different parameters affect performance
5. Try searching with synonyms and paraphrases
    """)
    
    print_section("Ready to Start!")
    print("\nNext steps:")
    print("1. Start the service: python main.py --debug")
    print("2. Run the demo: python test_client.py")
    print("3. Explore the API: http://localhost:8000/docs")
    print()


if __name__ == "__main__":
    main()
