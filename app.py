import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# --------- CUSTOM STYLING (Modern Jira-like) ---------
# --------- FONT AND STYLE (Poppins) ---------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        font-size: 15px;
        color: #172B4D;
    }

    h1, h2, h3 {
        font-weight: 700 !important;
        color: #172B4D;
    }

    .big-header {
        font-size: 26px !important;
        font-weight: 700 !important;
        margin-bottom: 8px;
    }

    .stButton > button {
        background-color: #0052CC;
        color: #fff;
        border-radius: 6px;
        padding: 0.55rem 1.4rem;
        font-weight: 600;
        border: none;
        transition: 0.2s all;
    }

    .stButton > button:hover {
        background-color: #0747A6;
    }

    code {
        background-color: #F4F5F7;
        padding: 4px 8px;
        border-radius: 4px;
        font-size: 14px;
        color: #091E42;
        display: inline-block;
    }
</style>
""", unsafe_allow_html=True)



# --------- HEADER ---------
st.markdown("### 📋 AI-Powered Test Case Generator")
st.markdown("Generate QA test cases directly from your Jira ticket summary using AI.")

# --------- JIRA CONFIG ---------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

# --------- FETCH ALL TICKETS ---------
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

# --------- FETCH SUMMARY & PRIORITY ---------
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

# --------- PARSE MARKDOWN ---------
def extract_test_cases(markdown_text):
    lines = markdown_text.split("\n")
    test_cases = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            test_cases.append({"Test Case": line})
    return test_cases

# --------- UI ---------
ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("🎟️ Select Jira Ticket", ticket_ids)

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown("### 📝 Ticket Summary")
    st.markdown(f"<code>{summary} (Priority: {priority})</code>", unsafe_allow_html=True)

    if st.button("🚀 Generate Test Cases"):
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

                try:
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
                    st.error(f"❌ Failed to generate Excel file: {e}")
            except Exception as e:
                st.error(f"❌ Failed to generate test cases: {e}")
