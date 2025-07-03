import streamlit as st
import openai
import os

st.title("AI Test Case Generator from Jira Ticket")

ticket_summary = st.text_area("Enter Jira Ticket Summary or Description")

if st.button("Generate Test Cases"):
    if ticket_summary:
        with st.spinner("Generating test cases..."):
            # Example output for now (static)
            st.write("### Suggested Test Cases:")
            st.write(f"1. Verify functionality based on: `{ticket_summary}`")
            st.write("2. Test edge cases")
            st.write("3. Validate success and failure paths")
    else:
        st.warning("Please enter a ticket summary.")

