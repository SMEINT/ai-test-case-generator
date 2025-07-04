import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# --------- STYLING FOR CASECRAFT ---------
st.set_page_config(page_title="CaseCraft - Test Case Generator", page_icon="🧠", layout="centered")

st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        color: #1F2937;
    }
    .main-container {
        background-color: #F9FAFB;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 0 12px rgba(0,0,0,0.06);
    }
    .card {
        background-color: #FFFFFF;
        padding: 2rem;
        border-radius: 12px;
        box-shadow: 0 2px 12px rgba(0,0,0,0.05);
        margin-bottom: 2rem;
    }
    .title {
        font-size: 32px;
        font-weight: 700;
        color: #111827;
        margin-bottom: 0.25rem;
    }
    .subtitle {
        font-size: 16px;
        font-weight: 400;
        color: #6B7280;
        margin-bottom: 1.5rem;
    }
    .section-header {
        font-size: 20px;
        font-weight: 600;
        color: #111827;
        margin-bottom: 1rem;
    }
    .stButton > button {
        background-color: #2563EB;
        color: white;
        font-weight: 600;
        border: none;
        border-radius: 8px;
        padding: 0.6rem 1.5rem;
        transition: background-color 0.3s ease;
    }
    .stButton > button:hover {
        background-color: #1E40AF;
    }
    code {
        background-color: #F3F4F6;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 14px;
        color: #1F2937;
    }
</style>
""", unsafe_allow_html=True)

# --------- HEADER ---------
st.markdown('<div class="main-container">', unsafe_allow_html=True)
st.markdown('<div class="title">🧠 CaseCraft</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart Test Case Generation from Jira Tickets</div>', unsafe_allow_html=True)

# --------- JIRA CONFIG ---------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

# --------- FETCH TICKETS ---------
def fetch_all_ticket_ids(jira_project_key="SCRUM"):
    api_token = st.secrets["JIRA_API_TOKEN"]
    url = f"{JIRA_DOMAIN}/rest/api/3/search?jql=project={jira_project_key}&maxResults=10"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{api_token}'.encode()).decode()}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return [issue["key"] for issue in response.json()["issues"]]
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
        st.error("❌ Couldn't fetch ticket details.")
        return None, None

def extract_test_cases(markdown_text):
    return [{"Test Case": line.strip()} for line in markdown_text.split("\n") if line.strip() and line[0].isdigit()]

# --------- FORM CARD ---------
st.markdown('<div class="card">', unsafe_allow_html=True)
st.markdown('<div class="section-header">📑 Ticket Info</div>', unsafe_allow_html=True)

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids)

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown(f"**Ticket Summary**: `{selected_ticket} - {summary}`")
    st.markdown(f"**Priority**: `{priority}`")

if st.button("🚀 Generate Test Cases"):
    with st.spinner("Generating test cases..."):
        try:
            response = openai.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a QA expert generating test cases from Jira ticket summaries."},
                    {"role": "user", "content": f"Generate test cases for:\n\n{summary}\n(Priority: {priority})\n\nInclude:\n- Positive test cases\n- Negative test cases\n- Edge case scenarios"}
                ],
                temperature=0.7
            )

            test_cases = response.choices[0].message.content
            st.markdown('<div class="section-header">🧪 Test Case Output</div>', unsafe_allow_html=True)
            st.markdown(test_cases)

            try:
                df = pd.DataFrame(extract_test_cases(test_cases))
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Test Cases")
                st.download_button("📥 Download Test Cases (Excel)", output.getvalue(), "generated_test_cases.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
            except Exception as e:
                st.error(f"Excel Error: {e}")
        except Exception as e:
            st.error(f"OpenAI Error: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # Close card
st.markdown('</div>', unsafe_allow_html=True)  # Close main container
