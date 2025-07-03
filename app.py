import streamlit as st
import openai
import os

# Set API key from Streamlit secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

# UI Title
st.title("AI Test Case Generator from Jira Ticket")

# Input box
ticket_summary = st.text_area("Enter Jira Ticket Summary or Description")

# Button
if st.button("Generate Test Cases"):
    if ticket_summary:
        with st.spinner("Generating test cases..."):
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a QA expert helping generate test cases from Jira ticket summaries."},
                    {"role": "user", "content": f"Generate 3 test cases for: {ticket_summary}"}
                ],
                temperature=0.7
            )
            # Show the AI response
            st.subheader("Suggested Test Cases:")
            st.write(response["choices"][0]["message"]["content"])
    else:
        st.warning("Please enter a ticket summary.")

