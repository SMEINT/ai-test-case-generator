import streamlit as st
import openai
import os

# Load API key securely from secrets
openai.api_key = st.secrets["OPENAI_API_KEY"]

st.title("AI Test Case Generator from Jira Ticket")

ticket_summary = st.text_area("Enter Jira Ticket Summary or Description")

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
        st.write("### ✅ Suggested Test Cases:")
        st.write(generated_test_cases)

    except openai.AuthenticationError:
        st.error("❌ Authentication failed. Please double-check your OpenAI API key.")
    except Exception as e:
        st.error(f"❌ An unexpected error occurred: {e}")
