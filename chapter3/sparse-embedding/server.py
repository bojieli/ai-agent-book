"""
HTTP API Server for Sparse Vector Search Engine
Educational server with extensive logging and visualization
"""

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field
from typing import List, Dict, Optional
import uvicorn
import logging
import json
from datetime import datetime

from bm25_engine import SparseSearchEngine

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Educational Sparse Vector Search Engine",
    description="BM25-based search engine with inverted index for educational purposes",
    version="1.0.0"
)

# Initialize search engine
search_engine = SparseSearchEngine()


# Pydantic models for request/response
class IndexDocumentRequest(BaseModel):
    text: str = Field(..., description="Text content to index")
    metadata: Optional[Dict] = Field(None, description="Optional metadata")
    doc_id: Optional[str] = Field(None, description="Optional external document ID")


class BatchIndexRequest(BaseModel):
    documents: List[Dict] = Field(..., description="List of documents to index")


class SearchRequest(BaseModel):
    query: str = Field(..., description="Search query")
    top_k: int = Field(10, description="Number of results to return")


class DocumentResponse(BaseModel):
    doc_id: str  # Changed to str to support external IDs
    text: str
    metadata: Optional[Dict]
    score: Optional[float] = None
    debug: Optional[Dict] = None


# Root endpoint with UI
@app.get("/", response_class=HTMLResponse)
async def root():
    """Serve a simple HTML interface for the search engine"""
    html_content = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Educational Sparse Vector Search Engine</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }
            .section {
                background: white;
                border-radius: 8px;
                padding: 20px;
                margin: 20px 0;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            .form-group {
                margin: 15px 0;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #555;
            }
            input, textarea {
                width: 100%;
                padding: 8px;
                border: 1px solid #ddd;
                border-radius: 4px;
                box-sizing: border-box;
            }
            button {
                background-color: #007bff;
                color: white;
                padding: 10px 20px;
                border: none;
                border-radius: 4px;
                cursor: pointer;
                font-size: 16px;
            }
            button:hover {
                background-color: #0056b3;
            }
            pre {
                background-color: #f8f9fa;
                padding: 15px;
                border-radius: 4px;
                overflow-x: auto;
                border: 1px solid #dee2e6;
            }
            .results {
                margin-top: 20px;
            }
            .result-item {
                background: #f8f9fa;
                padding: 15px;
                margin: 10px 0;
                border-radius: 4px;
                border-left: 4px solid #007bff;
            }
            .score {
                font-weight: bold;
                color: #007bff;
            }
            .debug-info {
                margin-top: 10px;
                padding: 10px;
                background: #fff;
                border: 1px solid #ddd;
                border-radius: 4px;
                font-size: 0.9em;
            }
            .stats {
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 15px;
                margin-top: 15px;
            }
            .stat-item {
                background: #f8f9fa;
                padding: 10px;
                border-radius: 4px;
                text-align: center;
            }
            .stat-value {
                font-size: 24px;
                font-weight: bold;
                color: #007bff;
            }
            .stat-label {
                font-size: 14px;
                color: #666;
                margin-top: 5px;
            }
        </style>
    </head>
    <body>
        <h1>🔍 Educational Sparse Vector Search Engine</h1>
        
        <div class="section">
            <h2>Index Documents</h2>
            <div class="form-group">
                <label for="indexText">Document Text:</label>
                <textarea id="indexText" rows="4" placeholder="Enter document text to index..."></textarea>
            </div>
            <div class="form-group">
                <label for="indexMetadata">Metadata (JSON, optional):</label>
                <input id="indexMetadata" placeholder='{"title": "Document Title", "author": "Author Name"}'>
            </div>
            <button onclick="indexDocument()">Index Document</button>
        </div>
        
        <div class="section">
            <h2>Search</h2>
            <div class="form-group">
                <label for="searchQuery">Query:</label>
                <input id="searchQuery" placeholder="Enter search query...">
            </div>
            <div class="form-group">
                <label for="topK">Number of Results:</label>
                <input id="topK" type="number" value="5" min="1" max="100">
            </div>
            <button onclick="search()">Search</button>
            <div id="searchResults" class="results"></div>
        </div>
        
        <div class="section">
            <h2>Index Statistics</h2>
            <button onclick="loadStatistics()">Load Statistics</button>
            <div id="statistics"></div>
        </div>
        
        <div class="section">
            <h2>Index Structure Visualization</h2>
            <button onclick="loadIndexStructure()">Load Index Structure</button>
            <div id="indexStructure"></div>
        </div>

        <script>
            async function indexDocument() {
                const text = document.getElementById('indexText').value;
                const metadataStr = document.getElementById('indexMetadata').value;
                
                let metadata = null;
                if (metadataStr) {
                    try {
                        metadata = JSON.parse(metadataStr);
                    } catch (e) {
                        alert('Invalid JSON in metadata field');
                        return;
                    }
                }
                
                const response = await fetch('/index', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({text: text, metadata: metadata, doc_id: null})
                });
                
                if (response.ok) {
                    const result = await response.json();
                    alert(`Document indexed successfully! ID: ${result.doc_id}`);
                    document.getElementById('indexText').value = '';
                    document.getElementById('indexMetadata').value = '';
                    loadStatistics();
                } else {
                    alert('Error indexing document');
                }
            }
            
            async function search() {
                const query = document.getElementById('searchQuery').value;
                const topK = document.getElementById('topK').value;
                
                const response = await fetch('/search', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query: query, top_k: parseInt(topK)})
                });
                
                if (response.ok) {
                    const results = await response.json();
                    displaySearchResults(results);
                } else {
                    alert('Error performing search');
                }
            }
            
            function displaySearchResults(results) {
                const container = document.getElementById('searchResults');
                
                if (results.length === 0) {
                    container.innerHTML = '<p>No results found</p>';
                    return;
                }
                
                let html = '<h3>Search Results</h3>';
                results.forEach((result, index) => {
                    html += `
                        <div class="result-item">
                            <div><strong>Rank ${index + 1}</strong> - Doc ID: ${result.doc_id}</div>
                            <div class="score">Score: ${result.score.toFixed(4)}</div>
                            <div style="margin-top: 10px;">${result.text}</div>
                            ${result.metadata ? `<div style="margin-top: 10px;"><strong>Metadata:</strong> ${JSON.stringify(result.metadata)}</div>` : ''}
                            <div class="debug-info">
                                <strong>Debug Info:</strong>
                                <pre>${JSON.stringify(result.debug, null, 2)}</pre>
                            </div>
                        </div>
                    `;
                });
                
                container.innerHTML = html;
            }
            
            async function loadStatistics() {
                const response = await fetch('/stats');
                if (response.ok) {
                    const stats = await response.json();
                    displayStatistics(stats);
                }
            }
            
            function displayStatistics(stats) {
                const container = document.getElementById('statistics');
                
                let html = '<div class="stats">';
                html += `
                    <div class="stat-item">
                        <div class="stat-value">${stats.total_documents}</div>
                        <div class="stat-label">Total Documents</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${stats.unique_terms}</div>
                        <div class="stat-label">Unique Terms</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${stats.total_terms}</div>
                        <div class="stat-label">Total Terms</div>
                    </div>
                    <div class="stat-item">
                        <div class="stat-value">${stats.average_document_length.toFixed(2)}</div>
                        <div class="stat-label">Avg Doc Length</div>
                    </div>
                `;
                html += '</div>';
                
                if (stats.terms_by_frequency && stats.terms_by_frequency.length > 0) {
                    html += '<h4>Top Terms by Frequency</h4>';
                    html += '<ul>';
                    stats.terms_by_frequency.forEach(([term, freq]) => {
                        html += `<li>${term}: ${freq}</li>`;
                    });
                    html += '</ul>';
                }
                
                container.innerHTML = html;
            }
            
            async function loadIndexStructure() {
                const response = await fetch('/index/structure');
                if (response.ok) {
                    const structure = await response.json();
                    displayIndexStructure(structure);
                }
            }
            
            function displayIndexStructure(structure) {
                const container = document.getElementById('indexStructure');
                
                let html = '<h4>Inverted Index Sample (Top Terms)</h4>';
                html += '<pre>' + JSON.stringify(structure.inverted_index, null, 2) + '</pre>';
                
                html += '<h4>Document Information</h4>';
                html += '<pre>' + JSON.stringify(structure.document_info, null, 2) + '</pre>';
                
                html += '<h4>BM25 Parameters</h4>';
                html += '<pre>' + JSON.stringify(structure.bm25_params, null, 2) + '</pre>';
                
                container.innerHTML = html;
            }
            
            // Load statistics on page load
            window.onload = function() {
                loadStatistics();
            };
        </script>
    </body>
    </html>
    """
    return html_content


@app.post("/index", response_model=Dict)
async def index_document(request: IndexDocumentRequest):
    """Index a single document"""
    logger.info(f"Received index request for document of length {len(request.text)}")
    if request.doc_id:
        logger.info(f"External doc_id provided: {request.doc_id}")
    
    try:
        # Extract doc_id from metadata if not provided directly
        external_doc_id = request.doc_id
        if not external_doc_id and request.metadata and 'doc_id' in request.metadata:
            external_doc_id = request.metadata['doc_id']
        
        doc_id = search_engine.index_document(request.text, request.metadata, external_doc_id)
        logger.info(f"Document indexed successfully with ID {doc_id}")
        
        return {
            "success": True,
            "doc_id": doc_id,
            "message": f"Document indexed successfully with ID {doc_id}"
        }
    except Exception as e:
        logger.error(f"Error indexing document: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/index/batch", response_model=Dict)
async def index_batch(request: BatchIndexRequest):
    """Index multiple documents at once"""
    logger.info(f"Received batch index request for {len(request.documents)} documents")
    
    try:
        doc_ids = search_engine.index_batch(request.documents)
        logger.info(f"Batch indexing successful: {len(doc_ids)} documents indexed")
        
        return {
            "success": True,
            "doc_ids": doc_ids,
            "message": f"Successfully indexed {len(doc_ids)} documents"
        }
    except Exception as e:
        logger.error(f"Error in batch indexing: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/search", response_model=List[DocumentResponse])
async def search(request: SearchRequest):
    """Search for documents"""
    logger.info(f"Received search request: '{request.query}' (top_k={request.top_k})")
    
    try:
        results = search_engine.search(request.query, request.top_k)
        logger.info(f"Search completed, returning {len(results)} results")
        
        return results
    except Exception as e:
        logger.error(f"Error performing search: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/document/{doc_id}", response_model=DocumentResponse)
async def get_document(doc_id: str):
    """Retrieve a specific document by ID"""
    logger.info(f"Retrieving document {doc_id}")
    
    document = search_engine.get_document(doc_id)
    if document is None:
        logger.warning(f"Document {doc_id} not found")
        raise HTTPException(status_code=404, detail=f"Document {doc_id} not found")
    
    logger.info(f"Document {doc_id} retrieved successfully")
    return document


@app.get("/stats", response_model=Dict)
async def get_statistics():
    """Get index statistics"""
    logger.info("Retrieving index statistics")
    
    stats = search_engine.index.get_statistics()
    logger.info(f"Statistics retrieved: {stats['total_documents']} documents, "
                f"{stats['unique_terms']} unique terms")
    
    return stats


@app.get("/index/structure", response_model=Dict)
async def get_index_structure():
    """Get detailed index structure for visualization"""
    logger.info("Retrieving index structure")
    
    info = search_engine.get_index_info()
    logger.info("Index structure retrieved successfully")
    
    return info


@app.delete("/index", response_model=Dict)
async def clear_index():
    """Clear all indexed documents"""
    logger.warning("Clearing entire index")
    
    search_engine.clear_index()
    logger.info("Index cleared successfully")
    
    return {
        "success": True,
        "message": "Index cleared successfully"
    }


@app.get("/logs", response_model=Dict)
async def get_recent_logs(lines: int = Query(100, description="Number of log lines to retrieve")):
    """Get recent application logs for educational purposes"""
    # This is a simplified version - in production you'd read from a log file
    return {
        "message": "Logs are being written to console. Check terminal for detailed logs.",
        "log_level": "DEBUG",
        "description": "Educational logging is enabled. All indexing and search operations are logged."
    }


if __name__ == "__main__":
    import sys
    # Allow overriding port from command line
    port = 4241  # Default to 4241 to avoid conflicts with common services
    if len(sys.argv) > 1:
        try:
            port = int(sys.argv[1])
        except ValueError:
            pass
    
    logger.info("Starting Educational Sparse Vector Search Engine Server")
    logger.info(f"Server will run on http://localhost:{port}")
    logger.info(f"Visit http://localhost:{port} for the web interface")
    logger.info(f"API documentation available at http://localhost:{port}/docs")
    
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
