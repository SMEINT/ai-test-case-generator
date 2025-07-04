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
    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
        background-color: #f9fbfc;
        font-size: 15px;
    }

    .app-box {
        background-color: white;
        padding: 24px 32px;
        border-radius: 12px;
        box-shadow: 0px 2px 8px rgba(0,0,0,0.05);
        margin-bottom: 24px;
    }

    .app-title {
        font-size: 36px;
        font-weight: 700;
        color: #1c274c;
        margin-bottom: 0;
    }

    .app-subtitle {
        font-size: 16px;
        color: #4a5568;
        margin-top: 0;
        margin-bottom: 32px;
    }

    .section-title {
        font-weight: 700;
        font-size: 18px;
        margin-bottom: 12px;
        display: flex;
        align-items: center;
        color: #2d3748;
    }

    .section-title span {
        margin-left: 8px;
    }

    .summary-box {
        background-color: #f1f5f9;
        border-radius: 8px;
        padding: 12px 16px;
        display: flex;
        justify-content: space-between;
        font-weight: 500;
        color: #1a202c;
    }

    .generate-btn button {
        background-color: #0052CC;
        color: #fff;
        font-weight: 600;
        padding: 12px 20px;
        border: none;
        border-radius: 8px;
        font-size: 15px;
        transition: 0.2s;
    }

    .generate-btn button:hover {
        background-color: #0747A6;
    }

</style>
""", unsafe_allow_html=True)

# --------- Header ---------
st.markdown('<h1 class="app-title">🧠 CaseCraft</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">Smart Test Case Generation from Jira Tickets</p>', unsafe_allow_html=True)

# --------- JIRA CONFIG ---------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

# --------- Fetch Jira Tickets ---------
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
        st.error(f"❌ Error fetching ticket summary: {response.status_code}")
        return None, None

def extract_test_cases(markdown_text):
    lines = markdown_text.split("\n")
    test_cases = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            test_cases.append({"Test Case": line})
    return test_cases

# --------- UI Block: Ticket Info ---------
st.markdown('<div class="app-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">📁 <span>Ticket Info</span></div>', unsafe_allow_html=True)

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids)

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown('<div class="section-title" style="font-size:14px; margin-top:20px;">Ticket Summary</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="summary-box"><div>{selected_ticket} &nbsp;&nbsp; {summary}</div><div>{priority}</div></div>', unsafe_allow_html=True)

    if st.button("🚀 Generate Test Cases", key="generate", help="Click to generate cases using AI", type="primary"):
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
                st.markdown('</div>', unsafe_allow_html=True)  # Close previous box
                st.markdown('<div class="app-box">', unsafe_allow_html=True)
                st.markdown('<div class="section-title">🧪 <span>Test Case Output</span></div>', unsafe_allow_html=True)
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

st.markdown('</div>', unsafe_allow_html=True)  # Close last box
