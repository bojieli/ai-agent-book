"""
Enhanced Google Search tools.
Based on AWorld google-search server.
"""
import json
import logging
import os
import traceback
from typing import Union

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.types import TextContent

from base import ActionResponse


load_dotenv()


async def google_search_api(
    query: str,
    num_results: int = 5,
    safe_search: bool = True,
    language: str = "en",
    country: str = "us"
) -> Union[str, TextContent]:
    """
    Search Google using Custom Search API.
    
    Args:
        query: Search query
        num_results: Number of results (1-10)
        safe_search: Enable safe search
        language: Language code
        country: Country code
        
    Returns:
        TextContent with search results
    """
    try:
        api_key = os.getenv("GOOGLE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        
        if not api_key or not cse_id:
            return await _fallback_google_search(query, num_results)
        
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": api_key,
            "cx": cse_id,
            "q": query,
            "num": min(num_results, 10),
            "safe": "active" if safe_search else "off",
            "hl": language,
            "gl": country
        }
        
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
        
        results = []
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "title": item.get("title"),
                    "url": item.get("link"),
                    "snippet": item.get("snippet"),
                    "display_url": item.get("displayLink")
                })
        
        action_response = ActionResponse(
            success=True,
            message={"query": query, "results": results, "count": len(results)},
            metadata={"engine": "google_api", "results_count": len(results)}
        )
        
        logging.info(f"✅ Google Search: {len(results)} results")
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        logging.error(f"Google API search failed: {traceback.format_exc()}")
        return await _fallback_google_search(query, num_results)


async def _fallback_google_search(query: str, num_results: int) -> TextContent:
    """Fallback to DuckDuckGo if Google API not available."""
    try:
        logging.info("Using DuckDuckGo fallback")
        
        url = "https://html.duckduckgo.com/html/"
        headers = {"User-Agent": "Mozilla/5.0"}
        data = {"q": query}
        
        response = requests.post(url, data=data, headers=headers, timeout=15)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        result_divs = soup.find_all('div', class_='result')
        
        results = []
        for i, div in enumerate(result_divs[:num_results]):
            title_tag = div.find('a', class_='result__a')
            if title_tag:
                results.append({
                    "title": title_tag.get_text(strip=True),
                    "url": title_tag.get('href', ''),
                    "snippet": div.find('a', class_='result__snippet').get_text(strip=True) if div.find('a', class_='result__snippet') else ""
                })
        
        action_response = ActionResponse(
            success=True,
            message={"query": query, "results": results, "count": len(results)},
            metadata={"engine": "duckduckgo_fallback"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Search failed: {str(e)}",
            metadata={"error_type": "search_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def read_webpage_content(
    url: str,
    extract_links: bool = False
) -> Union[str, TextContent]:
    """
    Read and extract content from webpage.
    
    Args:
        url: URL to read
        extract_links: Whether to extract links
        
    Returns:
        TextContent with webpage content
    """
    try:
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove scripts and styles
        for script in soup(["script", "style"]):
            script.decompose()
        
        text = soup.get_text()
        lines = (line.strip() for line in text.splitlines())
        text = ' '.join(line for line in lines if line)
        
        result = {
            "url": url,
            "title": soup.title.string if soup.title else "No title",
            "text": text[:10000],
            "text_length": len(text)
        }
        
        if extract_links:
            links = []
            for link in soup.find_all('a', href=True)[:50]:
                links.append({
                    "text": link.get_text().strip(),
                    "href": link['href']
                })
            result["links"] = links
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"url": url}
        )
        
        logging.info(f"✅ Read webpage: {len(text)} chars")
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Failed to read webpage: {str(e)}",
            metadata={"error_type": "webpage_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
