import streamlit as st
from openai import OpenAI
import os

st.title("AI Test Case Generator from Jira Ticket")

# Capture input
ticket_summary = st.text_area("Enter Jira Ticket Summary or Description")

# On button click
if st.button("Generate Test Cases"):
    if ticket_summary:
        with st.spinner("Generating test cases..."):
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

            response = client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a QA expert helping generate test cases from Jira ticket summaries."},
                    {"role": "user", "content": f"Generate 3 test cases for: {ticket_summary}"}
                ],
                temperature=0.7
            )

            generated_test_cases = response.choices[0].message.content

            st.write("### Suggested Test Cases:")
            st.write(generated_test_cases)
    else:
        st.warning("Please enter a ticket summary.")
