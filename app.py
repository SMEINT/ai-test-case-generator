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
if st.button("Generate Test Cases") and ticket_summary.strip():
    try:
        response = openai.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a QA expert helping generate test cases from Jira ticket summaries."},
                {"role": "user", "content": f"Generate 3 test cases for: {ticket_summary}"}
            ],
            temperature=0.7
        )

        generated_test_cases = response.choices[0].message.content
        st.success("✅ Suggested Test Cases:")
        st.markdown(generated_test_cases)

    except Exception as e:
        st.error(f"❌ Error occurred: {e}")
