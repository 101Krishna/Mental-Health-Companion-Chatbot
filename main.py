import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import nltk
import time

# --- INITIAL SETUP ---
st.set_page_config(page_title="MindfulMate AI", page_icon="🌱", layout="centered")

# Download NLTK data needed for TextBlob sentiment analysis
@st.cache_resource
def download_nltk_data():
    try:
        nltk.download('punkt')
        nltk.download('movie_reviews')
        nltk.download('punkt_tab')
    except Exception as e:
        st.error(f"Error downloading NLTK data: {e}")

download_nltk_data()

# --- MENTAL HEALTH PERSONA ---
SYSTEM_PROMPT = """
You are MindfulMate, a compassionate and motivational AI companion designed for university students.
Your mission is to provide a safe, non-judgmental space for students facing stress, anxiety, or loneliness.

Guidelines:
1. Detect user mood: If the user sounds sad or stressed, acknowledge their feelings first.
2. Be Motivational: Offer encouraging words and remind them of their strengths.
3. Relaxation Tips: Suggest actionable tips like 4-7-8 breathing, short walks, or mindfulness.
4. Professional Boundary: You are NOT a doctor. If a user mentions self-harm, provide helpline numbers immediately.
5. Tone: Warm, empathetic, and supportive.
"""

st.title("🌱 MindfulMate")
st.markdown("### Your Student Well-being Companion")

# --- SIDEBAR & API KEY ---
with st.sidebar:
    st.header("Settings & Resources")
    api_key = st.text_input("Enter your Gemini API Key:", type="password")
    
    st.divider()
    st.info("🆘 **Emergency Resources:**\n- iCall India: 9152987821\n- Vandrevala Foundation: 9999666555")
    
    if st.button("Clear Chat History", use_container_width=True):
        st.session_state.history = []
        st.rerun()

# Initialize Session State
if "history" not in st.session_state:
    st.session_state.history = []

# --- MAIN CHAT LOGIC ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using Gemini 2.5 Flash for speed and reliability in 2026
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

        # User Input
        if prompt := st.chat_input("How are you feeling right now?"):
            # 1. Sentiment Analysis
            analysis = TextBlob(prompt)
            sentiment_score = analysis.sentiment.polarity # Range -1 to 1

            with st.chat_message("user"):
                st.markdown(prompt)
                # Visual Mood Feedback
                if sentiment_score < -0.3:
                    st.caption("✨ *MindfulMate is listening. It's okay to feel this way.*")

            # 2. Generate AI Response
            with st.chat_message("assistant"):
                response_placeholder = st.empty()
                full_response = ""
                
                # Streaming response with typewriter effect
                stream = chat.send_message(prompt, stream=True)
                for chunk in stream:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01) # Small delay for realism
                response_placeholder.markdown(full_response)
            
            # Save history
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"API Error: {e}")
else:
    st.warning("Please enter your Gemini API Key in the sidebar to start.")
