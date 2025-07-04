import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# --------- Custom Font and Style ---------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    .dropdown-box select {
        background-color: #ffffff;
        border-radius: 8px;
        padding: 12px;
        width: 100%;
        border: 1px solid #cbd5e0;
        font-size: 15px;
        color: #2d3748;
    }

    .ticket-header {
        display: flex;
        align-items: center;
        font-size: 18px;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 16px;
    }

    .ticket-header i {
        margin-right: 10px;
        font-size: 22px;
        color: #f97316; /* orange */
    }

    .test-header i {
        margin-right: 10px;
        font-size: 22px;
        color: #3b82f6;
    }

    .test-header {
        display: flex;
        align-items: center;
        font-size: 18px;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 16px;
    }

    .summary-box {
        background-color: #f8fafc;
        border-radius: 8px;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 500;
        color: #1e293b;
        margin-top: 12px;
        font-size: 14px;
    }

    .btn-blue button {
        background-color: #0052CC !important;
        color: white !important;
        font-weight: 600;
        padding: 12px 24px;
        border-radius: 8px;
        font-size: 15px;
        margin-top: 20px;
    }

    .btn-blue button:hover {
        background-color: #0747A6 !important;
    }
</style>

""", unsafe_allow_html=True)

# --------- Header ---------
# --------- Ticket Info UI Block ---------
st.markdown('<div class="app-box">', unsafe_allow_html=True)
st.markdown('<div class="ticket-header"><i>📄</i> Ticket Info</div>', unsafe_allow_html=True)

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids, key="ticket_dropdown")

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown(f"""
        <div class="summary-box">
            <div><strong>{selected_ticket}</strong> &nbsp; {summary}</div>
            <div><strong>{priority}</strong></div>
        </div>
    """, unsafe_allow_html=True)

    with st.container():
        col1, col2 = st.columns([1, 1])
        with col1:
            st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
            if st.button("Generate Test Cases", key="generate", help="Click to generate cases using AI"):
                # Your test case generation logic here
                pass
            st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close Ticket Info box
