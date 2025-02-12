import streamlit as st
import requests

# Configure the page
st.set_page_config(page_title="Nova", page_icon="🚀")

st.title("Nova")
st.caption("Assisting you in building an empire 🚀")

# Webhook URLs
HISTORY_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/3764813c-37c3-412c-b051-377c72a9049a"
SEND_MESSAGE_WEBHOOK = "https://emperorjosh.app.n8n.cloud/webhook/d7374fd4-5d48-4229-ae39-2ebbfdc9a33f"

# User & Nova avatars
USER_AVATAR = "assets/josh.png"
NOVA_AVATAR = "assets/nova.png"
ACTION_ICON = "🔹"  # Universal icon for AI-executed actions

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

        return messages[::-1]  # Reverse for latest messages first (newest at the bottom)

    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

# Load initial chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = fetch_chat_history()

# JavaScript for ensuring chat starts from bottom (but no forced scrolling)
st.markdown("""
    <script>
        function scrollToBottom() {
            var chatContainer = window.parent.document.querySelector('.main');
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }
        setTimeout(scrollToBottom, 500);
    </script>
""", unsafe_allow_html=True)

# Function to render messages with distinction for AI actions
def render_message(msg):
    role = "user" if msg["Role"] == "user" else "assistant"
    avatar = USER_AVATAR if role == "user" else NOVA_AVATAR

    if "ActionType" in msg:
        # Special format for AI-executed actions
        with st.chat_message("assistant", avatar=avatar):
            st.markdown(
                f"""
                <div style="border-left: 4px solid #4CAF50; background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px;">
                    <strong>{ACTION_ICON} {msg["ActionType"]} Completed</strong>  
                    <p>{msg["Content"]}</p>
                    {f'<a href="{msg["ActionLink"]}" target="_blank">🔗 View Event</a>' if "ActionLink" in msg else ""}
                </div>
                """,
                unsafe_allow_html=True
            )
    else:
        # Normal chat message
        with st.chat_message(role, avatar=avatar):
            st.write(msg["Content"])

# Render chat history
for msg in st.session_state["chat_history"]:
    render_message(msg)

# Button to load older messages (only appears when scrolling up)
if st.session_state.get("show_load_button", False):
    if st.button("🔼 Load Older Messages"):
        old_messages = fetch_chat_history()
        if old_messages:
            st.session_state["chat_history"] = old_messages + st.session_state["chat_history"]
            st.experimental_rerun()

# JavaScript to listen for scroll events (to toggle the "Load Older Messages" button)
st.markdown("""
    <script>
        var chatContainer = window.parent.document.querySelector('.main');
        chatContainer.addEventListener('scroll', function() {
            if (chatContainer.scrollTop === 0) {
                window.parent.postMessage('scroll_top', '*');
            }
        });
    </script>
""", unsafe_allow_html=True)

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
            action_type = response.json().get("actionType", None)
            action_link = response.json().get("actionLink", None)

            message = {"Role": "assistant", "Content": ai_response}
            if action_type:
                message["ActionType"] = action_type
            if action_link:
                message["ActionLink"] = action_link

            st.session_state["chat_history"].append(message)
            render_message(message)
            
            # Auto-scroll to the bottom after receiving a response
            st.markdown("<script>setTimeout(scrollToBottom, 500);</script>", unsafe_allow_html=True)

        else:
            st.error(f"Error: {response.status_code} - {response.text}")
    except Exception as e:
        st.error(f"Connection error: {e}")
