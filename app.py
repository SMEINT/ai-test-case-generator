import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# ---------- Page Config ----------
st.set_page_config(page_title="CaseCraft - AI Test Case Generator", layout="centered")

# ---------- Modern UI Styling ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #F5F6FA;
        color: #172B4D;
        font-size: 15px;
    }
    h1, h2, h3, h4 {
        font-weight: 700;
        color: #172B4D;
    }
    .main-title {
        font-size: 2rem;
        font-weight: 700;
        margin-bottom: 0.25rem;
        color: #2C3E50;
    }
    .sub-text {
        color: #5E6C84;
        font-size: 0.95rem;
        margin-bottom: 2rem;
    }
    .ticket-box {
        background-color: #FFFFFF;
        padding: 1rem 1.5rem;
        border-radius: 8px;
        border: 1px solid #DFE1E6;
        margin-top: 0.75rem;
    }
    .stSelectbox>div>div {
        border-radius: 6px;
        padding: 8px 10px;
    }
    .stButton > button {
        background-color: #0052CC;
        color: #fff;
        font-weight: 600;
        padding: 0.55rem 1.5rem;
        border-radius: 6px;
        border: none;
    }
    .stButton > button:hover {
        background-color: #0747A6;
    }
    .stMarkdown code {
        background: #F4F5F7;
        padding: 4px 8px;
        border-radius: 4px;
    }
    .section-header {
        font-weight: 600;
        margin-top: 2rem;
        color: #253858;
        font-size: 1.1rem;
    }
</style>
""", unsafe_allow_html=True)

# ---------- Header ----------
st.markdown('<div class="main-title">🚀 CaseCraft</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-text">Generate intelligent test cases from your Jira tickets using AI</div>', unsafe_allow_html=True)

# ---------- Jira Config ----------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

def fetch_all_ticket_ids(jira_project_key="SCRUM"):
    api_token = st.secrets["JIRA_API_TOKEN"]
    url = f"{JIRA_DOMAIN}/rest/api/3/search?jql=project={jira_project_key}&maxResults=10"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{api_token}'.encode()).decode()}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        return [issue["key"] for issue in data["issues"]]
    else:
        st.error(f"❌ Failed to fetch Jira tickets: {response.status_code}")
        return []

def fetch_jira_ticket_summary(ticket_id):
    api_token = st.secrets["JIRA_API_TOKEN"]
    url = f"{JIRA_DOMAIN}/rest/api/3/issue/{ticket_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{api_token}'.encode()).decode()}",
        "Accept": "application/json"
    }

    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        data = response.json()["fields"]
        summary = data.get("summary", "No Summary")
        priority = data.get("priority", {}).get("name", "Not set")
        return summary, priority
    else:
        st.error(f"❌ Error fetching ticket summary: {response.status_code} - {response.text}")
        return None, None

def extract_test_cases(markdown_text):
    lines = markdown_text.split("\n")
    return [{"Test Case": line.strip()} for line in lines if line.strip() and line[0].isdigit()]

# ---------- UI Logic ----------
ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("🎟️ Select Jira Ticket", ticket_ids)

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown('<div class="section-header">🎫 Ticket Summary</div>', unsafe_allow_html=True)
    st.markdown(f"""
        <div class="ticket-box">
            <strong>{selected_ticket}</strong>: {summary}<br>
            <code>Priority: {priority}</code>
        </div>
    """, unsafe_allow_html=True)

    if st.button("✨ Generate Test Cases"):
        with st.spinner("Generating test cases using AI..."):
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a QA expert helping generate test cases from Jira ticket summaries."},
                        {"role": "user", "content": f"Generate detailed test cases for the following feature:\n\n{summary}\n(Priority: {priority})\n\nInclude:\n- Positive test cases\n- Negative test cases\n- Edge case scenarios"}
                    ],
                    temperature=0.7
                )
                generated_test_cases = response.choices[0].message.content
                st.success("✅ Suggested Test Cases:")
                st.markdown(generated_test_cases)

                df = pd.DataFrame(extract_test_cases(generated_test_cases))
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Test Cases")
                st.download_button(
                    label="📥 Download Test Cases (Excel)",
                    data=output.getvalue(),
                    file_name="generated_test_cases.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
            except Exception as e:
                st.error(f"❌ Failed to generate test cases: {e}")
