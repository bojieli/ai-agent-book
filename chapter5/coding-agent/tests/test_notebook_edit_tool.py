"""
Test cases for NotebookEdit tool
Tests all features from tools.json
"""

import pytest
import json
from pathlib import Path
from tools.notebook_edit_tool import NotebookEditTool


@pytest.fixture
def sample_notebook(temp_dir):
    """Create a sample Jupyter notebook"""
    notebook_path = temp_dir / "test.ipynb"
    notebook_data = {
        "cells": [
            {
                "id": "cell-1",
                "cell_type": "code",
                "source": ["print('hello')"],
                "outputs": [],
                "execution_count": None
            },
            {
                "id": "cell-2",
                "cell_type": "markdown",
                "source": ["# Title"]
            },
            {
                "id": "cell-3",
                "cell_type": "code",
                "source": ["x = 1\n", "y = 2"],
                "outputs": [],
                "execution_count": None
            }
        ],
        "metadata": {},
        "nbformat": 4,
        "nbformat_minor": 2
    }
    notebook_path.write_text(json.dumps(notebook_data, indent=2))
    return notebook_path


class TestNotebookEditTool:
    """Test NotebookEdit tool functionality"""
    
    def test_replace_cell(self, system_state, sample_notebook):
        """Test edit_mode=replace (default)"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "cell_id": "cell-1",
            "new_source": "print('world')",
            "edit_mode": "replace"
        })
        
        assert result.success
        assert result.data["action"] == "replaced"
        
        # Verify change
        notebook = json.loads(sample_notebook.read_text())
        cell = next(c for c in notebook["cells"] if c.get("id") == "cell-1")
        assert "world" in ''.join(cell["source"])
    
    def test_insert_cell(self, system_state, sample_notebook):
        """Test edit_mode=insert"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "cell_id": "cell-1",
            "new_source": "# New cell",
            "cell_type": "markdown",
            "edit_mode": "insert"
        })
        
        assert result.success
        assert result.data["action"] == "inserted"
        
        # Verify insertion
        notebook = json.loads(sample_notebook.read_text())
        # Should have 4 cells now (3 original + 1 inserted)
        assert len(notebook["cells"]) == 4
    
    def test_delete_cell(self, system_state, sample_notebook):
        """Test edit_mode=delete"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "cell_id": "cell-2",
            "new_source": "",  # Not used for delete
            "edit_mode": "delete"
        })
        
        assert result.success
        assert result.data["action"] == "deleted"
        
        # Verify deletion
        notebook = json.loads(sample_notebook.read_text())
        assert len(notebook["cells"]) == 2
        assert not any(c.get("id") == "cell-2" for c in notebook["cells"])
    
    def test_insert_at_beginning(self, system_state, sample_notebook):
        """Test inserting at beginning when cell_id not specified"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "new_source": "# First cell",
            "cell_type": "markdown",
            "edit_mode": "insert"
        })
        
        assert result.success
        
        # Verify it was inserted at beginning
        notebook = json.loads(sample_notebook.read_text())
        assert "First cell" in ''.join(notebook["cells"][0]["source"])
    
    def test_change_cell_type(self, system_state, sample_notebook):
        """Test changing cell type during replace"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "cell_id": "cell-1",
            "new_source": "# Now markdown",
            "cell_type": "markdown",
            "edit_mode": "replace"
        })
        
        assert result.success
        
        # Verify cell type changed
        notebook = json.loads(sample_notebook.read_text())
        cell = next(c for c in notebook["cells"] if c.get("id") == "cell-1")
        assert cell["cell_type"] == "markdown"
    
    def test_multiline_source(self, system_state, sample_notebook):
        """Test editing with multiline source"""
        tool = NotebookEditTool(system_state)
        
        multiline_source = "def hello():\n    print('world')\n    return True"
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "cell_id": "cell-1",
            "new_source": multiline_source,
            "edit_mode": "replace"
        })
        
        assert result.success
        
        # Verify multiline source was saved correctly
        notebook = json.loads(sample_notebook.read_text())
        cell = next(c for c in notebook["cells"] if c.get("id") == "cell-1")
        assert len(cell["source"]) == 3
    
    def test_cell_not_found(self, system_state, sample_notebook):
        """Test error when cell_id doesn't exist"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "cell_id": "nonexistent-cell",
            "new_source": "test",
            "edit_mode": "replace"
        })
        
        assert "error" in result.data
        assert "not found" in result.data["error"]
    
    def test_notebook_not_found(self, system_state):
        """Test error when notebook doesn't exist"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": "/nonexistent/notebook.ipynb",
            "cell_id": "cell-1",
            "new_source": "test"
        })
        
        assert "error" in result.data
        assert "not found" in result.data["error"].lower()
    
    def test_invalid_notebook_format(self, system_state, temp_dir):
        """Test error with invalid JSON notebook"""
        tool = NotebookEditTool(system_state)
        
        bad_notebook = temp_dir / "bad.ipynb"
        bad_notebook.write_text("not valid json")
        
        result = tool.execute({
            "notebook_path": str(bad_notebook),
            "cell_id": "cell-1",
            "new_source": "test"
        })
        
        assert "error" in result.data
        assert "Invalid Jupyter notebook" in result.data["error"]
    
    def test_delete_requires_cell_id(self, system_state, sample_notebook):
        """Test that delete mode requires cell_id"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "new_source": "",
            "edit_mode": "delete"
        })
        
        assert "error" in result.data
        assert "cell_id required" in result.data["error"]
    
    def test_replace_requires_cell_id(self, system_state, sample_notebook):
        """Test that replace mode requires cell_id"""
        tool = NotebookEditTool(system_state)
        
        result = tool.execute({
            "notebook_path": str(sample_notebook),
            "new_source": "test",
            "edit_mode": "replace"
        })
        
        assert "error" in result.data
        assert "cell_id required" in result.data["error"]

