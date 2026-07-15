"""
KillBash tool - Terminate shell sessions
"""

from typing import Dict, Any
from .base import BaseTool


class KillBashTool(BaseTool):
    """Kills a running background bash shell by its ID"""
    
    @property
    def name(self) -> str:
        return "KillBash"
    
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Kill a shell session
        
        - Kills a running background bash shell by its ID
        - Takes a shell_id parameter identifying the shell to kill
        - Returns a success or failure status
        """
        shell_id = params["shell_id"]
        
        if shell_id not in self.state.shell_sessions:
            return {"error": f"Shell session not found: {shell_id}"}
        
        try:
            session = self.state.shell_sessions[shell_id]
            session.kill()
            del self.state.shell_sessions[shell_id]
            
            return {
                "shell_id": shell_id,
                "status": "terminated"
            }
            
        except Exception as e:
            return {"error": f"Error killing shell: {str(e)}"}

