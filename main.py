import streamlit as st
import sys
import pkgutil

st.set_page_config(page_title="Student Wellness Companion", page_icon="🌱")
st.title("🌱 Student Wellness Companion")
st.caption("A supportive AI chat for students – powered by Gemini")

# ---------- Debug / Diagnostics ----------
with st.expander("Debug: Environment & Imports (open if you see import errors)"):
    st.write("Python:", sys.version)

    # Show installed top-level google-related packages
    google_like = sorted([m.name for m in pkgutil.iter_modules() if m.name.startswith("google")])
    st.write("Top-level modules starting with 'google':")
    st.code("\n".join(google_like) if google_like else "(none found)")

# ---------- System instruction ----------
SYSTEM_INSTRUCTION = """
You are a compassionate and supportive AI companion designed specifically for students.

- Infer mood (stress/anxiety/loneliness/sadness/overwhelm) from messages.
- Respond with empathy first, then gentle motivation.
- When appropriate, offer short, practical coping tips (breathing, grounding, breaks).
- If user mentions self-harm/suicide/immediate danger: respond seriously and encourage
  contacting local emergency services or crisis lines (US: call/text 988).
- For non-mental-health questions, answer normally and helpfully.
"""

# ---------- API key ----------
if "app_key" not in st.session_state:
    key = st.text_input("Enter Gemini API Key", type="password")
    if key:
        st.session_state.app_key = key
        st.rerun()

if "messages" not in st.session_state:
    st.session_state.messages = []

if "app_key" not in st.session_state:
    st.info("🔑 Please enter your API key to start.")
    st.stop()

# ---------- Import google-genai (this is where your ImportError happens) ----------
try:
    from google import genai
    from google.genai import types
except Exception as e:
    st.error("Failed to import the Google GenAI SDK.")
    st.code(str(e))
    st.markdown(
        """
**Fix checklist (Streamlit Cloud):**
1. Ensure `requirements.txt` includes **google-genai** (not google-generativeai).
2. Commit + push to GitHub.
3. In Streamlit Cloud: **Manage app → Clear cache → Reboot app**.
4. Verify `requirements.txt` is at repo root (same level as `main.py`).
"""
    )
    st.stop()

# ---------- Build client ----------
client = genai.Client(api_key=st.session_state.app_key)

# ---------- Sidebar ----------
with st.sidebar:
    st.header("🧘 Quick Relaxation Tips")
    with st.expander("4-7-8 breathing"):
        st.write("Inhale 4s • hold 7s • exhale 8s • repeat 3–4 rounds.")
    with st.expander("5-4-3-2-1 grounding"):
        st.write("5 see • 4 touch • 3 hear • 2 smell • 1 taste")
    if st.button("Clear chat", use_container_width=True, type="primary"):
        st.session_state.messages = []
        st.rerun()

# ---------- Display history ----------
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown("Hey — I’m here with you. How are you feeling today? 💚")

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.markdown(m["content"])

# ---------- Chat input ----------
prompt = st.chat_input("Share what's on your mind...")
if prompt:
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Convert our history into API contents
    contents = []
    for m in st.session_state.messages:
        role = "user" if m["role"] == "user" else "model"
        contents.append(
            types.Content(
                role=role,
                parts=[types.Part.from_text(text=m["content"])]
            )
        )

    with st.chat_message("assistant"):
        stream = client.models.generate_content_stream(
            model="gemini-2.5-flash",
            contents=contents,
            config=types.GenerateContentConfig(
                system_instruction=SYSTEM_INSTRUCTION,
                temperature=0.8,
                top_p=0.95,
                max_output_tokens=800,
            ),
        )

        full = st.write_stream(chunk.text for chunk in stream if getattr(chunk, "text", None))

    st.session_state.messages.append({"role": "assistant", "content": full})
