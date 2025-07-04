import streamlit as st
import openai
import pandas as pd
import io
import requests
import base64

# --------- CUSTOM STYLING ---------
# ------- TICKET INFO DISPLAY (Clean, Aligned Block) -------
st.markdown("""
<div class="ticket-card">
    <div class="ticket-title"><strong>Ticket Summary:</strong> {ticket_id} – {summary}</div>
    <div class="priority-tag">{priority}</div>
</div>
""".format(ticket_id=selected_ticket, summary=summary, priority=priority), unsafe_allow_html=True)

# Add styling
st.markdown("""
<style>
.ticket-card {
    background-color: #f7f9fb;
    border: 1px solid #dfe3e6;
    border-radius: 8px;
    padding: 12px 16px;
    margin-top: 12px;
    display: flex;
    justify-content: space-between;
    align-items: center;
    font-size: 15px;
}
.ticket-title {
    color: #172B4D;
}
.priority-tag {
    background-color: #E3FCEF;
    color: #006644;
    padding: 4px 12px;
    border-radius: 20px;
    font-size: 13px;
    font-weight: 600;
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
