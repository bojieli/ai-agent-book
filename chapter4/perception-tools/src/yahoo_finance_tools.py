"""
Yahoo Finance comprehensive tools.
Based on AWorld MCP server implementation.
Provides stock quotes, historical data, company info, and financial statements.
"""
import json
import logging
import time
import traceback
from datetime import datetime
from typing import Union, Literal

import yfinance as yf
from dotenv import load_dotenv
from mcp.types import TextContent
from pydantic import BaseModel, Field

from base import ActionResponse


load_dotenv()


class YFinanceMetadata(BaseModel):
    """Metadata for Yahoo Finance operation results."""
    
    symbol: str
    operation: str
    execution_time: float | None = None
    data_points: int | None = None
    error_type: str | None = None
    timestamp: str | None = None


async def get_stock_quote(
    symbol: str
) -> Union[str, TextContent]:
    """
    Get current stock quote information.
    
    Args:
        symbol: Stock ticker symbol (e.g., AAPL, MSFT)
        
    Returns:
        TextContent with quote data
    """
    try:
        start_time = time.time()
        logging.info(f"📈 Fetching stock quote for: {symbol}")
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or (info.get("regularMarketPrice") is None and info.get("currentPrice") is None):
            # Try to get basic history to validate symbol
            hist = ticker.history(period="1d")
            if hist.empty:
                raise ValueError(f"No data found for symbol: {symbol}")
            raise ValueError(f"Could not retrieve detailed quote for symbol: {symbol}")
        
        # Extract key quote information
        quote_data = {
            "symbol": symbol.upper(),
            "company_name": info.get("shortName", info.get("longName")),
            "current_price": info.get("regularMarketPrice", info.get("currentPrice")),
            "previous_close": info.get("previousClose"),
            "open": info.get("regularMarketOpen", info.get("open")),
            "day_high": info.get("regularMarketDayHigh", info.get("dayHigh")),
            "day_low": info.get("regularMarketDayLow", info.get("dayLow")),
            "volume": info.get("regularMarketVolume", info.get("volume")),
            "average_volume": info.get("averageVolume"),
            "market_cap": info.get("marketCap"),
            "fifty_two_week_high": info.get("fiftyTwoWeekHigh"),
            "fifty_two_week_low": info.get("fiftyTwoWeekLow"),
            "currency": info.get("currency"),
            "exchange": info.get("exchange")
        }
        
        # Filter out None values
        quote_data = {k: v for k, v in quote_data.items() if v is not None}
        
        # Calculate change
        if quote_data.get("current_price") and quote_data.get("previous_close"):
            change = quote_data["current_price"] - quote_data["previous_close"]
            change_pct = (change / quote_data["previous_close"]) * 100
            quote_data["change"] = round(change, 2)
            quote_data["change_percent"] = round(change_pct, 2)
        
        execution_time = time.time() - start_time
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_stock_quote",
            execution_time=execution_time,
            data_points=len(quote_data),
            timestamp=datetime.now().isoformat()
        )
        
        logging.info(f"✅ Stock quote: ${quote_data.get('current_price')}")
        
        action_response = ActionResponse(
            success=True,
            message=quote_data,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Failed to fetch stock quote: {str(e)}"
        logging.error(f"Stock quote error: {traceback.format_exc()}")
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_stock_quote",
            error_type=type(e).__name__,
            timestamp=datetime.now().isoformat()
        )
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_historical_data(
    symbol: str,
    start: str,
    end: str,
    interval: str = "1d",
    max_rows_preview: int = 10
) -> Union[str, TextContent]:
    """
    Retrieve historical stock data.
    
    Args:
        symbol: Stock ticker symbol
        start: Start date (YYYY-MM-DD)
        end: End date (YYYY-MM-DD)
        interval: Data interval (1d, 1wk, 1mo, etc.)
        max_rows_preview: Maximum rows to show in preview (0 for all)
        
    Returns:
        TextContent with historical data
    """
    try:
        start_time = time.time()
        logging.info(f"📈 Fetching historical data for: {symbol}")
        
        ticker = yf.Ticker(symbol)
        hist_df = ticker.history(start=start, end=end, interval=interval)
        
        if hist_df.empty:
            raise ValueError(f"No historical data found for {symbol}")
        
        # Convert DataFrame to list of dictionaries
        hist_df.reset_index(inplace=True)
        
        # Ensure date columns are strings
        if "Date" in hist_df.columns:
            hist_df["Date"] = hist_df["Date"].astype(str)
        if "Datetime" in hist_df.columns:
            hist_df["Datetime"] = hist_df["Datetime"].astype(str)
        
        # Clean column names
        hist_df.columns = hist_df.columns.str.replace(" ", "")
        
        historical_data = hist_df.to_dict(orient="records")
        execution_time = time.time() - start_time
        
        # Prepare result with preview
        result = {
            "symbol": symbol.upper(),
            "start_date": start,
            "end_date": end,
            "interval": interval,
            "total_records": len(historical_data),
            "data": historical_data if max_rows_preview == 0 else historical_data[:max_rows_preview]
        }
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_historical_data",
            execution_time=execution_time,
            data_points=len(historical_data),
            timestamp=datetime.now().isoformat()
        )
        
        logging.info(f"✅ Retrieved {len(historical_data)} historical records")
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Failed to fetch historical data: {str(e)}"
        logging.error(f"Historical data error: {traceback.format_exc()}")
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_historical_data",
            error_type=type(e).__name__,
            timestamp=datetime.now().isoformat()
        )
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_company_info(
    symbol: str
) -> Union[str, TextContent]:
    """
    Get company information and business details.
    
    Args:
        symbol: Stock ticker symbol
        
    Returns:
        TextContent with company information
    """
    try:
        start_time = time.time()
        logging.info(f"🏢 Fetching company info for: {symbol}")
        
        ticker = yf.Ticker(symbol)
        info = ticker.info
        
        if not info or not info.get("symbol"):
            raise ValueError(f"No company information found for symbol: {symbol}")
        
        # Extract key company information
        company_data = {
            "symbol": info.get("symbol"),
            "short_name": info.get("shortName"),
            "long_name": info.get("longName"),
            "sector": info.get("sector"),
            "industry": info.get("industry"),
            "full_time_employees": info.get("fullTimeEmployees"),
            "business_summary": info.get("longBusinessSummary"),
            "city": info.get("city"),
            "state": info.get("state"),
            "country": info.get("country"),
            "website": info.get("website"),
            "exchange": info.get("exchange"),
            "currency": info.get("currency"),
            "market_cap": info.get("marketCap"),
            "pe_ratio": info.get("trailingPE"),
            "forward_pe": info.get("forwardPE"),
            "dividend_yield": info.get("dividendYield"),
            "beta": info.get("beta")
        }
        
        # Filter out None values
        company_data = {k: v for k, v in company_data.items() if v is not None}
        
        execution_time = time.time() - start_time
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_company_info",
            execution_time=execution_time,
            data_points=len(company_data),
            timestamp=datetime.now().isoformat()
        )
        
        logging.info(f"✅ Retrieved company info: {company_data.get('long_name', company_data.get('short_name'))}")
        
        action_response = ActionResponse(
            success=True,
            message=company_data,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Failed to fetch company info: {str(e)}"
        logging.error(f"Company info error: {traceback.format_exc()}")
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_company_info",
            error_type=type(e).__name__,
            timestamp=datetime.now().isoformat()
        )
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )


