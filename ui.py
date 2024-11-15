import streamlit as st
import requests
from streamlit_chat import message
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

# Set base API URL
API_BASE_URL = "http://localhost:5000/rag/api/v1"

# Initialize session state
if "token" not in st.session_state:
    st.session_state.token = None
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "login_failed" not in st.session_state:
    st.session_state.login_failed = False

# Utility: Check token validity
def check_token():
    headers = {"Authorization": f"Bearer {st.session_state.token}"}
    try:
        response = requests.get(f"{API_BASE_URL}/health", headers=headers)
        return response.status_code == 200
    except Exception as e:
        logging.error(f"Error checking token: {e}")
        return False

# Login Page
def login_page():
    st.markdown("<h1 style='text-align: center;'>🔒 Login</h1>", unsafe_allow_html=True)
    username = st.text_input("👤 Username", placeholder="Enter your username")
    password = st.text_input("🔑 Password", type="password", placeholder="Enter your password")
    login_btn = st.button("Login")

    if login_btn:
        response = requests.post(f"{API_BASE_URL}/login", json={"username": username, "password": password})
        if response.status_code == 200:
            st.session_state.token = response.json().get("token")
            st.session_state.login_failed = False
        else:
            st.session_state.login_failed = True
            error_message = response.json().get("message", "Invalid credentials.")
            st.error(error_message)

# Main Page
def main_page():
    st.markdown("<h1 style='text-align: center;'>📚 RAG System</h1>", unsafe_allow_html=True)

    # Sidebar: URL Indexing
    st.sidebar.markdown("### 🌐 Index URLs")
    url = st.sidebar.text_input("Enter URL to index", placeholder="https://example.com/article")
    if st.sidebar.button("Index URL") and url.strip():
        headers = {"Authorization": f"Bearer {st.session_state.token}"}
        response = requests.post(f"{API_BASE_URL}/index", json={"url": [url]}, headers=headers)
        if response.status_code == 200:
            data = response.json()
            indexed = data.get("indexed_url", [])
            failed = data.get("failed_url", [])
            if indexed:
                st.sidebar.success(f"✅ Indexed: {', '.join(indexed)}")
            if failed:
                st.sidebar.error(f"❌ Failed: {', '.join(failed)}")
        else:
            st.sidebar.error("Failed to index the URL. Check the API or token.")

    # Session management in Sidebar
    st.sidebar.markdown("---")
    if st.sidebar.button("🔄 Refresh Session"):
        st.session_state.update(chat_history=[])
    if st.sidebar.button("🔓 Logout"):
        st.session_state.update(token=None, chat_history=[])

    # Chat Window (Center Screen)
    st.markdown("---")
    st.markdown("### 🤖 Chat with Documents")
    chat_container = st.container()
    with chat_container:
        user_input = st.text_input("💬 Ask a question...", placeholder="Type your message here...")
        if st.button("Send") and user_input.strip():
            headers = {"Authorization": f"Bearer {st.session_state.token}"}
            messages = st.session_state.chat_history + [{"role": "user", "content": user_input}]
            response = requests.post(f"{API_BASE_URL}/chat", json={"messages": messages}, headers=headers)
            if response.status_code == 200:
                data = response.json()["response"][0]
                assistant_response = data["answer"]["content"]
                citations = data.get("citation", [])
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": assistant_response, "citation": citations})
            elif response.status_code == 401:
                st.error("Session expired. Please log in again.")
                st.session_state.update(token=None, chat_history=[])
                st.experimental_rerun()
            else:
                st.error("Failed to get a response. Check the token or API.")

        # Display Chat History
        st.markdown("---")
        for mes in st.session_state.chat_history:
            if mes["role"] == "user":
                message(mes["content"], is_user=True)
            else:
                message(mes["content"])
                if mes.get("citation"):
                    st.caption(f"📖 Citation: {', '.join(mes['citation'])}")

# Main Workflow
if st.session_state.token and check_token():
    main_page()
else:
    login_page()
