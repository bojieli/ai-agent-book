"""Browser automation tools using browser-use library."""

import asyncio
import json
from typing import Optional, Dict, Any, List
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

# Browser session singleton
_browser_session = None


async def init_browser(headless: bool = False, user_data_dir: Optional[str] = None):
    """Initialize browser session."""
    global _browser_session
    
    if _browser_session is not None:
        return _browser_session
    
    try:
        from browser_use import Browser
        from browser_use.browser.profile import BrowserProfile
        
        # Create browser profile
        profile_data = {
            'headless': headless,
            'keep_alive': True,
        }
        
        if user_data_dir:
            profile_data['user_data_dir'] = str(Path(user_data_dir).expanduser())
        
        profile = BrowserProfile(**profile_data)
        
        # Create browser session
        browser = Browser(browser_profile=profile)
        await browser.start()
        
        _browser_session = browser
        
        # Note: ChatOpenAI is initialized on-demand in browser_execute_task()
        # to avoid Pydantic v2 initialization issues during browser startup
        
        logger.info("Browser session initialized successfully")
        return _browser_session
        
    except Exception as e:
        logger.error(f"Failed to initialize browser: {e}")
        raise


async def close_browser():
    """Close browser session."""
    global _browser_session
    
    if _browser_session:
        try:
            await _browser_session.close()
            _browser_session = None
            logger.info("Browser session closed")
        except Exception as e:
            logger.error(f"Error closing browser: {e}")


async def browser_navigate(url: str, new_tab: bool = False) -> Dict[str, Any]:
    """Navigate to a URL in the browser.
    
    Args:
        url: The URL to navigate to
        new_tab: Whether to open in a new tab
        
    Returns:
        Dictionary with success status and page information
    """
    try:
        browser = await init_browser()
        
        if new_tab:
            page = await browser.new_page(url)
        else:
            page = await browser.get_current_page()
            await page.goto(url)
        
        return {
            "success": True,
            "url": url,
            "title": page.title if hasattr(page, 'title') else "N/A",
            "message": f"Successfully navigated to {url}"
        }
        
    except Exception as e:
        logger.error(f"Browser navigation failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": f"Failed to navigate to {url}"
        }


async def browser_get_content(selector: Optional[str] = None) -> Dict[str, Any]:
    """Get content from the current page.
    
    Args:
        selector: Optional CSS selector to extract specific content
        
    Returns:
        Dictionary with page content
    """
    try:
        browser = await init_browser()
        page = await browser.get_current_page()
        
        if selector:
            # Get specific elements
            elements = await page.get_elements_by_css_selector(selector)
            content = []
            for elem in elements[:10]:  # Limit to 10 elements
                try:
                    text = await elem.get_text()
                    content.append(text)
                except:
                    pass
            
            return {
                "success": True,
                "content": content,
                "selector": selector,
                "count": len(content)
            }
        else:
            # Get page text content
            content = await page.get_text()
            return {
                "success": True,
                "content": content[:5000],  # Limit to 5000 characters
                "message": "Retrieved page content"
            }
            
    except Exception as e:
        logger.error(f"Failed to get content: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to retrieve page content"
        }


async def browser_execute_task(task: str, max_steps: int = 20) -> Dict[str, Any]:
    """Execute a high-level browser task using the browser-use agent.
    
    Args:
        task: Natural language description of the task to perform
        max_steps: Maximum number of steps the agent can take
        
    Returns:
        Dictionary with task execution results
    """
    try:
        from browser_use import Agent
        from langchain_openai import ChatOpenAI
        import os
        
        browser = await init_browser()
        
        # Create LLM
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            return {
                "success": False,
                "error": "OPENAI_API_KEY not configured",
                "message": "Cannot execute autonomous tasks without LLM configuration"
            }
        
        llm = ChatOpenAI(
            model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
            api_key=api_key,
            temperature=0.7,
        )
        
        # Create and run agent
        agent = Agent(
            task=task,
            llm=llm,
            browser_session=browser,
            max_steps=max_steps,
        )
        
        result = await agent.run()
        
        return {
            "success": True,
            "task": task,
            "result": str(result),
            "message": "Task completed successfully"
        }
        
    except Exception as e:
        logger.error(f"Browser task execution failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "task": task,
            "message": "Failed to execute browser task"
        }


async def browser_screenshot(full_page: bool = False) -> Dict[str, Any]:
    """Take a screenshot of the current page.
    
    Args:
        full_page: Whether to capture the full page or just viewport
        
    Returns:
        Dictionary with screenshot path and metadata
    """
    try:
        browser = await init_browser()
        page = await browser.get_current_page()
        
        # Create screenshots directory
        screenshot_dir = Path.home() / ".config" / "collaboration-tools" / "screenshots"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        # Generate filename with timestamp
        import time
        filename = f"screenshot_{int(time.time())}.png"
        filepath = screenshot_dir / filename
        
        # Take screenshot
        await page.screenshot(path=str(filepath), full_page=full_page)
        
        return {
            "success": True,
            "path": str(filepath),
            "full_page": full_page,
            "message": f"Screenshot saved to {filepath}"
        }
        
    except Exception as e:
        logger.error(f"Screenshot failed: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to take screenshot"
        }


async def browser_list_tabs() -> Dict[str, Any]:
    """List all open browser tabs.
    
    Returns:
        Dictionary with list of tabs
    """
    try:
        browser = await init_browser()
        pages = await browser.get_pages()
        
        tabs = []
        for idx, page in enumerate(pages):
            tabs.append({
                "index": idx,
                "url": page.url if hasattr(page, 'url') else "N/A",
                "title": page.title if hasattr(page, 'title') else "N/A"
            })
        
        return {
            "success": True,
            "tabs": tabs,
            "count": len(tabs),
            "message": f"Found {len(tabs)} open tabs"
        }
        
    except Exception as e:
        logger.error(f"Failed to list tabs: {e}")
        return {
            "success": False,
            "error": str(e),
            "message": "Failed to list browser tabs"
        }
