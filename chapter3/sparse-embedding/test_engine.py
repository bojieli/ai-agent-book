"""
Test script for the Educational Sparse Vector Search Engine
Tests core functionality and demonstrates educational aspects
"""

import logging
from bm25_engine import TextProcessor, InvertedIndex, BM25, SparseSearchEngine

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def test_text_processor():
    """Test text processing functionality"""
    logger.info("\n" + "="*50)
    logger.info("TESTING TEXT PROCESSOR")
    logger.info("="*50)
    
    processor = TextProcessor()
    
    # Test basic tokenization
    text1 = "The quick brown fox jumps over the lazy dog."
    tokens1 = processor.tokenize(text1, remove_stop_words=False)
    logger.info(f"Input: {text1}")
    logger.info(f"Tokens (with stop words): {tokens1}")
    
    tokens2 = processor.tokenize(text1, remove_stop_words=True)
    logger.info(f"Tokens (without stop words): {tokens2}")
    
    # Test with technical text
    text2 = "Machine learning algorithms process data to identify patterns."
    tokens3 = processor.tokenize(text2)
    logger.info(f"\nInput: {text2}")
    logger.info(f"Tokens: {tokens3}")
    
    # Test with mixed case and punctuation
    text3 = "Python, JavaScript, and C++ are POPULAR programming languages!"
    tokens4 = processor.tokenize(text3)
    logger.info(f"\nInput: {text3}")
    logger.info(f"Tokens: {tokens4}")
    
    assert len(tokens2) < len(tokens1), "Stop word removal should reduce token count"
    logger.info("\n✓ Text processor tests passed")


def test_inverted_index():
    """Test inverted index functionality"""
    logger.info("\n" + "="*50)
    logger.info("TESTING INVERTED INDEX")
    logger.info("="*50)
    
    index = InvertedIndex()
    
    # Add test documents
    doc1 = "Python is a programming language"
    doc2 = "JavaScript is also a programming language"
    doc3 = "Python and JavaScript are both popular"
    
    logger.info("\nAdding documents to index...")
    index.add_document(0, doc1, {"title": "Doc1"})
    index.add_document(1, doc2, {"title": "Doc2"})
    index.add_document(2, doc3, {"title": "Doc3"})
    
    # Test posting lists
    logger.info("\nTesting posting lists:")
    python_docs = index.get_posting_list("python")
    logger.info(f"Documents containing 'python': {python_docs}")
    assert python_docs == {0, 2}, "Python should be in docs 0 and 2"
    
    programming_docs = index.get_posting_list("programming")
    logger.info(f"Documents containing 'programming': {programming_docs}")
    assert programming_docs == {0, 1}, "Programming should be in docs 0 and 1"
    
    # Test statistics
    stats = index.get_statistics()
    logger.info(f"\nIndex statistics:")
    logger.info(f"  Total documents: {stats['total_documents']}")
    logger.info(f"  Unique terms: {stats['unique_terms']}")
    logger.info(f"  Average doc length: {stats['average_document_length']:.2f}")
    
    assert stats['total_documents'] == 3, "Should have 3 documents"
    logger.info("\n✓ Inverted index tests passed")


