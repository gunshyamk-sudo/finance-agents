"""Day 23 - Finance-grade guardrails you can reuse: audit log, PII masking, approval threshold."""
import csv, functools, re
from datetime import datetime
from config import OUT

AUDIT_FILE = OUT / "audit_log.csv"

def audited(func):
    """Decorator: writes every tool call (time, tool, inputs, output) to audit_log.csv."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        new = not AUDIT_FILE.exists()
        with open(AUDIT_FILE, "a", newline="") as f:
            w = csv.writer(f)
            if new:
                w.writerow(["timestamp", "tool", "inputs", "output"])
            w.writerow([datetime.now().isoformat(timespec="seconds"), func.__name__, kwargs or args, str(result)[:300]])
        return result
    return wrapper

PII_PATTERNS = {
    "IBAN": r"\bAE\d{2}[ ]?(?:\d{4}[ ]?){4}\d{3}\b",
    "EMAIL": r"\b[\w.+-]+@[\w-]+\.[\w.]+\b",
    "EMIRATES_ID": r"\b784-?\d{4}-?\d{7}-?\d\b",   # checked before CARD so it is not mistaken for a card
    "CARD": r"\b(?:\d[ -]?){13,16}\b",
}

def mask_pii(text: str) -> str:
    """Mask sensitive data BEFORE sending text to an external AI API."""
    for label, pattern in PII_PATTERNS.items():
        text = re.sub(pattern, f"[{label}]", text)
    return text

APPROVAL_LIMIT_AED = 10000

def requires_approval(amount_aed: float) -> bool:
    return amount_aed > APPROVAL_LIMIT_AED

@audited
def post_payment(vendor: str, amount_aed: float, approved_by: str = "") -> str:
    if requires_approval(amount_aed) and not approved_by:
        return f"BLOCKED: AED {amount_aed:,.2f} to {vendor} needs human approval (limit {APPROVAL_LIMIT_AED:,})"
    return f"Payment of AED {amount_aed:,.2f} to {vendor} queued (approved by {approved_by or 'auto - under limit'})"

if __name__ == "__main__":
    print(mask_pii("Pay AE07 0331 2345 6789 0123 456 and email ap@vendor.com, card 4111 1111 1111 1111, EID 784-1990-1234567-1"))
    print(post_payment(vendor="Desert IT Services", amount_aed=15300))
    print(post_payment(vendor="Desert IT Services", amount_aed=15300, approved_by="CFO"))
    print(post_payment(vendor="Gulf Office Supplies", amount_aed=980))
    print("Audit log written to", AUDIT_FILE)
