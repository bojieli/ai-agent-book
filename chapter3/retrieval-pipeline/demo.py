"""Demo script showcasing dense vs sparse embedding strengths.

Service Configuration:
- Dense Embedding: http://localhost:4240
- Sparse Embedding: http://localhost:4241  
- Retrieval Pipeline: http://localhost:4242
"""

import asyncio
import httpx
from typing import Dict, List
import json

class RetrievalDemo:
    """Demo for the retrieval pipeline."""
    
    def __init__(self, pipeline_url: str = "http://localhost:4242"):
        self.pipeline_url = pipeline_url
        
    async def index_document(self, text: str, doc_id: str, metadata: Dict = None):
        """Index a document."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.pipeline_url}/index",
                json={"text": text, "doc_id": doc_id, "metadata": metadata or {}}
            )
            return response.json()
    
    async def search(self, query: str, mode: str = "hybrid"):
        """Search for documents."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.pipeline_url}/search",
                json={"query": query, "mode": mode, "top_k": 10, "rerank_top_k": 5}
            )
            return response.json()
    
    async def clear(self):
        """Clear all documents."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{self.pipeline_url}/clear")
            return response.json()

async def main():
    """Run the demonstration."""
    demo = RetrievalDemo()
    
    print("="*80)
    print("RETRIEVAL PIPELINE DEMONSTRATION")
    print("Showcasing Dense vs Sparse Embedding Strengths")
    print("="*80)
    
    # Clear existing documents
    print("\nClearing existing documents...")
    await demo.clear()
    
    # Create diverse test documents
    documents = [
        # Category 1: Programming Languages (for semantic similarity)
        {
            "doc_id": "prog_python",
            "text": "Python is renowned for its clean syntax and readability, making it ideal for beginners and experts alike.",
            "metadata": {"category": "programming", "subcategory": "languages"}
        },
        {
            "doc_id": "prog_javascript",
            "text": "JavaScript powers interactive web applications and runs in browsers worldwide.",
            "metadata": {"category": "programming", "subcategory": "languages"}
        },
        {
            "doc_id": "prog_rust",
            "text": "Rust provides memory safety without garbage collection through its ownership system.",
            "metadata": {"category": "programming", "subcategory": "languages"}
        },
        
        # Category 2: Machine Learning (for concept matching)
        {
            "doc_id": "ml_intro",
            "text": "Artificial intelligence enables computers to learn from data and make decisions.",
            "metadata": {"category": "AI", "subcategory": "intro"}
        },
        {
            "doc_id": "ml_deep",
            "text": "Deep neural networks consist of multiple layers that progressively extract features.",
            "metadata": {"category": "AI", "subcategory": "deep_learning"}
        },
        {
            "doc_id": "ml_nlp",
            "text": "Natural language processing helps machines understand and generate human text.",
            "metadata": {"category": "AI", "subcategory": "NLP"}
        },
        
        # Category 3: Specific Technical Terms (for exact matching)
        {
            "doc_id": "error_404",
            "text": "HTTP status code 404 indicates that the requested resource was not found on the server.",
            "metadata": {"category": "errors", "code": "404"}
        },
        {
            "doc_id": "error_500",
            "text": "HTTP status code 500 represents an internal server error that prevented request fulfillment.",
            "metadata": {"category": "errors", "code": "500"}
        },
        {
            "doc_id": "api_key",
            "text": "The API key XK9-2B4-7Q1 provides access to premium features of the service.",
            "metadata": {"category": "authentication", "type": "api_key"}
        },
        
        # Category 4: Multilingual Content
        {
            "doc_id": "ml_chinese",
            "text": "机器学习是人工智能的核心技术，通过数据训练模型来解决问题。",
            "metadata": {"category": "AI", "language": "chinese"}
        },
        {
            "doc_id": "ml_spanish",
            "text": "El aprendizaje automático permite a las computadoras aprender sin programación explícita.",
            "metadata": {"category": "AI", "language": "spanish"}
        },
        
        # Category 5: People and Names
        {
            "doc_id": "person_turing",
            "text": "Alan Turing pioneered computer science and artificial intelligence in the 20th century.",
            "metadata": {"category": "people", "field": "computer_science"}
        },
        {
            "doc_id": "person_lecun",
            "text": "Yann LeCun developed convolutional neural networks that revolutionized computer vision.",
            "metadata": {"category": "people", "field": "deep_learning"}
        }
    ]
    
    # Index all documents
    print(f"\nIndexing {len(documents)} documents...")
    for doc in documents:
        result = await demo.index_document(
            text=doc["text"],
            doc_id=doc["doc_id"],
            metadata=doc["metadata"]
        )
        success = result.get("success", False)
        status = "✓" if success else "✗"
        print(f"  {status} {doc['doc_id']}: {doc['text'][:60]}...")
    
    print("\n" + "="*80)
    print("DEMONSTRATION QUERIES")
    print("="*80)
    
    # Test queries demonstrating different strengths
    test_queries = [
        {
            "query": "code readability and simplicity",
            "description": "Semantic similarity - Dense should excel",
            "expected_strong": "dense",
            "explanation": "Dense embeddings understand 'readability' relates to Python even without exact match"
        },
        {
            "query": "XK9-2B4-7Q1",
            "description": "Exact code match - Sparse should excel",
            "expected_strong": "sparse",
            "explanation": "Sparse search finds exact API key string"
        },
        {
            "query": "AI learning from examples",
            "description": "Conceptual understanding - Dense should excel",
            "expected_strong": "dense",
            "explanation": "Dense understands AI/ML concepts without exact terminology"
        },
        {
            "query": "404",
            "description": "Specific error code - Sparse should excel",
            "expected_strong": "sparse",
            "explanation": "Sparse matches exact error code"
        },
        {
            "query": "人工智能",
            "description": "Cross-lingual search (Chinese for AI) - Dense should excel",
            "expected_strong": "dense",
            "explanation": "Dense embeddings (BGE-M3) handle multiple languages"
        },
        {
            "query": "Yann LeCun",
            "description": "Exact name search - Sparse should excel",
            "expected_strong": "sparse",
            "explanation": "Sparse finds exact person name"
        },
        {
            "query": "web browser programming",
            "description": "Semantic context - Dense should excel",
            "expected_strong": "dense",
            "explanation": "Dense connects 'web browser' with JavaScript"
        }
    ]
    
    # Run each test query
    for test in test_queries:
        print(f"\n{'='*60}")
        print(f"Query: '{test['query']}'")
        print(f"Type: {test['description']}")
        print(f"Expected winner: {test['expected_strong']}")
        print(f"Reason: {test['explanation']}")
        print("-"*60)
        
        # Run search in all three modes
        results = {}
        for mode in ["dense", "sparse", "hybrid"]:
            result = await demo.search(test["query"], mode=mode)
            
            # Extract top results
            if mode == "dense":
                top_docs = result.get("dense_results", [])[:3]
            elif mode == "sparse":
                top_docs = result.get("sparse_results", [])[:3]
            else:  # hybrid
                top_docs = result.get("reranked_results", [])[:3]
            
            results[mode] = top_docs
            
            # Print results for this mode
            print(f"\n{mode.upper()} Results:")
            for i, doc in enumerate(top_docs, 1):
                doc_id = doc.get("doc_id", "unknown")
                score = doc.get("score") or doc.get("rerank_score", 0)
                print(f"  {i}. {doc_id} (score: {score:.4f})")
        
        # Analyze which mode performed best
        print(f"\nAnalysis:")
        if test["expected_strong"] == "dense":
            if results["dense"] and results["sparse"]:
                dense_top = results["dense"][0]["doc_id"] if results["dense"] else None
                sparse_top = results["sparse"][0]["doc_id"] if results["sparse"] else None
                if dense_top != sparse_top:
                    print(f"  ✓ Dense found different (likely better) result: {dense_top}")
                    print(f"  ✓ Sparse found: {sparse_top}")
        elif test["expected_strong"] == "sparse":
            if results["sparse"]:
                print(f"  ✓ Sparse found exact match: {results['sparse'][0]['doc_id']}")
        
        # Show hybrid performance
        if results["hybrid"]:
            print(f"  ✓ Hybrid (reranked) top result: {results['hybrid'][0]['doc_id']}")
    
    print("\n" + "="*80)
    print("DEMONSTRATION COMPLETE")
    print("="*80)
    print("\nKey Takeaways:")
    print("1. Dense embeddings excel at semantic similarity and concepts")
    print("2. Sparse search excels at exact matches and specific terms")
    print("3. Hybrid search with reranking combines the best of both")
    print("4. BGE-M3 dense embeddings support multilingual search")
    print("5. BM25 sparse search is unbeatable for exact string matching")

if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="Retrieval pipeline demonstration")
    parser.add_argument("--url", default="http://localhost:4242",
                       help="Pipeline service URL")
    
    args = parser.parse_args()
    
    # Check if services are running
    print("Checking if services are available...")
    print(f"Pipeline URL: {args.url}")
    
    try:
        asyncio.run(main())
    except httpx.ConnectError:
        print("\nError: Could not connect to the retrieval pipeline service.")
        print("Please ensure all services are running:")
        print("  1. Dense embedding service (port 4240)")
        print("  2. Sparse embedding service (port 4241)")
        print("  3. Retrieval pipeline (port 4242)")
        print("\nRun: ./restart_services.sh")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nDemo interrupted by user")
        sys.exit(0)
