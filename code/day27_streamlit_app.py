"""Day 27 - Web app for the Close Assistant.  Run:  streamlit run day27_streamlit_app.py"""
import os, sys
import pandas as pd
import streamlit as st

sys.path.append(os.path.dirname(__file__))
from day25_bank_recon import load, reconcile

st.set_page_config(page_title="Month-End Close Assistant", layout="wide")
st.title("Month-End Close Assistant")
st.caption("Matching is done by code; AI only drafts explanations. Nothing is posted without your approval.")

c1, c2 = st.columns(2)
bank_file = c1.file_uploader("Bank statement CSV", type="csv")
gl_file = c2.file_uploader("GL cash CSV", type="csv")
st.info("No files? The sample September 2026 data will be used.")

if st.button("Run reconciliation", type="primary"):
    bank, gl = load(bank_file, gl_file)
    st.session_state["summary"], st.session_state["exceptions"] = reconcile(bank, gl)

if "summary" in st.session_state:
    s = st.session_state["summary"]
    m1, m2, m3 = st.columns(3)
    m1.metric("Matched lines", s["matched_lines"]); m2.metric("Exceptions", s["exceptions"]); m3.metric("Difference (AED)", f'{s["difference"]:,.2f}')
    st.subheader("Exceptions")
    st.dataframe(st.session_state["exceptions"], use_container_width=True)

    if st.button("Draft close memo with AI"):
        from day26_close_graph import graph
        config = {"configurable": {"thread_id": "streamlit"}}
        st.session_state["memo"] = graph.invoke({}, config)["memo"]
    if "memo" in st.session_state:
        memo = st.text_area("Draft memo (you can edit)", st.session_state["memo"], height=350)
        if st.checkbox("I have reviewed this memo and approve it"):
            st.download_button("Download approved memo", memo, file_name="close_memo.md")
