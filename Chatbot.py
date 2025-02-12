import streamlit as st
import requests

# Configure the page
st.title("Nova")
st.caption("Assisting you in building an empire 🚀")

# Webhook URL for fetching chat history
WEBHOOK_URL = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"

# Function to fetch chat history
def fetch_chat_history():
    try:
        response = requests.get(WEBHOOK_URL)
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

# Display chat messages
if st.session_state["chat_history"]:
    for msg in st.session_state["chat_history"]:
        role = "👤 You" if msg["Role"] == "user" else "🤖 Nova"
        st.chat_message(role).write(msg["Content"])
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
    st.chat_message("👤 You").write(prompt)

    # Send message to N8N for AI response
    try:
        response = requests.post(WEBHOOK_URL, json={"chatInput": prompt})
        if response.status_code == 200:
            ai_response = response.json().get("response", "Nova is thinking...")
            st.session_state["chat_history"].append({"Role": "assistant", "Content": ai_response})
            st.chat_message("🤖 Nova").write(ai_response)
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")
