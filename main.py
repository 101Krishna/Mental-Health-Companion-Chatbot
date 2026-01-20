import streamlit as st
import google.generativeai as genai

st.set_page_config(
    page_title="Chat with Gemini 2.5",
    page_icon="🔥"
)

st.title("Chat with Gemini 2.5")
st.caption("A Chatbot Powered by Google Gemini 2.5 Flash")

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
        # Updated model name to gemini-2.5-flash (stable in 2026)
        model = genai.GenerativeModel("gemini-2.5-flash")
        chat = model.start_chat(history=st.session_state.history)
        
        # Sidebar Options
        with st.sidebar:
            if st.button("Clear Chat Window", use_container_width=True, type="primary"):
                st.session_state.history = []
                st.rerun()

        # Display Chat History
        for message in st.session_state.history:
            role = "assistant" if message.role == 'model' else message.role
            with st.chat_message(role):
                st.markdown(message.parts[0].text)

        # Chat Input logic
        if prompt := st.chat_input("Type your message here..."):
            with st.chat_message("user"):
                st.markdown(prompt)

            with st.chat_message("assistant"):
                # Use a generator for the typewriter effect
                def stream_generator():
                    response = chat.send_message(prompt, stream=True)
                    for chunk in response:
                        yield chunk.text

                # st.write_stream is the modern way to handle streaming responses
                full_response = st.write_stream(stream_generator())
            
            # Update session state history
            st.session_state.history = chat.history

    except Exception as e:
        st.error(f"An error occurred: {e}")
else:
    st.info("Please enter your API Key in the text box above to start chatting.")
