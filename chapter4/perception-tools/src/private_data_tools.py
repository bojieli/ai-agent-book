"""
Private data source tools: Google Calendar, Notion.
"""
import json
import logging
import os
import traceback
from datetime import datetime, timedelta
from typing import Union

from dotenv import load_dotenv
from mcp.types import TextContent

from base import ActionResponse


load_dotenv()


async def get_calendar_events(
    start_date: str | None = None,
    end_date: str | None = None,
    calendar_id: str = "primary",
    max_results: int = 10
) -> Union[str, TextContent]:
    """
    Get events from Google Calendar.
    
    Args:
        start_date: Start date (ISO format, defaults to today)
        end_date: End date (ISO format, defaults to 7 days from now)
        calendar_id: Calendar ID (default: primary)
        max_results: Maximum number of events to return
        
    Returns:
        TextContent with calendar events
    """
    try:
        from google.oauth2.credentials import Credentials
        from googleapiclient.discovery import build
        from google.auth.transport.requests import Request
        import pickle
        
        logging.info(f"📅 Getting calendar events")
        
        # Token file path
        token_path = os.path.expanduser("~/.perception-tools/google_token.pickle")
        
        if not os.path.exists(token_path):
            return ActionResponse(
                success=False,
                message="Google Calendar not configured. Please run setup to authenticate.",
                metadata={"error_type": "missing_credentials"}
            )
        
        # Load credentials
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)
        
        # Refresh if expired
        if creds.expired and creds.refresh_token:
            creds.refresh(Request())
        
        service = build('calendar', 'v3', credentials=creds)
        
        # Set default date range if not provided
        if not start_date:
            start_date = datetime.utcnow().isoformat() + 'Z'
        if not end_date:
            end_dt = datetime.utcnow() + timedelta(days=7)
            end_date = end_dt.isoformat() + 'Z'
        
        # Query calendar
        events_result = service.events().list(
            calendarId=calendar_id,
            timeMin=start_date,
            timeMax=end_date,
            maxResults=max_results,
            singleEvents=True,
            orderBy='startTime'
        ).execute()
        
        events = events_result.get('items', [])
        
        formatted_events = []
        for event in events:
            start = event['start'].get('dateTime', event['start'].get('date'))
            end = event['end'].get('dateTime', event['end'].get('date'))
            
            formatted_events.append({
                "id": event['id'],
                "summary": event.get('summary', 'No title'),
                "start": start,
                "end": end,
                "location": event.get('location'),
                "description": event.get('description'),
                "attendees": [a.get('email') for a in event.get('attendees', [])]
            })
        
        logging.info(f"✅ Found {len(formatted_events)} calendar events")
        
        action_response = ActionResponse(
            success=True,
            message={
                "events": formatted_events,
                "count": len(formatted_events),
                "calendar_id": calendar_id
            },
            metadata={"start_date": start_date, "end_date": end_date}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except ImportError:
        error_msg = "Google Calendar libraries not installed. Install with: pip install google-auth-oauthlib google-auth-httplib2 google-api-python-client"
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "missing_library"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Calendar query failed: {str(e)}"
        logging.error(f"Calendar error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "calendar_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def search_notion(
    query: str,
    database_id: str | None = None,
    page_size: int = 10
) -> Union[str, TextContent]:
    """
    Search Notion workspace or specific database.
    
    Args:
        query: Search query
        database_id: Optional specific database ID
        page_size: Number of results per page
        
    Returns:
        TextContent with Notion search results
    """
    try:
        from notion_client import Client
        
        logging.info(f"📝 Searching Notion for: {query}")
        
        api_key = os.getenv("NOTION_API_KEY")
        
        if not api_key:
            return ActionResponse(
                success=False,
                message="Notion API key not configured. Set NOTION_API_KEY.",
                metadata={"error_type": "missing_credentials"}
            )
        
        notion = Client(auth=api_key)
        
        if database_id:
            # Search specific database
            response = notion.databases.query(
                database_id=database_id,
                filter={
                    "property": "Name",
                    "rich_text": {
                        "contains": query
                    }
                },
                page_size=page_size
            )
        else:
            # Search entire workspace
            response = notion.search(
                query=query,
                page_size=page_size
            )
        
        results = []
        for item in response.get("results", []):
            result_data = {
                "id": item["id"],
                "type": item["object"],
                "url": item.get("url"),
                "created_time": item.get("created_time"),
                "last_edited_time": item.get("last_edited_time")
            }
            
            # Extract title/name
            if "properties" in item:
                for prop_name, prop_value in item["properties"].items():
                    if prop_value.get("type") == "title" and prop_value.get("title"):
                        title_parts = [t.get("plain_text", "") for t in prop_value["title"]]
                        result_data["title"] = "".join(title_parts)
                        break
            
            results.append(result_data)
        
        logging.info(f"✅ Found {len(results)} Notion items")
        
        action_response = ActionResponse(
            success=True,
            message={
                "query": query,
                "results": results,
                "count": len(results)
            },
            metadata={"database_id": database_id}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except ImportError:
        error_msg = "Notion SDK not installed. Install with: pip install notion-client"
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "missing_library"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Notion search failed: {str(e)}"
        logging.error(f"Notion error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "notion_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
