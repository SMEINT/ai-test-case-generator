import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# --------- Custom Font and Styles ---------
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
        color: #f97316;
    }

    .test-header {
        display: flex;
        align-items: center;
        font-size: 18px;
        font-weight: 700;
        color: #2d3748;
        margin-bottom: 16px;
    }

    .test-header i {
        margin-right: 10px;
        font-size: 22px;
        color: #3b82f6;
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

# --------- App Header ---------
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

    st.markdown('<div class="btn-blue">', unsafe_allow_html=True)
    if st.button("Generate Test Cases", key="generate", help="Click to generate cases using AI"):
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

                # --------- Test Case Output Section ---------
                st.markdown('</div>', unsafe_allow_html=True)
                st.markdown('<div class="app-box">', unsafe_allow_html=True)
                st.markdown('<div class="test-header"><i>🧪</i> Test Case Output</div>', unsafe_allow_html=True)
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
    st.markdown('</div>', unsafe_allow_html=True)

st.markdown('</div>', unsafe_allow_html=True)  # Close Ticket Info Box