def test_bm25_scoring():
    """Test BM25 scoring algorithm"""
    logger.info("\n" + "="*50)
    logger.info("TESTING BM25 SCORING")
    logger.info("="*50)
    
    # Create index with test documents
    index = InvertedIndex()
    index.add_document(0, "The cat sat on the mat", {"title": "Simple"})
    index.add_document(1, "The dog sat on the log", {"title": "Similar"})
    index.add_document(2, "Cats and dogs are pets", {"title": "Pets"})
    index.add_document(3, "The mat was comfortable", {"title": "Mat"})
    
    # Initialize BM25
    bm25 = BM25(index, k1=1.5, b=0.75)
    
    # Test IDF calculation
    logger.info("\nTesting IDF calculations:")
    idf_cat = bm25.calculate_idf("cat")
    idf_the = bm25.calculate_idf("the")  # Common word
    idf_mat = bm25.calculate_idf("mat")
    
    logger.info(f"IDF('cat'): {idf_cat:.4f}")
    logger.info(f"IDF('the'): {idf_the:.4f}")
    logger.info(f"IDF('mat'): {idf_mat:.4f}")
    
    # IDF of rare words should be higher than common words
    assert idf_cat > idf_the, "Rare words should have higher IDF"
    
    # Test document scoring
    logger.info("\nTesting document scoring for query 'cat mat':")
    query_terms = ["cat", "mat"]
    
    for doc_id in range(4):
        score = bm25.score_document(query_terms, doc_id)
        logger.info(f"Document {doc_id} score: {score:.4f}")
    
    # Document 0 should have the highest score as it contains both terms
    score_0 = bm25.score_document(query_terms, 0)
    score_1 = bm25.score_document(query_terms, 1)
    assert score_0 > score_1, "Doc with both terms should score higher"
    
    logger.info("\n✓ BM25 scoring tests passed")


def test_search_engine():
    """Test the complete search engine"""
    logger.info("\n" + "="*50)
    logger.info("TESTING SEARCH ENGINE")
    logger.info("="*50)
    
    engine = SparseSearchEngine()
    
    # Index test documents
    logger.info("\nIndexing test documents...")
    doc_ids = []
    
    test_docs = [
        ("Information retrieval is the science of searching for information in documents.", 
         {"topic": "IR"}),
        ("Search engines use inverted indices to quickly find relevant documents.", 
         {"topic": "Search"}),
        ("BM25 is a probabilistic ranking function used in information retrieval.", 
         {"topic": "BM25"}),
        ("The inverted index maps terms to the documents that contain them.", 
         {"topic": "Index"}),
        ("Relevance ranking determines the order of search results.", 
         {"topic": "Ranking"})
    ]
    
    for text, metadata in test_docs:
        doc_id = engine.index_document(text, metadata)
        doc_ids.append(doc_id)
        logger.info(f"Indexed: {metadata['topic']} (ID: {doc_id})")
    
    # Test search queries
    test_queries = [
        ("information retrieval", 3),
        ("inverted index", 2),
        ("search ranking", 3),
        ("BM25 algorithm", 2)
    ]
    
    for query, top_k in test_queries:
        logger.info(f"\nSearching for: '{query}' (top {top_k})")
        results = engine.search(query, top_k)
        
        for rank, result in enumerate(results, 1):
            logger.info(f"  Rank {rank}: {result['metadata']['topic']} "
                       f"(score: {result['score']:.4f}, "
                       f"matched: {result['debug']['matched_terms']})")
    
    # Test document retrieval
    logger.info("\nTesting document retrieval:")
    doc = engine.get_document(0)
    assert doc is not None, "Should retrieve document"
    logger.info(f"Retrieved document 0: {doc['metadata']['topic']}")
    
    # Test index clearing
    logger.info("\nTesting index clearing:")
    initial_stats = engine.index.get_statistics()
    engine.clear_index()
    final_stats = engine.index.get_statistics()
    assert final_stats['total_documents'] == 0, "Index should be empty after clearing"
    logger.info("✓ Index cleared successfully")
    
    logger.info("\n✓ Search engine tests passed")


