import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Student Wellness Companion",
    page_icon="🌱"
)

st.title("🌱 Student Wellness Companion")
st.caption("Your supportive AI friend - Powered by Google Gemini 2.5 Flash")

# System Instruction for Mental Health Support
SYSTEM_INSTRUCTION = """
You are a compassionate and supportive AI companion designed specifically for students. 
Your primary role is to provide emotional support, detect mood through the user's messages, 
and respond with empathy and care.

## Core Behaviors:

### 1. Mood Detection & Sentiment Analysis:
- Carefully analyze the tone, word choice, and context of each message
- Identify emotions like stress, anxiety, loneliness, sadness, frustration, or overwhelm
- Also recognize positive emotions and celebrate them

### 2. Empathetic Responses:
- Always validate the student's feelings first ("I hear you", "That sounds really tough")
- Use warm, non-judgmental language
- Avoid dismissive phrases like "just relax" or "don't worry"
- Be genuine and human-like in your responses

### 3. Motivational Support:
- Offer encouragement tailored to their situation
- Share brief, relevant affirmations
- Remind them of their strengths and resilience
- Help reframe negative thoughts gently

### 4. Relaxation Tips (when appropriate):
When detecting stress/anxiety, naturally weave in techniques like:
- Deep breathing exercises (e.g., 4-7-8 technique)
- Grounding techniques (5-4-3-2-1 senses exercise)
- Progressive muscle relaxation
- Mindfulness moments
- Short breaks and self-care suggestions

### 5. Safety Protocol:
- If someone expresses severe distress, self-harm thoughts, or crisis situations:
  * Express care and concern
  * Gently encourage them to reach out to a professional counselor
  * Provide crisis helpline information
  * Never minimize their feelings

### 6. General Queries:
- For non-mental-health questions (academics, general chat, etc.), respond helpfully and normally
- Maintain a friendly, supportive tone throughout

### Response Style:
- Keep responses concise but warm (not too long)
- Use gentle emoji occasionally to add warmth 🌟💚
- Ask follow-up questions to show you care
- Remember context from the conversation

Remember: You are NOT a replacement for professional help, but a supportive first step 
and a safe space for students to express themselves.
"""

# 1. Secure API Key Input
if "app_key" not in st.session_state:
    app_key = st.text_input("Please enter your Gemini API Key", type='password')
    if app_key:
        st.session_state.app_key = app_key
        st.rerun()

# 2. Initialize Session State for History
if "history" not in st.session_state:
    st.session_state.history = []

# 3. Model Initialization (Only if Key exists)
if "app_key" in st.session_state:
    try:
        genai.configure(api_key=st.session_state.app_key)
        
        # Initialize model with system instruction for mental health support
        model = genai.GenerativeModel(
            model_name="gemini-2.5-flash",
            system_instruction=SYSTEM_INSTRUCTION,
            generation_config={
                "temperature": 0.8,
                "top_p": 0.95,
                "max_output_tokens": 1024,
            }
        )
        chat = model.start_chat(history=st.session_state.history)
        
        # Sidebar Options
        with st.sidebar:
            st.header("🧘 Quick Relaxation Tips")
            
            with st.expander("🌬️ Deep Breathing (4-7-8)"):
                st.write("""
                1. Breathe in for **4 seconds**
                2. Hold for **7 seconds**  
                3. Exhale for **8 seconds**
                4. Repeat 3-4 times
                """)
            
            with st.expander("🌍 Grounding (5-4-3-2-1)"):
                st.write("""
                Notice around you:
                - **5** things you can see
                - **4** things you can touch
                - **3** things you can hear
                - **2** things you can smell
                - **1** thing you can taste
                """)
            
            with st.expander("💪 Quick Stress Relief"):
                st.write("""
                - Take 5 slow, deep breaths
                - Roll your shoulders back
                - Stretch your arms overhead
                - Drink a glass of water
                - Step outside for 2 minutes
                """)
            
            with st.expander("📞 Crisis Resources"):
                st.write("""
                **India:**
                - iCall: 9152987821
                - Vandrevala Foundation: 1860-2662-345
                - NIMHANS: 080-46110007
                
                **International:**
                - Crisis Text Line: Text HOME to 741741
                - Check your campus counseling center
                """)
            
            st.divider()
            
            if st.button("🔄 Clear Chat", use_container_width=True, type="primary"):
                st.session_state.history = []
                st.rerun()

        # Welcome message for new users
        if not st.session_state.history:
            with st.chat_message("assistant"):
                st.markdown("""
                Hey there! 👋 I'm your Student Wellness Companion. 
                
                I'm here to listen, support, and chat with you about anything on your mind - 
                whether it's stress, studies, or just wanting someone to talk to.
                
                **How are you feeling today?** 💚
                """)

        # Display Chat History
        for message in st.session_state.history:
            role = "assistant" if message.role == 'model' else message.role
            with st.chat_message(role):
                st.markdown(message.parts.text)

        # Chat Input logic
        if prompt := st.chat_input("Share what's on your mind..."):
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                def stream_generator():
                    response = chat.send_message(prompt, stream=True)
                    for chunk in response:
                        yield chunk.text

                full_response = st.write_stream(stream_generator())
            
            # Update session state history
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"An error occurred: {e}")
        
else:
    st.info("🔑 Please enter your API Key above to start chatting.")
    st.markdown("""
    ### About This App
    This is a **safe space** for students to:
    - 💬 Talk about stress, anxiety, or loneliness
    - 🧘 Get relaxation techniques and coping strategies
    - 💪 Receive motivational support
    - 📚 Ask general questions too!
    
    *Your conversations are private and not stored permanently.*
    
    ---
    **⚠️ Disclaimer:** This chatbot is not a replacement for professional mental health care. 
    If you're in crisis, please reach out to a counselor or helpline.
    """)
