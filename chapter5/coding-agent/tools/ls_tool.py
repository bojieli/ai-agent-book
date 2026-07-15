"""
LS tool - Directory listing
"""

import os
from pathlib import Path
import fnmatch
from typing import Dict, Any, List
from .base import BaseTool


class LSTool(BaseTool):
    """Lists files and directories"""
    
    @property
    def name(self) -> str:
        return "LS"
    
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        List directory contents
        
        - The path parameter must be an absolute path
        - You can optionally provide an array of glob patterns to ignore
        """
        path = Path(params["path"]).expanduser().resolve()
        ignore_patterns = params.get("ignore", [])
        
        if not path.exists():
            return {"error": f"Path not found: {path}"}
        
        if not path.is_dir():
            return {"error": f"Not a directory: {path}"}
        
        try:
            entries = []
            
            for entry in sorted(path.iterdir()):
                # Skip hidden files (starting with .)
                if entry.name.startswith('.'):
                    continue
                
                # Check ignore patterns
                should_ignore = False
                for pattern in ignore_patterns:
                    if fnmatch.fnmatch(entry.name, pattern):
                        should_ignore = True
                        break
                
                if should_ignore:
                    continue
                
                # Get entry info
                entry_type = "dir" if entry.is_dir() else "file"
                size = entry.stat().st_size if entry.is_file() else 0
                
                entries.append({
                    "name": entry.name,
                    "type": entry_type,
                    "size": size,
                    "path": str(entry)
                })
            
            return {
                "path": str(path),
                "entries": entries,
                "total_entries": len(entries)
            }
            
        except PermissionError:
            return {"error": f"Permission denied: {path}"}
        except Exception as e:
            return {"error": f"Error listing directory: {str(e)}"}

