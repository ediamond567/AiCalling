import os
from dotenv import load_dotenv
import streamlit as st
import pandas as pd
import requests

load_dotenv()

# Define the API key
API_KEY = os.getenv("API_KEY")
# Logo image
logo_image = "Screenshot (959).png"

# Hint prompt
hint_prompt = """
1. You are calling {{business}} to renew their subscription to {{service}} before it expires on {{date}}.
2. You are contacting {{business}} to discuss the upcoming product launch scheduled for {{date}}.
3. You are reaching out to {{business}} to provide assistance with their recent order {{order_id}}.
4. You are calling {{business}} to follow up on the service request made by {{customer_name}}.
5. You are contacting {{business}} to offer a special discount on their next purchase.
6. You are reaching out to {{business}} to inform them about the new features added to our platform.
7. You are calling {{business}} to remind them about the upcoming webinar on {{date}}.
8. You are contacting {{business}} to gather feedback on their recent experience with our services.
"""

# Main Streamlit app
def main():
    st.title("AI Call")
    
    st.sidebar.image(logo_image, width=100, use_column_width='always')  # Adding logo with glow effect
    
    option = st.sidebar.radio("Select an option", ["Single Call", "Bulk Call", "Call Details", "Call Logs"])

    # Display hint prompt
    if st.button("Hint Prompt"):
        st.write("Hint Prompts:")
        st.write(hint_prompt)

    if option == "Single Call":
        single_call()
    elif option == "Bulk Call":
        bulk_call()
    elif option == "Call Details":
        call_details()
    elif option == "Call Logs":
        call_logs()

# Function to make a single call
def single_call():
    st.subheader("Single Call")
    phone_number = st.text_input("Enter Phone Number")
    task = st.text_area("Enter task prompt")
    transfer_phone_number = st.text_input("Enter the Transfer Phone Number")
    make_call_button = st.button("Make Call")
    if make_call_button and phone_number and task and transfer_phone_number:
        response = make_single_call_api(phone_number, task,transfer_phone_number)

# Function to make bulk calls 
def bulk_call():
    st.subheader("Bulk Call")
    uploaded_file = st.file_uploader("Upload CSV File", type=["csv"])
    task = st.text_area("Enter task prompt")
    transfer_phone_number = st.text_input("Enter the Transfer Phone Number")
    make_bulk_call_button = st.button("Make Bulk Call")
    if make_bulk_call_button and uploaded_file is not None and task and transfer_phone_number:
        response = make_bulk_call_api(uploaded_file, task,transfer_phone_number)

# Function to fetch call details
def call_details():
    st.subheader("Call Details")
    call_id = st.text_input("Enter Call ID")
    fetch_call_details_button = st.button("Fetch Call Details")
    if fetch_call_details_button and call_id:
        response = fetch_call_details_api(call_id)

        if response:
            df = pd.json_normalize(response)
            st.write(df)

            if "transcripts" in response:
                for transcript in response["transcripts"]:
                    st.write(f"{transcript['user']}: {transcript['text']}")

# Function to fetch call logs
def call_logs():
    st.subheader("Call Logs")
    response = fetch_call_logs_api()

    if response:
        df = pd.json_normalize(response["calls"])
        st.write(df)

# Function to make a single call using API
def make_single_call_api(phone_number, task, transfer_phone_number):
    headers = {"Authorization": API_KEY}
    data = {"phone_number": phone_number, "task": task, "voice": "e1289219-0ea2-4f22-a994-c542c2a48a0f", "transfer_phone_number": transfer_phone_number}
    response = requests.post("https://api.bland.ai/v1/calls", data=data, headers=headers)
    st.write(response.json())
    return response

# Function to make bulk calls using API
def make_bulk_call_api(uploaded_file, task, transfer_phone_number):
    headers = {"Authorization": API_KEY}
    try:
        df = pd.read_csv(uploaded_file)
        if "Phone Number" in df.columns:
            phone_numbers = df["Phone Number"].tolist()
            for phone_number in phone_numbers:
                data = {"phone_number": phone_number, "task": task, "transfer_phone_number": transfer_phone_number}
                response = requests.post("https://api.bland.ai/v1/calls", data=data, headers=headers)
                st.write(response.json())  # You can modify this to handle the responses as needed
            return response
        else:
            st.error("Column 'Phone Number' not found in the uploaded file.")
    except Exception as e:
        st.error(f"Error: {e}")

# Function to fetch call details using API
def fetch_call_details_api(call_id):
    url = f"https://api.bland.ai/v1/calls/{call_id}"
    headers = {"Authorization": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch call details.")
        return None

# Function to fetch call logs using API
def fetch_call_logs_api():
    url = "https://api.bland.ai/v1/calls"
    headers = {"Authorization": API_KEY}
    response = requests.get(url, headers=headers)
    if response.status_code == 200:
        return response.json()
    else:
        st.error("Failed to fetch call logs.")
        return None

if __name__ == "__main__":
    main()
