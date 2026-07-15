"""
Real API tests for Yahoo Finance tools.
These tests make actual API calls to Yahoo Finance to verify functionality.
"""
import asyncio
import json
import pytest
from pathlib import Path
import sys
from datetime import datetime, timedelta

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

from yahoo_finance_tools import (
    get_stock_quote,
    get_historical_data,
    get_company_info,
    get_financial_statements
)


class TestYFinanceQuote:
    """Tests for stock quote functionality."""
    
    @pytest.mark.asyncio
    async def test_get_stock_quote_aapl(self):
        """Test getting stock quote for AAPL."""
        result = await get_stock_quote(symbol="AAPL")
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        quote = data["message"]
        assert quote["symbol"] == "AAPL"
        assert quote["current_price"] is not None
        assert quote["current_price"] > 0
        assert quote["company_name"] is not None
        
        print(f"✅ AAPL Quote: ${quote['current_price']}")
        print(f"   Company: {quote['company_name']}")
        if "change_percent" in quote:
            print(f"   Change: {quote['change_percent']}%")
    
    @pytest.mark.asyncio
    async def test_get_stock_quote_multiple(self):
        """Test getting quotes for multiple symbols."""
        symbols = ["MSFT", "GOOGL", "TSLA"]
        
        for symbol in symbols:
            result = await get_stock_quote(symbol=symbol)
            data = json.loads(result.text)
            assert data["success"] is True
            
            quote = data["message"]
            assert quote["symbol"] == symbol
            assert quote["current_price"] > 0
            
            print(f"✅ {symbol}: ${quote['current_price']}")
    
    @pytest.mark.asyncio
    async def test_get_stock_quote_invalid(self):
        """Test getting quote for invalid symbol."""
        result = await get_stock_quote(symbol="INVALIDXYZ999")
        
        data = json.loads(result.text)
        assert data["success"] is False
        assert "error" in data["message"].lower() or "not found" in data["message"].lower() or "no data" in data["message"].lower()
        
        print("✅ Correctly handled invalid symbol")
    
    @pytest.mark.asyncio
    async def test_get_stock_quote_with_metadata(self):
        """Test that quote includes proper metadata."""
        result = await get_stock_quote(symbol="AAPL")
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        metadata = data["metadata"]
        assert metadata["symbol"] == "AAPL"
        assert metadata["operation"] == "get_stock_quote"
        assert metadata["execution_time"] is not None
        assert metadata["execution_time"] > 0
        assert metadata["data_points"] > 0
        
        print(f"✅ Metadata OK: {metadata['execution_time']:.2f}s, {metadata['data_points']} fields")


