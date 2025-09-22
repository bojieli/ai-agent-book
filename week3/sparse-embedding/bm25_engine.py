"""
BM25 Sparse Vector Search Engine
An educational implementation of BM25 algorithm with inverted index
"""

import math
import re
import logging
from collections import defaultdict, Counter
from typing import List, Dict, Set, Tuple, Optional
import json

# Configure logging for educational purposes
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TextProcessor:
    """Text preprocessing for indexing and searching"""
    
    def __init__(self):
        # Common English stop words
        self.stop_words = {
            'the', 'is', 'at', 'which', 'on', 'a', 'an', 'as', 'are', 'was',
            'been', 'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will',
            'would', 'could', 'should', 'may', 'might', 'must', 'can', 'this',
            'that', 'these', 'those', 'i', 'you', 'he', 'she', 'it', 'we',
            'they', 'what', 'who', 'when', 'where', 'why', 'how', 'all', 'each',
            'every', 'both', 'few', 'more', 'most', 'other', 'some', 'such',
            'only', 'own', 'same', 'so', 'than', 'too', 'very', 'just'
        }
        logger.info(f"TextProcessor initialized with {len(self.stop_words)} stop words")
    
    def tokenize(self, text: str, remove_stop_words: bool = True) -> List[str]:
        """Tokenize text into words"""
        logger.debug(f"Tokenizing text of length {len(text)}")
        
        # Convert to lowercase and split by non-alphanumeric characters
        text = text.lower()
        tokens = re.findall(r'\b[a-z]+\b', text)
        
        logger.debug(f"Found {len(tokens)} raw tokens")
        
        if remove_stop_words:
            tokens = [t for t in tokens if t not in self.stop_words]
            logger.debug(f"After removing stop words: {len(tokens)} tokens")
        
        return tokens


class InvertedIndex:
    """Inverted index data structure for efficient term lookup"""
    
    def __init__(self):
        # Main inverted index: term -> set of document IDs
        self.index: Dict[str, Set[int]] = defaultdict(set)
        
        # Document frequency: term -> number of documents containing term
        self.document_frequency: Dict[str, int] = defaultdict(int)
        
        # Term frequency in documents: doc_id -> term -> frequency
        self.term_frequency: Dict[int, Counter] = {}
        
        # Document lengths (number of terms)
        self.doc_lengths: Dict[int, int] = {}
        
        # Original documents for retrieval
        self.documents: Dict[int, str] = {}
        
        # Document metadata
        self.doc_metadata: Dict[int, Dict] = {}
        
        # Statistics
        self.total_documents = 0
        self.total_terms = 0
        self.unique_terms = 0
        
        logger.info("InvertedIndex initialized")
    
    def add_document(self, doc_id: int, text: str, metadata: Optional[Dict] = None):
        """Add a document to the index"""
        logger.info(f"Adding document {doc_id} to index")
        logger.debug(f"Document text: {text[:100]}..." if len(text) > 100 else f"Document text: {text}")
        
        # Store original document
        self.documents[doc_id] = text
        if metadata:
            self.doc_metadata[doc_id] = metadata
            logger.debug(f"Document metadata: {metadata}")
        
        # Process text
        processor = TextProcessor()
        tokens = processor.tokenize(text)
        
        # Count term frequencies
        term_freq = Counter(tokens)
        self.term_frequency[doc_id] = term_freq
        self.doc_lengths[doc_id] = len(tokens)
        
        logger.debug(f"Document {doc_id}: {len(tokens)} tokens, {len(term_freq)} unique terms")
        
        # Update inverted index
        for term in term_freq:
            self.index[term].add(doc_id)
            
        # Update document frequency
        for term in term_freq:
            if doc_id not in self.index[term]:
                self.document_frequency[term] += 1
        
        self.total_documents += 1
        self._update_statistics()
        
        logger.info(f"Document {doc_id} indexed successfully")
    
    def _update_statistics(self):
        """Update index statistics"""
        self.unique_terms = len(self.index)
        self.total_terms = sum(self.doc_lengths.values())
        logger.debug(f"Index statistics: {self.total_documents} documents, "
                    f"{self.unique_terms} unique terms, {self.total_terms} total terms")
    
    def get_posting_list(self, term: str) -> Set[int]:
        """Get document IDs containing the term"""
        return self.index.get(term, set())
    
    def get_statistics(self) -> Dict:
        """Get comprehensive index statistics"""
        stats = {
            'total_documents': self.total_documents,
            'unique_terms': self.unique_terms,
            'total_terms': self.total_terms,
            'average_document_length': self.total_terms / self.total_documents if self.total_documents > 0 else 0,
            'terms_by_frequency': self._get_term_frequency_distribution()
        }
        return stats
    
    def _get_term_frequency_distribution(self, top_n: int = 10) -> List[Tuple[str, int]]:
        """Get top N most frequent terms across all documents"""
        global_term_freq = Counter()
        for doc_term_freq in self.term_frequency.values():
            global_term_freq.update(doc_term_freq)
        return global_term_freq.most_common(top_n)
    
    def get_index_structure(self) -> Dict:
        """Get a visualization-friendly representation of the index"""
        structure = {
            'inverted_index': {},
            'document_info': {},
            'statistics': self.get_statistics()
        }
        
        # Include top terms in the structure
        for term, doc_ids in list(self.index.items())[:20]:  # Limit to 20 terms for readability
            structure['inverted_index'][term] = {
                'document_ids': list(doc_ids),
                'document_frequency': len(doc_ids)
            }
        
        # Include document information
        for doc_id in self.documents:
            structure['document_info'][doc_id] = {
                'length': self.doc_lengths[doc_id],
                'unique_terms': len(self.term_frequency[doc_id]),
                'top_terms': self.term_frequency[doc_id].most_common(5)
            }
        
        return structure


