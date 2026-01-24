import streamlit as st
import google.generativeai as genai

# Page Config
st.set_page_config(
    page_title="Student Wellness Companion",
    page_icon="🌱",
    layout="centered"
)

# App Title
st.title("🌱 Student Wellness Companion")
st.caption("A supportive AI chat for students – powered by Gemini")

# System Instruction
SYSTEM_INSTRUCTION = """
You are a compassionate and supportive AI companion designed specifically for students.
Your primary role is to provide emotional support, detect mood through user messages,
and respond with empathy and care.

Core Behaviors:
1. Mood Detection: Analyze tone and identify emotions like stress, anxiety, loneliness, sadness
2. Empathetic Responses: Validate feelings first, use warm non-judgmental language
3. Motivational Support: Offer encouragement and help reframe negative thoughts
4. Relaxation Tips: Suggest breathing exercises, grounding techniques when needed
5. Safety Protocol: For severe distress, express care and provide crisis resources
6. Keep responses concise but warm, use gentle emoji occasionally 🌟💚
"""

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = None

# API Key Input
if not st.session_state.api_key:
    st.markdown("### 🔑 Enter Your Gemini API Key")
    
    key = st.text_input("API Key", type="password")
    
    if st.button("Submit", type="primary"):
        if key:
            try:
                genai.configure(api_key=key)
                # Test the key
                model = genai.GenerativeModel("gemini-1.5-flash")
                model.generate_content("test")
                st.session_state.api_key = key
                st.success("✅ Connected!")
                st.rerun()
            except Exception as e:
                st.error(f"Invalid API Key: {e}")
        else:
            st.warning("Please enter a key")
    
    st.info("Get your key here: [Google AI Studio](https://aistudio.google.com/app/apikey)")
    st.stop()

# Configure API
genai.configure(api_key=st.session_state.api_key)
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION
)

# Sidebar
with st.sidebar:
    st.header("🧘 Relaxation Tips")
    with st.expander("Deep Breathing"):
        st.write("Inhale 4s → Hold 7s → Exhale 8s")
    with st.expander("Grounding 5-4-3-2-1"):
        st.write("5 see, 4 touch, 3 hear, 2 smell, 1 taste")
    with st.expander("📞 Crisis Help"):
        st.write("USA: 988 | India: 9152987821")
    
    if st.button("Clear Chat"):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("Reset Key"):
        st.session_state.api_key = None
        st.rerun()

# Chat Interface
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Hey! 👋 I'm here to support you. **How are you feeling today?** 💚")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Share what's on your mind..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)
    
    # Generate Response
    history = [{"role": "user" if m["role"] == "user" else "model", "parts": [m["content"]]} for m in st.session_state.messages[:-1]]
    
    with st.chat_message("assistant"):
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt, stream=True)
            text = st.write_stream(chunk.text for chunk in response if chunk.text)
            st.session_state.messages.append({"role": "assistant", "content": text})
        except Exception as e:
            st.error(f"Error: {e}")
