"""
Test cases for Read tool
Tests all features from tools.json including images, PDFs, notebooks
"""

import pytest
import json
from pathlib import Path
from tools.read_tool import ReadTool


class TestReadTool:
    """Test Read tool functionality"""
    
    def test_basic_read(self, system_state, sample_files):
        """Test basic file reading"""
        tool = ReadTool(system_state)
        result = tool.execute({
            "file_path": str(sample_files["python_file"])
        })
        
        assert result.success
        assert "def hello" in result.data["content"]
        assert "total_lines" in result.data
    
    def test_line_numbers_format(self, system_state, sample_files):
        """Test cat -n format with line numbers starting at 1"""
        tool = ReadTool(system_state)
        result = tool.execute({
            "file_path": str(sample_files["python_file"])
        })
        
        assert result.success
        content = result.data["content"]
        # Should have format: "     1|line content"
        lines = content.split('\n')
        first_line = lines[0]
        assert "|" in first_line
        # Extract line number
        line_num = first_line.split('|')[0].strip()
        assert line_num.isdigit()
        assert int(line_num) >= 1
    
    def test_offset_and_limit(self, system_state, sample_files):
        """Test offset and limit parameters for large files"""
        tool = ReadTool(system_state)
        
        # Create a file with many lines
        large_file = sample_files["temp_dir"] / "large.txt"
        large_file.write_text('\n'.join([f"Line {i}" for i in range(100)]))
        
        result = tool.execute({
            "file_path": str(large_file),
            "offset": 10,
            "limit": 5
        })
        
        assert result.success
        assert "showing_lines" in result.data
        assert "11-15" in result.data["showing_lines"]
        # Should have exactly 5 lines
        lines = result.data["content"].split('\n')
        assert len(lines) == 5
    
    def test_long_line_truncation(self, system_state, sample_files):
        """Test that lines longer than 2000 chars are truncated"""
        tool = ReadTool(system_state)
        
        # Create file with very long line
        long_file = sample_files["temp_dir"] / "long.txt"
        long_line = "A" * 3000
        long_file.write_text(long_line)
        
        result = tool.execute({
            "file_path": str(long_file)
        })
        
        assert result.success
        assert "truncated" in result.data["content"]
    
    def test_empty_file(self, system_state, sample_files):
        """Test reading empty file"""
        tool = ReadTool(system_state)
        
        empty_file = sample_files["temp_dir"] / "empty.txt"
        empty_file.write_text("")
        
        result = tool.execute({
            "file_path": str(empty_file)
        })
        
        assert result.success
        assert "File is empty" in result.data["content"]
    
    def test_nonexistent_file(self, system_state):
        """Test reading nonexistent file"""
        tool = ReadTool(system_state)
        result = tool.execute({
            "file_path": "/nonexistent/file.txt"
        })
        
        assert "error" in result.data
        assert "not found" in result.data["error"].lower()
    
    def test_binary_file_detection(self, system_state, sample_files):
        """Test binary file detection"""
        tool = ReadTool(system_state)
        
        # Create a binary file
        binary_file = sample_files["temp_dir"] / "binary.bin"
        binary_file.write_bytes(b'\x00\x01\x02\x03\x04\x05')
        
        result = tool.execute({
            "file_path": str(binary_file)
        })
        
        # Should detect as binary
        assert "binary" in result.data.get("error", "").lower()
    
    def test_image_file_handling(self, system_state, sample_files):
        """Test image file handling"""
        tool = ReadTool(system_state)
        
        # Create a dummy image file
        image_file = sample_files["temp_dir"] / "test.png"
        image_file.write_bytes(b'\x89PNG\r\n\x1a\n')  # PNG header
        
        result = tool.execute({
            "file_path": str(image_file)
        })
        
        assert result.success
        assert result.data["file_type"] == "image"
        assert "PNG" in result.data["format"]
    
    def test_pdf_file_handling(self, system_state, sample_files):
        """Test PDF file handling"""
        tool = ReadTool(system_state)
        
        # Create a dummy PDF file
        pdf_file = sample_files["temp_dir"] / "test.pdf"
        pdf_file.write_bytes(b'%PDF-1.4')
        
        result = tool.execute({
            "file_path": str(pdf_file)
        })
        
        assert result.success
        assert result.data["file_type"] == "pdf"
    
    def test_jupyter_notebook_reading(self, system_state, sample_files):
        """Test Jupyter notebook reading"""
        tool = ReadTool(system_state)
        
        # Create a simple notebook
        notebook_file = sample_files["temp_dir"] / "test.ipynb"
        notebook_data = {
            "cells": [
                {
                    "cell_type": "code",
                    "source": ["print('hello')"],
                    "outputs": []
                },
                {
                    "cell_type": "markdown",
                    "source": ["# Title"]
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 2
        }
        notebook_file.write_text(json.dumps(notebook_data))
        
        result = tool.execute({
            "file_path": str(notebook_file)
        })
        
        assert result.success
        assert result.data["file_type"] == "jupyter_notebook"
        assert result.data["total_cells"] == 2
        assert "hello" in result.data["content"]
    
    def test_not_a_file_error(self, system_state, sample_files):
        """Test reading a directory instead of file"""
        tool = ReadTool(system_state)
        result = tool.execute({
            "file_path": str(sample_files["temp_dir"])
        })
        
        assert "error" in result.data
        assert "not a file" in result.data["error"].lower()

