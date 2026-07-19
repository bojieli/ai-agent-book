"""Test client with educational test cases for dense vs sparse retrieval."""

import asyncio
import httpx
import json
from typing import List, Dict, Any
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class TestClient:
    """Test client for the retrieval pipeline."""
    
    def __init__(self, base_url: str = "http://localhost:4242"):
        self.base_url = base_url.rstrip('/')
        self.test_results = []
    
    async def index_document(self, text: str, doc_id: str = None, metadata: Dict = None) -> Dict:
        """Index a document."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/index",
                json={"text": text, "doc_id": doc_id, "metadata": metadata or {}}
            )
            return response.json()
    
    async def search(self, query: str, mode: str = "hybrid", top_k: int = 20, rerank_top_k: int = 10) -> Dict:
        """Search for documents."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.post(
                f"{self.base_url}/search",
                json={
                    "query": query,
                    "mode": mode,
                    "top_k": top_k,
                    "rerank_top_k": rerank_top_k
                }
            )
            return response.json()
    
    async def clear_documents(self) -> Dict:
        """Clear all documents."""
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.delete(f"{self.base_url}/clear")
            return response.json()
    
    def print_results(self, results: Dict, title: str = "Search Results"):
        """Pretty print search results."""
        print(f"\n{'='*80}")
        print(f"{title}")
        print(f"{'='*80}")
        print(f"Query: {results.get('query', 'N/A')}")
        print(f"Mode: {results.get('mode', 'N/A')}")
        print(f"Times: Retrieval={results.get('retrieval_time_ms', 0):.1f}ms, "
              f"Rerank={results.get('rerank_time_ms', 0):.1f}ms, "
              f"Total={results.get('total_time_ms', 0):.1f}ms")
        
        # Show top dense results
        if results.get('dense_results'):
            print(f"\nTop Dense Results:")
            for r in results['dense_results'][:5]:
                print(f"  #{r['rank']}: {r['doc_id']} (score: {r['score']:.4f})")
        
        # Show top sparse results
        if results.get('sparse_results'):
            print(f"\nTop Sparse Results:")
            for r in results['sparse_results'][:5]:
                matched = r.get('matched_terms', [])
                print(f"  #{r['rank']}: {r['doc_id']} (score: {r['score']:.4f}, matched: {matched})")
        
        # Show reranked results
        if results.get('reranked_results'):
            print(f"\nReranked Results:")
            for r in results['reranked_results'][:5]:
                changes = r.get('rank_changes', [])
                print(f"  #{r['rank']}: {r['doc_id']} (score: {r['rerank_score']:.4f})")
                if changes:
                    print(f"    Rank changes: {', '.join(changes)}")
        
        # Show statistics
        if results.get('statistics'):
            stats = results['statistics']
            print(f"\nStatistics:")
            print(f"  Dense retrieved: {stats.get('dense_retrieved', 0)}")
            print(f"  Sparse retrieved: {stats.get('sparse_retrieved', 0)}")
            print(f"  Overlap: {stats.get('overlap_count', 0)} ({stats.get('overlap_percentage', 0):.1f}%)")
    
    async def run_test_case(self, name: str, documents: List[Dict], queries: List[Dict]) -> Dict:
        """Run a complete test case."""
        print(f"\n{'='*80}")
        print(f"TEST CASE: {name}")
        print(f"{'='*80}")
        
        test_result = {
            "name": name,
            "timestamp": datetime.now().isoformat(),
            "documents": len(documents),
            "queries": len(queries),
            "results": []
        }
        
        # Index documents
        print(f"\nIndexing {len(documents)} documents...")
        for doc in documents:
            result = await self.index_document(
                text=doc["text"],
                doc_id=doc.get("doc_id"),
                metadata=doc.get("metadata", {})
            )
            print(f"  Indexed: {doc.get('doc_id', 'auto')} - {doc['text'][:50]}...")
        
        # Run queries
        print(f"\nRunning {len(queries)} queries...")
        for query_spec in queries:
            query = query_spec["query"]
            expected = query_spec.get("expected", [])
            explanation = query_spec.get("explanation", "")
            
            print(f"\nQuery: '{query}'")
            if explanation:
                print(f"Explanation: {explanation}")
            if expected:
                print(f"Expected top results: {expected}")
            
            # Test all modes
            for mode in ["dense", "sparse", "hybrid"]:
                print(f"\n--- Mode: {mode} ---")
                result = await self.search(query, mode=mode, top_k=10, rerank_top_k=5)
                
                # Extract top results
                top_results = []
                if mode == "hybrid" and result.get("reranked_results"):
                    top_results = [r["doc_id"] for r in result["reranked_results"][:3]]
                elif mode == "dense" and result.get("dense_results"):
                    top_results = [r["doc_id"] for r in result["dense_results"][:3]]
                elif mode == "sparse" and result.get("sparse_results"):
                    top_results = [r["doc_id"] for r in result["sparse_results"][:3]]
                
                print(f"Top 3: {top_results}")
                
                # Check if expected results are in top positions
                if expected:
                    matches = [doc_id in top_results for doc_id in expected]
                    accuracy = sum(matches) / len(expected) * 100
                    print(f"Accuracy: {accuracy:.0f}% ({sum(matches)}/{len(expected)} expected found)")
                
                test_result["results"].append({
                    "query": query,
                    "mode": mode,
                    "top_results": top_results,
                    "expected": expected,
                    "time_ms": result.get("total_time_ms", 0)
                })
        
        self.test_results.append(test_result)
        return test_result

