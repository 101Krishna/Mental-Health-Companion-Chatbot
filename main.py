import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import nltk
import time

# --- 1. CLOUD ENVIRONMENT SETUP ---
st.set_page_config(page_title="MindfulMate AI", page_icon="🌱")

# Force-download the NLTK data required for sentiment analysis
@st.cache_resource
def initialize_nlp_data():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('movie_reviews')
    except Exception as e:
        st.error(f"NLP Data Error: {e}")

initialize_nlp_data()

# --- 2. AI PERSONA CONFIGURATION ---
SYSTEM_PROMPT = """
You are MindfulMate, a compassionate and motivational AI companion for university students.
Your goal is to support student well-being:
- Detect mood: If the user sounds sad or anxious, acknowledge it immediately.
- Be Motivational: Use warm, encouraging language to build resilience.
- Relaxation Tips: Offer quick tips like the 4-7-8 breathing technique or mindfulness exercises.
- Safety: If self-harm is mentioned, provide helpline numbers (e.g., 9152987821) immediately.
"""

st.title("🌱 MindfulMate")
st.markdown("### Safe & Empathetic Student Support")

# --- 3. SIDEBAR & API KEY ---
with st.sidebar:
    st.header("Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    st.divider()
    st.info("🆘 **Resources:**\n- iCall (India): 9152987821\n- Vandrevala: 9999666555")
    
    if st.button("Reset Chat", use_container_width=True):
        st.session_state.history = []
        st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []

# --- 4. CHAT ENGINE ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using Gemini 2.5 Flash for 2026 performance and stability
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        chat = model.start_chat(history=st.session_state.history)

        # Display History
        for message in st.session_state.history:
            role = "assistant" if message.role == 'model' else "user"
            with st.chat_message(role):
                st.markdown(message.parts[0].text)

        # User Input & Sentiment Logic
        if prompt := st.chat_input("How are you feeling right now?"):
            # Real-time sentiment analysis
            score = TextBlob(prompt).sentiment.polarity 
            
            with st.chat_message("user"):
                st.markdown(prompt)
                # Immediate visual validation for negative sentiment
                if score < -0.3:
                    st.caption("✨ *MindfulMate detects you're having a hard time. I'm listening.*")

            # Streaming AI Response
            with st.chat_message("assistant"):
                full_response = ""
                res_box = st.empty()
                stream = chat.send_message(prompt, stream=True)
                for chunk in stream:
                    full_response += chunk.text
                    res_box.markdown(full_response + "▌")
                    time.sleep(0.01)
                res_box.markdown(full_response)
            
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"App Error: {e}")
else:
    st.info("Please enter your API Key in the sidebar to begin.")
