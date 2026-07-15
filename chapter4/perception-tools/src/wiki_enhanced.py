"""
Enhanced Wikipedia tools with full article access.
Based on AWorld wiki-server complete implementation.
"""
import json
import logging
import traceback
import calendar
from datetime import datetime
from typing import Union

import requests
import wikipedia
from dotenv import load_dotenv
from mcp.types import TextContent

from base import ActionResponse


load_dotenv()


async def get_article_content(
    title: str,
    language: str = "en"
) -> Union[str, TextContent]:
    """
    Get full Wikipedia article content.
    
    Args:
        title: Article title
        language: Language code
        
    Returns:
        TextContent with full article
    """
    try:
        wikipedia.set_lang(language)
        
        logging.info(f"📚 Getting full article: {title}")
        
        page = wikipedia.page(title, auto_suggest=True)
        
        result = {
            "title": page.title,
            "url": page.url,
            "content": page.content,
            "summary": page.summary,
            "categories": page.categories[:20] if page.categories else [],
            "links": page.links[:50] if page.links else [],
            "images": page.images[:10] if page.images else []
        }
        
        logging.info(f"✅ Retrieved article: {len(page.content)} chars")
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"language": language, "title": page.title}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Failed to get article: {str(e)}"
        logging.error(f"Wiki error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "wiki_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_article_categories(
    title: str,
    language: str = "en"
) -> Union[str, TextContent]:
    """
    Get categories for Wikipedia article.
    
    Args:
        title: Article title
        language: Language code
        
    Returns:
        TextContent with categories
    """
    try:
        wikipedia.set_lang(language)
        page = wikipedia.page(title, auto_suggest=True)
        
        result = {
            "title": page.title,
            "categories": page.categories,
            "count": len(page.categories)
        }
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"language": language}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Failed: {str(e)}",
            metadata={"error_type": "wiki_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_article_links(
    title: str,
    language: str = "en"
) -> Union[str, TextContent]:
    """
    Get links from Wikipedia article.
    
    Args:
        title: Article title
        language: Language code
        
    Returns:
        TextContent with links
    """
    try:
        wikipedia.set_lang(language)
        page = wikipedia.page(title, auto_suggest=True)
        
        result = {
            "title": page.title,
            "links": page.links[:100],  # Limit to 100
            "total_links": len(page.links),
            "count": min(100, len(page.links))
        }
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"language": language}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Failed: {str(e)}",
            metadata={"error_type": "wiki_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_article_history(
    title: str,
    date: str,
    language: str = "en"
) -> Union[str, TextContent]:
    """
    Get historical version of Wikipedia article.
    
    Args:
        title: Article title
        date: Target date (YYYY/MM/DD)
        language: Language code
        
    Returns:
        TextContent with historical content
    """
    try:
        logging.info(f"📚 Getting historical version: {title} at {date}")
        
        # Parse date
        date_parts = date.split("/")
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2]) if len(date_parts) > 2 else calendar.monthrange(year, month)[1]
        
        target_date = datetime(year, month, day)
        
        # Get page revisions via Wikipedia API
        params = {
            "action": "query",
            "prop": "revisions",
            "titles": title,
            "rvprop": "ids|timestamp|user|comment|content",
            "rvlimit": 1,
            "rvdir": "older",
            "rvstart": target_date.isoformat(),
            "format": "json"
        }
        
        api_url = f"https://{language}.wikipedia.org/w/api.php"
        response = requests.get(api_url, params=params, timeout=10)
        data = response.json()
        
        page = next(iter(data["query"]["pages"].values()))
        
        if "revisions" in page:
            revision = page["revisions"][0]
            actual_date = datetime.fromisoformat(revision["timestamp"].replace("Z", "+00:00"))
            
            result = {
                "title": title,
                "requested_date": date,
                "actual_date": actual_date.strftime("%Y/%m/%d"),
                "content": revision["*"],
                "editor": revision["user"],
                "comment": revision.get("comment", "")
            }
            
            action_response = ActionResponse(
                success=True,
                message=result,
                metadata={"language": language}
            )
        else:
            action_response = ActionResponse(
                success=False,
                message="No historical version found",
                metadata={"error_type": "not_found"}
            )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Failed: {str(e)}",
            metadata={"error_type": "wiki_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
