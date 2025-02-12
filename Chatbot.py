import streamlit as st
import requests

# Configure the page
st.title("Nova")
st.caption("Assisting you in building an empire 🚀")

# Webhook URLs for fetching chat history & sending messages
HISTORY_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"
SEND_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/d7374fd4-5d48-4229-ae39-2ebbfdc9a33f"

# User & Nova avatars
USER_AVATAR = "assets/josh.png"
NOVA_AVATAR = "assets/nova.png"

# Function to fetch chat history
def fetch_chat_history():
    try:
        response = requests.get(HISTORY_WEBHOOK)
        data = response.json()

        # Extract history messages safely
        messages = data.get("messages", {}).get("history", [])

        # Ensure it's always a list
        if not isinstance(messages, list):
            messages = [messages]

        # Reverse for latest messages first
        return messages[::-1]  

    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

# Load initial chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = fetch_chat_history()

# Display chat messages with avatars
if st.session_state["chat_history"]:
    for msg in st.session_state["chat_history"]:
        role = "user" if msg["Role"] == "user" else "assistant"
        avatar = USER_AVATAR if role == "user" else NOVA_AVATAR
        with st.chat_message(role, avatar=avatar):
            st.write(msg["Content"])
else:
    st.error("Failed to load chat history.")

# Button to load older messages
if st.button("🔼 Load Older Messages"):
    old_messages = fetch_chat_history()
    if old_messages:
        st.session_state["chat_history"] = old_messages + st.session_state["chat_history"]
        st.experimental_rerun()

# Chat input
prompt = st.chat_input("Type your message here...")

if prompt:
    # Append new message
    st.session_state["chat_history"].append({"Role": "user", "Content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)

    # Send message to N8N for AI response
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
