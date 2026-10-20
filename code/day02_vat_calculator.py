"""Day 2 - Python basics: variables, lists, loops, if/else, dictionaries."""
VAT_RATE = 0.05  # UAE VAT 5%

invoices = [
    {"vendor": "Gulf Office Supplies", "net": 2500},
    {"vendor": "Desert IT Services", "net": 15300},
    {"vendor": "Blue Wave Marketing", "net": 6500},
    {"vendor": "Gulf Office Supplies", "net": 980},
    {"vendor": "Falcon Facilities", "net": 4050},
    {"vendor": "Desert IT Services", "net": 1200},
    {"vendor": "Legal Advisors LLC", "net": 4500},
    {"vendor": "Blue Wave Marketing", "net": 11250},
    {"vendor": "Falcon Facilities", "net": 850},
    {"vendor": "Al Noor Trading", "net": 7800},
]

total_net = 0
total_vat = 0
for inv in invoices:
    vat = round(inv["net"] * VAT_RATE, 2)
    gross = inv["net"] + vat
    total_net += inv["net"]
    total_vat += vat
    flag = "  <-- needs CFO approval" if gross > 10000 else ""
    print(f'{inv["vendor"]:<22} net {inv["net"]:>10,.2f}  VAT {vat:>8,.2f}  gross {gross:>10,.2f}{flag}')

print("-" * 70)
print(f"TOTAL net {total_net:,.2f} | VAT {total_vat:,.2f} | gross {total_net + total_vat:,.2f}")

# PRACTICE (do it yourself): build a dictionary of total spend per vendor
by_vendor = {}
for inv in invoices:
    by_vendor[inv["vendor"]] = by_vendor.get(inv["vendor"], 0) + inv["net"]
print(by_vendor)
