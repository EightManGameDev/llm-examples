import streamlit as st
import requests

# Configure the page
st.title("Nova")
st.caption("Assisting you in building an empire 🚀")

# Webhook URLs
N8N_HISTORY_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"
N8N_CHAT_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/d7374fd4-5d48-4229-ae39-2ebbfdc9a33f"

# Initialize session state
if "messages" not in st.session_state:
    st.session_state["messages"] = []
if "loaded_messages" not in st.session_state:
    st.session_state["loaded_messages"] = 30  # Start with the latest 30 messages

# Function to load chat history
def load_chat_history():
    try:
        response = requests.get(N8N_HISTORY_WEBHOOK)
        if response.status_code == 200:
            chat_data = response.json().get("messages", [])
            st.session_state["messages"] = chat_data[::-1]  # Reverse for correct order
        else:
            st.error("Failed to load chat history.")
    except Exception as e:
        st.error(f"Error loading chat history: {e}")

# Function to load older messages
def load_older_messages():
    st.session_state["loaded_messages"] += 10  # Load 10 more messages
    try:
        response = requests.get(N8N_HISTORY_WEBHOOK)
        if response.status_code == 200:
            chat_data = response.json().get("messages", [])
            st.session_state["messages"] = chat_data[::-1][:st.session_state["loaded_messages"]]
        else:
            st.error("Failed to load older messages.")
    except Exception as e:
        st.error(f"Error loading older messages: {e}")

# Load chat history on startup
if not st.session_state["messages"]:
    load_chat_history()

# Display chat history
for msg in st.session_state["messages"]:
    st.chat_message(msg["role"]).write(msg["content"])

# Load older messages button
if st.button("⬆️ Load Older Messages"):
    load_older_messages()

# Handle user input
if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Send request to n8n webhook
    payload = {"chatInput": prompt, "messages": st.session_state.messages}
    try:
        response = requests.post(N8N_CHAT_WEBHOOK, json=payload)
        if response.status_code == 200:
            assistant_message = response.json().get("response", "Sorry, I couldn't process your request.")
            st.session_state.messages.append({"role": "assistant", "content": assistant_message})
            st.chat_message("assistant").write(assistant_message)
        else:
            st.error(f"⚠️ Error: Status code {response.status_code} - {response.reason}")
    except Exception as e:
        st.error(f"⚠️ Connection error: {e}")
