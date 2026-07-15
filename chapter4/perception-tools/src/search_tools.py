"""
Search tools: knowledge base, web search, and file download.
"""
import json
import logging
import os
import time
import traceback
from pathlib import Path
from typing import Union

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.types import TextContent
from pydantic import BaseModel, Field

from base import ActionResponse, is_url, download_file_from_url


load_dotenv()


class SearchResult(BaseModel):
    """Individual search result with structured data."""
    
    id: str
    title: str
    url: str
    snippet: str
    source: str


class SearchMetadata(BaseModel):
    """Metadata for search operations."""
    
    query: str
    search_engine: str
    total_results: int
    search_time: float | None = None
    language: str = "en"
    country: str = "us"


async def search_web(
    query: str,
    num_results: int = 5,
    region: str = "wt-wt"
) -> Union[str, TextContent]:
    """
    Search the web using DuckDuckGo (free, no API key required).
    
    Args:
        query: The search query string
        num_results: Number of results to return (1-10)
        region: Region code (e.g., 'us-en', 'uk-en', 'wt-wt' for worldwide)
        
    Returns:
        TextContent with search results
    """
    try:
        if not query or not query.strip():
            raise ValueError("Search query cannot be empty")
        
        validated_num_results = max(1, min(num_results, 10))
        
        logging.info(f"🔍 Searching for: '{query}'")
        start_time = time.time()
        
        # Use DuckDuckGo HTML version for scraping
        url = "https://html.duckduckgo.com/html/"
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        
        data = {
            "q": query.strip(),
            "kl": region
        }
        
        response = requests.post(url, data=data, headers=headers, timeout=15)
        response.raise_for_status()
        
        search_time = time.time() - start_time
        
        # Parse HTML results
        soup = BeautifulSoup(response.text, 'html.parser')
        result_divs = soup.find_all('div', class_='result')
        
        search_results = []
        for i, result_div in enumerate(result_divs[:validated_num_results]):
            try:
                # Extract title and URL
                title_tag = result_div.find('a', class_='result__a')
                if not title_tag:
                    continue
                    
                title = title_tag.get_text(strip=True)
                url_link = title_tag.get('href', '')
                
                # Extract snippet
                snippet_tag = result_div.find('a', class_='result__snippet')
                snippet = snippet_tag.get_text(strip=True) if snippet_tag else ""
                
                result = SearchResult(
                    id=f"ddg-{i}",
                    title=title,
                    url=url_link,
                    snippet=snippet,
                    source="duckduckgo"
                )
                search_results.append(result)
            except Exception as e:
                logging.warning(f"Error parsing search result {i}: {e}")
                continue
        
        metadata = SearchMetadata(
            query=query,
            search_engine="duckduckgo",
            total_results=len(search_results),
            search_time=search_time,
            language="en",
            country=region
        )
        
        formatted_content = {
            "query": query,
            "results": [result.model_dump() for result in search_results],
            "count": len(search_results)
        }
        
        logging.info(f"✅ Found {len(search_results)} results in {search_time:.2f}s")
        
        action_response = ActionResponse(
            success=True,
            message=formatted_content,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Search operation failed: {str(e)}"
        logging.error(f"Search error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "search_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def download_file(
    url: str,
    output_path: str,
    overwrite: bool = False,
    timeout: int = 180
) -> Union[str, TextContent]:
    """
    Download a file from a URL.
    
    Args:
        url: URL to download from
        output_path: Local path to save the file
        overwrite: Whether to overwrite existing files
        timeout: Download timeout in seconds
        
    Returns:
        TextContent with download result
    """
    try:
        if not url.startswith(("http://", "https://")):
            raise ValueError("Only HTTP/HTTPS URLs are supported")
        
        output_file = Path(output_path).expanduser().resolve()
        
        if output_file.exists() and not overwrite:
            raise ValueError(f"File already exists: {output_file}. Use overwrite=True to replace.")
        
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.info(f"📥 Downloading from: {url}")
        start_time = time.time()
        
        temp_path, content = download_file_from_url(url, timeout=timeout)
        
        # Move to final destination
        with open(output_file, 'wb') as f:
            f.write(content)
        
        # Clean up temp file
        Path(temp_path).unlink(missing_ok=True)
        
        duration = time.time() - start_time
        file_size = len(content)
        
        logging.info(f"✅ Downloaded {file_size / 1024:.2f} KB in {duration:.2f}s")
        
        action_response = ActionResponse(
            success=True,
            message=f"Successfully downloaded file to {output_file}",
            metadata={
                "url": url,
                "output_path": str(output_file),
                "file_size_bytes": file_size,
                "duration_seconds": duration
            }
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Download failed: {str(e)}"
        logging.error(f"Download error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "download_error", "url": url}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def search_knowledge_base(
    query: str,
    knowledge_base_path: str,
    top_k: int = 5
) -> Union[str, TextContent]:
    """
    Search a local knowledge base using simple text matching.
    
    Args:
        query: Search query
        knowledge_base_path: Path to knowledge base directory
        top_k: Number of top results to return
        
    Returns:
        TextContent with search results
    """
    try:
        kb_path = Path(knowledge_base_path).expanduser().resolve()
        
        if not kb_path.exists():
            raise FileNotFoundError(f"Knowledge base not found: {kb_path}")
        
        if not kb_path.is_dir():
            raise ValueError(f"Knowledge base path must be a directory: {kb_path}")
        
        logging.info(f"🔍 Searching knowledge base: {kb_path}")
        
        # Simple file search - find files containing the query
        results = []
        query_lower = query.lower()
        
        for file_path in kb_path.rglob("*"):
            if file_path.is_file() and file_path.suffix in [".txt", ".md", ".json"]:
                try:
                    content = file_path.read_text(encoding="utf-8", errors="ignore")
                    if query_lower in content.lower():
                        # Get snippet around first occurrence
                        idx = content.lower().index(query_lower)
                        start = max(0, idx - 100)
                        end = min(len(content), idx + 200)
                        snippet = content[start:end].strip()
                        
                        results.append({
                            "file": str(file_path.relative_to(kb_path)),
                            "snippet": snippet,
                            "relevance": content.lower().count(query_lower)
                        })
                except Exception as e:
                    logging.warning(f"Error reading {file_path}: {e}")
                    continue
        
        # Sort by relevance and limit
        results.sort(key=lambda x: x["relevance"], reverse=True)
        results = results[:top_k]
        
        logging.info(f"✅ Found {len(results)} results")
        
        action_response = ActionResponse(
            success=True,
            message={
                "query": query,
                "results": results,
                "total_found": len(results)
            },
            metadata={
                "knowledge_base": str(kb_path),
                "top_k": top_k
            }
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Knowledge base search failed: {str(e)}"
        logging.error(f"KB search error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "kb_search_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
