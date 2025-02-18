import streamlit as st
import requests
import time

# Configure the page
st.set_page_config(page_title="Nova", page_icon="🚀")

st.title("Nova")
st.caption("Assisting you in building an empire 🚀")

# Webhook URLs
HISTORY_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"
SEND_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/7337a77e-1ec8-45da-86b9-c06628865d86"

# User & Nova avatars
USER_AVATAR = "assets/josh.png"
NOVA_AVATAR = "assets/nova.png"

# Function to fetch chat history
def fetch_chat_history():
    try:
        response = requests.get(HISTORY_WEBHOOK)
        data = response.json()
        messages = data.get("messages", {}).get("history", [])
        return messages[::-1] if isinstance(messages, list) else [messages]  # Reverse order for latest first
    except Exception as e:
        return []

# Initialize session state
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = fetch_chat_history()

# Function to fetch new messages from Nova proactively
def fetch_new_messages():
    try:
        response = requests.get(SEND_MESSAGE_WEBHOOK)
        data = response.json()
        new_messages = data.get("messages", [])

        # Only append if messages are new
        for msg in new_messages:
            if msg not in st.session_state["chat_history"]:  
                st.session_state["chat_history"].append(msg)

    except Exception as e:
        pass  # Don't interrupt the UI on fetch errors

# **Background auto-refresh for new messages**
polling_interval = 5  # Check every 5 seconds
if "last_poll" not in st.session_state or time.time() - st.session_state["last_poll"] > polling_interval:
    fetch_new_messages()
    st.session_state["last_poll"] = time.time()

# Display chat messages
for msg in st.session_state["chat_history"]:
    role = "user" if msg["Role"] == "user" else "assistant"
    avatar = USER_AVATAR if role == "user" else NOVA_AVATAR
    with st.chat_message(role, avatar=avatar):
        st.write(msg["Content"])

# Chat input
prompt = st.chat_input("Type your message here...")

if prompt:
    # Append user message
    st.session_state["chat_history"].append({"Role": "user", "Content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)

    # Send message to n8n for AI response
    try:
        response = requests.post(SEND_MESSAGE_WEBHOOK, json={"chatInput": prompt})
        if response.status_code == 200:
            ai_response = response.json().get("response", "Nova is thinking...")
            st.session_state["chat_history"].append({"Role": "assistant", "Content": ai_response})
            with st.chat_message("assistant", avatar=NOVA_AVATAR):
                st.write(ai_response)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")
