"""
Tests for Excel operation tools.
Uses real Excel files for testing.
"""
import asyncio
import json
import pytest
import tempfile
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent / "src"))

from excel_tools import (
    read_excel_data,
    write_excel_data,
    create_excel_workbook,
    create_excel_worksheet,
    apply_excel_formula,
    get_excel_metadata
)


class TestExcelBasics:
    """Tests for basic Excel operations."""
    
    @pytest.mark.asyncio
    async def test_create_workbook(self):
        """Test creating a new workbook."""
        excel_path = Path(tempfile.mktemp(suffix=".xlsx"))
        
        try:
            result = await create_excel_workbook(str(excel_path))
            
            assert result["success"] is True
            assert excel_path.exists()
            
            print("✅ Created Excel workbook")
        finally:
            excel_path.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_write_and_read_data(self):
        """Test writing and reading Excel data."""
        excel_path = Path(tempfile.mktemp(suffix=".xlsx"))
        
        try:
            # Write data
            data = {
                "Sheet1": [
                    {"name": "Alice", "age": 30, "city": "NYC"},
                    {"name": "Bob", "age": 25, "city": "LA"}
                ]
            }
            
            write_result = await write_excel_data(str(excel_path), data, overwrite=True)
            assert write_result["success"] is True
            
            # Read data
            read_result = await read_excel_data(str(excel_path))
            assert read_result["success"] is True
            assert read_result["sheet_count"] >= 1
            
            print(f"✅ Write and read: {read_result['sheet_count']} sheets")
        finally:
            excel_path.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_get_metadata(self):
        """Test getting Excel metadata."""
        excel_path = Path(tempfile.mktemp(suffix=".xlsx"))
        
        try:
            # Create workbook with data
            data = {"Sheet1": [{"A": 1, "B": 2}, {"A": 3, "B": 4}]}
            await write_excel_data(str(excel_path), data, overwrite=True)
            
            # Get metadata
            result = await get_excel_metadata(str(excel_path))
            
            assert result["success"] is True
            assert result["sheet_count"] >= 1
            assert len(result["sheets"]) >= 1
            
            print(f"✅ Metadata: {result['sheet_count']} sheets")
        finally:
            excel_path.unlink(missing_ok=True)


class TestExcelAdvanced:
    """Tests for advanced Excel operations."""
    
    @pytest.mark.asyncio
    async def test_create_worksheet(self):
        """Test creating a new worksheet."""
        excel_path = Path(tempfile.mktemp(suffix=".xlsx"))
        
        try:
            # Create workbook
            await create_excel_workbook(str(excel_path))
            
            # Create worksheet
            result = await create_excel_worksheet(str(excel_path), "NewSheet")
            
            assert result["success"] is True
            assert result["sheet_name"] == "NewSheet"
            
            print("✅ Created worksheet 'NewSheet'")
        finally:
            excel_path.unlink(missing_ok=True)
    
    @pytest.mark.asyncio
    async def test_apply_formula(self):
        """Test applying formula to cell."""
        excel_path = Path(tempfile.mktemp(suffix=".xlsx"))
        
        try:
            # Create workbook with data
            data = {"Sheet1": [{"A": 1}, {"A": 2}, {"A": 3}]}
            await write_excel_data(str(excel_path), data, overwrite=True)
            
            # Apply formula
            result = await apply_excel_formula(
                str(excel_path),
                "Sheet1",
                "A4",
                "=SUM(A1:A3)"
            )
            
            assert result["success"] is True
            assert result["cell"] == "A4"
            assert result["formula"] == "=SUM(A1:A3)"
            
            print("✅ Applied formula =SUM(A1:A3)")
        finally:
            excel_path.unlink(missing_ok=True)


if __name__ == "__main__":
    print("=" * 70)
    print("Running Excel Tools Tests")
    print("=" * 70)
    print()
    
    pytest.main([__file__, "-v", "-s"])
