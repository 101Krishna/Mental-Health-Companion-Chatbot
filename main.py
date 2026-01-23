import streamlit as st
from google import genai
from google.genai import types

# Page Config
st.set_page_config(
    page_title="Student Wellness Companion",
    page_icon="🌱",
)

st.title("🌱 Student Wellness Companion")
st.caption("A supportive AI chat for students – powered by Gemini 2.5 Flash")

# System Instruction for Mental Health Support
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

# Session State
if "app_key" not in st.session_state:
    app_key = st.text_input("Please enter your Gemini API Key", type="password")
    if app_key:
        st.session_state.app_key = app_key
        st.rerun()

if "history" not in st.session_state:
    st.session_state.history = []

# Main App
if "app_key" in st.session_state:
    try:
        # Initialize client with new SDK
        client = genai.Client(api_key=st.session_state.app_key)

        # Create chat session
        chat = client.chats.create(
            model="gemini-2.5-flash",
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                top_p=0.95,
                max_output_tokens=1024,
            ),
            history=st.session_state.history,
        )

        # Sidebar
        with st.sidebar:
            st.header("🧘 Quick Relaxation Tips")

            with st.expander("Deep Breathing (4-7-8)"):
                st.write("""
                1. Inhale for **4 seconds**
                2. Hold for **7 seconds**
                3. Exhale for **8 seconds**
                4. Repeat 3-4 times
                """)

            with st.expander("Grounding (5-4-3-2-1)"):
                st.write("""
                Notice around you:
                - **5** things you can see
                - **4** things you can touch
                - **3** things you can hear
                - **2** things you can smell
                - **1** thing you can taste
                """)

            with st.expander("📞 Crisis Resources"):
                st.write("""
                - **988** - Suicide & Crisis Lifeline (US)
                - **iCall**: 9152987821 (India)
                - **Vandrevala Foundation**: 1860-2662-345
                - Contact your campus counseling center
                """)

            st.divider()

            if st.button("🔄 Clear Chat", use_container_width=True, type="primary"):
                st.session_state.history = []
                st.rerun()

        # Welcome message
        if not st.session_state.history:
            with st.chat_message("assistant"):
                st.markdown("""
                Hey there! 👋 I'm your Student Wellness Companion.

                This is a safe space to talk about stress, studies, loneliness,
                or anything else on your mind.

                **How are you feeling today?** 💚
                """)

        # Display chat history
        for message in st.session_state.history:
            role = "assistant" if message.role == "model" else message.role
            text = ""
            if hasattr(message, "parts") and message.parts:
                if hasattr(message.parts[0], "text"):
                    text = message.parts[0].text
            if text:
                with st.chat_message(role):
                    st.markdown(text)

        # Chat input
        if prompt := st.chat_input("Share what's on your mind..."):
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                def stream_generator():
                    response = chat.send_message_stream(prompt)
                    for chunk in response:
                        if chunk.text:
                            yield chunk.text

                st.write_stream(stream_generator())

            # Update history
            st.session_state.history = chat.get_history()

    except Exception as e:
        st.error(f"An error occurred: {e}")

else:
    st.info("🔑 Please enter your API Key above to start chatting.")
    st.markdown("""
    ### About This App
    A **safe space** for students to:
    - 💬 Talk about stress, anxiety, or loneliness
    - 🧘 Get relaxation techniques
    - 💪 Receive motivational support
    - 📚 Ask general questions too!
    """)
