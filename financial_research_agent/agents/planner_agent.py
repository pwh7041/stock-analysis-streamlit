from datetime import datetime
from pydantic import BaseModel
from agents import Agent

# --- Get the current year dynamically ---
CURRENT_YEAR = datetime.now().year
LAST_YEAR = CURRENT_YEAR - 1

# --- Dynamic prompt ---
PROMPT = (
    f"You are a financial research planner. Given a request for financial analysis, "
    f"produce a set of web searches to gather the context needed. "
    f"Only focus on information from {CURRENT_YEAR} or {LAST_YEAR}. "
    f"Completely ignore anything older. If necessary, include the year in your search queries, "
    f"for example 'Tesla earnings {CURRENT_YEAR}' or 'Microsoft {LAST_YEAR} annual report'. "
    f"Aim for recent headlines, earnings calls or 10‑K snippets, analyst commentary, and industry background. "
    f"Output 3 to 5 search terms to query for."
    
)
'''
Output between 3 and 5 search terms to query for.
'''
class FinancialSearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web (or file) search."""


class FinancialSearchPlan(BaseModel):
    searches: list[FinancialSearchItem]
    """A list of searches to perform."""


planner_agent = Agent(
    name="FinancialPlannerAgent",
    instructions=PROMPT,
    model="o1",
    output_type=FinancialSearchPlan,
)

