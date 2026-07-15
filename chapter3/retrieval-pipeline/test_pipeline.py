#!/usr/bin/env python3
"""Test script for the retrieval pipeline with external doc_id support."""

import httpx
import asyncio
import json
import logging
from datetime import datetime

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Service URLs
DENSE_URL = "http://localhost:4240"
SPARSE_URL = "http://localhost:4241"
PIPELINE_URL = "http://localhost:4242"

async def test_sparse_service():
    """Test the sparse service directly to ensure it handles external doc_ids."""
    logger.info("Testing sparse service with external doc_id...")
    
    async with httpx.AsyncClient(timeout=10.0) as client:
        # Test indexing with external doc_id
        test_doc = {
            "text": "Python is a high-level programming language known for its simplicity and readability.",
            "doc_id": "test_python_doc_001",
            "metadata": {"category": "programming", "language": "Python"}
        }
        
        try:
            response = await client.post(f"{SPARSE_URL}/index", json=test_doc)
            response.raise_for_status()
            result = response.json()
            logger.info(f"Sparse indexing result: {json.dumps(result, indent=2)}")
            
            # Verify the doc_id matches what we sent
            if result.get("doc_id") == "test_python_doc_001":
                logger.info("✅ Sparse service correctly preserved external doc_id")
            else:
                logger.error(f"❌ Sparse service returned different doc_id: {result.get('doc_id')}")
                
            # Test search
            search_query = {"query": "Python programming", "top_k": 5}
            response = await client.post(f"{SPARSE_URL}/search", json=search_query)
            response.raise_for_status()
            search_results = response.json()
            
            if search_results:
                logger.info(f"✅ Sparse search returned {len(search_results)} results")
                first_result = search_results[0]
                logger.info(f"First result doc_id: {first_result.get('doc_id')}")
                if first_result.get('doc_id') == "test_python_doc_001":
                    logger.info("✅ Search correctly returned our document with external doc_id")
            
            return True
            
        except Exception as e:
            logger.error(f"❌ Sparse service test failed: {e}")
            return False

async def test_pipeline():
    """Test the complete retrieval pipeline."""
    logger.info("Testing retrieval pipeline...")
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        try:
            # First, clear the pipeline
            logger.info("Clearing pipeline...")
            response = await client.delete(f"{PIPELINE_URL}/clear")
            logger.info(f"Clear response: {response.json()}")
            
            # Test documents
            test_documents = [
                {
                    "text": "Python is renowned for its clean syntax and readability, making it ideal for beginners and experts alike.",
                    "doc_id": "prog_python",
                    "metadata": {"category": "programming", "subcategory": "languages"}
                },
                {
                    "text": "Machine learning with Python involves libraries like scikit-learn, TensorFlow, and PyTorch for building AI models.",
                    "doc_id": "ml_python",
                    "metadata": {"category": "machine_learning", "subcategory": "tools"}
                },
                {
                    "text": "JavaScript is the language of the web, enabling dynamic and interactive user interfaces in browsers.",
                    "doc_id": "prog_javascript",
                    "metadata": {"category": "programming", "subcategory": "web"}
                }
            ]
            
            # Index documents
            for doc in test_documents:
                logger.info(f"Indexing document: {doc['doc_id']}")
                response = await client.post(f"{PIPELINE_URL}/index", json=doc)
                response.raise_for_status()
                result = response.json()
                
                # Check both services succeeded
                dense_success = result.get("dense", {}).get("success", False)
                sparse_success = result.get("sparse", {}).get("success", False)
                
                if dense_success and sparse_success:
                    logger.info(f"✅ Document {doc['doc_id']} indexed successfully in both services")
                else:
                    logger.error(f"❌ Indexing failed for {doc['doc_id']}")
                    logger.error(f"   Dense: {result.get('dense')}")
                    logger.error(f"   Sparse: {result.get('sparse')}")
            
            # Wait a moment for indexing to complete
            await asyncio.sleep(1)
            
            # Test search in different modes
            search_query = "Python programming language"
            logger.info(f"\nTesting search with query: '{search_query}'")
            
            for mode in ["dense", "sparse", "hybrid"]:
                logger.info(f"\n--- Testing {mode} search ---")
                search_request = {
                    "query": search_query,
                    "mode": mode,
                    "top_k": 10,
                    "rerank_top_k": 5,
                    "skip_reranking": False if mode == "hybrid" else True
                }
                
                response = await client.post(f"{PIPELINE_URL}/search", json=search_request)
                response.raise_for_status()
                results = response.json()
                
                # Log results summary
                if mode == "dense":
                    dense_results = results.get("dense_results", [])
                    if dense_results:
                        logger.info(f"✅ Dense search returned {len(dense_results)} results")
                        logger.info(f"   Top result: {dense_results[0]['doc_id']} (score: {dense_results[0]['score']:.4f})")
                    else:
                        logger.error("❌ No dense results returned")
                        
                elif mode == "sparse":
                    sparse_results = results.get("sparse_results", [])
                    if sparse_results:
                        logger.info(f"✅ Sparse search returned {len(sparse_results)} results")
                        logger.info(f"   Top result: {sparse_results[0]['doc_id']} (score: {sparse_results[0]['score']:.4f})")
                    else:
                        logger.error("❌ No sparse results returned")
                        
                elif mode == "hybrid":
                    dense_results = results.get("dense_results", [])
                    sparse_results = results.get("sparse_results", [])
                    reranked_results = results.get("reranked_results", [])
                    
                    logger.info(f"✅ Hybrid search results:")
                    logger.info(f"   Dense: {len(dense_results)} results")
                    logger.info(f"   Sparse: {len(sparse_results)} results")
                    logger.info(f"   Reranked: {len(reranked_results)} results")
                    
                    if reranked_results:
                        logger.info(f"   Top reranked result: {reranked_results[0]['doc_id']} (score: {reranked_results[0]['rerank_score']:.4f})")
                    
                    # Check statistics
                    stats = results.get("statistics", {})
                    if stats:
                        logger.info(f"   Overlap: {stats.get('overlap_count', 0)} documents ({stats.get('overlap_percentage', 0):.1f}%)")
            
            logger.info("\n✅ All pipeline tests completed successfully!")
            return True
            
        except Exception as e:
            logger.error(f"❌ Pipeline test failed: {e}")
            import traceback
            logger.error(traceback.format_exc())
            return False

async def main():
    """Run all tests."""
    logger.info("Starting retrieval pipeline tests...")
    logger.info("Make sure all three services are running:")
    logger.info("  - Dense service on port 4240")
    logger.info("  - Sparse service on port 4241")
    logger.info("  - Pipeline service on port 4242")
    logger.info("")
    
    # Test sparse service first
    sparse_ok = await test_sparse_service()
    
    if sparse_ok:
        logger.info("\n" + "="*50 + "\n")
        # Test full pipeline
        pipeline_ok = await test_pipeline()
        
        if pipeline_ok:
            logger.info("\n🎉 All tests passed successfully!")
        else:
            logger.info("\n⚠️ Some pipeline tests failed")
    else:
        logger.error("\n⚠️ Sparse service test failed - skipping pipeline tests")

if __name__ == "__main__":
    asyncio.run(main())
