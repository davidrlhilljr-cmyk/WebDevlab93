import streamlit as st
import google.generativeai as genai
import os

st.set_page_config(page_title="AI Weather Chatbot", page_icon="💬", layout="wide")

st.title("💬 AI Weather Chatbot")
st.caption("Ask general weather‑related questions (Metric units: °C, m/s).")

# Sidebar inputs (≥ 2 interactions REQUIRED)
with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# ✅ Chat memory (REQUIRED)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("Chat")
st.info("Responses may take a few seconds due to external AI service latency.")

user_input = st.text_input("Ask a weather‑related question:")

if st.button("Ask"):
    if user_input.strip():
        prompt = f"""
        You are a helpful AI weather assistant.
        Location: {city}
        Units: Metric (°C, m/s)
        Question: {user_input}
        Provide general weather advice without using real‑time data.
        """
        try:
            with st.spinner("Thinking..."):
                response = model.generate_content(prompt)
                st.session_state.chat_history.append(("You", user_input))
                st.session_state.chat_history.append(("AI", response.text))
        except Exception as e:
            st.error(f"AI Error: {e}")

# Display conversation history
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
    st.markdown(f"**{speaker}:** {msg}")
