import streamlit as st
import openai
import pandas as pd
import io
import requests
import os

def extract_test_cases(markdown_text):
    def get_ticket_summary_from_jira(ticket_id):
    jira_url = "https://mitalisengar125.atlassian.net"  # Your Jira server
    email = os.getenv("JIRA_EMAIL")
    api_token = os.getenv("JIRA_API_TOKEN")

    headers = {
        "Accept": "application/json"
    }

    response = requests.get(
        f"{jira_url}/rest/api/3/issue/{ticket_id}",
        headers=headers,
        auth=(email, api_token)
    )

    if response.status_code == 200:
        return response.json()["fields"]["summary"]
    else:
        return f"❌ Error fetching ticket summary: {response.status_code} - {response.text}"

    lines = markdown_text.split("\n")
    test_cases = []
    for line in lines:
        line = line.strip()
        if line and line[0].isdigit():
            test_cases.append({"Test Case": line})
    return test_cases

jira_ticket_ids = ["SCRUM-1", "SCRUM-2", "SCRUM-3"]  # Use your actual ticket IDs
selected_ticket = st.selectbox("🧾 Select Jira Ticket", jira_ticket_ids)
ticket_summary = get_ticket_summary_from_jira(selected_ticket)

# Dropdown for selecting dummy Jira ticket
selected_ticket = st.selectbox("🎫 Select Jira Ticket", list(dummy_tickets.keys()))
ticket_summary = dummy_tickets[selected_ticket]

st.markdown(f"**📝 Ticket Summary:** {ticket_summary}")

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
            # Extract structured test case data from the generated markdown
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
