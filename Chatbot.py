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
ACTION_ICON = "⚡"  # Distinct icon for AI actions

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

# JavaScript to start chat at the bottom (without forced scrolling)
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

# Function to render messages, handling normal responses and AI actions separately
def render_message(msg):
    role = "user" if msg["Role"] == "user" else "assistant"
    avatar = USER_AVATAR if role == "user" else NOVA_AVATAR

    if "ActionConfirmation" in msg:
        # Special format for AI-executed actions
        with st.chat_message("assistant", avatar=avatar):
            st.markdown(
                f"""
                <div style="border-left: 4px solid #FFD700; background-color: rgba(255, 215, 0, 0.1); padding: 10px; border-radius: 5px;">
                    <strong>{ACTION_ICON} Nova Action Taken</strong>  
                    <p>{msg["ActionConfirmation"]}</p>
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
    # Append user message
    st.session_state["chat_history"].append({"Role": "user", "Content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)

    # Temporary "thinking" message
    thinking_message = {"Role": "assistant", "Content": "Nova is thinking..."}
    st.session_state["chat_history"].append(thinking_message)
    thinking_index = len(st.session_state["chat_history"]) - 1  # Track index

    with st.chat_message("assistant", avatar=NOVA_AVATAR):
        st.write("Nova is thinking...")

    # Send message to N8N for AI response
    try:
        response = requests.post(SEND_MESSAGE_WEBHOOK, json={"chatInput": prompt})
        if response.status_code == 200:
            response_data = response.json().get("output", {})

            # Ensure we have a messages array
            messages = response_data.get("messages", [])

            if messages:
                # Remove "Nova is thinking..." placeholder
                st.session_state["chat_history"].pop(thinking_index)

                for msg in messages:
                    role = msg.get("role", "")
                    content = msg.get("content", "")

                    if role == "assistant":
                        message = {"Role": "assistant", "Content": content}
                        st.session_state["chat_history"].append(message)
                        with st.chat_message("assistant", avatar=NOVA_AVATAR):
                            st.write(content)

                    elif role == "system":
                        # Display system messages as "Nova Action" log
                        action_message = {"Role": "system", "Content": content}
                        st.session_state["chat_history"].append(action_message)
                        with st.chat_message("system"):
                            st.markdown(
                                f"""
                                <div style="border-left: 4px solid #4CAF50; background-color: rgba(76, 175, 80, 0.1); padding: 10px; border-radius: 5px;">
                                    <strong>🔹 Nova Action Taken:</strong>  
                                    <p>{content}</p>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

            # Auto-scroll to bottom
            st.markdown("<script>setTimeout(scrollToBottom, 500);</script>", unsafe_allow_html=True)

        else:
            st.error(f"Error: {response.status_code} - {response.text}")

    except Exception as e:
        st.error(f"Connection error: {e}")



