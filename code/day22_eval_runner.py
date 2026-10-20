"""Day 22 - Evaluate the Day 7 expense categoriser against the answer key.
Run: python day22_eval_runner.py 50"""
import sys
import pandas as pd
from config import DATA, OUT
from day07_expense_categoriser import categorise

n = int(sys.argv[1]) if len(sys.argv) > 1 else 50
exp = pd.read_csv(DATA / "expenses.csv").head(n)
key = pd.read_csv(DATA / "expenses_answer_key.csv")
rows = []
for r in exp.itertuples():
    pred = categorise(r)
    rows.append({"expense_id": r.expense_id, "merchant": r.merchant, "description": r.description,
                 "predicted": pred.get("account_code"), "confidence": pred.get("confidence"), "reason": pred.get("reason")})
res = pd.DataFrame(rows).merge(key, on="expense_id")
res["correct"] = res.predicted == res.correct_account_code
acc = res.correct.mean()
print(f"Accuracy: {acc:.1%} on {len(res)} expenses")
print("\nMistakes:\n", res[~res.correct][["expense_id", "description", "predicted", "correct_account_code", "reason"]].to_string(index=False))
with pd.ExcelWriter(OUT / "eval_results.xlsx") as w:
    res.to_excel(w, sheet_name="Results", index=False)
    pd.DataFrame([{"rows": len(res), "accuracy": acc}]).to_excel(w, sheet_name="Summary", index=False)
print("Saved", OUT / "eval_results.xlsx")
