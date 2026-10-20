"""Day 10 - Finance Analyst Agent built from scratch (no framework).
Run:  python day10_raw_agent.py "Which cost centre had the biggest overspend in Q3?" """
import sys
import pandas as pd
from config import DATA
from agent_core import run_agent

df = pd.read_csv(DATA / "budget_vs_actual.csv")
df["variance_aed"] = (df["actual_aed"] - df["budget_aed"]).round(2)
df["quarter"] = "Q" + ((pd.to_datetime(df["month"]).dt.month - 1) // 3 + 1).astype(str)

def describe_data() -> dict:
    return {"columns": list(df.columns), "months": sorted(df.month.unique()),
            "cost_centres": sorted(df.cost_centre.unique()), "rows": len(df)}

def variance_by(group_by: str, month: str = None, quarter: str = None, cost_centre: str = None) -> list:
    d = df
    if month: d = d[d.month == month]
    if quarter: d = d[d.quarter == quarter]
    if cost_centre: d = d[d.cost_centre == cost_centre]
    g = d.groupby(group_by)[["budget_aed", "actual_aed", "variance_aed"]].sum().round(2)
    g["variance_pct"] = (g["variance_aed"] / g["budget_aed"]).round(4)
    return g.reset_index().to_dict("records")

def top_variances(n: int = 5, month: str = None) -> list:
    d = df if not month else df[df.month == month]
    d = d.assign(variance_pct=(d.variance_aed / d.budget_aed).round(4))
    return d.reindex(d.variance_aed.abs().sort_values(ascending=False).index).head(n).to_dict("records")

TOOLS = [
    {"name": "describe_data", "description": "Show columns, available months and cost centres in the budget vs actual data. Call this first.",
     "input_schema": {"type": "object", "properties": {}}},
    {"name": "variance_by", "description": "Sum budget, actual and variance (actual minus budget; positive = overspend) grouped by a column, with optional filters.",
     "input_schema": {"type": "object", "properties": {
         "group_by": {"type": "string", "enum": ["cost_centre", "account_name", "month", "quarter"]},
         "month": {"type": "string", "description": "YYYY-MM"}, "quarter": {"type": "string", "enum": ["Q1", "Q2", "Q3"]},
         "cost_centre": {"type": "string"}}, "required": ["group_by"]}},
    {"name": "top_variances", "description": "Largest individual line variances by absolute amount.",
     "input_schema": {"type": "object", "properties": {"n": {"type": "integer"}, "month": {"type": "string"}}}},
]
FUNCS = {"describe_data": describe_data, "variance_by": variance_by, "top_variances": top_variances}
SYSTEM = ("You are an FP&A analyst. ALWAYS use the tools to get numbers - never guess or calculate totals yourself. "
          "Amounts are AED. Positive variance = overspend. Answer clearly with the key numbers.")

if __name__ == "__main__":
    q = sys.argv[1] if len(sys.argv) > 1 else "Which cost centre had the biggest overspend in Q3 2026, and which line items drove it?"
    print("\nANSWER:\n", run_agent(q, TOOLS, FUNCS, SYSTEM))
