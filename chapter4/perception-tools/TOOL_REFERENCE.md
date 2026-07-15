# Tool Reference Guide

Complete reference for all 22 perception tools available in this MCP server.

## Table of Contents

- [Search Tools (3)](#search-tools)
- [Multimodal Understanding Tools (4)](#multimodal-understanding-tools)
- [File System Tools (3)](#file-system-tools)
- [Public Data Source Tools (6)](#public-data-source-tools)
- [Private Data Source Tools (2)](#private-data-source-tools)

---

## Search Tools

### 1. web_search

Search the web using Google Custom Search API.

**Parameters:**
- `query` (string, required): Search query string
- `num_results` (int, default: 5): Number of results to return (1-10)
- `language` (string, default: "en"): Language code (en, zh, es, etc.)
- `country` (string, default: "us"): Country code (us, cn, uk, etc.)

**Returns:**
```json
{
  "success": true,
  "message": {
    "query": "Python programming",
    "results": [
      {
        "id": "google-0",
        "title": "Python.org",
        "url": "https://www.python.org",
        "snippet": "Official Python website...",
        "source": "google"
      }
    ],
    "count": 5
  },
  "metadata": {
    "query": "Python programming",
    "search_engine": "google",
    "total_results": 5,
    "search_time": 0.45
  }
}
```

**Requirements:** Google API Key, Google CSE ID

---

### 2. download

Download a file from a URL to local storage.

**Parameters:**
- `url` (string, required): HTTP/HTTPS URL to download from
- `output_path` (string, required): Local path to save the file
- `overwrite` (bool, default: false): Whether to overwrite existing files
- `timeout` (int, default: 180): Download timeout in seconds

**Returns:**
```json
{
  "success": true,
  "message": "Successfully downloaded file to /path/to/file.pdf",
  "metadata": {
    "url": "https://example.com/file.pdf",
    "output_path": "/path/to/file.pdf",
    "file_size_bytes": 1048576,
    "duration_seconds": 2.3
  }
}
```

**Limits:** Maximum 100MB file size by default

---

### 3. knowledge_base_search

Search a local knowledge base directory for relevant documents.

**Parameters:**
- `query` (string, required): Search query
- `knowledge_base_path` (string, required): Path to knowledge base directory
- `top_k` (int, default: 5): Number of top results to return

**Returns:**
```json
{
  "success": true,
  "message": {
    "query": "machine learning",
    "results": [
      {
        "file": "docs/ml_basics.md",
        "snippet": "...machine learning algorithms...",
        "relevance": 12
      }
    ],
    "total_found": 3
  },
  "metadata": {
    "knowledge_base": "/path/to/kb",
    "top_k": 5
  }
}
```

**Supported file types:** .txt, .md, .json

---

## Multimodal Understanding Tools

### 4. webpage_reader

Extract content from web pages including text and links.

**Parameters:**
- `url` (string, required): URL of the webpage
- `extract_text` (bool, default: true): Whether to extract main text content
- `extract_links` (bool, default: false): Whether to extract all links

**Returns:**
```json
{
  "success": true,
  "message": {
    "url": "https://example.com",
    "title": "Example Page",
    "text": "Page content...",
    "text_length": 5000,
    "links": []
  },
  "metadata": {
    "url": "https://example.com"
  }
}
```

---

### 5. document_reader

Extract content from documents (PDF, DOCX, PPTX).

**Parameters:**
- `file_path` (string, required): Path to document file or URL
- `extract_images` (bool, default: false): Whether to extract images

**Returns:**
```json
{
  "success": true,
  "message": {
    "file_name": "document.pdf",
    "file_type": "pdf",
    "page_count": 10,
    "text": "Document content...",
    "text_length": 15000
  },
  "metadata": {
    "file_path": "/path/to/document.pdf",
    "file_type": ".pdf"
  }
}
```

**Supported formats:** PDF, DOCX, PPTX

---

### 6. image_parser

Parse and analyze image files.

**Parameters:**
- `image_path` (string, required): Path to image file or URL
- `use_llm` (bool, default: true): Use LLM for image understanding

**Returns:**
```json
{
  "success": true,
  "message": {
    "file_name": "image.jpg",
    "format": "JPEG",
    "mode": "RGB",
    "size": [1920, 1080],
    "width": 1920,
    "height": 1080,
    "note": "Full base64 data available for vision API analysis"
  },
  "metadata": {
    "file_path": "/path/to/image.jpg"
  }
}
```

**Supported formats:** JPG, PNG, GIF, BMP, TIFF, WEBP

---

### 7. video_parser

Extract metadata and information from video files.

**Parameters:**
- `video_path` (string, required): Path to video file or URL
- `extract_frames` (bool, default: false): Extract sample frames
- `frame_interval` (int, default: 30): Extract one frame every N seconds

**Returns:**
```json
{
  "success": true,
  "message": {
    "file_name": "video.mp4",
    "duration_seconds": 120.5,
    "fps": 30.0,
    "frame_count": 3615,
    "resolution": "1920x1080",
    "width": 1920,
    "height": 1080
  },
  "metadata": {
    "file_path": "/path/to/video.mp4"
  }
}
```

**Supported formats:** MP4, AVI, MOV, MKV, WEBM

---

## File System Tools

### 8. file_reader

Read a file and return its contents.

**Parameters:**
- `file_path` (string, required): Path to the file
- `encoding` (string, default: "utf-8"): File encoding
- `max_length` (int, default: 50000): Maximum characters to read

**Returns:**
```json
{
  "success": true,
  "message": {
    "file_path": "/path/to/file.txt",
    "content": "File contents...",
    "size_bytes": 1024,
    "truncated": false,
    "encoding": "utf-8"
  },
  "metadata": {
    "file_path": "/path/to/file.txt"
  }
}
```

---

### 9. grep

Search for patterns in files using regular expressions.

**Parameters:**
- `pattern` (string, required): Regular expression pattern to search for
- `directory` (string, required): Directory to search in
- `file_pattern` (string, default: "*"): File pattern to match (e.g., "*.py")
- `recursive` (bool, default: true): Search recursively
- `case_sensitive` (bool, default: false): Case-sensitive search
- `max_results` (int, default: 100): Maximum number of results

**Returns:**
```json
{
  "success": true,
  "message": {
    "pattern": "def.*:",
    "results": [
      {
        "file": "src/main.py",
        "line_number": 42,
        "line": "def my_function():",
        "absolute_path": "/full/path/to/src/main.py"
      }
    ],
    "total_found": 15,
    "truncated": false
  },
  "metadata": {
    "directory": "/path/to/search",
    "file_pattern": "*.py",
    "recursive": true
  }
}
```

---

### 10. text_summarizer

Summarize long text content.

**Parameters:**
- `text` (string, required): Text to summarize
- `max_length` (int, default: 500): Target summary length in characters
- `use_llm` (bool, default: true): Use LLM for better summarization

**Returns:**
```json
{
  "success": true,
  "message": {
    "original_length": 5000,
    "summary_length": 500,
    "summary": "Summary text...",
    "method": "extractive",
    "compression_ratio": 0.1
  },
  "metadata": {
    "method": "extractive"
  }
}
```

---

## Public Data Source Tools

### 11. weather

Get current weather information for a location.

**Parameters:**
- `location` (string, required): City name, coordinates, or zip code
- `units` (string, default: "metric"): Temperature units (metric/imperial/standard)

**Returns:**
```json
{
  "success": true,
  "message": {
    "location": "London",
    "country": "GB",
    "temperature": 15.5,
    "feels_like": 14.2,
    "humidity": 72,
    "pressure": 1013,
    "weather": "Clouds",
    "description": "overcast clouds",
    "wind_speed": 5.2,
    "units": "metric"
  },
  "metadata": {
    "location": "London",
    "units": "metric"
  }
}
```

**Requirements:** OpenWeather API key

---

### 12. stock_price

Get current stock price and market information.

**Parameters:**
- `symbol` (string, required): Stock ticker symbol (e.g., "AAPL", "TSLA")
- `interval` (string, default: "1d"): Data interval

**Returns:**
```json
{
  "success": true,
  "message": {
    "symbol": "AAPL",
    "currency": "USD",
    "current_price": 175.43,
    "previous_close": 174.20,
    "open": 174.50,
    "day_high": 176.00,
    "day_low": 173.80,
    "volume": 52341000,
    "exchange": "NASDAQ"
  },
  "metadata": {
    "symbol": "AAPL"
  }
}
```

**Source:** Yahoo Finance (no API key required)

---

### 13. currency_converter

Convert between different currencies.

**Parameters:**
- `amount` (float, required): Amount to convert
- `from_currency` (string, required): Source currency code (e.g., "USD")
- `to_currency` (string, required): Target currency code (e.g., "EUR")

**Returns:**
```json
{
  "success": true,
  "message": {
    "amount": 100.0,
    "from_currency": "USD",
    "to_currency": "EUR",
    "exchange_rate": 0.92,
    "converted_amount": 92.0,
    "timestamp": "2024-01-15"
  },
  "metadata": {
    "rate": 0.92
  }
}
```

**Source:** Exchange Rate API (no API key required)

---

### 14. wikipedia_search

Search Wikipedia and retrieve article summaries.

**Parameters:**
- `query` (string, required): Search query
- `language` (string, default: "en"): Wikipedia language (en, zh, es, etc.)
- `sentences` (int, default: 5): Number of sentences in summary

**Returns:**
```json
{
  "success": true,
  "message": {
    "title": "Artificial Intelligence",
    "url": "https://en.wikipedia.org/wiki/Artificial_intelligence",
    "summary": "Artificial intelligence (AI) is...",
    "language": "en",
    "search_results": ["Artificial Intelligence", "AI", "Machine Learning"]
  },
  "metadata": {
    "query": "artificial intelligence",
    "language": "en"
  }
}
```

---

### 15. arxiv_search

Search ArXiv for academic papers.

**Parameters:**
- `query` (string, required): Search query
- `max_results` (int, default: 5): Maximum number of papers
- `sort_by` (string, default: "relevance"): Sort method (relevance/lastUpdatedDate/submittedDate)

**Returns:**
```json
{
  "success": true,
  "message": {
    "query": "machine learning",
    "papers": [
      {
        "title": "Deep Learning Paper",
        "authors": ["John Doe", "Jane Smith"],
        "summary": "Paper summary...",
        "published": "2024-01-15T00:00:00",
        "url": "https://arxiv.org/abs/2401.12345",
        "pdf_url": "https://arxiv.org/pdf/2401.12345",
        "categories": ["cs.LG", "cs.AI"]
      }
    ],
    "count": 5
  },
  "metadata": {
    "query": "machine learning",
    "max_results": 5
  }
}
```

---

### 16. wayback_search

Search Wayback Machine for archived versions of web pages.

**Parameters:**
- `url` (string, required): URL to search for
- `year` (int, optional): Filter results by specific year
- `limit` (int, default: 10): Maximum number of snapshots

**Returns:**
```json
{
  "success": true,
  "message": {
    "url": "https://example.com",
    "snapshots": [
      {
        "timestamp": "2024-01-15T10:30:00",
        "url": "https://web.archive.org/web/20240115103000/https://example.com",
        "status_code": "200",
        "mime_type": "text/html"
      }
    ],
    "count": 10
  },
  "metadata": {
    "url": "https://example.com",
    "year": null
  }
}
```

---

## Private Data Source Tools

### 17. calendar_events

Get events from Google Calendar.

**Parameters:**
- `start_date` (string, optional): Start date in ISO format (defaults to today)
- `end_date` (string, optional): End date in ISO format (defaults to 7 days from now)
- `calendar_id` (string, default: "primary"): Calendar ID
- `max_results` (int, default: 10): Maximum number of events

**Returns:**
```json
{
  "success": true,
  "message": {
    "events": [
      {
        "id": "event_id_123",
        "summary": "Team Meeting",
        "start": "2024-01-15T10:00:00Z",
        "end": "2024-01-15T11:00:00Z",
        "location": "Conference Room A",
        "description": "Weekly team sync",
        "attendees": ["john@example.com", "jane@example.com"]
      }
    ],
    "count": 5,
    "calendar_id": "primary"
  },
  "metadata": {
    "start_date": "2024-01-15T00:00:00Z",
    "end_date": "2024-01-22T00:00:00Z"
  }
}
```

**Requirements:** Google Calendar API OAuth2 authentication

---

### 18. notion_search

Search Notion workspace or specific database.

**Parameters:**
- `query` (string, required): Search query
- `database_id` (string, optional): Specific database ID to search
- `page_size` (int, default: 10): Results per page

**Returns:**
```json
{
  "success": true,
  "message": {
    "query": "project notes",
    "results": [
      {
        "id": "page_id_123",
        "type": "page",
        "url": "https://notion.so/page_id_123",
        "title": "Project Planning",
        "created_time": "2024-01-15T10:00:00Z",
        "last_edited_time": "2024-01-16T14:30:00Z"
      }
    ],
    "count": 3
  },
  "metadata": {
    "database_id": null
  }
}
```

**Requirements:** Notion API key

---

## Error Response Format

All tools return errors in a standardized format:

```json
{
  "success": false,
  "message": "Error description here",
  "metadata": {
    "error_type": "specific_error_type"
  }
}
```

Common error types:
- `missing_credentials`: API keys not configured
- `api_request_failed`: External API request failed
- `file_not_found`: Specified file doesn't exist
- `invalid_parameters`: Invalid input parameters
- `timeout`: Operation timed out
- `permission_denied`: Insufficient permissions