async def get_financial_statements(
    symbol: str,
    statement_type: Literal["income_statement", "balance_sheet", "cash_flow"],
    period_type: Literal["annual", "quarterly"] = "annual",
    max_columns_preview: int = 4
) -> Union[str, TextContent]:
    """
    Get financial statements for a company.
    
    Args:
        symbol: Stock ticker symbol
        statement_type: Type of statement (income_statement, balance_sheet, cash_flow)
        period_type: Period type (annual or quarterly)
        max_columns_preview: Maximum periods to show (0 for all)
        
    Returns:
        TextContent with financial statement data
    """
    try:
        start_time = time.time()
        logging.info(f"📋 Fetching {statement_type} for: {symbol}")
        
        ticker = yf.Ticker(symbol)
        statement_df = None
        
        # Get appropriate statement
        if statement_type == "income_statement":
            statement_df = ticker.income_stmt if period_type == "annual" else ticker.quarterly_income_stmt
        elif statement_type == "balance_sheet":
            statement_df = ticker.balance_sheet if period_type == "annual" else ticker.quarterly_balance_sheet
        elif statement_type == "cash_flow":
            statement_df = ticker.cashflow if period_type == "annual" else ticker.quarterly_cashflow
        else:
            raise ValueError(f"Invalid statement_type: {statement_type}")
        
        if statement_df is None or statement_df.empty:
            raise ValueError(f"No {period_type} {statement_type} data found for symbol {symbol}")
        
        # Process DataFrame
        statement_df.reset_index(inplace=True)
        statement_df.rename(columns={"index": "Item"}, inplace=True)
        
        # Convert date columns to strings
        for col in statement_df.columns:
            if col != "Item":
                try:
                    if hasattr(col, "strftime"):
                        new_col_name = col.strftime("%Y-%m-%d")
                        statement_df.rename(columns={col: new_col_name}, inplace=True)
                except Exception:
                    pass
        
        # Limit columns if needed
        if max_columns_preview > 0 and len(statement_df.columns) > (max_columns_preview + 1):
            columns_to_keep = ["Item"] + list(statement_df.columns[1:max_columns_preview + 1])
            statement_df = statement_df[columns_to_keep]
        
        statement_data = statement_df.to_dict(orient="records")
        execution_time = time.time() - start_time
        
        result = {
            "symbol": symbol.upper(),
            "statement_type": statement_type,
            "period_type": period_type,
            "total_line_items": len(statement_data),
            "periods": len(statement_df.columns) - 1,
            "data": statement_data
        }
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_financial_statements",
            execution_time=execution_time,
            data_points=len(statement_data),
            timestamp=datetime.now().isoformat()
        )
        
        logging.info(f"✅ Retrieved {statement_type}: {len(statement_data)} items")
        
        action_response = ActionResponse(
            success=True,
            message=result,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
        
    except Exception as e:
        error_msg = f"Failed to fetch financial statements: {str(e)}"
        logging.error(f"Financial statements error: {traceback.format_exc()}")
        
        metadata = YFinanceMetadata(
            symbol=symbol.upper(),
            operation="get_financial_statements",
            error_type=type(e).__name__,
            timestamp=datetime.now().isoformat()
        )
        
        action_response = ActionResponse(
            success=False,
            message=error_msg,
            metadata=metadata.model_dump()
        )
        
        return TextContent(
            type="text",
            text=json.dumps(action_response.model_dump())
        )
