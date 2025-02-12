import streamlit as st
import requests

# Configure the page
st.title("Nove")
st.caption("Assisting you in building an empire 🚀")

# N8N production webhook URL
N8N_WEBHOOK_URL = "https://emperorjosh.app.n8n.cloud/webhook/d7374fd4-5d48-4229-ae39-2ebbfdc9a33f"

# Initialize session state variables
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "How can I help you?"}]

if "debug_mode" not in st.session_state:
    st.session_state["debug_mode"] = False  # Default is OFF

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Settings")
    st.session_state["debug_mode"] = st.toggle("Enable Debug Mode", st.session_state["debug_mode"])

# Display chat history
for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

# Handle user input
if prompt := st.chat_input():
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)

    # Modify payload to send full conversation history
    payload = {
        "chatInput": prompt,  # Latest user message
        "messages": st.session_state.messages  # Full chat history
    }


    try:
        if st.session_state["debug_mode"]:
            st.info(f"📤 Sending message: {prompt}")

        # Send request to n8n webhook
        response = requests.post(N8N_WEBHOOK_URL, json=payload)

        if st.session_state["debug_mode"]:
            st.info(f"🔄 Raw response: {response.text}")

        if response.status_code == 200:
            try:
                response_data = response.json()
                assistant_message = response_data.get("response", "Sorry, I couldn't process your request.")

                # Add bot response to chat history
                st.session_state.messages.append({"role": "assistant", "content": assistant_message})
                st.chat_message("assistant").write(assistant_message)

            except Exception as e:
                st.error(f"⚠️ Error processing response: {str(e)}")

        else:
            st.error(f"⚠️ Error: Status code {response.status_code} - {response.reason}")

    except Exception as e:
        st.error(f"⚠️ Connection error: {str(e)}")
