"""Day 18 - Financial Statement Analyst Agent using FREE official SEC EDGAR data.
Set SEC_USER_AGENT in your .env, e.g.  SEC_USER_AGENT=Your Name your.email@example.com
Run:  python day18_edgar_analyst.py "Analyse MSFT and compare it with AAPL" """
import os, sys
from datetime import date
import requests
from agent_core import run_agent

HEADERS = {"User-Agent": os.getenv("SEC_USER_AGENT", "Finance Agent Learner learner@example.com")}
_tickers = None

def lookup_cik(ticker: str) -> str:
    global _tickers
    if _tickers is None:
        _tickers = requests.get("https://www.sec.gov/files/company_tickers.json", headers=HEADERS, timeout=30).json()
    for row in _tickers.values():
        if row["ticker"].upper() == ticker.upper():
            return str(row["cik_str"]).zfill(10)
    raise ValueError(f"Ticker {ticker} not found")

def _latest_annual(facts, tags, duration=True):
    """Pick the latest full-year value from 10-K filings for the first tag that exists."""
    for tag in tags:
        units = facts.get("us-gaap", {}).get(tag, {}).get("units", {}).get("USD")
        if not units:
            continue
        rows = [u for u in units if u.get("form") == "10-K" and u.get("fp") == "FY"]
        if duration:
            rows = [u for u in rows if "start" in u and 350 <= (date.fromisoformat(u["end"]) - date.fromisoformat(u["start"])).days <= 380]
        if rows:
            best = max(rows, key=lambda u: (u["end"], u["filed"]))
            return {"tag": tag, "value": best["val"], "period_end": best["end"], "filed": best["filed"]}
    return None

def get_financials(ticker: str) -> dict:
    """Latest annual figures (USD) from the company's 10-K XBRL data."""
    cik = lookup_cik(ticker)
    facts = requests.get(f"https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json", headers=HEADERS, timeout=60).json()["facts"]
    out = {"ticker": ticker.upper(), "cik": cik}
    out["revenue"] = _latest_annual(facts, ["Revenues", "RevenueFromContractWithCustomerExcludingAssessedTax", "SalesRevenueNet"])
    out["net_income"] = _latest_annual(facts, ["NetIncomeLoss"])
    out["operating_income"] = _latest_annual(facts, ["OperatingIncomeLoss"])
    for k, tag in [("total_assets", "Assets"), ("total_liabilities", "Liabilities"), ("equity", "StockholdersEquity"),
                   ("current_assets", "AssetsCurrent"), ("current_liabilities", "LiabilitiesCurrent")]:
        out[k] = _latest_annual(facts, [tag], duration=False)
    return out

def compute_ratios(ticker: str) -> dict:
    """Ratios are computed in Python (not by the LLM) so they are exact."""
    f = get_financials(ticker)
    v = lambda k: (f.get(k) or {}).get("value")
    div = lambda a, b: round(a / b, 4) if a is not None and b else None
    return {"ticker": f["ticker"], "period_end": (f.get("revenue") or {}).get("period_end"),
            "revenue": v("revenue"), "net_income": v("net_income"),
            "net_margin": div(v("net_income"), v("revenue")), "operating_margin": div(v("operating_income"), v("revenue")),
            "current_ratio": div(v("current_assets"), v("current_liabilities")),
            "debt_to_equity": div(v("total_liabilities"), v("equity")), "return_on_assets": div(v("net_income"), v("total_assets"))}

TOOLS = [
    {"name": "get_financials", "description": "Get latest annual 10-K figures (USD) for a US-listed ticker from SEC EDGAR.",
     "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}},
    {"name": "compute_ratios", "description": "Compute net margin, operating margin, current ratio, debt-to-equity and ROA for a ticker.",
     "input_schema": {"type": "object", "properties": {"ticker": {"type": "string"}}, "required": ["ticker"]}},
]
FUNCS = {"get_financials": get_financials, "compute_ratios": compute_ratios}
SYSTEM = ("You are an equity research analyst. Use the tools for ALL numbers. Write a one-page analysis: "
          "key figures table, ratio interpretation, strengths, risks. State the period end and that data is from SEC 10-K filings.")

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Analyse MSFT and compare its profitability and liquidity with AAPL."
    print(run_agent(q, TOOLS, FUNCS, SYSTEM))