class BM25:
    """BM25 ranking algorithm implementation"""
    
    def __init__(self, index: InvertedIndex, k1: float = 1.5, b: float = 0.75):
        """
        Initialize BM25 with tuning parameters
        k1: controls term frequency saturation (typically 1.2 to 2.0)
        b: controls length normalization (0.0 to 1.0)
        """
        self.index = index
        self.k1 = k1
        self.b = b
        
        # Calculate average document length
        self.avgdl = 0
        if index.total_documents > 0:
            self.avgdl = sum(index.doc_lengths.values()) / index.total_documents
        
        logger.info(f"BM25 initialized with k1={k1}, b={b}, avgdl={self.avgdl:.2f}")
    
    def calculate_idf(self, term: str) -> float:
        """Calculate Inverse Document Frequency for a term"""
        N = self.index.total_documents
        df = len(self.index.get_posting_list(term))
        
        if df == 0:
            return 0
        
        # BM25 IDF formula
        idf = math.log((N - df + 0.5) / (df + 0.5) + 1)
        
        logger.debug(f"IDF for '{term}': N={N}, df={df}, idf={idf:.4f}")
        return idf
    
    def calculate_term_score(self, term: str, doc_id: int) -> float:
        """Calculate BM25 score for a single term in a document"""
        # Get term frequency in document
        tf = self.index.term_frequency.get(doc_id, Counter()).get(term, 0)
        if tf == 0:
            return 0
        
        # Get document length
        dl = self.index.doc_lengths.get(doc_id, 0)
        
        # Calculate IDF
        idf = self.calculate_idf(term)
        
        # BM25 term score formula
        numerator = tf * (self.k1 + 1)
        denominator = tf + self.k1 * (1 - self.b + self.b * (dl / self.avgdl))
        score = idf * (numerator / denominator)
        
        logger.debug(f"Term '{term}' in doc {doc_id}: tf={tf}, dl={dl}, score={score:.4f}")
        return score
    
    def score_document(self, query_terms: List[str], doc_id: int) -> float:
        """Calculate total BM25 score for a document given query terms"""
        total_score = 0
        term_scores = {}
        
        for term in query_terms:
            term_score = self.calculate_term_score(term, doc_id)
            term_scores[term] = term_score
            total_score += term_score
        
        logger.debug(f"Document {doc_id} total score: {total_score:.4f}")
        logger.debug(f"Term contributions: {term_scores}")
        
        return total_score
    
    def search(self, query: str, top_k: int = 10) -> List[Tuple[int, float, Dict]]:
        """
        Search for documents matching the query
        Returns list of (doc_id, score, debug_info) tuples
        """
        logger.info(f"Searching for: '{query}'")
        
        # Process query
        processor = TextProcessor()
        query_terms = processor.tokenize(query)
        logger.info(f"Query terms after processing: {query_terms}")
        
        # Find candidate documents (documents containing at least one query term)
        candidate_docs = set()
        term_doc_mapping = {}
        
        for term in query_terms:
            docs = self.index.get_posting_list(term)
            candidate_docs.update(docs)
            term_doc_mapping[term] = docs
            logger.debug(f"Term '{term}' appears in {len(docs)} documents")
        
        logger.info(f"Found {len(candidate_docs)} candidate documents")
        
        # Score each candidate document
        doc_scores = []
        for doc_id in candidate_docs:
            score = self.score_document(query_terms, doc_id)
            
            # Collect debug information
            debug_info = {
                'matched_terms': [term for term in query_terms 
                                 if doc_id in self.index.get_posting_list(term)],
                'doc_length': self.index.doc_lengths[doc_id],
                'term_frequencies': {term: self.index.term_frequency[doc_id].get(term, 0) 
                                    for term in query_terms}
            }
            
            doc_scores.append((doc_id, score, debug_info))
        
        # Sort by score (descending)
        doc_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = doc_scores[:top_k]
        
        logger.info(f"Returning top {len(results)} results")
        for rank, (doc_id, score, _) in enumerate(results, 1):
            logger.info(f"Rank {rank}: Document {doc_id} (score: {score:.4f})")
        
        return results


