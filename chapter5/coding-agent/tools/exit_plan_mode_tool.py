"""
ExitPlanMode tool - Exit plan mode after presenting plan
"""

from typing import Dict, Any
from .base import BaseTool


class ExitPlanModeTool(BaseTool):
    """Use this tool when you are in plan mode and ready to code"""
    
    @property
    def name(self) -> str:
        return "ExitPlanMode"
    
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Exit plan mode
        
        - Use this tool when you are in plan mode and have finished presenting your plan
        - This will prompt the user to exit plan mode
        - IMPORTANT: Only use for tasks that require planning implementation steps for code writing
        """
        plan = params["plan"]
        
        return {
            "action": "exit_plan_mode",
            "plan": plan,
            "message": "Plan presented. Ready to implement."
        }

