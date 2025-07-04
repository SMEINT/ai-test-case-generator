import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# ---------- FIXED: Style (wrapped in markdown safely) ----------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap" rel="stylesheet">
<style>
html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
    background-color: #f9fbfc;
}

.app-title {
    font-size: 36px;
    font-weight: 700;
    color: #1c1c1c;
    margin-top: 20px;
    text-align: center;
}

.app-subtitle {
    font-size: 16px;
    color: #4a5568;
    text-align: center;
    margin-bottom: 32px;
}

.app-box {
    background: #ffffff;
    padding: 24px 32px;
    border-radius: 12px;
    box-shadow: 0px 4px 12px rgba(0,0,0,0.06);
    width: 100%;
    max-width: 600px;
    margin: 0 auto 32px auto;
}

.section-header {
    font-size: 18px;
    font-weight: 700;
    margin-bottom: 16px;
    display: flex;
    align-items: center;
    color: #1a202c;
}

.section-header span {
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
    font-size: 14px;
    margin-top: 16px;
}

.stButton > button {
    background-color: #0052cc;
    color: #fff;
    font-weight: 600;
    padding: 10px 24px;
    font-size: 15px;
    border: none;
    border-radius: 8px;
    margin-top: 20px;
}

.stButton > button:hover {
    background-color: #0747a6;
}
</style>
""", unsafe_allow_html=True)

# ---------- Title + Branding ----------
st.markdown('<h1 class="app-title">🧠 CaseCraft</h1>', unsafe_allow_html=True)
st.markdown('<p class="app-subtitle">Smart Test Case Generation from Jira Tickets</p>', unsafe_allow_html=True)

# ---------- Jira Auth ----------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

# ---------- Fetch Jira Tickets ----------
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

# ---------- Fetch Ticket Summary ----------
def fetch_jira_ticket_summary(ticket_id):
    api_token = st.secrets["JIRA_API_TOKEN"]
    url = f"{JIRA_DOMAIN}/rest/api/3/issue/{ticket_id}"
    headers = {
        "Authorization": f"Basic {base64.b64encode(f'{JIRA_EMAIL}:{api_token}'.encode()).decode()}",
        "Accept": "application/json"
    }
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        fields = response.json()["fields"]
        return fields.get("summary", ""), fields.get("priority", {}).get("name", "Not set")
    else:
        st.error("Failed to fetch ticket details.")
        return "", ""

def extract_test_cases(markdown_text):
    lines = markdown_text.split("\n")
    return [{"Test Case": line.strip()} for line in lines if line.strip() and line.strip()[0].isdigit()]

# ---------- UI Card ----------
st.markdown('<div class="app-box">', unsafe_allow_html=True)
st.markdown('<div class="section-header">📄 <span>Ticket Info</span></div>', unsafe_allow_html=True)

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids, key="ticket_select")

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown(f"""
        <div class="summary-box">
            <div>{selected_ticket} &nbsp;&nbsp; {summary}</div>
            <div>{priority}</div>
        </div>
    """, unsafe_allow_html=True)

    if st.button("Generate Test Cases"):
        with st.spinner("Generating test cases using AI..."):
            try:
                response = openai.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "You are a QA expert generating test cases from Jira ticket summaries."},
                        {"role": "user", "content": f"Generate test cases for this Jira summary:\n\n{summary}\nPriority: {priority}\n\nInclude positive, negative, and edge case scenarios."}
                    ]
                )
                generated_text = response.choices[0].message.content

                st.markdown('<div class="app-box">', unsafe_allow_html=True)
                st.markdown('<div class="section-header">🧪 <span>Test Case Output</span></div>', unsafe_allow_html=True)
                st.success("✅ Generated Test Cases")
                st.markdown(generated_text)

                df = pd.DataFrame(extract_test_cases(generated_text))
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine="openpyxl") as writer:
                    df.to_excel(writer, index=False, sheet_name="Test Cases")

                st.download_button(
                    label="📥 Download Test Cases (Excel)",
                    data=output.getvalue(),
                    file_name="generated_test_cases.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )

                st.markdown('</div>', unsafe_allow_html=True)
            except Exception as e:
                st.error(f"❌ Error generating test cases: {e}")

st.markdown('</div>', unsafe_allow_html=True)  # Close first card
