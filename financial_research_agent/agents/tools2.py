import os, requests, time, logging
from typing import Dict, Optional
from pydantic import BaseModel, Field
from agents import function_tool

from pathlib import Path
from dotenv import load_dotenv
dotenv_path = Path(__file__).resolve().parent.parent.parent / ".env"
load_dotenv(dotenv_path)

API_KEY = os.getenv("FMP_API_KEY")
if not API_KEY:
    raise RuntimeError("Set FMP_API_KEY in the .env file")

def safe_get(url, tries=3, pause=3):
    for i in range(tries):
        r = requests.get(url, timeout=10)
        if r.status_code == 200:
            return r.json()
        if r.status_code in (429, 403):  # rate limit / exhausted
            wait = pause * (i + 1)
            logging.warning(f"{r.status_code} on {url}. Retry in {wait}s")
            time.sleep(wait)
            continue
        r.raise_for_status()
    return None

def stmt(endpoint, symbol):
    url = (f"https://financialmodelingprep.com/api/v3/{endpoint}/"
           f"{symbol}?period=annual&limit=1&apikey={API_KEY}")
    data = safe_get(url)
    if isinstance(data, list) and data:
        rec = data[0]
        numeric = {k: float(v) for k, v in rec.items() if isinstance(v, (int, float))}
        return rec.get("date"), numeric
    return None, {}

class CompanyInfo(BaseModel):
    ticker: str; name: Optional[str]=None; industry: Optional[str]=None
    sector: Optional[str]=None; market_cap: Optional[float]=None
    currency: Optional[str]=None; exchange: Optional[str]=None
    country: Optional[str]=None; stock_price: Optional[float]=None

class FinancialStatementData(BaseModel):
    date: Optional[str]=None; data: Dict[str, Optional[float]] = Field(default_factory=dict)

class FinancialStatements(BaseModel):
    income_statement: Optional[FinancialStatementData]=None
    balance_sheet: Optional[FinancialStatementData]=None
    cash_flow: Optional[FinancialStatementData]=None

class FinancialData(BaseModel):
    company_info: CompanyInfo; financial_statements: FinancialStatements
    status: str="success"; error: Optional[str]=None

@function_tool
def get_latest_financials(ticker: str) -> FinancialData:
    ci = CompanyInfo(ticker=ticker)
    try:
        prof = safe_get(f"https://financialmodelingprep.com/api/v3/profile/{ticker}?apikey={API_KEY}")
        if prof:
            p = prof[0]
            ci.name = p.get("companyName"); ci.industry = p.get("industry")
            ci.sector = p.get("sector"); ci.market_cap = p.get("mktCap")
            ci.currency = p.get("currency"); ci.exchange = p.get("exchangeShortName")
            ci.country = p.get("country"); ci.stock_price = p.get("price")

        fs = FinancialStatements()
        for tag, ep in (("income_statement","income-statement"),
                        ("balance_sheet","balance-sheet-statement"),
                        ("cash_flow","cash-flow-statement")):
            date, data = stmt(ep, ticker)
            if data:
                setattr(fs, tag, FinancialStatementData(date=date, data=data))

        status = "success" if any(vars(fs).values()) else "empty"
        return FinancialData(company_info=ci, financial_statements=fs, status=status)

    except Exception as e:
        logging.error(e)
        return FinancialData(company_info=ci, financial_statements=FinancialStatements(),
                             status="error", error=str(e))