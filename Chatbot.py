import streamlit as st
import requests
import streamlit.components.v1 as components

# Configure the page
st.set_page_config(page_title="Nova", page_icon="🚀", layout="wide")

# Custom CSS for a futuristic UI with Glassmorphism
def set_custom_style():
    st.markdown("""
        <style>
            body {
                background-color: #0D1117;
                color: white;
                font-family: 'Orbitron', sans-serif;
            }
            .stChatMessage {
                border-radius: 15px;
                padding: 12px;
                margin-bottom: 10px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                transition: all 0.3s ease-in-out;
            }
            .stChatMessage:hover {
                background: rgba(255, 255, 255, 0.2);
            }
            .stTextInput > div > div > input {
                background: rgba(255, 255, 255, 0.1);
                color: white;
                border-radius: 15px;
                padding: 10px;
                font-size: 18px;
            }
            .title {
                font-size: 50px;
                font-weight: bold;
                text-align: center;
                color: #39FF14;
                margin-bottom: 10px;
            }
            .subtitle {
                font-size: 22px;
                text-align: center;
                color: #AAAAAA;
                margin-bottom: 20px;
            }
            .chat-container {
                max-width: 900px;
                margin: auto;
                padding: 20px;
                border-radius: 20px;
                background: rgba(255, 255, 255, 0.05);
                backdrop-filter: blur(20px);
                box-shadow: 0 8px 32px rgba(0, 0, 0, 0.5);
            }
            .stButton > button {
                background: linear-gradient(90deg, #39FF14, #00D4FF);
                color: black;
                font-size: 18px;
                border-radius: 10px;
                transition: 0.3s;
            }
            .stButton > button:hover {
                background: linear-gradient(90deg, #00D4FF, #39FF14);
            }
        </style>
    """, unsafe_allow_html=True)

set_custom_style()

st.markdown("<div class='title'>Nova</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Your Ultimate AI Personal Assistant 🚀</div>", unsafe_allow_html=True)

# Webhook URLs
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
        messages = data.get("messages", {}).get("history", [])
        return messages[::-1] if isinstance(messages, list) else []
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
        return []

# Load initial chat history
if "chat_history" not in st.session_state:
    st.session_state["chat_history"] = fetch_chat_history()

# Display chat messages in a futuristic chat container
st.markdown("<div class='chat-container'>", unsafe_allow_html=True)
if st.session_state["chat_history"]:
    for msg in st.session_state["chat_history"]:
        role = "user" if msg["Role"] == "user" else "assistant"
        avatar = USER_AVATAR if role == "user" else NOVA_AVATAR
        with st.chat_message(role, avatar=avatar):
            st.write(msg["Content"])
st.markdown("</div>", unsafe_allow_html=True)

# Chat input with animations
prompt = st.chat_input("Type your message here...")

if prompt:
    st.session_state["chat_history"].append({"Role": "user", "Content": prompt})
    with st.chat_message("user", avatar=USER_AVATAR):
        st.write(prompt)
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
