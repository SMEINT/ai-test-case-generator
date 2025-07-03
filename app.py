import streamlit as st
import openai
import os

# Load API key securely from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("AI Test Case Generator from Jira Ticket")

st.markdown("### 🧩 Select a Dummy Jira Ticket")

# Dummy ticket data to simulate Jira integration
dummy_tickets = {
    "JIRA-001": "As a user, I want to log in using OTP which should be valid for 5 mins",
    "JIRA-002": "As an admin, I want to reset user passwords securely",
    "JIRA-003": "As a user, I want to view my transaction history with filters",
}

# Dropdown for selecting dummy Jira ticket
selected_ticket = st.selectbox(" Select Jira Ticket", list(dummy_tickets.keys()))
ticket_summary = dummy_tickets[selected_ticket]

st.markdown(f"** Ticket Summary:** {ticket_summary}")
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
                    "content": f"Generate detailed test cases for the following feature:\n\n{ticket_summary}\n\nInclude:\n- ✅ Positive test cases\n- ❌ Negative test cases\n- ⚠️ Edge test cases\n\nFormat clearly by sections."
                }
            ],
            temperature=0.7
        )
        generated_test_cases = response.choices[0].message.content
        st.success("✅ Suggested Test Cases:")
        st.markdown(generated_test_cases)
        # Extract structured test case data from the generated markdown
df = pd.DataFrame(extract_test_cases(generated_test_cases))

# Create downloadable Excel file
buffer = io.BytesIO()
df.to_excel(buffer, index=False, engine='openpyxl')
buffer.seek(0)

# Add Download Button
st.download_button(
    label="📥 Download Test Cases as Excel",
    data=buffer,
    file_name="generated_test_cases.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

import pandas as pd
import io

# Convert response to structured data (assumes markdown format parsing)
def extract_test_cases(generated_text):
    sections = {"Positive Test Cases": [], "Negative Test Cases": [], "Edge Test Cases": []}
    current_section = None

    for line in generated_text.splitlines():
        line = line.strip()
        if "Positive Test Cases:" in line:
            current_section = "Positive Test Cases"
        elif "Negative Test Cases:" in line:
            current_section = "Negative Test Cases"
        elif "Edge Test Cases:" in line:
            current_section = "Edge Test Cases"
        elif line and current_section:
            sections[current_section].append(line)

    # Flatten for DataFrame
    data = []
    for section, cases in sections.items():
        for case in cases:
            if case.startswith(("1.", "2.", "3.", "-")):  # main test case
                data.append({"Category": section, "Test Case": case})
            elif case.startswith("•") or line.startswith("-"):  # sub-step
                data[-1]["Test Case"] += f"\n  {case.strip()}"

    return pd.DataFrame(data)

df = extract_test_cases(generated_test_cases)

# Button to download Excel file
buffer = io.BytesIO()
df.to_excel(buffer, index=False, engine='openpyxl')
st.download_button(
    label="📥 Download Test Cases as Excel",
    data=buffer,
    file_name="generated_test_cases.xlsx",
    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
)

    except Exception as e:
        st.error(f"❌ Error: {e}")
