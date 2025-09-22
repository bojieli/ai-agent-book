#!/usr/bin/env python
"""Quick start script to verify the retrieval pipeline setup."""

import asyncio
import httpx
import sys
import time

async def check_service(url: str, name: str) -> bool:
    """Check if a service is running."""
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            if response.status_code == 200:
                print(f"✓ {name} is running at {url}")
                return True
    except:
        pass
    print(f"✗ {name} is not running at {url}")
    return False

async def quick_test():
    """Run a quick test of the pipeline."""
    print("\nRunning quick test...")
    
    pipeline_url = "http://localhost:8002"
    
    async with httpx.AsyncClient(timeout=30.0) as client:
        # Index a test document
        print("\n1. Indexing test document...")
        response = await client.post(
            f"{pipeline_url}/index",
            json={
                "text": "Python is a versatile programming language loved by developers worldwide.",
                "doc_id": "test_python",
                "metadata": {"category": "programming"}
            }
        )
        if response.status_code == 200:
            print("   ✓ Document indexed successfully")
        
        # Search with different modes
        print("\n2. Testing search modes...")
        
        for mode in ["dense", "sparse", "hybrid"]:
            response = await client.post(
                f"{pipeline_url}/search",
                json={
                    "query": "coding language",
                    "mode": mode,
                    "top_k": 5,
                    "rerank_top_k": 3
                }
            )
            if response.status_code == 200:
                data = response.json()
                
                if mode == "dense" and data.get("dense_results"):
                    print(f"   ✓ Dense search: Found {len(data['dense_results'])} results")
                elif mode == "sparse" and data.get("sparse_results"):
                    print(f"   ✓ Sparse search: Found {len(data['sparse_results'])} results")
                elif mode == "hybrid" and data.get("reranked_results"):
                    print(f"   ✓ Hybrid search: Found {len(data['reranked_results'])} reranked results")

async def main():
    """Main function."""
    print("="*60)
    print("RETRIEVAL PIPELINE QUICK START")
    print("="*60)
    
    print("\nChecking services...")
    
    # Check if all services are running
    services_ok = True
    
    dense_ok = await check_service("http://localhost:8000", "Dense Embedding Service")
    sparse_ok = await check_service("http://localhost:8001", "Sparse Embedding Service") 
    pipeline_ok = await check_service("http://localhost:8002", "Retrieval Pipeline")
    
    if not (dense_ok and sparse_ok and pipeline_ok):
        print("\n⚠️  Some services are not running!")
        print("\nTo start all services, run:")
        print("  ./start_all_services.sh")
        print("\nOr start them individually:")
        print("  cd ../dense-embedding && python main.py")
        print("  cd ../sparse-embedding && python server.py")
        print("  cd ../retrieval-pipeline && python main.py")
        return False
    
    print("\n✓ All services are running!")
    
    # Run quick test
    try:
        await quick_test()
        print("\n✓ Quick test completed successfully!")
        
        print("\n" + "="*60)
        print("NEXT STEPS")
        print("="*60)
        print("\n1. Run the full test suite:")
        print("   python test_client.py")
        print("\n2. Try the interactive demo:")
        print("   python demo.py")
        print("\n3. Explore the API:")
        print("   http://localhost:8002/docs")
        print("\n4. Read the README for more details:")
        print("   cat README.md")
        
        return True
        
    except Exception as e:
        print(f"\n✗ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    try:
        success = asyncio.run(main())
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInterrupted by user")
        sys.exit(0)
