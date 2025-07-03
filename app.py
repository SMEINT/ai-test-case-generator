from openai import OpenAI

client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

response = client.chat.completions.create(
    model="gpt-3.5-turbo",
    messages=[
        {
            "role": "system",
            "content": "You are a QA expert helping generate test cases from Jira ticket summaries."
        },
        {
            "role": "user",
            "content": f"Generate 3 test cases for: {ticket_summary}"
        }
    ],
    temperature=0.7
)

st.write("### Suggested Test Cases:")
st.write(response.choices[0].message.content)


