import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# --------- CUSTOM STYLING ---------
st.markdown("""
<link href="https://fonts.googleapis.com/css2?family=Poppins:wght@400;600;700&display=swap" rel="stylesheet">
<style>
    html, body, [class*="css"] {
        font-family: 'Poppins', sans-serif;
        font-size: 15px;
        color: #172B4D;
    }

    .app-container {
        max-width: 700px;
        margin: 0 auto;
        padding-top: 2rem;
    }

    h1.big-title {
        font-size: 32px;
        font-weight: 700;
        margin-bottom: 4px;
        display: flex;
        align-items: center;
    }

    .subtitle {
        font-size: 15px;
        color: #5E6C84;
        margin-bottom: 24px;
    }

    .section-box {
        background-color: #fff;
        border-radius: 12px;
        padding: 1.5rem 1.75rem;
        box-shadow: 0 4px 10px rgba(0,0,0,0.06);
        margin-bottom: 2rem;
    }

    .section-title {
        font-size: 20px;
        font-weight: 600;
        margin-bottom: 1rem;
        display: flex;
        align-items: center;
    }

    .section-title:before {
        content: "🗂️";
        margin-right: 8px;
    }

    .summary-box {
        background-color: #F4F5F7;
        padding: 8px 12px;
        border-radius: 6px;
        font-size: 14px;
        margin: 8px 0 12px 0;
        display: inline-block;
    }

    .priority-badge {
        background-color: #D3F9D8;
        color: #267B4A;
        font-weight: 600;
        font-size: 13px;
        padding: 4px 10px;
        border-radius: 20px;
        display: inline-block;
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
</style>
""", unsafe_allow_html=True)

# --------- HEADER ---------
st.markdown('<div class="app-container">', unsafe_allow_html=True)
st.markdown('<h1 class="big-title">🧠 CaseCraft</h1>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Smart Test Case Generation from Jira Tickets</div>', unsafe_allow_html=True)

# --------- JIRA CONFIG ---------
JIRA_DOMAIN = "https://mitalisengar125.atlassian.net"
JIRA_EMAIL = "mitalisengar125@gmail.com"

# --------- FETCH TICKET LIST ---------
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
        st.error(f"❌ Error fetching ticket summary: {response.status_code}")
        return None, None

# --------- PARSE TEST CASES ---------
def extract_test_cases(markdown_text):
    lines = markdown_text.split("\n")
    test_cases = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            test_cases.append({"Test Case": line})
    return test_cases

# --------- UI ---------
st.markdown('<div class="section-box">', unsafe_allow_html=True)
st.markdown('<div class="section-title">Ticket Info</div>', unsafe_allow_html=True)

ticket_ids = fetch_all_ticket_ids()
selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids)

summary, priority = fetch_jira_ticket_summary(selected_ticket)

if summary:
    st.markdown(f'<div class="summary-box"><strong>Ticket Summary:</strong> {selected_ticket} – {summary}</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="priority-badge">{priority}</div>', unsafe_allow_html=True)

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

                # Excel export
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

st.markdown("</div>", unsafe_allow_html=True)  # close .section-box
st.markdown("</div>", unsafe_allow_html=True)  # close .app-container
