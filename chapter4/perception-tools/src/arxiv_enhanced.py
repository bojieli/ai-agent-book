"""
Enhanced ArXiv tools with download and details.
Based on AWorld parxiv-server complete implementation.
"""
import json
import logging
import traceback
from typing import Union

import arxiv
from dotenv import load_dotenv
from mcp.types import TextContent

from base import ActionResponse


load_dotenv()


async def get_paper_details(
    paper_id: str
) -> Union[str, TextContent]:
    """
    Get detailed information about an ArXiv paper.
    
    Args:
        paper_id: ArXiv paper ID (e.g., '2301.07041')
        
    Returns:
        TextContent with paper details
    """
    try:
        clean_id = paper_id.replace("arxiv:", "").strip()
        
        logging.info(f"📄 Getting paper details: {clean_id}")
        
        search = arxiv.Search(id_list=[clean_id])
        paper = next(arxiv.Client().results(search), None)
        
        if not paper:
            raise ValueError(f"Paper not found: {clean_id}")
        
        result = {
            "entry_id": paper.entry_id,
            "title": paper.title,
            "authors": [author.name for author in paper.authors],
            "summary": paper.summary,
            "published": paper.published.isoformat(),
            "updated": paper.updated.isoformat() if paper.updated else None,
            "categories": paper.categories,
            "primary_category": paper.primary_category,
            "pdf_url": paper.pdf_url,
            "doi": paper.doi,
            "journal_ref": paper.journal_ref
        }
        
        logging.info(f"✅ Retrieved paper: {paper.title}")
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"paper_id": clean_id}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Failed to get paper details: {str(e)}"
        logging.error(f"ArXiv error: {traceback.format_exc()}")
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata={"error_type": "arxiv_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def download_paper(
    paper_id: str,
    download_dir: str = "."
) -> Union[str, TextContent]:
    """
    Download ArXiv paper PDF.
    
    Args:
        paper_id: ArXiv paper ID
        download_dir: Directory to save PDF
        
    Returns:
        TextContent with download result
    """
    try:
        from pathlib import Path
        
        clean_id = paper_id.replace("arxiv:", "").strip()
        
        logging.info(f"📥 Downloading paper: {clean_id}")
        
        search = arxiv.Search(id_list=[clean_id])
        paper = next(arxiv.Client().results(search), None)
        
        if not paper:
            raise ValueError(f"Paper not found: {clean_id}")
        
        # Download
        download_path = Path(download_dir)
        download_path.mkdir(parents=True, exist_ok=True)
        
        filename = f"{clean_id.replace('/', '_')}.pdf"
        paper.download_pdf(dirpath=str(download_path), filename=filename)
        
        file_path = download_path / filename
        file_size = file_path.stat().st_size if file_path.exists() else 0
        
        result = {
            "paper_id": clean_id,
            "title": paper.title,
            "file_path": str(file_path),
            "file_size": file_size,
            "pdf_url": paper.pdf_url
        }
        
        logging.info(f"✅ Downloaded: {file_size} bytes")
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata={"paper_id": clean_id}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        action_response = ActionResponse(
            success=False,
            message=f"Download failed: {str(e)}",
            metadata={"error_type": "download_error"}
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_arxiv_categories() -> Union[str, TextContent]:
    """
    Get list of ArXiv subject categories.
    
    Returns:
        TextContent with categories
    """
    categories = {
        "cs": "Computer Science",
        "math": "Mathematics",
        "physics": "Physics",
        "astro-ph": "Astrophysics",
        "cond-mat": "Condensed Matter",
        "q-bio": "Quantitative Biology",
        "q-fin": "Quantitative Finance",
        "stat": "Statistics",
        "econ": "Economics",
        "eess": "Electrical Engineering"
    }
    
    result = {
        "categories": categories,
        "count": len(categories)
    }
    
    action_response = ActionResponse(
        success=True,
        message=result,
        metadata={"total_categories": len(categories)}
    )
    
    return TextContent(
        type="text",
        text=json.dumps(action_response.model_dump())
    )
