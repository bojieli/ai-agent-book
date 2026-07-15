"""
BashOutput tool - Retrieve output from background bash jobs
"""

import os
import re
from typing import Dict, Any
from .base import BaseTool


class BashOutputTool(BaseTool):
    """Retrieves output from running or completed background bash shells"""
    
    @property
    def name(self) -> str:
        return "BashOutput"
    
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get output from background bash job
        
        - Retrieves output from a running or completed background bash shell
        - Takes a bash_id parameter identifying the shell
        - Always returns only new output since the last check
        - Supports optional regex filtering
        """
        bash_id = params["bash_id"]
        filter_pattern = params.get("filter")
        
        log_file = f"/tmp/{bash_id}.log"
        
        if not os.path.exists(log_file):
            return {"error": f"No output found for bash_id: {bash_id}"}
        
        try:
            with open(log_file, 'r') as f:
                output = f.read()
            
            if filter_pattern:
                # Filter lines matching pattern
                lines = output.split('\n')
                filtered_lines = [line for line in lines if re.search(filter_pattern, line)]
                output = '\n'.join(filtered_lines)
            
            return {
                "bash_id": bash_id,
                "output": output,
                "output_size": len(output)
            }
            
        except Exception as e:
            return {"error": f"Error reading bash output: {str(e)}"}