class SparseSearchEngine:
    """Main search engine combining all components"""
    
    def __init__(self):
        self.index = InvertedIndex()
        self.bm25 = None
        self.next_doc_id = 0
        logger.info("SparseSearchEngine initialized")
    
    def index_document(self, text: str, metadata: Optional[Dict] = None) -> int:
        """Index a new document and return its ID"""
        doc_id = self.next_doc_id
        self.next_doc_id += 1
        
        logger.info(f"Indexing document with ID {doc_id}")
        self.index.add_document(doc_id, text, metadata)
        
        # Reinitialize BM25 with updated index
        self.bm25 = BM25(self.index)
        
        return doc_id
    
    def index_batch(self, documents: List[Dict]) -> List[int]:
        """Index multiple documents at once"""
        logger.info(f"Batch indexing {len(documents)} documents")
        doc_ids = []
        
        for doc in documents:
            text = doc.get('text', '')
            metadata = doc.get('metadata', None)
            doc_id = self.index_document(text, metadata)
            doc_ids.append(doc_id)
        
        logger.info(f"Batch indexing complete. Indexed {len(doc_ids)} documents")
        return doc_ids
    
    def search(self, query: str, top_k: int = 10) -> List[Dict]:
        """Search for documents matching the query"""
        if self.bm25 is None:
            logger.warning("No documents indexed yet")
            return []
        
        logger.info(f"Executing search query: '{query}'")
        results = self.bm25.search(query, top_k)
        
        # Format results
        formatted_results = []
        for doc_id, score, debug_info in results:
            result = {
                'doc_id': doc_id,
                'score': score,
                'text': self.index.documents[doc_id],
                'metadata': self.index.doc_metadata.get(doc_id, {}),
                'debug': debug_info
            }
            formatted_results.append(result)
        
        return formatted_results
    
    def get_document(self, doc_id: int) -> Optional[Dict]:
        """Retrieve a document by ID"""
        if doc_id not in self.index.documents:
            return None
        
        return {
            'doc_id': doc_id,
            'text': self.index.documents[doc_id],
            'metadata': self.index.doc_metadata.get(doc_id, {}),
            'statistics': {
                'length': self.index.doc_lengths[doc_id],
                'unique_terms': len(self.index.term_frequency[doc_id]),
                'top_terms': self.index.term_frequency[doc_id].most_common(10)
            }
        }
    
    def get_index_info(self) -> Dict:
        """Get comprehensive information about the index"""
        return {
            'statistics': self.index.get_statistics(),
            'structure': self.index.get_index_structure(),
            'bm25_params': {
                'k1': self.bm25.k1 if self.bm25 else None,
                'b': self.bm25.b if self.bm25 else None,
                'avgdl': self.bm25.avgdl if self.bm25 else None
            }
        }
    
    def clear_index(self):
        """Clear all indexed documents"""
        logger.info("Clearing index")
        self.index = InvertedIndex()
        self.bm25 = None
        self.next_doc_id = 0
        logger.info("Index cleared")
