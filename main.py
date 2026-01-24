import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(page_title="Wellness Companion", page_icon="🌱")

st.title("🌱 Student Wellness Companion")

# API Key Handling
if "api_key" not in st.session_state:
    st.session_state.api_key = None

if not st.session_state.api_key:
    st.info("Please enter your Gemini API Key to continue.")
    key = st.text_input("API Key", type="password")
    if st.button("Connect"):
        if key:
            st.session_state.api_key = key
            st.rerun()
    st.stop()

# Configure Model
try:
    genai.configure(api_key=st.session_state.api_key)
    model = genai.GenerativeModel('gemini-1.5-flash')
except Exception as e:
    st.error(f"Configuration error: {e}")
    st.stop()

# Chat Interface
if "messages" not in st.session_state:
    st.session_state.messages = [{"role": "assistant", "content": "Hi! How are you feeling today?"}]

for msg in st.session_state.messages:
    st.chat_message(msg["role"]).write(msg["content"])

if prompt := st.chat_input():
    st.session_state.messages.append({"role": "user", "content": prompt})
    st.chat_message("user").write(prompt)
    
    try:
        response = model.generate_content(prompt)
        st.session_state.messages.append({"role": "assistant", "content": response.text})
        st.chat_message("assistant").write(response.text)
    except Exception as e:
        st.error(f"Error: {e}")
