"""Day 9 - Tool use (function calling), written out step by step so you can see each message."""
import json
import anthropic
from config import MODEL

client = anthropic.Anthropic()

FX_TO_AED = {"USD": 3.6725, "EUR": 3.98, "GBP": 4.65, "INR": 0.0417, "SAR": 0.979}   # sample fixed rates

def get_fx_rate(currency: str) -> float:
    return FX_TO_AED[currency.upper()]

def gross_margin(revenue: float, cogs: float) -> float:
    return round((revenue - cogs) / revenue, 4)

TOOLS = [
    {"name": "get_fx_rate", "description": "Get the exchange rate to convert 1 unit of a currency into AED.",
     "input_schema": {"type": "object", "properties": {"currency": {"type": "string", "description": "ISO code e.g. USD"}},
                      "required": ["currency"]}},
    {"name": "gross_margin", "description": "Calculate gross margin as a fraction from revenue and cost of goods sold.",
     "input_schema": {"type": "object", "properties": {"revenue": {"type": "number"}, "cogs": {"type": "number"}},
                      "required": ["revenue", "cogs"]}},
]
FUNCS = {"get_fx_rate": get_fx_rate, "gross_margin": gross_margin}

question = "A deal has revenue of USD 12,500 and cost of USD 7,900. Convert both to AED and give me the gross margin."
messages = [{"role": "user", "content": question}]

while True:
    resp = client.messages.create(model=MODEL, max_tokens=1000, tools=TOOLS, messages=messages)
    print("stop_reason:", resp.stop_reason)
    messages.append({"role": "assistant", "content": resp.content})
    if resp.stop_reason != "tool_use":
        print("\nFINAL ANSWER:\n", resp.content[-1].text)
        break
    results = []
    for b in resp.content:
        if b.type == "tool_use":
            out = FUNCS[b.name](**b.input)
            print(f"Model asked for {b.name}{b.input} -> we returned {out}")
            results.append({"type": "tool_result", "tool_use_id": b.id, "content": json.dumps(out)})
    messages.append({"role": "user", "content": results})
