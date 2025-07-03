import streamlit as st
from openai import OpenAI

# Initialize OpenAI client using the correct secrets key
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.title("AI Test Case Generator from Jira Ticket")

ticket_summary = st.text_area("Enter Jira Ticket Summary or Description")

if st.button("Generate Test Cases") and ticket_summary.strip():
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
