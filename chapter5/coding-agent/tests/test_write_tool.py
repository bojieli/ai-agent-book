"""
Test cases for Write tool
Tests all features from tools.json
"""

import pytest
from pathlib import Path
from tools.write_tool import WriteTool


class TestWriteTool:
    """Test Write tool functionality"""
    
    def test_basic_write(self, system_state, temp_dir):
        """Test basic file writing"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "new_file.txt"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": "Hello, World!"
        })
        
        assert result.success
        assert file_path.exists()
        assert file_path.read_text() == "Hello, World!"
        assert result.data["bytes_written"] > 0
        assert result.data["lines_written"] == 1
    
    def test_overwrite_existing_file(self, system_state, sample_files):
        """Test that Write overwrites existing files"""
        tool = WriteTool(system_state)
        file_path = sample_files["text_file1"]
        
        original_content = file_path.read_text()
        new_content = "New content"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": new_content
        })
        
        assert result.success
        assert file_path.read_text() == new_content
        assert file_path.read_text() != original_content
    
    def test_create_parent_directories(self, system_state, temp_dir):
        """Test that Write creates parent directories if needed"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "deep" / "nested" / "dir" / "file.txt"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": "Content"
        })
        
        assert result.success
        assert file_path.exists()
        assert file_path.parent.exists()
    
    def test_multiline_content(self, system_state, temp_dir):
        """Test writing multiline content"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "multiline.txt"
        content = "Line 1\nLine 2\nLine 3\n"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": content
        })
        
        assert result.success
        assert result.data["lines_written"] == 4  # 3 lines + final newline
        assert file_path.read_text() == content
    
    def test_python_lint_check_success(self, system_state, temp_dir):
        """Test automatic lint checking for valid Python file"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "valid.py"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": "def hello():\n    return 'world'\n"
        })
        
        assert result.success
        assert "lint_check" in result.data
        assert result.data["lint_check"]["language"] == "python"
        assert not result.data["lint_check"]["has_errors"]
    
    def test_python_lint_check_failure(self, system_state, temp_dir):
        """Test automatic lint checking for invalid Python file"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "invalid.py"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": "def hello(\n    invalid syntax here\n"
        })
        
        assert result.success  # Write succeeds even with syntax errors
        assert "lint_check" in result.data
        assert result.data["lint_check"]["has_errors"]
        assert "errors" in result.data["lint_check"]
    
    def test_unicode_content(self, system_state, temp_dir):
        """Test writing Unicode content"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "unicode.txt"
        content = "Hello 世界! 🌍 Привет мир!"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": content
        })
        
        assert result.success
        assert file_path.read_text(encoding='utf-8') == content
    
    def test_empty_content(self, system_state, temp_dir):
        """Test writing empty file"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "empty.txt"
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": ""
        })
        
        assert result.success
        assert file_path.exists()
        assert file_path.read_text() == ""
    
    def test_large_file_write(self, system_state, temp_dir):
        """Test writing large file"""
        tool = WriteTool(system_state)
        file_path = temp_dir / "large.txt"
        content = "A" * 100000  # 100K characters
        
        result = tool.execute({
            "file_path": str(file_path),
            "content": content
        })
        
        assert result.success
        assert result.data["bytes_written"] == 100000
        assert file_path.read_text() == content

