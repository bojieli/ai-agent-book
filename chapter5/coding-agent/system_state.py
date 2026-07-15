"""
System state tracking for the coding agent
"""

import os
import subprocess
from dataclasses import dataclass, field
from typing import Dict, Any, List
from datetime import datetime


@dataclass
class SystemState:
    """System state tracking for system hints"""
    current_directory: str = field(default_factory=lambda: os.getcwd())
    tool_call_counts: Dict[str, int] = field(default_factory=dict)
    todos: List[Dict[str, Any]] = field(default_factory=list)
    shell_sessions: Dict[str, Any] = field(default_factory=dict)
    default_shell_id: str = "default"
    os_type: str = field(default_factory=lambda: os.uname().sysname)
    python_version: str = field(default_factory=lambda: subprocess.getoutput("python3 --version"))
    
    def get_system_hint(self) -> str:
        """Generate system hint message to append to context"""
        hint_parts = []
        
        # Environment information
        hint_parts.append("# System State")
        hint_parts.append(f"Current Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        hint_parts.append(f"Working Directory: {self.current_directory}")
        hint_parts.append(f"OS: {self.os_type}")
        hint_parts.append(f"Python: {self.python_version}")
        
        # Tool call statistics
        if self.tool_call_counts:
            hint_parts.append("\n# Tool Call Statistics")
            for tool, count in sorted(self.tool_call_counts.items()):
                hint_parts.append(f"- {tool}: {count} calls")
                if count >= 3:
                    hint_parts.append(f"  ⚠️  Tool '{tool}' has been called {count} times. Consider alternative approaches.")
        
        # TODO list
        if self.todos:
            hint_parts.append("\n# Current TODO List")
            for todo in self.todos:
                status_icon = {"pending": "⬜", "in_progress": "🔄", "completed": "✅"}[todo["status"]]
                hint_parts.append(f"{status_icon} [{todo['id']}] {todo['content']} ({todo['status']})")
        
        return "\n".join(hint_parts)