def test_edge_cases():
    """Test edge cases and special scenarios"""
    logger.info("\n" + "="*50)
    logger.info("TESTING EDGE CASES")
    logger.info("="*50)
    
    engine = SparseSearchEngine()
    
    # Test empty query
    logger.info("\nTesting empty query:")
    results = engine.search("", top_k=5)
    assert len(results) == 0, "Empty query should return no results"
    logger.info("✓ Empty query handled correctly")
    
    # Test query with only stop words
    logger.info("\nTesting query with only stop words:")
    engine.index_document("This is a test document about nothing specific.")
    results = engine.search("the is a", top_k=5)
    logger.info(f"Results for stop words query: {len(results)} documents")
    
    # Test single word document
    logger.info("\nTesting single word document:")
    doc_id = engine.index_document("Python")
    doc = engine.get_document(doc_id)
    assert doc is not None, "Should index single word document"
    logger.info("✓ Single word document indexed")
    
    # Test duplicate documents
    logger.info("\nTesting duplicate documents:")
    text = "This is a duplicate document"
    id1 = engine.index_document(text)
    id2 = engine.index_document(text)
    assert id1 != id2, "Duplicate documents should have different IDs"
    logger.info(f"✓ Duplicate documents have different IDs: {id1}, {id2}")
    
    # Test very long document
    logger.info("\nTesting very long document:")
    long_text = " ".join(["word" + str(i) for i in range(1000)])
    long_doc_id = engine.index_document(long_text)
    long_doc = engine.get_document(long_doc_id)
    logger.info(f"✓ Long document indexed (length: {long_doc['statistics']['length']} terms)")
    
    # Test special characters
    logger.info("\nTesting special characters:")
    special_text = "Email: test@example.com, URL: https://example.com, Price: $99.99"
    special_id = engine.index_document(special_text)
    results = engine.search("email test example", top_k=1)
    logger.info(f"✓ Special characters handled, found {len(results)} results")
    
    logger.info("\n✓ All edge case tests passed")


def test_ranking_quality():
    """Test the quality of search result ranking"""
    logger.info("\n" + "="*50)
    logger.info("TESTING RANKING QUALITY")
    logger.info("="*50)
    
    engine = SparseSearchEngine()
    
    # Create documents with varying relevance
    docs = [
        "Machine learning is a subset of artificial intelligence",
        "Deep learning uses neural networks for machine learning",
        "Machine learning algorithms learn from data",
        "Artificial intelligence includes machine learning and robotics",
        "Data science often uses machine learning techniques",
        "Neural networks are inspired by biological brains",
        "Supervised learning is a type of machine learning",
        "Unsupervised learning discovers patterns in data",
        "Reinforcement learning uses rewards and penalties",
        "Computer vision is an application of deep learning"
    ]
    
    logger.info("Indexing documents about machine learning...")
    for i, doc in enumerate(docs):
        engine.index_document(doc, {"id": i})
    
    # Search for "machine learning"
    query = "machine learning"
    logger.info(f"\nSearching for: '{query}'")
    results = engine.search(query, top_k=5)
    
    logger.info("\nTop 5 results:")
    for rank, result in enumerate(results, 1):
        logger.info(f"  Rank {rank}: Score {result['score']:.4f}")
        logger.info(f"    Text: {result['text']}")
        logger.info(f"    Term frequencies: {result['debug']['term_frequencies']}")
    
    # Verify that documents with both terms rank higher
    first_result_text = results[0]['text'].lower()
    assert 'machine' in first_result_text and 'learning' in first_result_text, \
        "Top result should contain both query terms"
    
    logger.info("\n✓ Ranking quality test passed")


def main():
    """Run all tests"""
    logger.info("Starting Educational Sparse Vector Search Engine Tests")
    logger.info("This will test all components and demonstrate educational logging")
    
    try:
        test_text_processor()
        test_inverted_index()
        test_bm25_scoring()
        test_search_engine()
        test_edge_cases()
        test_ranking_quality()
        
        logger.info("\n" + "="*50)
        logger.info("ALL TESTS PASSED SUCCESSFULLY!")
        logger.info("="*50)
        logger.info("\nThe educational sparse vector search engine is working correctly.")
        logger.info("Run 'python server.py' to start the HTTP server.")
        logger.info("Run 'python demo.py' to see a full demonstration.")
        
    except Exception as e:
        logger.error(f"Test failed: {str(e)}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
