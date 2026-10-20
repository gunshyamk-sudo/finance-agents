"""Day 4 - pandas: read a general ledger, build a trial balance, export to Excel."""
import pandas as pd
from config import DATA, OUT

gl = pd.read_csv(DATA / "general_ledger.csv", parse_dates=["date"])
print(gl.head(), "\n", gl.shape)

# 1) Trial balance: total debits and credits per account
tb = gl.groupby(["account_code", "account_name"], as_index=False)[["debit", "credit"]].sum()
tb["balance"] = tb["debit"] - tb["credit"]
print(tb)
print("Debits = Credits?", round(tb["debit"].sum(), 2) == round(tb["credit"].sum(), 2))

# 2) Monthly movement per account (pivot table, like Excel)
gl["month"] = gl["date"].dt.to_period("M").astype(str)
gl["net"] = gl["debit"] - gl["credit"]
monthly = gl.pivot_table(index=["account_code", "account_name"], columns="month", values="net", aggfunc="sum", fill_value=0)

# 3) Export both to one Excel file
with pd.ExcelWriter(OUT / "trial_balance.xlsx") as w:
    tb.to_excel(w, sheet_name="Trial Balance", index=False)
    monthly.to_excel(w, sheet_name="Monthly Movement")
print("Saved", OUT / "trial_balance.xlsx")
