import streamlit as st
import google.generativeai as genai
from textblob import TextBlob

st.set_page_config(page_title="MindfulMate AI", page_icon="🌱")

# 1. Empathetic System Instruction
SYSTEM_PROMPT = """
You are MindfulMate, a supportive and empathetic AI companion for university students. 
Your goal is to provide a safe, non-judgmental space for students to express stress, anxiety, or loneliness. 
- Use warm, motivational language.
- If a user seems stressed, offer quick relaxation tips (e.g., 4-7-8 breathing).
- Avoid giving clinical medical advice. 
- Always encourage professional help if the user mentions self-harm.
"""

st.title("🌱 MindfulMate: Student Support")
st.caption("A safe space to talk, breathe, and find motivation.")

with st.sidebar:
    st.header("Help & Resources")
    st.info("Remember: I am an AI, not a doctor. If you're in crisis, please reach out to a professional.")
    if st.button("🆘 Urgent Help Resources"):
        st.toast("National Helpline: 9152987821 (iCall India)", icon="📞")
    
    if st.button("Clear Conversation"):
        st.session_state.history = []
        st.rerun()

# API Setup
if "app_key" not in st.session_state:
    st.session_state.app_key = st.text_input("Enter Gemini API Key", type='password')

if st.session_state.app_key:
    genai.configure(api_key=st.session_state.app_key)
    # Applying the System Instruction to the model
    model = genai.GenerativeModel(
        model_name="gemini-2.5-flash",
        system_instruction=SYSTEM_PROMPT
    )
    
    if "history" not in st.session_state:
        st.session_state.history = []

    chat = model.start_chat(history=st.session_state.history)

    # Display Chat
    for message in st.session_state.history:
        with st.chat_message("assistant" if message.role == 'model' else "user"):
            st.markdown(message.parts[0].text)

    if prompt := st.chat_input("How are you feeling today?"):
        # Real-time Sentiment Analysis
        sentiment = TextBlob(prompt).sentiment.polarity
        
        with st.chat_message("user"):
            st.markdown(prompt)
            if sentiment < -0.3:
                st.caption("✨ *It sounds like you're having a tough time. I'm here for you.*")

        with st.chat_message("assistant"):
            response_placeholder = st.empty()
            full_response = ""
            
            # Stream the response
            stream = chat.send_message(prompt, stream=True)
            for chunk in stream:
                full_response += chunk.text
                response_placeholder.markdown(full_response + "▌")
            response_placeholder.markdown(full_response)
        
        st.session_state.history = chat.history
else:
    st.warning("Please enter your API Key to begin.")
