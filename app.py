import streamlit as st
import requests

# ----- CONFIG -----
JIRA_DOMAIN = "https://your-domain.atlassian.net"
JIRA_EMAIL = "your-email@example.com"
JIRA_API_TOKEN = "your-api-token"
JIRA_PROJECT_KEY = "SCRUM"

# ----- CUSTOM CSS -----
st.markdown("""
<style>
    .header-container {
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 12px;
        margin-top: -20px;
    }
    .title-text {
        font-size: 36px;
        font-weight: 700;
        color: #111827;
        margin: 0;
    }
    .subtitle {
        text-align: center;
        font-size: 16px;
        color: #6b7280;
        margin-top: -10px;
        margin-bottom: 32px;
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

# ----- FETCH JIRA TICKETS -----
def fetch_all_ticket_ids(jira_project_key="SCRUM"):
    url = f"{JIRA_DOMAIN}/rest/api/3/search"
    query = {
        'jql': f'project={jira_project_key}',
        'fields': 'summary,priority',
        'maxResults': 50
    }
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json"
    }

    response = requests.get(url, headers=headers, auth=(JIRA_EMAIL, JIRA_API_TOKEN), params=query)
    if response.status_code == 200:
        issues = response.json().get("issues", [])
        return [
            {
                "id": issue["key"],
                "summary": issue["fields"]["summary"],
                "priority": issue["fields"]["priority"]["name"]
            }
            for issue in issues
        ]
    else:
        return []

# ----- HEADER -----
col1, col2 = st.columns([1, 6])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/4140/4140047.png", width=48)
with col2:
    st.markdown("<div class='header-container'><h1 class='title-text'>CaseCraft</h1></div>", unsafe_allow_html=True)

st.markdown("<p class='subtitle'>Smart Test Case Generation from Jira Tickets</p>", unsafe_allow_html=True)

# ----- MAIN CARD -----
st.markdown("<div class='card'>", unsafe_allow_html=True)
st.markdown(
    "<div class='section-title'><img src='https://cdn-icons-png.flaticon.com/512/2861/2861369.png'/> Ticket Info</div>",
    unsafe_allow_html=True
)

tickets = fetch_all_ticket_ids(JIRA_PROJECT_KEY)

if not tickets:
    st.warning("⚠️ Could not load Jira tickets. Check credentials or project key.")
else:
    ticket_ids = [ticket["id"] for ticket in tickets]
    selected_ticket = st.selectbox("Select Jira Ticket", ticket_ids)

    selected_summary = next((t["summary"] for t in tickets if t["id"] == selected_ticket), "")
    selected_priority = next((t["priority"] for t in tickets if t["id"] == selected_ticket), "")

    st.markdown(
        f"<div class='summary-row'><span>{selected_ticket}  &nbsp; {selected_summary}</span><span>{selected_priority}</span></div>",
        unsafe_allow_html=True
    )

    st.button("Generate Test Cases")

st.markdown("</div>", unsafe_allow_html=True)
