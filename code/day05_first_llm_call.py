"""Day 5 - Your first call to an LLM API."""
import anthropic
from config import MODEL

client = anthropic.Anthropic()   # reads ANTHROPIC_API_KEY from your .env file

pnl = """
P&L (AED)            Sep-2026     Aug-2026
Revenue              1,250,000    1,180,000
Cost of sales         (690,000)    (640,000)
Gross profit           560,000      540,000
Salaries              (210,000)    (205,000)
Marketing              (95,000)     (60,000)
Rent                   (75,000)     (75,000)
Other opex             (48,000)     (52,000)
Operating profit       132,000      148,000
"""

response = client.messages.create(
    model=MODEL,
    max_tokens=600,
    temperature=0.2,             # low = more consistent; try 1.0 and compare
    system="You are a senior financial analyst. Be concise and only use numbers given to you.",
    messages=[{"role": "user", "content": f"Summarise this P&L for the CFO in 5 bullet points, with % changes:\n{pnl}"}],
)

print(response.content[0].text)
print("\nInput tokens:", response.usage.input_tokens, "| Output tokens:", response.usage.output_tokens)
