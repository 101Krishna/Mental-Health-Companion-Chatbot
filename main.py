import streamlit as st
import requests

# -------------------- CONFIG --------------------

st.set_page_config(
    page_title="Student Wellness Companion",
    page_icon="🌱",
    layout="centered",
)

API_URL = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent"

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

# -------------------- HELPERS --------------------

def call_gemini(api_key: str, history, user_message: str) -> str:
    """
    Call the Gemini REST API directly using requests.
    history: list of {"role": "user"|"assistant", "content": str}
    user_message: latest user input
    """
    # Build contents for the API from chat history
    contents = []

    # Add system instruction as a "hidden" first message
    contents.append({
        "role": "user",
        "parts": [{"text": SYSTEM_INSTRUCTION.strip()}],
    })

    # Add previous conversation
    for msg in history:
        role = "user" if msg["role"] == "user" else "model"
        contents.append({
            "role": role,
            "parts": [{"text": msg["content"]}],
        })

    # Add the latest user message
    contents.append({
        "role": "user",
        "parts": [{"text": user_message}],
    })

    payload = {
        "contents": contents
        # You can add "generationConfig" here if you want to tune temperature, etc.
    }

    try:
        resp = requests.post(
            f"{API_URL}?key={api_key}",
            headers={"Content-Type": "application/json"},
            json=payload,
            timeout=30,
        )
        resp.raise_for_status()
    except requests.exceptions.HTTPError as e:
        # Try to show useful error info from the API
        try:
            err = resp.json()
            msg = err.get("error", {}).get("message", str(e))
        except Exception:
            msg = str(e)
        raise RuntimeError(f"Gemini API error: {msg}") from e
    except Exception as e:
        raise RuntimeError(f"Request failed: {e}") from e

    data = resp.json()

    # Extract text from the first candidate
    try:
        candidates = data.get("candidates", [])
        if not candidates:
            raise RuntimeError("No candidates returned from API")
        parts = candidates[0]["content"]["parts"]
        text = "".join(part.get("text", "") for part in parts)
        return text.strip()
    except Exception as e:
        raise RuntimeError(f"Unexpected API response format: {e}\nFull response: {data}") from e


# -------------------- SESSION STATE INIT --------------------

if "messages" not in st.session_state:
    st.session_state.messages = []

if "api_key" not in st.session_state:
    st.session_state.api_key = None

# -------------------- UI: TITLE & SIDEBAR --------------------

st.title("🌱 Student Wellness Companion")
st.caption("A supportive AI chat for students – powered by Gemini (via REST API)")

with st.sidebar:
    st.header("🧘 Quick Relaxation Tips")

    with st.expander("Deep Breathing (4-7-8)"):
        st.write(
            "1. Inhale for **4 seconds**\n"
            "2. Hold for **7 seconds**\n"
            "3. Exhale for **8 seconds**\n"
            "4. Repeat 3–4 times"
        )

    with st.expander("Grounding (5-4-3-2-1)"):
        st.write(
            "Notice around you:\n"
            "- **5** things you can see\n"
            "- **4** things you can touch\n"
            "- **3** things you can hear\n"
            "- **2** things you can smell\n"
            "- **1** thing you can taste"
        )

    with st.expander("📞 Crisis Resources"):
        st.write(
            "**If you're in immediate danger, please contact local emergency services.**\n\n"
            "- 🇺🇸 **988** – Suicide & Crisis Lifeline (US)\n"
            "- 🇮🇳 **iCall**: 9152987821 (India)\n"
            "- 🇮🇳 **Vandrevala Foundation**: 1860-2662-345\n"
            "- 🇬🇧 **116 123** – Samaritans (UK)\n"
            "- 🌐 More: https://findahelpline.com\n"
            "- Or reach out to your campus counseling center 💚"
        )

    st.divider()

    if st.button("🔄 Clear Chat", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    if st.button("🔑 Reset API Key", use_container_width=True):
        st.session_state.api_key = None
        st.session_state.messages = []
        st.rerun()

    st.markdown(
        "<hr><p style='font-size:11px;color:gray;text-align:center;'>"
        "This app is not a substitute for professional help."
        "</p>",
        unsafe_allow_html=True,
    )

# -------------------- API KEY ENTRY --------------------

if not st.session_state.api_key:
    st.markdown("### 🔑 Enter Your Gemini API Key")

    key = st.text_input(
        "API Key",
        type="password",
        placeholder="Paste your Gemini API key here...",
        help="Get one at https://aistudio.google.com/app/apikey",
    )

    if st.button("Connect", type="primary"):
        if not key:
            st.warning("Please enter an API key.")
        else:
            # We can't fully validate without calling the API, but we save it.
            st.session_state.api_key = key
            st.success("API key saved. You can start chatting now.")
            st.rerun()

    st.stop()

# -------------------- CHAT UI --------------------

# Initial assistant message
if not st.session_state.messages:
    st.session_state.messages.append({
        "role": "assistant",
        "content": (
            "Hey there! 👋 I'm your **Student Wellness Companion**.\n\n"
            "This is a safe space to talk about stress, studies, friendships, "
            "or anything else on your mind.\n\n"
            "**How are you feeling today?** 💚"
        ),
    })

# Display chat history
for msg in st.session_state.messages:
    avatar = "😊" if msg["role"] == "user" else "🌱"
    with st.chat_message(msg["role"], avatar=avatar):
        st.markdown(msg["content"])

# Input box
if prompt := st.chat_input("Share what's on your mind..."):
    # Add user message
    st.session_state.messages.append({"role": "user", "content": prompt})

    with st.chat_message("user", avatar="😊"):
        st.markdown(prompt)

    # Call Gemini via REST
    with st.chat_message("assistant", avatar="🌱"):
        with st.spinner("Thinking with care..."):
            try:
                reply = call_gemini(
                    api_key=st.session_state.api_key,
                    history=st.session_state.messages[:-1],  # all previous messages
                    user_message=prompt,
                )
            except Exception as e:
                st.error(str(e))
                reply = "I'm having trouble responding right now. Could you try again in a moment?"

            st.markdown(reply)

    # Save assistant reply
    st.session_state.messages.append({"role": "assistant", "content": reply})
