import streamlit as st
import openai
import pandas as pd
import io
import requests
import os
import base64

# ---------- Jira Config ----------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

st.set_page_config(page_title="Jira AI Test Case Generator", layout="centered")

# ---------- CSS Styling ----------
st.markdown("""
    <style>
        body {
            background-color: #ffffff;
        }
        .stButton>button {
            background-color: #0052CC;
            color: white;
            border: none;
            padding: 0.6em 1.2em;
            font-weight: 600;
            border-radius: 4px;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            background-color: #0065FF;
        }
        .stSelectbox label, .stMarkdown {
            font-weight: 600;
            color: #172B4D;
        }
        .stSelectbox div[role="combobox"] {
            background-color: #F4F5F7;
            border-radius: 4px;
        }
        .stDownloadButton>button {
            background-color: #36B37E;
            color: white;
            border: none;
        }
        .stDownloadButton>button:hover {
            background-color: #57D9A3;
        }
        .block-container {
            padding-top: 2rem;
            padding-bottom: 2rem;
        }
    </style>
""", unsafe_allow_html=True)

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
        return response.json()["fields"]["summary"]
    else:
        return f"❌ Error fetching ticket summary: {response.status_code} - {response.text}"

# ---------- Parse Output ----------
def extract_test_cases(markdown_text):
    lines = markdown_text.split("\n")
    test_cases = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            test_cases.append({"Test Case": line})
    return test_cases

# ---------- UI ----------
st.title("📋 AI-Powered Test Case Generator")
st.caption("Generate QA test cases directly from your Jira ticket summary using AI.")

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("🧾 Select Jira Ticket", ticket_ids)

ticket_summary = fetch_jira_ticket_summary(selected_ticket)
st.markdown(f"### 📝 Ticket Summary\n`{ticket_summary}`")

if st.button("🚀 Generate Test Cases") and ticket_summary.strip():
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a QA expert helping generate test cases from Jira ticket summaries."
                },
                {
                    "role": "user",
                    "content": f"Generate detailed test cases for the following feature:\n\n{ticket_summary}\n\nInclude:\n- ✅ Positive test cases\n- ❌ Negative test cases\n- 🟡 Edge case scenarios"
                }
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
