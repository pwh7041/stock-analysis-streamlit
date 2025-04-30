from pydantic import BaseModel

from agents import Agent

# -----------------------------------------------------------------------------
# Wrap it as an agent-usable Tool
# -----------------------------------------------------------------------------
from .tools import fetch_financials
from .tools2 import get_latest_financials

# A sub‑agent focused on analyzing a company's fundamentals.
FINANCIALS_PROMPT = (
    "You are a financial analyst focused on company's current stock price and company fundamentals such as revenue, "
    "profit, margins and growth trajectory. Must perform a collection of web (and optional file) "
    "search about a company and its current stock price, and also must use the fetch_financials tool about a company" 
    "(by passing ticker such as AAPL). and then provide the results/outputs"""
    )



class AnalysisSummary(BaseModel):
    summary: str
    """Short text summary for this aspect of the analysis."""


financials_agent = Agent(
    name="FundamentalsAnalystAgent",
    instructions=FINANCIALS_PROMPT,
    output_type=AnalysisSummary,
    model="gpt-4o",
    tools=[get_latest_financials]
)
