"""
Write tool - File writing with automatic lint checking
"""

import subprocess
from pathlib import Path
from typing import Dict, Any, Optional
from .base import BaseTool


class WriteTool(BaseTool):
    """Writes files to the local filesystem"""
    
    @property
    def name(self) -> str:
        return "Write"
    
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Write content to file
        
        - This tool will overwrite the existing file if there is one at the provided path
        - ALWAYS prefer editing existing files in the codebase
        - NEVER write new files unless explicitly required
        - NEVER proactively create documentation files (*.md) or README files
        """
        file_path = Path(params["file_path"]).expanduser().resolve()
        content = params["content"]
        
        try:
            # Create parent directories if needed
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write file
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            result = {
                "file_path": str(file_path),
                "bytes_written": len(content.encode('utf-8')),
                "lines_written": len(content.split('\n'))
            }
            
            # Check for lint errors
            lint_result = self._check_lint_errors(file_path)
            if lint_result:
                result["lint_check"] = lint_result
            
            return result
            
        except Exception as e:
            return {"error": f"Error writing file: {str(e)}"}
    
    def _check_lint_errors(self, file_path: Path) -> Optional[Dict[str, Any]]:
        """Check for lint errors after file modification"""
        suffix = file_path.suffix
        
        try:
            if suffix == ".py":
                # Check Python syntax
                result = subprocess.run(
                    ["python3", "-m", "py_compile", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return {
                        "language": "python",
                        "has_errors": True,
                        "errors": result.stderr
                    }
                else:
                    return {
                        "language": "python",
                        "has_errors": False,
                        "message": "No syntax errors detected"
                    }
            
            elif suffix in [".js", ".jsx", ".ts", ".tsx"]:
                # Check JavaScript/TypeScript with node if available
                result = subprocess.run(
                    ["node", "--check", str(file_path)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.returncode != 0:
                    return {
                        "language": "javascript/typescript",
                        "has_errors": True,
                        "errors": result.stderr
                    }
                else:
                    return {
                        "language": "javascript/typescript",
                        "has_errors": False,
                        "message": "No syntax errors detected"
                    }
            
            # No linter available for this file type
            return None
            
        except FileNotFoundError:
            # Linter not installed
            return None
        except subprocess.TimeoutExpired:
            return {"error": "Lint check timed out"}
        except Exception:
            return None

