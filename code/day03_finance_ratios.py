"""Day 3 - Functions. Agent 'tools' are just functions like these."""

def gross_margin(revenue: float, cogs: float) -> float:
    """Gross margin as a fraction, e.g. 0.42 = 42%."""
    if revenue == 0:
        return 0.0
    return (revenue - cogs) / revenue

def current_ratio(current_assets: float, current_liabilities: float) -> float:
    return current_assets / current_liabilities if current_liabilities else float("inf")

def dso(accounts_receivable: float, revenue: float, days: int = 365) -> float:
    """Days Sales Outstanding."""
    return accounts_receivable / revenue * days if revenue else 0.0

def debt_to_equity(total_liabilities: float, equity: float) -> float:
    return total_liabilities / equity if equity else float("inf")

def net_margin(net_income: float, revenue: float) -> float:
    return net_income / revenue if revenue else 0.0

if __name__ == "__main__":
    # Simple tests - if any line is wrong Python stops with AssertionError
    assert round(gross_margin(1000, 600), 2) == 0.40
    assert round(current_ratio(500, 250), 2) == 2.00
    assert round(dso(100, 1200), 1) == 30.4
    assert round(debt_to_equity(300, 600), 2) == 0.50
    assert round(net_margin(150, 1000), 2) == 0.15
    print("All 5 ratio tests passed")
    print(f"Gross margin example: {gross_margin(250000, 140000):.1%}")
