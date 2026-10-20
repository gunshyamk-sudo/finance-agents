"""Day 26 - Month-End Close Assistant as a LangGraph workflow with a HUMAN APPROVAL step.
recon -> flux analysis -> draft memo -> [PAUSE for approval] -> finalise
Run: python day26_close_graph.py           (uses the API for the memo)
     python day26_close_graph.py --dry-run (no API call, template memo - free)"""
import sys
from typing import TypedDict
import pandas as pd
from langgraph.graph import StateGraph, START, END
from langgraph.checkpoint.memory import MemorySaver
from config import DATA, OUT, MODEL
from day25_bank_recon import load, reconcile

DRY_RUN = "--dry-run" in sys.argv

class CloseState(TypedDict, total=False):
    recon_summary: dict
    exceptions: list
    flux: list
    memo: str
    approved: bool

def recon_node(state):
    s, ex = reconcile(*load())
    return {"recon_summary": s, "exceptions": ex.assign(date=ex.date.dt.date.astype(str)).to_dict("records")}

def flux_node(state, threshold=0.10):
    tb = pd.read_csv(DATA / "trial_balance_aug_sep_2026.csv")
    tb["change_aed"] = (tb.sep_2026_aed - tb.aug_2026_aed).round(2)
    tb["change_pct"] = (tb.change_aed / tb.aug_2026_aed).round(4)
    big = tb[tb.change_pct.abs() > threshold]
    cols = ["account_code", "account_name", "aug_2026_aed", "sep_2026_aed", "change_aed", "change_pct"]
    return {"flux": [{k: (v.item() if hasattr(v, "item") else v) for k, v in r.items()} for r in big[cols].to_dict("records")]}

def memo_node(state):
    facts = f"Reconciliation summary: {state['recon_summary']}\nExceptions: {state['exceptions']}\nFlux items >10%: {state['flux']}"
    if DRY_RUN:
        memo = ("SEPTEMBER 2026 CLOSE MEMO (dry-run template)\n\n1. Bank reconciliation\n" + str(state["recon_summary"]) +
                f"\n{len(state['exceptions'])} exceptions to clear.\n\n2. Flux analysis\n" +
                "\n".join(f"- {f['account_name']}: {f['change_pct']:+.1%}" for f in state["flux"]) +
                "\n\n3. Open items / actions\n- Investigate each item above before sign-off.")
    else:
        import anthropic
        r = anthropic.Anthropic().messages.create(model=MODEL, max_tokens=1500, temperature=0,
            system="You are a financial controller writing a month-end close memo for the CFO. Use ONLY the facts given.",
            messages=[{"role": "user", "content": "Write the September 2026 close memo with sections: Bank reconciliation, "
                       "Exceptions & proposed journals, Flux analysis (explain likely drivers as questions to investigate), "
                       "Open items. Facts:\n" + facts}])
        memo = r.content[0].text
    return {"memo": memo}

def finalise_node(state):
    (OUT / "close_memo_sep2026.md").write_text(state["memo"], encoding="utf-8")
    return {"approved": True}

builder = StateGraph(CloseState)
for name, fn in [("recon", recon_node), ("flux", flux_node), ("memo", memo_node), ("finalise", finalise_node)]:
    builder.add_node(name, fn)
builder.add_edge(START, "recon"); builder.add_edge("recon", "flux"); builder.add_edge("flux", "memo")
builder.add_edge("memo", "finalise"); builder.add_edge("finalise", END)
graph = builder.compile(checkpointer=MemorySaver(), interrupt_before=["finalise"])   # <-- human-in-the-loop

if __name__ == "__main__":
    config = {"configurable": {"thread_id": "close-sep-2026"}}
    state = graph.invoke({}, config)
    print("=== DRAFT MEMO ===\n", state["memo"])
    if input("\nApprove and finalise? (yes/no): ").strip().lower() == "yes":
        graph.invoke(None, config)          # resume from the pause
        print("Finalised ->", OUT / "close_memo_sep2026.md")
    else:
        print("Not approved. Nothing was finalised.")
