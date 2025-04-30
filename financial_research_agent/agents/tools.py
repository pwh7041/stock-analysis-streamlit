import yfinance as yf
from pydantic import BaseModel
from agents import function_tool

# -----------------------------------------------------------------------------
# Tool prompt and logic
# -----------------------------------------------------------------------------
class FinancialsData(BaseModel):
    ticker: str
    market_cap: float | None
    pe_ratio: float | None
    eps: float | None
    revenue: float | None

@function_tool
def fetch_financials(ticker: str) -> FinancialsData:
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        return FinancialsData(
            ticker=ticker,
            market_cap=info.get("marketCap"),
            pe_ratio=info.get("trailingPE"),
            eps=info.get("trailingEps"),
            revenue=info.get("totalRevenue"),
        )
    except Exception as e:
        pass






















