import streamlit as st
import subprocess
import sys

# Page Config
st.set_page_config(
    page_title="Student Wellness Companion",
    page_icon="🌱",
    layout="centered"
)

# Function to install package if not found
def install_package(package):
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Try importing google.generativeai
try:
    import google.generativeai as genai
except ImportError:
    st.warning("Installing google-generativeai... Please wait.")
    install_package("google-generativeai")
    st.rerun()

# App Title
st.title("🌱 Student Wellness Companion")
st.caption("A supportive AI chat for students – powered by Gemini")

# System Instruction
SYSTEM_INSTRUCTION = """
You are a compassionate and supportive AI companion designed specifically for students.
Your primary role is to provide emotional support, detect mood through user messages,
and respond with empathy and care.

Core Behaviors:

1. Mood Detection:
- Analyze tone, word choice, and context of each message
- Identify emotions like stress, anxiety, loneliness, sadness, frustration
- Also recognize positive emotions and celebrate them

2. Empathetic Responses:
- Always validate feelings first ("I hear you", "That sounds really tough")
- Use warm, non-judgmental language
- Avoid dismissive phrases like "just relax" or "don't worry"

3. Motivational Support:
- Offer encouragement tailored to their situation
- Share brief, relevant affirmations
- Help reframe negative thoughts gently

4. Relaxation Tips (when appropriate):
When detecting stress/anxiety, suggest:
- Deep breathing exercises (4-7-8 technique)
- Grounding techniques (5-4-3-2-1 senses)
- Short breaks and self-care suggestions

5. Safety Protocol:
If someone expresses severe distress or self-harm thoughts:
- Express care and concern
- Encourage them to reach out to a professional
- Provide crisis helpline information
- Never minimize their feelings

6. General Queries:
- For non-mental-health questions, respond helpfully and normally
- Maintain a friendly, supportive tone throughout

Response Style:
- Keep responses concise but warm
- Use gentle emoji occasionally 🌟💚
- Ask follow-up questions to show you care
"""

# Initialize Session State
if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key_valid" not in st.session_state:
    st.session_state.api_key_valid = False

if "app_key" not in st.session_state:
    st.session_state.app_key = ""

# API Key Input Section
if not st.session_state.api_key_valid:
    st.markdown("### 🔑 Enter Your Gemini API Key")
    
    api_key_input = st.text_input(
        "API Key", 
        type="password", 
        placeholder="Paste your Gemini API key here..."
    )
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        submit_btn = st.button("✅ Submit", type="primary", use_container_width=True)
    
    if submit_btn:
        if api_key_input:
            try:
                genai.configure(api_key=api_key_input)
                model = genai.GenerativeModel("gemini-1.5-flash")
                model.generate_content("Hi")
                
                st.session_state.app_key = api_key_input
                st.session_state.api_key_valid = True
                st.success("✅ API Key verified!")
                st.rerun()
            except Exception as e:
                st.error(f"❌ Invalid API Key: {str(e)}")
        else:
            st.warning("⚠️ Please enter an API key")
    
    st.divider()
    
    st.markdown("""
    ### 📖 About This App
    
    A **safe space** for students to:
    - 💬 Talk about stress, anxiety, or loneliness
    - 🧘 Get relaxation techniques
    - 💪 Receive motivational support
    - 📚 Ask general questions too!
    
    ---
    
    ### 🔑 How to get an API Key:
    1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
    2. Sign in with your Google account
    3. Click **"Create API Key"**
    4. Copy and paste it above
    """)
    
    st.stop()

# ============ MAIN APP ============

# Configure API
genai.configure(api_key=st.session_state.app_key)

# Initialize model
model = genai.GenerativeModel(
    model_name="gemini-1.5-flash",
    system_instruction=SYSTEM_INSTRUCTION,
    generation_config={
        "temperature": 0.8,
        "top_p": 0.95,
        "max_output_tokens": 1024,
    }
)

# Sidebar
with st.sidebar:
    st.header("🧘 Quick Relaxation Tips")

    with st.expander("🫁 Deep Breathing (4-7-8)"):
        st.markdown("""
        1. **Inhale** for 4 seconds
        2. **Hold** for 7 seconds
        3. **Exhale** for 8 seconds
        4. Repeat 3-4 times
        """)

    with st.expander("🌍 Grounding (5-4-3-2-1)"):
        st.markdown("""
        Notice around you:
        - **5** things you can see 👀
        - **4** things you can touch ✋
        - **3** things you can hear 👂
        - **2** things you can smell 👃
        - **1** thing you can taste 👅
        """)

    with st.expander("💧 Quick Relief"):
        st.markdown("""
        - Splash cold water on face
        - Roll your shoulders
        - Take a 5-min walk
        - Listen to calming music
        """)

    with st.expander("📞 Crisis Resources"):
        st.markdown("""
        **USA:** 988 (Crisis Lifeline)
        
        **India:**
        - iCall: 9152987821
        - Vandrevala: 1860-2662-345
        
        **UK:** 116 123 (Samaritans)
        
        **International:** [findahelpline.com](https://findahelpline.com)
        """)

    st.divider()

    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    
    if st.button("🔑 Change API Key", use_container_width=True):
        st.session_state.api_key_valid = False
        st.session_state.app_key = ""
        st.session_state.messages = []
        st.rerun()

# Welcome Message
if not st.session_state.messages:
    with st.chat_message("assistant", avatar="🌱"):
        st.markdown("""
        Hey there! 👋 I'm your **Student Wellness Companion**.

        This is a safe space to talk about anything – stress, studies, 
        loneliness, or just life in general.

        I'm here to listen and support you. 💚

        **How are you feeling today?**
        """)

# Display Chat History
for message in st.session_state.messages:
    avatar = "😊" if message["role"] == "user" else "🌱"
    with st.chat_message(message["role"], avatar=avatar):
        st.markdown(message["content"])

# Chat Input
if prompt := st.chat_input("Share what's on your mind... 💭"):
    
    # Display user message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="😊"):
        st.markdown(prompt)

    # Build history
    history = []
    for msg in st.session_state.messages[:-1]:
        role = "user" if msg["role"] == "user" else "model"
        history.append({"role": role, "parts": [msg["content"]]})

    # Generate response
    with st.chat_message("assistant", avatar="🌱"):
        try:
            chat = model.start_chat(history=history)
            response = chat.send_message(prompt, stream=True)
            
            response_text = ""
            placeholder = st.empty()
            
            for chunk in response:
                if chunk.text:
                    response_text += chunk.text
                    placeholder.markdown(response_text + "▌")
            
            placeholder.markdown(response_text)
            
            st.session_state.messages.append({
                "role": "assistant", 
                "content": response_text
            })
            
        except Exception as e:
            st.error(f"Error: {e}")
