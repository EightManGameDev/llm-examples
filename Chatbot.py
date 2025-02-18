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

# **Ensure Chat History is Initialized**
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = []

# **Fetch Chat History (On Startup)**
try:
    response = requests.get(HISTORY_WEBHOOK)
    if response.status_code == 200:
        data = response.json()
        messages = data.get("messages", {}).get("history", [])
        if isinstance(messages, list):
            st.session_state["chat_history"] = messages[::-1]  # Reverse order for correct display
except Exception as e:
    st.error(f"Error loading chat history: {e}")

# **Send Message to n8n & Get AI Response**
def send_message_to_n8n(content, is_proactive=False):
    try:
        webhook_url = PROACTIVE_MESSAGE_WEBHOOK if is_proactive else SEND_MESSAGE_WEBHOOK
        response = requests.post(webhook_url, json={"chatInput": content})
        if response.status_code == 200:
            ai_response = response.json().get("response", "Nova is thinking...")
            st.session_state["chat_history"].append({"Role": "assistant", "Content": ai_response})
            st.rerun()  # Refresh UI when a new message arrives
        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")

# **Display Chat Messages**
for msg in st.session_state["chat_history"]:
    role = "user" if msg["Role"] == "user" else "assistant"
    avatar = "assets/josh.png" if role == "user" else "assets/nova.png"
    with st.chat_message(role, avatar=avatar):
        st.write(msg["Content"])

# **User Input for Sending Messages**
prompt = st.chat_input("Type your message here...")

if prompt:
    st.session_state["chat_history"].append({"Role": "user", "Content": prompt})
    with st.chat_message("user", avatar="assets/josh.png"):
        st.write(prompt)

    # **Send User Message to n8n**
    send_message_to_n8n(prompt)

# **Check for Proactive Messages Every 5 Seconds**
polling_interval = 5
if "last_poll" not in st.session_state or time.time() - st.session_state["last_poll"] > polling_interval:
    send_message_to_n8n("Nova, any updates?", is_proactive=True)
    st.session_state["last_poll"] = time.time()
