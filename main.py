import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import nltk
import time

# --- 1. ENVIRONMENT SETUP ---
st.set_page_config(page_title="MindfulMate AI", page_icon="🌱", layout="centered")

# This block downloads the required data for TextBlob to work on Streamlit Cloud
@st.cache_resource
def setup_nltk():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab') # Required for modern versions
        nltk.download('movie_reviews')
    except Exception as e:
        st.error(f"NLTK Download Error: {e}")

setup_nltk()

# --- 2. MENTAL HEALTH PERSONA ---
SYSTEM_PROMPT = """
You are MindfulMate, a compassionate AI peer companion for university students. 
Your goal is to provide a safe, non-judgmental space for students facing stress or loneliness.
- Use warm, motivational language.
- If the user is stressed, offer relaxation tips (e.g., 4-7-8 breathing).
- If self-harm is mentioned, provide emergency resources immediately.
- You are an AI, not a clinical counselor.
"""

st.title("🌱 MindfulMate")
st.markdown("### Safe & Empathetic Student Support")

# --- 3. SIDEBAR & KEY HANDLING ---
with st.sidebar:
    st.header("App Controls")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    st.divider()
    st.info("🆘 **Need Help?**\n- Helpline: 9152987821\n- iCall (India)")
    
    if st.button("Clear Conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []

# --- 4. MAIN CHAT LOGIC ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Fix for 404: Using gemini-2.5-flash (the 2026 stable version)
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        chat = model.start_chat(history=st.session_state.history)

        # Display Existing Messages
        for message in st.session_state.history:
            role = "assistant" if message.role == "model" else "user"
            with st.chat_message(role):
                st.markdown(message.parts[0].text)

        # User Input & Sentiment Analysis
        if prompt := st.chat_input("What's on your mind?"):
            # Sentiment Analysis (Detecting User Mood)
            analysis = TextBlob(prompt)
            mood_score = analysis.sentiment.polarity 

            with st.chat_message("user"):
                st.markdown(prompt)
                if mood_score < -0.3:
                    st.caption("✨ *MindfulMate detects you're feeling down. I'm here for you.*")

            # Generate AI Response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                # Streaming with typewriter effect
                stream = chat.send_message(prompt, stream=True)
                for chunk in stream:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
                response_placeholder.markdown(full_response)
            
            # Save history to session
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"Error: {e}")
else:
    st.warning("Please enter your API Key in the sidebar to begin.")
