"""Day 7 - A simple LLM *pipeline* (not yet an agent): categorise expenses into GL accounts.
Run:  python day07_expense_categoriser.py 20      (20 = number of rows, keep small to save cost)"""
import json, sys, re
import anthropic, pandas as pd
from config import DATA, OUT, MODEL

client = anthropic.Anthropic()
coa = pd.read_csv(DATA / "chart_of_accounts.csv")
EXPENSE_ACCOUNTS = coa[coa.account_type == "Expense"]
COA_TEXT = "\n".join(f"{r.account_code} {r.account_name}" for r in EXPENSE_ACCOUNTS.itertuples())

SYSTEM = f"""You are an accounts payable specialist. Map each expense to ONE account from this chart of accounts:
{COA_TEXT}
Reply with JSON only, no other text: {{"account_code": <int>, "confidence": <0-1>, "reason": "<short>"}}"""

def parse_json(text: str) -> dict:
    """Models sometimes wrap JSON in ```json fences - strip them."""
    text = re.sub(r"^```(json)?|```$", "", text.strip(), flags=re.M).strip()
    return json.loads(text)

def categorise(row) -> dict:
    msg = f"Merchant: {row.merchant}\nDescription: {row.description}\nAmount: AED {row.amount_aed}"
    resp = client.messages.create(model=MODEL, max_tokens=200, temperature=0, system=SYSTEM,
                                  messages=[{"role": "user", "content": msg}])
    try:
        return parse_json(resp.content[0].text)
    except Exception:
        return {"account_code": None, "confidence": 0, "reason": "Could not parse: " + resp.content[0].text[:80]}

if __name__ == "__main__":
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 20
    expenses = pd.read_csv(DATA / "expenses.csv").head(n)
    results = []
    for row in expenses.itertuples():
        r = categorise(row)
        print(row.expense_id, row.merchant, "->", r)
        results.append(r)
    out = pd.concat([expenses, pd.DataFrame(results)], axis=1)
    out.to_excel(OUT / "expenses_categorised.xlsx", index=False)
    print("Saved", OUT / "expenses_categorised.xlsx")
