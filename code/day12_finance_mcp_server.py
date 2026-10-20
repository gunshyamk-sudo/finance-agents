"""Day 12 - A tiny MCP server that lets Claude Desktop read your finance data.
Claude Desktop starts this file for you (see the Day 12 steps for the config)."""
import pandas as pd
from pathlib import Path

try:                                    # mcp version 2.x
    from mcp.server.mcpserver import MCPServer as Server
except ImportError:                     # mcp version 1.x (used in many courses)
    from mcp.server.fastmcp import FastMCP as Server

DATA = Path(__file__).resolve().parent.parent / "data"
server = Server("finance-data")

@server.tool()
def get_account_balance(account_code: int) -> dict:
    """Return total debits, credits and balance for one GL account code (e.g. 6800)."""
    gl = pd.read_csv(DATA / "general_ledger.csv")
    a = gl[gl.account_code == account_code]
    return {"account_code": account_code, "account_name": a.account_name.iloc[0] if len(a) else "unknown",
            "debits": round(float(a.debit.sum()), 2), "credits": round(float(a.credit.sum()), 2),
            "balance": round(float(a.debit.sum() - a.credit.sum()), 2)}

@server.tool()
def get_open_invoices(vendor: str = "") -> list:
    """List open AP invoices, optionally filtered by vendor name (partial match)."""
    ap = pd.read_csv(DATA / "ap_subledger.csv")
    ap = ap[ap.status == "Open"]
    if vendor:
        ap = ap[ap.vendor.str.contains(vendor, case=False)]
    return ap.to_dict("records")

if __name__ == "__main__":
    server.run()
