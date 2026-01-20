import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import nltk
import time

# --- 1. CLOUD INITIALIZATION ---
st.set_page_config(page_title="MindfulMate AI", page_icon="🌱")

# Force-download NLTK data required by TextBlob for sentiment analysis
@st.cache_resource
def initialize_nlp():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('movie_reviews')
    except Exception as e:
        st.error(f"NLP Data Error: {e}")

initialize_nlp()

# --- 2. AI CONFIGURATION (Gemini 2.5) ---
SYSTEM_PROMPT = """
You are MindfulMate, a supportive AI for students. 
1. Detect mood: Use empathetic language if the student is stressed.
2. Be motivational: Focus on resilience and student well-being.
3. Provide tips: Suggest relaxation techniques like deep breathing.
4. Safety: Provide helpline numbers (e.g., 9152987821) if self-harm is mentioned.
"""

st.title("🌱 MindfulMate")
st.caption("Empathetic support for university students")

# --- 3. SIDEBAR & API KEY ---
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    if st.button("Clear Chat"):
        st.session_state.history = []
        st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []

# --- 4. CHAT ENGINE ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using Gemini 2.5 Flash for 2026 stability
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        chat = model.start_chat(history=st.session_state.history)

        # Show previous messages
        for message in st.session_state.history:
            with st.chat_message("assistant" if message.role == 'model' else "user"):
                st.markdown(message.parts[0].text)

        # Sentiment Analysis & Response
        if prompt := st.chat_input("How are you feeling?"):
            # Real-time Sentiment Logic
            score = TextBlob(prompt).sentiment.polarity
            
            with st.chat_message("user"):
                st.markdown(prompt)
                if score < -0.3:
                    st.toast("I can feel that you're going through a lot. I'm here.", icon="❤️")

            with st.chat_message("assistant"):
                # Streaming UI
                full_response = ""
                res_box = st.empty()
                for chunk in chat.send_message(prompt, stream=True):
                    full_response += chunk.text
                    res_box.markdown(full_response + "▌")
                    time.sleep(0.01)
                res_box.markdown(full_response)
            
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"App Error: {e}")
else:
    st.info("Please enter your API Key in the sidebar to start.")
