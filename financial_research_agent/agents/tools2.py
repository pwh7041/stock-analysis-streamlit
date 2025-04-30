import yfinance as yf
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from agents import function_tool

class CompanyInfo(BaseModel):
    """Company information model"""
    ticker: str
    name: Optional[str] = None
    industry: Optional[str] = None
    sector: Optional[str] = None
    market_cap: Optional[float] = None
    currency: str = "USD"
    exchange: Optional[str] = None
    country: Optional[str] = None
    Stock_price: Optional[float] = None

class FinancialStatementData(BaseModel):
    """Model for a single financial statement"""
    date: str
    data: Dict[str, Optional[float]] = Field(default_factory=dict)

class FinancialStatements(BaseModel):
    """Container for all financial statements"""
    income_statement: Optional[FinancialStatementData] = None
    balance_sheet: Optional[FinancialStatementData] = None
    cash_flow: Optional[FinancialStatementData] = None

class FinancialData(BaseModel):
    """Top-level model for all financial data"""
    company_info: CompanyInfo
    financial_statements: FinancialStatements
    status: str = "success"
    error: Optional[str] = None

@function_tool
def get_latest_financials(ticker_symbol: str) -> FinancialData:
    """
    Pull latest annual financial statements for a company listed in US or Canada.
    Returns data in a Pydantic model format.
    
    Parameters:
    - ticker_symbol: Stock ticker symbol (add .TO for TSX listed companies)
    
    Returns:
    - FinancialData Pydantic model containing the latest financial statements
    """
    try:
        # Get ticker data
        ticker = yf.Ticker(ticker_symbol)
        
        # Initialize company info
        company_info = CompanyInfo(ticker=ticker_symbol)
        
        # Get company info
        try:
            info = ticker.info
            company_info.name = info.get("shortName") or info.get("longName")
            company_info.industry = info.get("industry")
            company_info.sector = info.get("sector")
            company_info.market_cap = info.get("marketCap")
            company_info.currency = info.get("currency", "USD")
            company_info.exchange = info.get("exchange")
            company_info.country = info.get("country")
            company_info.stock_price = info.get("regularMarketPrice")
        except Exception:
            pass
        
        # Initialize financial statements
        financial_statements = FinancialStatements()
        
        # Get income statement (latest year only)
        try:
            income_df = ticker.income_stmt
            if income_df is not None and not income_df.empty:
                latest_period = income_df.columns[0]
                period_str = latest_period.strftime('%Y-%m-%d') if hasattr(latest_period, 'strftime') else str(latest_period)
                
                # Extract and clean data
                statement_data = {}
                for k, v in income_df.iloc[:, 0].items():
                    if v is not None:
                        # Convert numpy types to native Python types if needed
                        if hasattr(v, 'item'):
                            v = v.item()
                        try:
                            statement_data[k] = float(v)
                        except (ValueError, TypeError):
                            pass
                
                financial_statements.income_statement = FinancialStatementData(
                    date=period_str,
                    data=statement_data
                )
        except Exception:
            pass
        
        # Get balance sheet (latest year only)
        try:
            balance_df = ticker.balance_sheet
            if balance_df is not None and not balance_df.empty:
                latest_period = balance_df.columns[0]
                period_str = latest_period.strftime('%Y-%m-%d') if hasattr(latest_period, 'strftime') else str(latest_period)
                
                # Extract and clean data
                statement_data = {}
                for k, v in balance_df.iloc[:, 0].items():
                    if v is not None:
                        if hasattr(v, 'item'):
                            v = v.item()
                        try:
                            statement_data[k] = float(v)
                        except (ValueError, TypeError):
                            pass
                
                financial_statements.balance_sheet = FinancialStatementData(
                    date=period_str,
                    data=statement_data
                )
        except Exception:
            pass
        
        # Get cash flow statement (latest year only)
        try:
            cash_df = ticker.cashflow
            if cash_df is not None and not cash_df.empty:
                latest_period = cash_df.columns[0]
                period_str = latest_period.strftime('%Y-%m-%d') if hasattr(latest_period, 'strftime') else str(latest_period)
                
                # Extract and clean data
                statement_data = {}
                for k, v in cash_df.iloc[:, 0].items():
                    if v is not None:
                        if hasattr(v, 'item'):
                            v = v.item()
                        try:
                            statement_data[k] = float(v)
                        except (ValueError, TypeError):
                            pass
                
                financial_statements.cash_flow = FinancialStatementData(
                    date=period_str,
                    data=statement_data
                )
        except Exception:
            pass
        
        # Create and return the full financial data model
        return FinancialData(
            company_info=company_info,
            financial_statements=financial_statements
        )
        
    except Exception as e:
        # Return error response in the same Pydantic format
        return FinancialData(
            status="error",
            error=str(e),
            company_info=CompanyInfo(ticker=ticker_symbol),
            financial_statements=FinancialStatements()
        )