# Test cases demonstrating dense vs sparse strengths
async def run_educational_tests():
    """Run educational test cases."""
    client = TestClient()
    
    # Clear existing documents
    await client.clear_documents()
    
    # Test Case 1: Semantic Similarity (Dense is better)
    semantic_docs = [
        {
            "doc_id": "cat_1",
            "text": "The feline jumped onto the couch and purred contentedly.",
            "metadata": {"category": "animals", "type": "behavior"}
        },
        {
            "doc_id": "cat_2", 
            "text": "A tabby cat sleeps on the windowsill in the afternoon sun.",
            "metadata": {"category": "animals", "type": "description"}
        },
        {
            "doc_id": "dog_1",
            "text": "The puppy barked excitedly and wagged its tail.",
            "metadata": {"category": "animals", "type": "behavior"}
        },
        {
            "doc_id": "car_1",
            "text": "The vehicle accelerated down the highway.",
            "metadata": {"category": "transportation", "type": "action"}
        }
    ]
    
    semantic_queries = [
        {
            "query": "kitty behavior",  # Uses different words but same concept
            "expected": ["cat_1", "cat_2"],
            "explanation": "Dense should find cat documents despite using 'kitty' instead of 'cat/feline'"
        },
        {
            "query": "automobile speed",  # Semantic similarity to car/vehicle
            "expected": ["car_1"],
            "explanation": "Dense should match 'automobile' to 'vehicle' and 'speed' to 'accelerated'"
        }
    ]
    
    await client.run_test_case(
        "Semantic Similarity (Dense Advantage)",
        semantic_docs,
        semantic_queries
    )
    
    # Test Case 2: Exact Terms and Names (Sparse is better)
    exact_docs = [
        {
            "doc_id": "person_1",
            "text": "Dr. Alexander Humphrey published groundbreaking research on quantum computing.",
            "metadata": {"type": "person", "field": "science"}
        },
        {
            "doc_id": "person_2",
            "text": "Professor Smith teaches computer science at the university.",
            "metadata": {"type": "person", "field": "education"}
        },
        {
            "doc_id": "company_1",
            "text": "XR-7000 is a new model released by TechCorp Industries.",
            "metadata": {"type": "product", "company": "TechCorp"}
        },
        {
            "doc_id": "company_2",
            "text": "The latest smartphone features advanced technology.",
            "metadata": {"type": "product", "category": "electronics"}
        }
    ]
    
    exact_queries = [
        {
            "query": "Alexander Humphrey",  # Exact name match
            "expected": ["person_1"],
            "explanation": "Sparse should excel at finding exact name 'Alexander Humphrey'"
        },
        {
            "query": "XR-7000",  # Specific product code
            "expected": ["company_1"],
            "explanation": "Sparse should find exact product code 'XR-7000'"
        }
    ]
    
    await client.run_test_case(
        "Exact Terms and Names (Sparse Advantage)",
        exact_docs,
        exact_queries
    )
    
    # Test Case 3: Multilingual (Dense is better)
    multilingual_docs = [
        {
            "doc_id": "ml_en_1",
            "text": "Machine learning is a subset of artificial intelligence.",
            "metadata": {"language": "english", "topic": "AI"}
        },
        {
            "doc_id": "ml_zh_1",
            "text": "机器学习是人工智能的一个子集。",  # Same content in Chinese
            "metadata": {"language": "chinese", "topic": "AI"}
        },
        {
            "doc_id": "ml_es_1",
            "text": "El aprendizaje automático es un subconjunto de la inteligencia artificial.",  # Spanish
            "metadata": {"language": "spanish", "topic": "AI"}
        },
        {
            "doc_id": "other_1",
            "text": "Database systems store and retrieve information efficiently.",
            "metadata": {"language": "english", "topic": "database"}
        }
    ]
    
    multilingual_queries = [
        {
            "query": "AI learning",  # English query
            "expected": ["ml_en_1", "ml_zh_1", "ml_es_1"],
            "explanation": "Dense embeddings (BGE-M3) should find similar content across languages"
        },
        {
            "query": "人工智能",  # Chinese query for "artificial intelligence"
            "expected": ["ml_zh_1", "ml_en_1"],
            "explanation": "Dense should match Chinese query to related documents in any language"
        }
    ]
    
    await client.run_test_case(
        "Multilingual Matching (Dense Advantage)",
        multilingual_docs,
        multilingual_queries
    )
    
    # Test Case 4: Technical Terms and Codes (Sparse is better)
    technical_docs = [
        {
            "doc_id": "error_1",
            "text": "Error code HTTP-403 indicates forbidden access to the resource.",
            "metadata": {"type": "error", "category": "http"}
        },
        {
            "doc_id": "error_2",
            "text": "The system returned status 500 for internal server problems.",
            "metadata": {"type": "error", "category": "http"}
        },
        {
            "doc_id": "config_1",
            "text": "Set parameter MAX_BUFFER_SIZE=8192 in the configuration file.",
            "metadata": {"type": "configuration"}
        },
        {
            "doc_id": "generic_1",
            "text": "The application encountered an issue during startup.",
            "metadata": {"type": "error", "category": "general"}
        }
    ]
    
    technical_queries = [
        {
            "query": "HTTP-403",  # Exact error code
            "expected": ["error_1"],
            "explanation": "Sparse should match exact error code 'HTTP-403'"
        },
        {
            "query": "MAX_BUFFER_SIZE",  # Exact parameter name
            "expected": ["config_1"],
            "explanation": "Sparse should find exact configuration parameter"
        }
    ]
    
    await client.run_test_case(
        "Technical Terms and Codes (Sparse Advantage)",
        technical_docs,
        technical_queries
    )
    
    # Test Case 5: Conceptual Understanding (Dense is better)
    conceptual_docs = [
        {
            "doc_id": "happy_1",
            "text": "She was filled with joy and couldn't stop smiling.",
            "metadata": {"emotion": "positive"}
        },
        {
            "doc_id": "happy_2",
            "text": "His elation was evident as he celebrated the victory.",
            "metadata": {"emotion": "positive"}
        },
        {
            "doc_id": "sad_1",
            "text": "Tears rolled down her face as she felt overwhelmed with sorrow.",
            "metadata": {"emotion": "negative"}
        },
        {
            "doc_id": "neutral_1",
            "text": "The meeting proceeded according to the scheduled agenda.",
            "metadata": {"emotion": "neutral"}
        }
    ]
    
    conceptual_queries = [
        {
            "query": "happiness and excitement",  # Concept not exact words
            "expected": ["happy_1", "happy_2"],
            "explanation": "Dense should understand happiness concept despite different words (joy, elation)"
        },
        {
            "query": "melancholy mood",  # Related to sadness
            "expected": ["sad_1"],
            "explanation": "Dense should connect 'melancholy' with 'sorrow' conceptually"
        }
    ]
    
    await client.run_test_case(
        "Conceptual Understanding (Dense Advantage)",
        conceptual_docs,
        conceptual_queries
    )
    
    # Print summary
    print(f"\n{'='*80}")
    print("TEST SUMMARY")
    print(f"{'='*80}")
    print(f"Total test cases: {len(client.test_results)}")
    
    for test in client.test_results:
        print(f"\n{test['name']}:")
        print(f"  Documents: {test['documents']}")
        print(f"  Queries: {test['queries']}")
        print(f"  Total searches: {len(test['results'])}")

