import os
import asyncio
from pathlib import Path

import streamlit as st
import nest_asyncio  # <–– allows async inside Streamlit

# --- Project imports ---------------------------------------------------------
# Adjust the import to match your project’s package layout.
# Assumes this file lives in the project root next to the `examples` package
from financial_research_agent.manager import FinancialResearchManager

from agents import set_default_openai_key
from dotenv import load_dotenv
load_dotenv()
set_default_openai_key(os.getenv("OPENAI_API_KEY"))

# -----------------------------------------------------------------------------
# Helper: run the manager step‑by‑step so we can surface progress to Streamlit
# -----------------------------------------------------------------------------
async def _run_analysis(query: str) -> tuple[
    "FinancialReportData",  # manager._write_report result
    "VerificationResult", # manager._verify_report result
    str,
]:
    """Executes the full research pipeline and returns the final artefacts."""

    mgr = FinancialResearchManager()

    # 1) PLAN -----------------------------------------------------------------
    plan = await mgr._plan_searches(query)

    # 2) SEARCH – show granular progress with Streamlit’s progress bar --------
    search_bar = st.progress(0, text="Running web searches…")
    tasks = [asyncio.create_task(mgr._search(item)) for item in plan.searches]
    results: list[str] = []
    for completed, task in enumerate(asyncio.as_completed(tasks), start=1):
        result = await task
        if result is not None:
            results.append(result)
        pct = completed / len(tasks)
        search_bar.progress(pct, text=f"Searching… {completed}/{len(tasks)}")

    search_bar.empty()  # remove once done

    # 3) WRITE REPORT ---------------------------------------------------------
    with st.status("Synthesising report …", expanded=False) as status:
        report = await mgr._write_report(query, results)
        status.update(label="Report drafted ✅", state="complete")

    # 4) VERIFY ---------------------------------------------------------------
    with st.status("Running verification …", expanded=False) as status:
        verification = await mgr._verify_report(report)
        status.update(label="Verification complete ✅", state="complete")

    return report, verification, mgr.trace_id


# -----------------------------------------------------------------------------
# Streamlit UI
# -----------------------------------------------------------------------------

def main() -> None:
    st.set_page_config(page_title="AI Financial Researcher", layout="wide")
    st.title("📈 AI‑Powered Financial Research")
    st.caption("Type a public company name or ticker and let the agents do the rest.")
    
    query = st.text_input("Company or research question", placeholder="Apple Inc")

    if st.button("Run analysis", disabled=not query.strip()):
        # Allow nested event loops inside Streamlit
        nest_asyncio.apply()

        # Kick off analysis ----------------------------------------------------
        report_placeholder = st.empty()
        verify_placeholder = st.empty()

        try:
            report, verification, trace_id = asyncio.run(_run_analysis(query))
        except Exception as e:
            st.error(f"⛔️ Something went wrong: {e}")
            raise  # Surface in Streamlit logs

        # Show results --------------------------------------------------------
        report_placeholder.markdown(report.markdown_report, unsafe_allow_html=True)

        with verify_placeholder.expander("🔍 Verification results"):
            if verification.verified:
                st.success("Report passed automated sanity checks ✅")
            else:
                st.error("Issues found during verification ❌")
                st.write(verification.issues)
                
        st.info("Analysis complete. Scroll up for details.")


if __name__ == "__main__":
    main()
