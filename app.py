import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# ------------ FIXED: Visual Styling (Wrapped correctly) ------------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f5f8fc;
}

.card {
    background-color: #ffffff;
    padding: 24px 32px;
    border-radius: 16px;
    box-shadow: 0px 4px 16px rgba(0,0,0,0.05);
    max-width: 700px;
    margin: 0 auto 32px auto;
}

.section-title {
    display: flex;
    align-items: center;
    font-weight: 700;
    font-size: 18px;
    color: #1f2937;
    margin-bottom: 16px;
}

.section-title img {
    width: 22px;
    height: 22px;
    margin-right: 10px;
}

.summary-row {
    background-color: #f1f5f9;
    border-radius: 8px;
    padding: 12px 16px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-weight: 500;
    font-size: 14px;
    color: #1e293b;
    margin-top: 8px;
}

.stButton > button {
    background-color: #0052cc;
    color: white;
    font-weight: 600;
    padding: 12px 0px;
    font-size: 15px;
    width: 100%;
    border: none;
    border-radius: 10px;
    margin-top: 20px;
}

.stButton > button:hover {
    background-color: #0747A6;
}
</style>
""", unsafe_allow_html=True)

# ------------ Header ------------
st.image("https://img.icons8.com/color/48/artificial-intelligence.png", width=50)  # blue AI icon
st.markdown("<h1>CaseCraft</h1>", unsafe_allow_html=True)
st.markdown('<p class="subtitle">Smart Test Case Generation from Jira Tickets</p>', unsafe_allow_html=True)

# ------------ Jira Setup ------------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

def fetch_all_ticket_ids(jira_project_key="SCRUM"):
    api_token = st.secrets["JIRA_API_TOKEN"]
    url = f"{JIRA_DOMAIN}/rest/api/3/search?jql=project={jira_project_key}&maxResults=10"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{api_token}'.encode()).decode()}",
        "Accept": "application/json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        return [i["key"] for i in res.json()["issues"]]
    return []

def fetch_jira_ticket_summary(ticket_id):
    api_token = st.secrets["JIRA_API_TOKEN"]
    url = f"{JIRA_DOMAIN}/rest/api/3/issue/{ticket_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{api_token}'.encode()).decode()}",
        "Accept": "application/json"
    }
    res = requests.get(url, headers=headers)
    if res.status_code == 200:
        f = res.json()["fields"]
        return f.get("summary", ""), f.get("priority", {}).get("name", "Unknown")
    return "", "Unknown"

def extract_test_cases(text):
    return [{"Test Case": line.strip()} for line in text.splitlines() if line.strip() and line.strip()[0].isdigit()]

# ------------ Ticket Info Card ------------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown("""
<div class="section-title">
    <img src="https://img.icons8.com/fluency/48/document.png" />
    Ticket Info
</div>
""", unsafe_allow_html=True)

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids)

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown(f"""
        <div style="margin-top:10px; font-size: 14px;">Ticket Summary</div>
        <div class="summary-row">
            <div>{selecte
