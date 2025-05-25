import streamlit as st
import pandas as pd
import google.generativeai as genai
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

st.title("📧 Event Email Generator & Sender (Top 10 Only)")

# User inputs
uploaded_file=st.file_uploader("Upload your CSV",type=["csv"])
google_api_key=st.text_input("Google Gemini API Key",type="password")
sender_email=st.text_input("Your Gmail",placeholder="you@gmail.com")
sender_password=st.text_input("App Password",type="password")
send_email_flag=st.checkbox("Send emails to first 10 users")

# Helpers
def clean_data(df):
    df=df[["name","email","has_joined_event","What is your LinkedIn profile?","Job Title"]]
    df=df.drop_duplicates().head(10)
    df["name"]=df["name"].str.split().str[0]
    df["has_joined_event"]=df["has_joined_event"].apply(lambda x: True if x == "Yes" else False)
    return df

def generate_message(name,job,joined):
    prompt = f"""
You are a friendly event host crafting personalized messages.

Examples:

Joined:
"Hey Venkatesh, thanks for joining! As a freelance developer, you will love our upcoming AI workflow tools. Want early access?"

Not Joined:
"Hi Arushi, sorry we missed you! We are planning another session suited for a Product Manager like you."

Now write a message for:

Name: {name}
Job Title: {job}
Has Joined: {joined}
Note dont return text ans with \\n or and other thing
"""
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text.strip()

def send_email(to_email,body,sender_email,sender_password):
    msg=MIMEMultipart()
    msg['From']=sender_email
    msg['To']=to_email
    msg.attach(MIMEText(body,'plain'))
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()
            server.login(sender_email,sender_password)
            server.send_message(msg)
            st.success(f"Email sent to {to_email}")
    except Exception as e:
        st.error(f"Failed to send to {to_email}: {e}")

# Main logic
if uploaded_file and google_api_key:
    df=pd.read_csv(uploaded_file)
    df=clean_data(df)
    genai.configure(api_key=google_api_key)

    st.subheader("Generated Messages (Top 10)")
    df["message"]=df.apply(lambda row: generate_message(row["name"], row["Job Title"], row["has_joined_event"]), axis=1)

    for _, row in df.iterrows():
        st.markdown(f"**{row['name']} ({row['email']}):** {row['message']}")

    if send_email_flag:
        if sender_email and sender_password:
            for _, row in df.iterrows():
                send_email(row["email"], row["message"], sender_email, sender_password)
        else:
            st.warning("Please enter both your email and app password.")
else:
    st.info("Upload a CSV and enter your Gemini API key to get started.")
