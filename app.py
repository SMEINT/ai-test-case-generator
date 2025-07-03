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
selected_ticket = st.selectbox("📋 Select Jira Ticket", list(dummy_tickets.keys()))
ticket_summary = dummy_tickets[selected_ticket]

st.markdown(f"**📝 Ticket Summary:** {ticket_summary}")
