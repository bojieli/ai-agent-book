"""
Glob tool - Pure Python file pattern matching
"""

import os
from pathlib import Path
from typing import Dict, Any, List
from .base import BaseTool


class GlobTool(BaseTool):
    """Fast file pattern matching tool"""
    
    @property
    def name(self) -> str:
        return "Glob"
    
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Find files matching glob pattern
        
        - Fast file pattern matching tool that works with any codebase size
        - Supports glob patterns like "**/*.js" or "src/**/*.ts"
        - Returns matching file paths sorted by modification time
        """
        pattern = params["pattern"]
        path = params.get("path", ".")
        
        # Resolve search path
        search_path = Path(path).expanduser().resolve()
        if not search_path.exists():
            return {"error": f"Path not found: {search_path}"}
        
        if not search_path.is_dir():
            return {"error": f"Path is not a directory: {search_path}"}
        
        # Ensure pattern starts with **/ for recursive search
        if not pattern.startswith("**/"):
            pattern = "**/" + pattern
        
        # Find matching files
        matches = []
        try:
            for match in search_path.glob(pattern):
                if match.is_file():
                    matches.append(str(match))
        except Exception as e:
            return {"error": f"Error in glob search: {str(e)}"}
        
        # Sort by modification time (newest first)
        try:
            matches.sort(key=lambda x: os.path.getmtime(x), reverse=True)
        except Exception:
            # If sorting fails, just use unsorted list
            pass
        
        return {
            "pattern": pattern,
            "search_path": str(search_path),
            "matches": matches,
            "total_matches": len(matches)
        }

