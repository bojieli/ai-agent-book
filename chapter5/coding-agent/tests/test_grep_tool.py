"""
Test cases for Grep tool - Pure Python implementation
Tests all features from tools.json
"""

import pytest
from tools.grep_tool import GrepTool


class TestGrepTool:
    """Test Grep tool functionality"""
    
    def test_basic_search(self, system_state, sample_files):
        """Test basic pattern search"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "files_with_matches"
        })
        
        assert result.success
        assert "file1.txt" in result.data["output"]
        assert result.data["matches"] >= 1
    
    def test_case_insensitive_search(self, system_state, sample_files):
        """Test -i flag for case insensitive search"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "error",  # lowercase
            "path": str(sample_files["temp_dir"]),
            "output_mode": "files_with_matches",
            "-i": True
        })
        
        assert result.success
        assert "file1.txt" in result.data["output"]
    
    def test_content_output_mode(self, system_state, sample_files):
        """Test output_mode: content shows matching lines"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "content"
        })
        
        assert result.success
        assert "ERROR" in result.data["output"]
        assert "file1.txt" in result.data["output"]
    
    def test_content_with_line_numbers(self, system_state, sample_files):
        """Test -n flag for line numbers"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "content",
            "-n": True
        })
        
        assert result.success
        output = result.data["output"]
        # Should contain line numbers in format "3:"
        assert ":" in output
    
    def test_context_lines_after(self, system_state, sample_files):
        """Test -A flag for context after match"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "content",
            "-A": 1
        })
        
        assert result.success
        # Should show line with ERROR and one line after
        assert "ERROR" in result.data["output"]
    
    def test_context_lines_before(self, system_state, sample_files):
        """Test -B flag for context before match"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "content",
            "-B": 1
        })
        
        assert result.success
        assert "ERROR" in result.data["output"]
    
    def test_context_lines_around(self, system_state, sample_files):
        """Test -C flag for context around match"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "content",
            "-C": 2
        })
        
        assert result.success
        assert "ERROR" in result.data["output"]
    
    def test_count_output_mode(self, system_state, sample_files):
        """Test output_mode: count shows match counts per file"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "count"
        })
        
        assert result.success
        # Should show file:count format
        assert "file1.txt:1" in result.data["output"]
    
    def test_glob_filtering(self, system_state, sample_files):
        """Test glob parameter to filter files"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "def",
            "path": str(sample_files["temp_dir"]),
            "glob": "*.py",
            "output_mode": "files_with_matches"
        })
        
        assert result.success
        assert ".py" in result.data["output"]
        assert ".txt" not in result.data["output"]
    
    def test_type_filtering(self, system_state, sample_files):
        """Test type parameter for file type filtering"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "def",
            "path": str(sample_files["temp_dir"]),
            "type": "py",
            "output_mode": "files_with_matches"
        })
        
        assert result.success
        assert "sample.py" in result.data["output"]
    
    def test_head_limit(self, system_state, sample_files):
        """Test head_limit parameter"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": ".",  # Match everything
            "path": str(sample_files["temp_dir"]),
            "output_mode": "files_with_matches",
            "head_limit": 1
        })
        
        assert result.success
        # Should only return 1 file
        files = result.data["output"].strip().split('\n')
        assert len(files) <= 1
    
    def test_regex_pattern(self, system_state, sample_files):
        """Test full regex syntax support"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": r"def\s+\w+",  # Match function definitions
            "path": str(sample_files["temp_dir"]),
            "output_mode": "content"
        })
        
        assert result.success
        assert "def" in result.data["output"]
    
    def test_multiline_mode(self, system_state, sample_files):
        """Test multiline mode"""
        tool = GrepTool(system_state)
        
        # Create a file with multiline pattern
        multiline_file = sample_files["temp_dir"] / "multiline.txt"
        multiline_file.write_text("Start\nMiddle\nEnd")
        
        result = tool.execute({
            "pattern": r"Start.*End",
            "path": str(sample_files["temp_dir"]),
            "multiline": True,
            "output_mode": "content"
        })
        
        assert result.success
    
    def test_no_matches(self, system_state, sample_files):
        """Test when pattern matches nothing"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "NONEXISTENT_PATTERN_12345",
            "path": str(sample_files["temp_dir"]),
            "output_mode": "files_with_matches"
        })
        
        assert result.success
        assert "No matches found" in result.data["output"]
        assert result.data["matches"] == 0
    
    def test_invalid_regex(self, system_state, sample_files):
        """Test invalid regex pattern"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "[invalid(",  # Invalid regex
            "path": str(sample_files["temp_dir"])
        })
        
        assert not result.success
        assert "error" in result.data
    
    def test_nonexistent_path(self, system_state):
        """Test searching in nonexistent path"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "test",
            "path": "/nonexistent/path/12345"
        })
        
        assert "error" in result.data
    
    def test_single_file_search(self, system_state, sample_files):
        """Test searching a single file"""
        tool = GrepTool(system_state)
        result = tool.execute({
            "pattern": "ERROR",
            "path": str(sample_files["text_file1"]),
            "output_mode": "content"
        })
        
        assert result.success
        assert "ERROR" in result.data["output"]

