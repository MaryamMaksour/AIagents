
import os
import uuid
import requests
import streamlit as st

# -----------------------
# Config
# -----------------------
API_BASE = os.getenv("AGENT_API_BASE", "http://localhost:8004")  # FastAPI base URL
CHAT_ENDPOINT = f"{API_BASE}/chat"
RESET_ENDPOINT = f"{API_BASE}/reset"
HEALTH_ENDPOINT = f"{API_BASE}/health"

st.set_page_config(page_title="Agent4 Chat", page_icon="🤖", layout="centered")

# -----------------------
# Session state
# -----------------------
if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    # Store chat UI history locally for display (server maintains its own history)
    st.session_state.messages = []  # list[{"role": "user"|"assistant", "content": str}]

# -----------------------
# Sidebar controls
# -----------------------
with st.sidebar:
    st.title("⚙️ Settings")
    st.caption(f"Session ID: `{st.session_state.session_id}`")

    if st.button("🔁 Reset conversation (server + UI)"):
        try:
            requests.post(RESET_ENDPOINT, json={"session_id": st.session_state.session_id}, timeout=15)
        except Exception as e:
            st.warning(f"Reset call failed: {e}")
        st.session_state.messages = []
        st.success("Conversation reset.")

    st.divider()
    if st.button("🔄 New session ID"):
        st.session_state.session_id = str(uuid.uuid4())
        st.session_state.messages = []
        st.success("Session updated. UI history cleared.")

    st.divider()
    try:
        resp = requests.get(HEALTH_ENDPOINT, timeout=5)
        ok = (resp.status_code == 200 and resp.json().get("status") == "ok")
        st.caption(f"API health: {'🟢 OK' if ok else '🔴 Unavailable'}")
    except Exception:
        st.caption("API health: 🔴 Unavailable")

# -----------------------
# Header
# -----------------------
st.title("🤖 Agent4 Chat - Deals")
st.write("Ask me anything. The assistant uses RAG and tools under the hood.")

# -----------------------
# Render chat history
# -----------------------
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# -----------------------
# Chat input
# -----------------------
user_input = st.chat_input("Type your message...")

if user_input:
    # Append user to UI
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    # Call backend
    try:
        payload = {
            "session_id": st.session_state.session_id,
            "user_input": user_input
        }
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                r = requests.post(CHAT_ENDPOINT, json=payload, timeout=3600)
                if r.status_code != 200:
                    st.error(f"API error {r.status_code}: {r.text}")
                    assistant_text = "Sorry, something went wrong while contacting the server."
                else:
                    data = r.json()
                    assistant_text = data.get("answer", "No answer returned.")
                st.markdown(assistant_text)

        # Append assistant to UI
        st.session_state.messages.append({"role": "assistant", "content": assistant_text})

    except requests.RequestException as e:
        st.error(f"Request failed: {e}")

