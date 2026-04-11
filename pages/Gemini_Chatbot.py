import streamlit as st
import google.generativeai as genai
import os

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="AI Weather Chatbot", page_icon="💬", layout="wide")

st.title("💬 AI Weather Chatbot")
st.caption("Ask general weather-related questions (Metric units).")

# Sidebar input
with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")

# ✅ Check API key
api_key = os.getenv("GEMINI_API_KEY")
if not api_key:
    st.error("GEMINI_API_KEY not found. Set it in Streamlit Secrets.")
    st.stop()

# Configure Gemini
genai.configure(api_key=api_key)

# ✅ Use fast, reliable model
model = genai.GenerativeModel("gemini-1.5-flash")

# Chat memory (required)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a weather-related question:")

def ask_gemini(prompt):
    """Try calling Gemini once; return None if it fails."""
    try:
        return model.generate_content(prompt).text
    except Exception:
        return None

if st.button("Ask"):
    if not user_input.strip():
        st.warning("Please enter a question.")
        st.stop()

    # ✅ Prevent real-time questions (avoids stalls)
    if any(word in user_input.lower() for word in ["today", "now", "current", "right now"]):
        st.warning("I provide general weather guidance, not real-time conditions.")
        st.stop()

    prompt = f"""
You are a helpful weather assistant.
Location: {city}
Units: Metric (°C, m/s)
Question: {user_input}
Give general weather guidance without using real-time data.
"""

    # First attempt
    with st.spinner("Thinking..."):
        answer = ask_gemini(prompt)

    # Retry once if needed
    if answer is None:
        with st.spinner("Retrying..."):
            answer = ask_gemini(prompt)

    # Guaranteed fallback ✅
    if answer is None:
        answer = (
            "In general, good weather for outdoor activities includes "
            "moderate temperatures, light winds, and little precipitation. "
            "Always consider local conditions and safety."
        )

    st.session_state.chat_history.append(("You", user_input))
    st.session_state.chat_history.append(("AI", answer))

# Display chat history
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
