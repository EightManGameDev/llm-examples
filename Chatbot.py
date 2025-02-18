import streamlit as st
import requests
import time


# 🖼️ Avatars
USER_AVATAR = "assets/josh.png"
NOVA_AVATAR = "assets/nova.png"


# 🌐 Webhook URLs
HISTORY_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"
SEND_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/d7374fd4-5d48-4229-ae39-2ebbfdc9a33f"
PROACTIVE_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/YOUR-NEW-PROACTIVE-WEBHOOK-ID"

# **Initialize Chat History If Not Set**
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []  # Set empty list first
    # ✅ Load previous chat history at startup
    try:
        response = requests.get(HISTORY_WEBHOOK)
        if response.status_code == 200:
            data = response.json()
            messages = data.get("messages", {}).get("history", [])
            if isinstance(messages, list):
                st.session_state["chat_history"] = messages[::-1]  # Reverse order for correct display
    except Exception as e:
        st.error(f"Error loading chat history: {e}")

# **Fetch New Proactive Messages from n8n**
def fetch_proactive_messages():
    try:
        response = requests.get(PROACTIVE_MESSAGE_WEBHOOK)
        if response.status_code == 200:
            data = response.json()

            # ✅ Ensure it's always a dictionary, even if it's inside a list
            if isinstance(data, list) and len(data) > 0:
                data = data[0]  # Extract the first dictionary inside the list

            new_messages = data.get("messages", [])

            # ✅ Append new messages ONLY if they aren't already in chat history
            added_new_message = False
            for msg in new_messages:
                if msg not in st.session_state["chat_history"]:
                    st.session_state["chat_history"].append(msg)
                    added_new_message = True  # ✅ Flag that a new message was added

            # 🔥 Force UI refresh ONLY IF a new message was added
            if added_new_message:
                st.rerun()

    except Exception as e:
        st.error(f"Error fetching proactive messages: {e}")


# **Auto-refresh for new proactive messages every 5 seconds**
polling_interval = 5
if "last_poll" not in st.session_state or time.time() - st.session_state["last_poll"] > polling_interval:
    fetch_proactive_messages()
    st.session_state["last_poll"] = time.time()

# **Display Chat Messages**
for msg in st.session_state["chat_history"]:
    role = "user" if msg["Role"] == "user" else "assistant"
    avatar = "assets/josh.png" if role == "user" else "assets/nova.png"
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
    try:
        response = requests.post(SEND_MESSAGE_WEBHOOK, json={"chatInput": prompt})
        if response.status_code == 200:
            ai_response = response.json().get("response", "Nova is thinking...")
            st.session_state["chat_history"].append({"Role": "assistant", "Content": ai_response})
            with st.chat_message("assistant", avatar=NOVA_AVATAR):
                st.write(ai_response)
    except Exception as e:
        st.error(f"Connection error: {e}")
