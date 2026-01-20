import streamlit as st
import google.generativeai as genai
from textblob import TextBlob
import nltk
import time

# --- 1. SETUP & DEPENDENCIES ---
st.set_page_config(page_title="MindfulMate AI", page_icon="🌱")

# Automatically download NLTK data for sentiment analysis on Streamlit Cloud
@st.cache_resource
def download_nltk():
    try:
        nltk.download('punkt')
        nltk.download('punkt_tab')
        nltk.download('movie_reviews')
    except Exception as e:
        st.error(f"Error loading NLP data: {e}")

download_nltk()

# --- 2. AI PERSONA CONFIGURATION ---
SYSTEM_PROMPT = """
You are MindfulMate, an empathetic AI companion for university students.
Your mission: Provide a safe, non-judgmental space for students facing stress or loneliness.
- Use warm, motivational language.
- Detect mood: If the user sounds sad, offer immediate validation.
- Tips: Suggest relaxation techniques like deep breathing or short walks.
- Safety: If a user mentions self-harm, provide helpline numbers immediately.
"""

st.title("🌱 MindfulMate")
st.markdown("### Support for Student Well-being")

# --- 3. SIDEBAR & KEY HANDLING ---
with st.sidebar:
    st.header("App Settings")
    api_key = st.text_input("Enter Gemini API Key:", type="password")
    
    st.divider()
    st.info("🆘 **Need to talk?**\n- iCall (India): 9152987821\n- Vandrevala: 9999666555")
    
    if st.button("Reset Conversation", use_container_width=True):
        st.session_state.history = []
        st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []

# --- 4. CHAT INTERFACE ---
if api_key:
    try:
        genai.configure(api_key=api_key)
        # Using gemini-2.5-flash: Fast, stable, and fixes the 404 'not found' error
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_PROMPT
        )
        chat = model.start_chat(history=st.session_state.history)

        # Display Chat History
        for message in st.session_state.history:
            role = "assistant" if message.role == 'model' else "user"
            with st.chat_message(role):
                st.markdown(message.parts[0].text)

        # User Prompt & Sentiment Detection
        if prompt := st.chat_input("How are you feeling today?"):
            # Sentiment Analysis
            analysis = TextBlob(prompt)
            mood_score = analysis.sentiment.polarity 

            with st.chat_message("user"):
                st.markdown(prompt)
                # Immediate visual feedback for low mood
                if mood_score < -0.3:
                    st.caption("✨ *MindfulMate is here for you. Take a deep breath.*")

            # Assistant Response
            with st.chat_message("assistant"):
                full_response = ""
                response_placeholder = st.empty()
                
                # Streaming with typing effect
                stream = chat.send_message(prompt, stream=True)
                for chunk in stream:
                    full_response += chunk.text
                    response_placeholder.markdown(full_response + "▌")
                    time.sleep(0.01)
                response_placeholder.markdown(full_response)
            
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"Something went wrong: {e}")
else:
    st.warning("Please enter your API Key in the sidebar to begin.")
