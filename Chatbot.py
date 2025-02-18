import streamlit as st
import requests
import time


# Ensure session state variables exist
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # Initialize chat history as an empty list

# 🌐 Webhook URLs
HISTORY_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"
SEND_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/d7374fd4-5d48-4229-ae39-2ebbfdc9a33f"
PROACTIVE_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/7337a77e-1ec8-45da-86b9-c06628865d86"

# 🖼️ Avatars
USER_AVATAR = "assets/josh.png"
NOVA_AVATAR = "assets/nova.png"

# **Fetch Chat History from n8n**
def fetch_chat_history():
    try:
        response = requests.get(HISTORY_WEBHOOK)
        data = response.json()
        messages = data.get("messages", {}).get("history", [])
        return messages[::-1] if isinstance(messages, list) else [messages]
    except Exception as e:
        return []

# **Send User Message to n8n**
def send_message_to_n8n(content):
    try:
        response = requests.post(SEND_MESSAGE_WEBHOOK, json={"chatInput": content})
        if response.status_code == 200:
            return response.json().get("response", "Nova is thinking...")
        else:
            return f"Error: {response.status_code} - {response.text}"
    except Exception as e:
        return f"Connection error: {e}"

# **Fetch New Proactive Messages from n8n**
def fetch_proactive_messages():
    try:
        response = requests.get(PROACTIVE_MESSAGE_WEBHOOK)
        if response.status_code == 200:
            data = response.json()

            # ✅ Ensure it's always treated as a dictionary
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Extract the first dictionary inside the list

            new_messages = data.get("messages", [])

            for msg in new_messages:
                if msg not in st.session_state["chat_history"]:
                    st.session_state["chat_history"].append(msg)
                    st.experimental_rerun()  # 🔥 Force Streamlit to refresh the UI

    except Exception as e:
        st.error(f"Error fetching proactive messages: {e}")

# **Auto-refresh every 5 seconds**
polling_interval = 5
if "last_poll" not in st.session_state or time.time() - st.session_state["last_poll"] > polling_interval:
    fetch_proactive_messages()
    st.session_state["last_poll"] = time.time()


# **Initialize Chat History**
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = fetch_chat_history()

# **Auto-refresh for new proactive messages every 5 seconds**
polling_interval = 5
if "last_poll" not in st.session_state or time.time() - st.session_state["last_poll"] > polling_interval:
    fetch_proactive_messages()
    st.session_state["last_poll"] = time.time()

# **Display Chat Messages**
for msg in st.session_state["chat_history"]:
    role = "user" if msg["Role"] == "user" else "assistant"
    avatar = USER_AVATAR if role == "user" else NOVA_AVATAR
    with st.chat_message(role, avatar=avatar):
        st.write(msg["Content"])

# **User Input for Sending Messages**
prompt = st.chat_input("Type your message here...")

if prompt:
    # Append user message
    st.session_state["chat_history"].append({"Role": "user", "Content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)

    # Send to n8n & Get Nova's Response
    ai_response = send_message_to_n8n(prompt)
    st.session_state["chat_history"].append({"Role": "assistant", "Content": ai_response})
    with st.chat_message("assistant", avatar=NOVA_AVATAR):
        st.write(ai_response)