class TestYFinanceHistorical:
    """Tests for historical data functionality."""
    
    @pytest.mark.asyncio
    async def test_get_historical_data_1week(self):
        """Test getting 1 week of historical data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)
        
        result = await get_historical_data(
            symbol="AAPL",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1d",
            max_rows_preview=10
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        hist = data["message"]
        assert hist["symbol"] == "AAPL"
        assert hist["total_records"] > 0
        assert len(hist["data"]) > 0
        
        # Check data structure
        first_record = hist["data"][0]
        assert "Close" in first_record or "close" in str(first_record).lower()
        assert "Volume" in first_record or "volume" in str(first_record).lower()
        
        print(f"✅ Retrieved {hist['total_records']} historical records")
        print(f"   Date range: {hist['start_date']} to {hist['end_date']}")
    
    @pytest.mark.asyncio
    async def test_get_historical_data_1month(self):
        """Test getting 1 month of historical data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        
        result = await get_historical_data(
            symbol="MSFT",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1d",
            max_rows_preview=5
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        hist = data["message"]
        assert hist["total_records"] >= 20  # At least ~20 trading days in a month
        
        print(f"✅ Retrieved {hist['total_records']} records for 1 month period")
    
    @pytest.mark.asyncio
    async def test_get_historical_data_weekly(self):
        """Test getting weekly interval data."""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=90)
        
        result = await get_historical_data(
            symbol="AAPL",
            start=start_date.strftime("%Y-%m-%d"),
            end=end_date.strftime("%Y-%m-%d"),
            interval="1wk",
            max_rows_preview=10
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        hist = data["message"]
        assert hist["interval"] == "1wk"
        
        print(f"✅ Retrieved {hist['total_records']} weekly records")


class TestYFinanceCompanyInfo:
    """Tests for company information functionality."""
    
    @pytest.mark.asyncio
    async def test_get_company_info_aapl(self):
        """Test getting company info for Apple."""
        result = await get_company_info(symbol="AAPL")
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        info = data["message"]
        assert info["symbol"] == "AAPL"
        assert info["sector"] is not None
        assert info["industry"] is not None
        assert info["business_summary"] is not None
        assert "apple" in info["business_summary"].lower()
        
        print(f"✅ Company Info for {info.get('long_name', info.get('short_name'))}")
        print(f"   Sector: {info['sector']}")
        print(f"   Industry: {info['industry']}")
        if "full_time_employees" in info:
            print(f"   Employees: {info['full_time_employees']:,}")
    
    @pytest.mark.asyncio
    async def test_get_company_info_multiple(self):
        """Test getting company info for multiple companies."""
        symbols = ["MSFT", "GOOGL", "AMZN"]
        
        for symbol in symbols:
            result = await get_company_info(symbol=symbol)
            data = json.loads(result.text)
            assert data["success"] is True
            
            info = data["message"]
            assert info["symbol"] == symbol
            assert info["sector"] is not None
            
            print(f"✅ {symbol}: {info.get('long_name', info.get('short_name'))} - {info['sector']}")
    
    @pytest.mark.asyncio
    async def test_get_company_info_with_website(self):
        """Test that company info includes website."""
        result = await get_company_info(symbol="AAPL")
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        info = data["message"]
        assert "website" in info
        assert "apple.com" in info["website"].lower()
        
        print(f"✅ Website: {info['website']}")


class TestYFinanceFinancialStatements:
    """Tests for financial statements functionality."""
    
    @pytest.mark.asyncio
    async def test_get_income_statement(self):
        """Test getting income statement."""
        result = await get_financial_statements(
            symbol="AAPL",
            statement_type="income_statement",
            period_type="annual",
            max_columns_preview=2
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        stmt = data["message"]
        assert stmt["symbol"] == "AAPL"
        assert stmt["statement_type"] == "income_statement"
        assert stmt["period_type"] == "annual"
        assert len(stmt["data"]) > 0
        
        # Check for key income statement items
        items = [item["Item"] for item in stmt["data"]]
        # Usually includes items like "Total Revenue", "Net Income", etc.
        assert len(items) > 10
        
        print(f"✅ Income Statement: {stmt['total_line_items']} items, {stmt['periods']} periods")
        print(f"   Sample items: {', '.join(items[:3])}")
    
    @pytest.mark.asyncio
    async def test_get_balance_sheet(self):
        """Test getting balance sheet."""
        result = await get_financial_statements(
            symbol="MSFT",
            statement_type="balance_sheet",
            period_type="annual",
            max_columns_preview=2
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        stmt = data["message"]
        assert stmt["statement_type"] == "balance_sheet"
        assert len(stmt["data"]) > 0
        
        print(f"✅ Balance Sheet: {stmt['total_line_items']} items")
    
    @pytest.mark.asyncio
    async def test_get_cash_flow(self):
        """Test getting cash flow statement."""
        result = await get_financial_statements(
            symbol="GOOGL",
            statement_type="cash_flow",
            period_type="annual",
            max_columns_preview=2
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        stmt = data["message"]
        assert stmt["statement_type"] == "cash_flow"
        assert len(stmt["data"]) > 0
        
        print(f"✅ Cash Flow: {stmt['total_line_items']} items")
    
    @pytest.mark.asyncio
    async def test_get_quarterly_income_statement(self):
        """Test getting quarterly income statement."""
        result = await get_financial_statements(
            symbol="AAPL",
            statement_type="income_statement",
            period_type="quarterly",
            max_columns_preview=4
        )
        
        data = json.loads(result.text)
        assert data["success"] is True
        
        stmt = data["message"]
        assert stmt["period_type"] == "quarterly"
        assert stmt["periods"] >= 4  # Should have at least 4 quarters
        
        print(f"✅ Quarterly Income Statement: {stmt['periods']} quarters")
    
    @pytest.mark.asyncio
    async def test_financial_statement_invalid_type(self):
        """Test getting financial statement with invalid type."""
        result = await get_financial_statements(
            symbol="AAPL",
            statement_type="invalid_type",  # type: ignore
            period_type="annual"
        )
        
        data = json.loads(result.text)
        assert data["success"] is False
        
        print("✅ Correctly handled invalid statement type")


class TestYFinanceIntegration:
    """Integration tests combining multiple operations."""
    
    @pytest.mark.asyncio
    async def test_complete_stock_analysis(self):
        """Test getting complete stock analysis data."""
        symbol = "AAPL"
        
        # Get quote
        quote_result = await get_stock_quote(symbol)
        quote_data = json.loads(quote_result.text)
        assert quote_data["success"] is True
        
        # Get company info
        info_result = await get_company_info(symbol)
        info_data = json.loads(info_result.text)
        assert info_data["success"] is True
        
        # Get historical data
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        hist_result = await get_historical_data(
            symbol,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d")
        )
        hist_data = json.loads(hist_result.text)
        assert hist_data["success"] is True
        
        # Get income statement
        stmt_result = await get_financial_statements(
            symbol,
            "income_statement",
            "annual"
        )
        stmt_data = json.loads(stmt_result.text)
        assert stmt_data["success"] is True
        
        quote = quote_data["message"]
        info = info_data["message"]
        hist = hist_data["message"]
        stmt = stmt_data["message"]
        
        print(f"\n{'='*60}")
        print(f"Complete Analysis for {symbol}")
        print(f"{'='*60}")
        print(f"Company: {info.get('long_name')}")
        print(f"Sector: {info['sector']}")
        print(f"Current Price: ${quote['current_price']}")
        if "change_percent" in quote:
            print(f"Change: {quote['change_percent']}%")
        print(f"Historical Data: {hist['total_records']} records")
        print(f"Financial Statements: {stmt['total_line_items']} line items")
        print(f"{'='*60}\n")


# Run tests
if __name__ == "__main__":
    print("=" * 70)
    print("Running Yahoo Finance Tools Real API Tests")
    print("=" * 70)
    print()
    
    # Run with pytest
    pytest.main([__file__, "-v", "-s"])
