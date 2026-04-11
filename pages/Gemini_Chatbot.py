import streamlit as st
import google.generativeai as genai
import os

# MUST be first Streamlit call
st.set_page_config(page_title="AI Weather Chatbot", page_icon="💬", layout="wide")

st.title("💬 AI Weather Chatbot")
st.caption("Ask general weather-related questions (Metric units).")

# Sidebar input
with st.sidebar:
    city = st.text_input("City / Place", value="Atlanta")

# ✅ Fail fast if API key missing
api_key = st.secrets["GEMINI_API_KEY"]
if not api_key:
    st.error("GEMINI_API_KEY not found. Set it as an environment variable.")
    st.stop()

genai.configure(api_key=api_key)

# ✅ Use fast, reliable model
model = genai.GenerativeModel("gemini-pro")

# Chat memory
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

user_input = st.text_input("Ask a weather-related question:")

if st.button("Ask"):
    if user_input.strip():
        prompt = f"""
You are a helpful weather assistant.
Location: {city}
Units: Metric (°C, m/s)
Question: {user_input}
Give general guidance without real-time data.
"""
        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", response.text))
        except Exception as e:
            st.error(f"Actual error: {e}")
    else:
        st.warning("Please enter a question.")

# Display chat
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
