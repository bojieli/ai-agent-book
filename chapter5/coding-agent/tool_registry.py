"""
Tool registry - Maps tool names to implementations
"""

from typing import Dict, Type
from tools import (
    BaseTool, BashTool, BashOutputTool, KillBashTool,
    ReadTool, WriteTool, EditTool, MultiEditTool,
    GrepTool, GlobTool, LSTool,
    TodoWriteTool, ExitPlanModeTool, NotebookEditTool,
    WebFetchTool, WebSearchTool, TaskTool
)


class ToolRegistry:
    """Registry of all available tools"""
    
    def __init__(self):
        self._tools: Dict[str, Type[BaseTool]] = {
            "Bash": BashTool,
            "BashOutput": BashOutputTool,
            "KillBash": KillBashTool,
            "Read": ReadTool,
            "Write": WriteTool,
            "Edit": EditTool,
            "MultiEdit": MultiEditTool,
            "Grep": GrepTool,
            "Glob": GlobTool,
            "LS": LSTool,
            "TodoWrite": TodoWriteTool,
            "ExitPlanMode": ExitPlanModeTool,
            "NotebookEdit": NotebookEditTool,
            "WebFetch": WebFetchTool,
            "WebSearch": WebSearchTool,
            "Task": TaskTool,
        }
    
    def get_tool(self, name: str, system_state) -> BaseTool:
        """Get tool instance by name"""
        tool_class = self._tools.get(name)
        if tool_class is None:
            raise ValueError(f"Unknown tool: {name}")
        return tool_class(system_state)
    
    def get_all_tool_names(self):
        """Get list of all tool names"""
        return list(self._tools.keys())

