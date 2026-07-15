"""
Integration tests for the complete agent system
Tests system hints, tool chaining, and end-to-end workflows
"""

import pytest
from system_state import SystemState
from tools.grep_tool import GrepTool
from tools.write_tool import WriteTool
from tools.todo_write_tool import TodoWriteTool


class TestSystemHints:
    """Test system hint generation"""
    
    def test_system_hint_structure(self, system_state):
        """Test that system hint includes all required sections"""
        hint = system_state.get_system_hint()
        
        assert "# System State" in hint
        assert "Current Time:" in hint
        assert "Working Directory:" in hint
        assert "OS:" in hint
        assert "Python:" in hint
    
    def test_tool_call_statistics_in_hint(self, system_state):
        """Test that tool calls are tracked in system hint"""
        # Make some tool calls
        grep_tool = GrepTool(system_state)
        grep_tool.execute({"pattern": "test", "path": "."})
        grep_tool.execute({"pattern": "test2", "path": "."})
        
        hint = system_state.get_system_hint()
        
        assert "# Tool Call Statistics" in hint
        assert "Grep: 2 calls" in hint
    
    def test_tool_warning_after_three_calls(self, system_state):
        """Test that system hint warns after 3+ tool calls"""
        tool = GrepTool(system_state)
        
        # Call tool 4 times
        for i in range(4):
            tool.execute({"pattern": f"test{i}", "path": "."})
        
        hint = system_state.get_system_hint()
        
        assert "⚠️" in hint
        assert "4 times" in hint
        assert "Consider alternative approaches" in hint
    
    def test_todo_list_in_hint(self, system_state):
        """Test that TODO list appears in system hint"""
        todo_tool = TodoWriteTool(system_state)
        
        todos = [
            {"id": "1", "content": "Task 1", "status": "completed"},
            {"id": "2", "content": "Task 2", "status": "in_progress"},
            {"id": "3", "content": "Task 3", "status": "pending"}
        ]
        
        todo_tool.execute({"todos": todos})
        
        hint = system_state.get_system_hint()
        
        assert "# Current TODO List" in hint
        assert "✅" in hint  # Completed
        assert "🔄" in hint  # In progress
        assert "⬜" in hint  # Pending
        assert "Task 1" in hint
        assert "Task 2" in hint
        assert "Task 3" in hint


class TestToolChaining:
    """Test chaining multiple tools together"""
    
    def test_write_then_read_workflow(self, system_state, temp_dir):
        """Test writing a file then reading it back"""
        from tools.write_tool import WriteTool
        from tools.read_tool import ReadTool
        
        write_tool = WriteTool(system_state)
        read_tool = ReadTool(system_state)
        
        file_path = temp_dir / "chained.txt"
        content = "This is a test"
        
        # Write file
        write_result = write_tool.execute({
            "file_path": str(file_path),
            "content": content
        })
        assert write_result.success
        
        # Read it back
        read_result = read_tool.execute({
            "file_path": str(file_path)
        })
        assert read_result.success
        assert content in read_result.data["content"]
    
    def test_write_search_edit_workflow(self, system_state, temp_dir):
        """Test complete workflow: write, search, edit"""
        from tools.write_tool import WriteTool
        from tools.grep_tool import GrepTool
        from tools.edit_tool import EditTool
        
        write_tool = WriteTool(system_state)
        grep_tool = GrepTool(system_state)
        edit_tool = EditTool(system_state)
        
        file_path = temp_dir / "workflow.py"
        
        # 1. Write initial file
        write_result = write_tool.execute({
            "file_path": str(file_path),
            "content": "def old_function():\n    return 'old'\n"
        })
        assert write_result.success
        
        # 2. Search for pattern
        grep_result = grep_tool.execute({
            "pattern": "old_function",
            "path": str(temp_dir),
            "output_mode": "files_with_matches"
        })
        assert grep_result.success
        assert str(file_path) in grep_result.data["output"]
        
        # 3. Edit the file
        edit_result = edit_tool.execute({
            "file_path": str(file_path),
            "old_string": "old_function",
            "new_string": "new_function"
        })
        assert edit_result.success
        
        # 4. Verify change with another search
        grep_result2 = grep_tool.execute({
            "pattern": "new_function",
            "path": str(temp_dir),
            "output_mode": "content"
        })
        assert grep_result2.success
        assert "new_function" in grep_result2.data["output"]
    
    def test_metadata_consistency(self, system_state):
        """Test that metadata is consistent across tool calls"""
        tool = GrepTool(system_state)
        
        # First call
        result1 = tool.execute({"pattern": "test", "path": "."})
        assert result1.data["_metadata"]["call_number"] == 1
        assert result1.data["_metadata"]["tool"] == "Grep"
        
        # Second call
        result2 = tool.execute({"pattern": "test2", "path": "."})
        assert result2.data["_metadata"]["call_number"] == 2
        
        # Third call
        result3 = tool.execute({"pattern": "test3", "path": "."})
        assert result3.data["_metadata"]["call_number"] == 3

