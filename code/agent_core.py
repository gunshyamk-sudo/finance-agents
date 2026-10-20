"""The agent loop - the heart of every agent. Used from Day 10 onwards.
LLM decides -> we run the tool -> give result back -> repeat until it gives a final answer."""
import json
import anthropic
from config import MODEL

client = anthropic.Anthropic()

def run_agent(question, tools, tool_functions, system="You are a helpful finance analyst.",
              max_steps=10, verbose=True, log=None):
    """tools = list of JSON tool definitions; tool_functions = {"tool_name": python_function}."""
    messages = [{"role": "user", "content": question}]
    for step in range(1, max_steps + 1):
        resp = client.messages.create(model=MODEL, max_tokens=2000, system=system,
                                      tools=tools, messages=messages)
        messages.append({"role": "assistant", "content": resp.content})

        if resp.stop_reason != "tool_use":                      # no more tools needed -> final answer
            return "".join(b.text for b in resp.content if b.type == "text")

        tool_results = []
        for block in resp.content:
            if block.type != "tool_use":
                continue
            if verbose:
                print(f"  [step {step}] calling {block.name}({block.input})")
            try:
                result = tool_functions[block.name](**block.input)
            except Exception as e:                              # give errors back so the model can recover
                result = f"ERROR: {e}"
            if log is not None:
                log.append({"step": step, "tool": block.name, "input": block.input, "output": str(result)[:500]})
            tool_results.append({"type": "tool_result", "tool_use_id": block.id,
                                 "content": json.dumps(result, default=str)})
        messages.append({"role": "user", "content": tool_results})
    return "Stopped: reached max_steps without a final answer."
