"""Day 13 - Reflection pattern: one LLM call drafts commentary, a second call REVIEWS it against the data."""
import anthropic, pandas as pd
from config import DATA, MODEL

client = anthropic.Anthropic()
df = pd.read_csv(DATA / "budget_vs_actual.csv")
month = "2026-09"
d = df[df.month == month].copy()
d["variance_aed"] = (d.actual_aed - d.budget_aed).round(2)
d["variance_pct"] = (d.variance_aed / d.budget_aed * 100).round(1)
table = d[["cost_centre", "account_name", "budget_aed", "actual_aed", "variance_aed", "variance_pct"]].to_string(index=False)

def ask(system, prompt):
    r = client.messages.create(model=MODEL, max_tokens=1200, temperature=0, system=system,
                               messages=[{"role": "user", "content": prompt}])
    return r.content[0].text

draft = ask("You are an FP&A analyst writing management commentary.",
            f"Write variance commentary for {month} (AED). Cover variances above 10%. Data:\n{table}")
print("=== DRAFT ===\n", draft)

review = ask("You are a strict financial controller. Check every number in the draft against the data. "
             "List any errors, then output a corrected final version under the heading FINAL.",
             f"DATA:\n{table}\n\nDRAFT:\n{draft}")
print("\n=== REVIEW + FINAL ===\n", review)
