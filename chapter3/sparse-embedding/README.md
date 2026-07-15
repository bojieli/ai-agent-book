# Educational Sparse Vector Search Engine

An educational implementation of a sparse vector search engine using inverted index and BM25 algorithm. This project demonstrates the fundamental concepts of information retrieval with extensive logging and visualization features for learning purposes.

## Features

- **Full BM25 Implementation**: Complete implementation of the BM25 ranking algorithm
- **Advanced Tokenization**: Comprehensive tokenizer handling numbers, codes, technical terms, and mixed case
- **Inverted Index**: Efficient inverted index data structure for term lookup
- **HTTP API**: RESTful API built with FastAPI
- **Interactive Web UI**: Browser-based interface for indexing and searching
- **Extensive Logging**: Detailed educational logging throughout indexing and search operations
- **Index Visualization**: APIs to inspect the internal structure of the index
- **In-Memory Storage**: Simple in-memory storage for educational purposes

### Tokenization Capabilities

The TextProcessor now provides comprehensive tokenization for real-world text:

- **Numbers**: `404`, `3.14`, `2.0.1`
- **Codes**: `XK9-2B4-7Q1`, `API_KEY_123`
- **Technical Terms**: `C++`, `.NET`, `Node.js`
- **Mixed Case**: `JavaScript`, `PyTorch`, `iPhone`
- **Email**: `user@example.com`
- **Hex Codes**: `#FF5733`, `0x1234`
- **Acronyms**: `API`, `HTTP`, `NASA`
- **Alphanumeric**: `Python3`, `ES6`, `HTML5`

## Architecture

### Core Components

1. **TextProcessor**: Advanced tokenizer handling words, numbers, codes, technical terms, and mixed case
2. **InvertedIndex**: Maintains the inverted index structure with term frequencies and document frequencies
3. **BM25**: Implements the BM25 ranking algorithm for relevance scoring
4. **SparseSearchEngine**: Main engine coordinating all components
5. **HTTP Server**: FastAPI-based server exposing the search engine functionality

### BM25 Algorithm

BM25 (Best Matching 25) is a probabilistic ranking function that scores documents based on query terms. The algorithm uses:

- **Term Frequency (TF)**: How often a term appears in a document
- **Inverse Document Frequency (IDF)**: How rare or common a term is across all documents
- **Document Length Normalization**: Adjusts scores based on document length

Key parameters:
- `k1` (default 1.5): Controls term frequency saturation
- `b` (default 0.75): Controls length normalization

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

## Usage

### Starting the Server

```bash
python server.py
```

The server will start on `http://localhost:4241`

### Web Interface

Open your browser and navigate to `http://localhost:4241` to access the interactive web UI.

### API Endpoints

#### Index a Document
```bash
POST /index
{
  "text": "Your document text here",
  "metadata": {"title": "Document Title", "category": "Category"}
}
```

#### Search Documents
```bash
POST /search
{
  "query": "your search query",
  "top_k": 10
}
```

#### Get Statistics
```bash
GET /stats
```

#### Get Index Structure
```bash
GET /index/structure
```

#### Retrieve Document by ID
```bash
GET /document/{doc_id}
```

#### Clear Index
```bash
DELETE /index
```

### Running the Demo

```bash
python demo.py
```

The demo script will:
1. Clear any existing index
2. Index sample documents about programming and computer science
3. Display index statistics
4. Show the internal index structure
5. Perform various search queries
6. Demonstrate document retrieval

## Educational Features

### Extensive Logging

The system provides detailed logging at every step:
- Document tokenization process
- Term frequency calculations
- IDF score computations
- BM25 scoring for each term
- Query processing steps
- Candidate document identification

### Index Visualization

The `/index/structure` endpoint returns:
- Inverted index mapping (terms to documents)
- Document statistics (length, unique terms, top terms)
- BM25 parameters
- Global term frequency distribution

### Debug Information in Search Results

Each search result includes debug information:
- Matched query terms
- Document length
- Term frequencies for query terms
- Individual term contributions to the final score

## Example Output

### Indexing Log
```
2024-01-15 10:30:45 - Indexing document with ID 0
2024-01-15 10:30:45 - Document text: Python is a high-level programming...
2024-01-15 10:30:45 - Tokenizing text of length 142
2024-01-15 10:30:45 - Found 23 raw tokens
2024-01-15 10:30:45 - After removing stop words: 15 tokens
2024-01-15 10:30:45 - Document 0: 15 tokens, 12 unique terms
2024-01-15 10:30:45 - Document 0 indexed successfully
```

### Search Log
```
2024-01-15 10:31:20 - Searching for: 'machine learning algorithms'
2024-01-15 10:31:20 - Query terms after processing: ['machine', 'learning', 'algorithms']
2024-01-15 10:31:20 - Term 'machine' appears in 2 documents
2024-01-15 10:31:20 - Term 'learning' appears in 3 documents
2024-01-15 10:31:20 - Term 'algorithms' appears in 1 document
2024-01-15 10:31:20 - Found 4 candidate documents
2024-01-15 10:31:20 - IDF for 'machine': N=10, df=2, idf=1.7918
2024-01-15 10:31:20 - Term 'machine' in doc 1: tf=2, dl=35, score=3.2451
2024-01-15 10:31:20 - Document 1 total score: 7.8923
2024-01-15 10:31:20 - Returning top 3 results
```

## API Documentation

Interactive API documentation is available at `http://localhost:4241/docs` when the server is running.

## Project Structure

```
sparse-embedding/
├── bm25_engine.py     # Core search engine implementation
├── server.py          # FastAPI HTTP server
├── demo.py            # Demonstration script
├── requirements.txt   # Python dependencies
└── README.md         # This file
```

## Learning Resources

This implementation demonstrates:
- How inverted indices work in search engines
- The mathematics behind BM25 ranking
- Term frequency and document frequency concepts
- The importance of text preprocessing
- How sparse vectors represent documents
- RESTful API design for search systems

## Limitations

This is an educational implementation with some limitations:
- In-memory storage (not persistent)
- Basic tokenization (could be improved with lemmatization)
- English-only stop words
- No support for phrase queries
- No query expansion or synonyms
- Single-threaded processing

## Further Improvements

Potential enhancements for learning:
- Add persistence with a database
- Implement more advanced text processing (stemming, lemmatization)
- Add support for phrase queries
- Implement query expansion
- Add multi-language support
- Implement index compression techniques
- Add support for field-specific searching
- Implement more ranking algorithms (TF-IDF, Okapi BM25+)
