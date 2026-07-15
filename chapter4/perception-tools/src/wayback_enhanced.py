"""
Enhanced Wayback Machine tools.
"""
import json
import logging
import traceback
from typing import Union

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from mcp.types import TextContent
from waybackpy import WaybackMachineCDXServerAPI

from base import ActionResponse


load_dotenv()


async def get_archived_content(
    url: str,
    timestamp: str
) -> Union[str, TextContent]:
    """
    Get content from archived webpage.
    
    Args:
        url: URL to retrieve
        timestamp: Wayback timestamp (YYYYMMDDhhmmss)
        
    Returns:
        TextContent with archived content
    """
    try:
        logging.info(f"🕰️ Getting archived content: {url} at {timestamp}")
        
        # Query for closest snapshot
        cdx_api = WaybackMachineCDXServerAPI(url)
        snapshot = cdx_api.near(wayback_machine_timestamp=timestamp)
        
        if not snapshot:
            raise ValueError("No archived version found")
        
        # Fetch content
        response = requests.get(snapshot.archive_url, timeout=30)
        response.raise_for_status()
        
        # Extract text
        soup = BeautifulSoup(response.content, 'html.parser')
        text = soup.get_text(separator=" ", strip=True)
        
        result = {
            "url": url,
            "timestamp": timestamp,
            "actual_timestamp": snapshot.timestamp,
            "archive_url": snapshot.archive_url,
            "content": text[:10000],  # Limit to 10k chars
            "content_length": len(text)
        }
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"url": url}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Failed: {str(e)}",
            metadata={"error_type": "wayback_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
