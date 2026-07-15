"""
Base classes for tool implementation
"""

from typing import Dict, Any, Optional
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass
class ToolResult:
    """Result from a tool execution"""
    success: bool
    data: Dict[str, Any]
    error: Optional[str] = None
    metadata: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        result = self.data.copy()
        if self.error:
            result["error"] = self.error
        if self.metadata:
            result["_metadata"] = self.metadata
        return result


class BaseTool(ABC):
    """Base class for all tools"""
    
    def __init__(self, system_state: 'SystemState'):
        self.state = system_state
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Tool name"""
        pass
    
    def execute(self, params: Dict[str, Any]) -> ToolResult:
        """
        Execute the tool with given parameters
        
        Args:
            params: Tool input parameters
            
        Returns:
            ToolResult with data and metadata
        """
        # Track tool call
        self.state.tool_call_counts[self.name] = self.state.tool_call_counts.get(self.name, 0) + 1
        
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        call_number = self.state.tool_call_counts[self.name]
        
        try:
            # Call implementation
            data = self._execute_impl(params)
            
            # Add metadata
            metadata = {
                "tool": self.name,
                "call_number": call_number,
                "timestamp": timestamp
            }
            
            return ToolResult(success=True, data=data, metadata=metadata)
            
        except Exception as e:
            error_data = {
                "error": str(e),
                "error_type": type(e).__name__,
                "tool": self.name,
                "input": params
            }
            
            metadata = {
                "tool": self.name,
                "call_number": call_number,
                "timestamp": timestamp
            }
            
            return ToolResult(success=False, data=error_data, error=str(e), metadata=metadata)
    
    @abstractmethod
    def _execute_impl(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """
        Implement tool-specific logic
        
        Args:
            params: Tool input parameters
            
        Returns:
            Dictionary with tool results
        """
        pass