async def run_interactive_demo():
    """Run an interactive demonstration."""
    client = TestClient()
    
    print("\n" + "="*80)
    print("INTERACTIVE RETRIEVAL PIPELINE DEMO")
    print("="*80)
    print("\nThis demo shows how dense and sparse retrieval work differently.")
    print("Dense is better for: semantic similarity, concepts, multilingual")
    print("Sparse is better for: exact names, codes, technical terms")
    
    # Sample documents for interactive demo
    sample_docs = [
        {
            "doc_id": "python_intro",
            "text": "Python is a high-level programming language known for its simplicity and readability.",
            "metadata": {"category": "programming", "language": "english"}
        },
        {
            "doc_id": "python_syntax",
            "text": "def hello_world(): print('Hello, World!') is a simple Python function.",
            "metadata": {"category": "code", "language": "english"}
        },
        {
            "doc_id": "ml_basics",
            "text": "Machine learning algorithms learn patterns from data without explicit programming.",
            "metadata": {"category": "AI", "language": "english"}
        },
        {
            "doc_id": "深度学习",
            "text": "深度学习是机器学习的一个分支，使用神经网络处理复杂数据。",
            "metadata": {"category": "AI", "language": "chinese"}
        },
        {
            "doc_id": "api_error",
            "text": "API returned error code E-2001: Invalid authentication token provided.",
            "metadata": {"category": "error", "type": "api"}
        }
    ]
    
    print("\nIndexing sample documents...")
    await client.clear_documents()
    
    for doc in sample_docs:
        await client.index_document(
            text=doc["text"],
            doc_id=doc["doc_id"],
            metadata=doc.get("metadata", {})
        )
        print(f"  ✓ {doc['doc_id']}: {doc['text'][:60]}...")
    
    # Interactive queries
    queries = [
        ("coding simplicity", "Should find Python docs via semantic similarity"),
        ("E-2001", "Should find exact error code via sparse search"),
        ("neural networks", "Should find ML/DL docs including Chinese via dense"),
        ("hello_world", "Should find exact function name via sparse")
    ]
    
    print("\n" + "="*80)
    print("RUNNING COMPARISON QUERIES")
    print("="*80)
    
    for query, explanation in queries:
        print(f"\nQuery: '{query}'")
        print(f"Expected: {explanation}")
        print("-" * 40)
        
        # Compare all three modes
        modes_results = {}
        for mode in ["dense", "sparse", "hybrid"]:
            result = await client.search(query, mode=mode, top_k=5, rerank_top_k=3)
            
            # Get top results based on mode
            if mode == "hybrid" and result.get("reranked_results"):
                top = [r["doc_id"] for r in result["reranked_results"][:3]]
            elif mode == "dense" and result.get("dense_results"):
                top = [r["doc_id"] for r in result["dense_results"][:3]]
            elif mode == "sparse" and result.get("sparse_results"):
                top = [r["doc_id"] for r in result["sparse_results"][:3]]
            else:
                top = []
            
            modes_results[mode] = top
            print(f"{mode:8}: {top}")
        
        # Show which mode performed best
        print("-" * 40)

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Test client for retrieval pipeline")
    parser.add_argument("--url", default="http://localhost:4242", help="Pipeline service URL")
    parser.add_argument("--mode", choices=["test", "demo"], default="test",
                       help="Run mode: test (all test cases) or demo (interactive)")
    
    args = parser.parse_args()
    
    if args.mode == "test":
        asyncio.run(run_educational_tests())
    else:
        asyncio.run(run_interactive_demo())
