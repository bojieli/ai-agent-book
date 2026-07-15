"""
Test cases for LS tool
Tests all features from tools.json
"""

import pytest
from pathlib import Path
from tools.ls_tool import LSTool


class TestLSTool:
    """Test LS tool functionality"""
    
    def test_basic_listing(self, system_state, sample_files):
        """Test basic directory listing"""
        tool = LSTool(system_state)
        result = tool.execute({
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        assert result.data["total_entries"] >= 2
        
        # Check entries structure
        entries = result.data["entries"]
        assert all("name" in e for e in entries)
        assert all("type" in e for e in entries)
        assert all("size" in e for e in entries)
        assert all("path" in e for e in entries)
    
    def test_files_and_directories(self, system_state, sample_files):
        """Test that both files and directories are listed"""
        tool = LSTool(system_state)
        result = tool.execute({
            "path": str(sample_files["temp_dir"])
        })
        
        assert result.success
        entries = result.data["entries"]
        
        # Should have files
        files = [e for e in entries if e["type"] == "file"]
        assert len(files) > 0
        
        # Should have directories
        dirs = [e for e in entries if e["type"] == "dir"]
        assert len(dirs) > 0
    
    def test_hidden_files_excluded(self, system_state, temp_dir):
        """Test that hidden files (starting with .) are excluded"""
        tool = LSTool(system_state)
        
        # Create hidden file
        hidden_file = temp_dir / ".hidden"
        hidden_file.write_text("secret")
        
        # Create normal file
        normal_file = temp_dir / "normal.txt"
        normal_file.write_text("public")
        
        result = tool.execute({
            "path": str(temp_dir)
        })
        
        assert result.success
        entry_names = [e["name"] for e in result.data["entries"]]
        assert "normal.txt" in entry_names
        assert ".hidden" not in entry_names
    
    def test_ignore_patterns(self, system_state, temp_dir):
        """Test ignore parameter with glob patterns"""
        tool = LSTool(system_state)
        
        # Create various files
        (temp_dir / "keep.txt").write_text("keep")
        (temp_dir / "ignore.log").write_text("ignore")
        (temp_dir / "also_keep.py").write_text("keep")
        
        result = tool.execute({
            "path": str(temp_dir),
            "ignore": ["*.log"]
        })
        
        assert result.success
        entry_names = [e["name"] for e in result.data["entries"]]
        assert "keep.txt" in entry_names
        assert "also_keep.py" in entry_names
        assert "ignore.log" not in entry_names
    
    def test_multiple_ignore_patterns(self, system_state, temp_dir):
        """Test multiple ignore patterns"""
        tool = LSTool(system_state)
        
        (temp_dir / "file.txt").write_text("1")
        (temp_dir / "file.log").write_text("2")
        (temp_dir / "file.tmp").write_text("3")
        
        result = tool.execute({
            "path": str(temp_dir),
            "ignore": ["*.log", "*.tmp"]
        })
        
        assert result.success
        entry_names = [e["name"] for e in result.data["entries"]]
        assert "file.txt" in entry_names
        assert "file.log" not in entry_names
        assert "file.tmp" not in entry_names
    
    def test_sorted_output(self, system_state, temp_dir):
        """Test that entries are sorted"""
        tool = LSTool(system_state)
        
        # Create files in specific order
        (temp_dir / "z_file.txt").write_text("1")
        (temp_dir / "a_file.txt").write_text("2")
        (temp_dir / "m_file.txt").write_text("3")
        
        result = tool.execute({
            "path": str(temp_dir)
        })
        
        assert result.success
        entry_names = [e["name"] for e in result.data["entries"]]
        # Should be sorted alphabetically
        sorted_names = sorted(entry_names)
        assert entry_names == sorted_names
    
    def test_file_sizes(self, system_state, temp_dir):
        """Test that file sizes are reported"""
        tool = LSTool(system_state)
        
        file_path = temp_dir / "sized.txt"
        content = "A" * 1000
        file_path.write_text(content)
        
        result = tool.execute({
            "path": str(temp_dir)
        })
        
        assert result.success
        entry = next(e for e in result.data["entries"] if e["name"] == "sized.txt")
        assert entry["size"] == 1000
    
    def test_directory_size_zero(self, system_state, temp_dir):
        """Test that directories have size 0"""
        tool = LSTool(system_state)
        
        subdir = temp_dir / "subdir"
        subdir.mkdir()
        
        result = tool.execute({
            "path": str(temp_dir)
        })
        
        assert result.success
        dir_entry = next(e for e in result.data["entries"] if e["name"] == "subdir")
        assert dir_entry["type"] == "dir"
        assert dir_entry["size"] == 0
    
    def test_path_not_found(self, system_state):
        """Test error when path doesn't exist"""
        tool = LSTool(system_state)
        result = tool.execute({
            "path": "/nonexistent/path"
        })
        
        assert "error" in result.data
        assert "not found" in result.data["error"].lower()
    
    def test_not_a_directory(self, system_state, sample_files):
        """Test error when path is a file not directory"""
        tool = LSTool(system_state)
        result = tool.execute({
            "path": str(sample_files["python_file"])
        })
        
        assert "error" in result.data
        assert "not a directory" in result.data["error"].lower()
    
    def test_permission_denied(self, system_state, temp_dir):
        """Test handling of permission errors"""
        # This test might not work on all systems
        tool = LSTool(system_state)
        
        restricted_dir = temp_dir / "restricted"
        restricted_dir.mkdir(mode=0o000)
        
        try:
            result = tool.execute({
                "path": str(restricted_dir)
            })
            
            # Should either succeed (if running as root) or fail with permission error
            if "error" in result.data:
                assert "permission" in result.data["error"].lower()
        finally:
            restricted_dir.chmod(0o755)  # Restore permissions for cleanup

