"""Day 25 - Bank reconciliation. The MATCHING is done by code (exact & auditable);
the AI agent only EXPLAINS exceptions and suggests journals.
Run:  python day25_bank_recon.py            (matching only, no API cost)
      python day25_bank_recon.py --agent    (adds the AI explanation)"""
import sys
import pandas as pd
from config import DATA, OUT

def load(bank_file=None, gl_file=None):
    bank = pd.read_csv(bank_file or DATA / "bank_statement_sep2026.csv", parse_dates=["date"])
    gl = pd.read_csv(gl_file or DATA / "gl_cash_sep2026.csv", parse_dates=["date"])
    return bank, gl

def reconcile(bank, gl, date_tolerance_days=3):
    bank, gl = bank.copy(), gl.copy()
    bank["matched_to"] = None; gl["matched_to"] = None
    # Pass 1: same reference and same amount
    for i, b in bank.iterrows():
        cand = gl[(gl.matched_to.isna()) & (gl.reference == b.reference) & ((gl.amount_aed - b.amount_aed).abs() < 0.01)]
        if len(cand):
            j = cand.index[0]; bank.at[i, "matched_to"] = gl.at[j, "gl_line"]; gl.at[j, "matched_to"] = b.bank_line
    # Pass 2: same amount within date tolerance (reference missing or different)
    for i, b in bank[bank.matched_to.isna()].iterrows():
        cand = gl[(gl.matched_to.isna()) & ((gl.amount_aed - b.amount_aed).abs() < 0.01) &
                  ((gl.date - b.date).abs().dt.days <= date_tolerance_days)]
        if len(cand):
            j = cand.index[0]; bank.at[i, "matched_to"] = gl.at[j, "gl_line"]; gl.at[j, "matched_to"] = b.bank_line
    exceptions = pd.concat([
        bank[bank.matched_to.isna()].assign(side="In bank, not matched in GL"),
        gl[gl.matched_to.isna()].assign(side="In GL, not matched in bank")])[["side", "date", "description", "reference", "amount_aed"]]
    summary = {"bank_net_movement": round(float(bank.amount_aed.sum()), 2), "gl_net_movement": round(float(gl.amount_aed.sum()), 2),
               "difference": round(float(bank.amount_aed.sum() - gl.amount_aed.sum()), 2),
               "matched_lines": int(bank.matched_to.notna().sum()), "exceptions": len(exceptions)}
    return summary, exceptions.reset_index(drop=True)

def get_exceptions() -> list:
    """Tool for the agent: run the reconciliation and return unmatched items."""
    s, ex = reconcile(*load())
    return {"summary": s, "exceptions": ex.assign(date=ex.date.dt.date.astype(str)).to_dict("records")}

if __name__ == "__main__":
    summary, ex = reconcile(*load())
    print(summary); print(ex.to_string())
    ex.to_excel(OUT / "recon_exceptions.xlsx", index=False)
    if "--agent" in sys.argv:
        from agent_core import run_agent
        tools = [{"name": "get_exceptions", "description": "Run the bank reconciliation and return the summary and unmatched items.",
                  "input_schema": {"type": "object", "properties": {}}}]
        system = ("You are a financial controller. For each reconciliation exception: classify it (timing difference, "
                  "bank item not recorded, error, duplicate), explain it in one line, and propose a journal entry "
                  "(Dr/Cr with account codes from: 1000 Cash at Bank, 2000 Accounts Payable, 1100 Accounts Receivable, "
                  "7000 Bank Charges, 4100 Service Revenue) or 'no entry - timing'. Note: matching amounts with different "
                  "references on the same date may be one transposition error.")
        print(run_agent("Reconcile September 2026 and explain all exceptions.", tools, {"get_exceptions": get_exceptions}, system))
