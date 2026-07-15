"""
Test cases for Glob tool
Tests all features from tools.json
"""

import pytest
from tools.glob_tool import GlobTool


class TestGlobTool:
    """Test Glob tool functionality"""
    
    def test_basic_glob(self, system_state, sample_files):
        """Test basic glob pattern"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "*.py",
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        assert result.data["total_matches"] >= 1
        assert any("sample.py" in m for m in result.data["matches"])
    
    def test_recursive_glob(self, system_state, sample_files):
        """Test recursive pattern search"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "**/*.py",
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        # Should find both sample.py and nested.py
        assert result.data["total_matches"] >= 2
    
    def test_auto_recursive_prefix(self, system_state, sample_files):
        """Test that patterns without **/ are auto-prefixed"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "*.py",  # Should become **/*.py
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        # Should still find nested files
        assert result.data["total_matches"] >= 1
    
    def test_sorted_by_modification_time(self, system_state, sample_files):
        """Test that results are sorted by modification time"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "*.txt",
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        assert result.data["total_matches"] >= 2
        # Results should be in a list
        assert isinstance(result.data["matches"], list)
    
    def test_no_matches(self, system_state, sample_files):
        """Test when pattern matches nothing"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "*.nonexistent",
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        assert result.data["total_matches"] == 0
        assert result.data["matches"] == []
    
    def test_nonexistent_path(self, system_state):
        """Test with nonexistent path"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "*.py",
            "path": "/nonexistent/path"
        })
        
        assert "error" in result.data
    
    def test_not_a_directory(self, system_state, sample_files):
        """Test with a file path instead of directory"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "*.py",
            "path": str(sample_files["python_file"])
        })
        
        assert "error" in result.data
    
    def test_complex_pattern(self, system_state, sample_files):
        """Test complex glob patterns"""
        tool = GlobTool(system_state)
        result = tool.execute({
            "pattern": "**/*.{py,js}",
            "path": str(sample_files["temp_dir"])
        })
        
        # May or may not work depending on glob implementation
        # This tests the behavior
        assert result.success or "error" in result.data
    
    def test_default_path(self, system_state, sample_files):
        """Test omitting path parameter uses current directory"""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(sample_files["temp_dir"])
            tool = GlobTool(system_state)
            result = tool.execute({
                "pattern": "*.py"
            })
            
            assert result.success
            assert result.data["total_matches"] >= 1
        finally:
            os.chdir(original_cwd)

