import streamlit as st
import google.generativeai as genai
import os

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="AI Weather Chatbot", page_icon="💬", layout="wide")

st.title("💬 AI Weather Chatbot")
st.caption("Ask general weather questions powered by Google Gemini.")

# Sidebar inputs (≥ 2 interactions)
with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")
    units = st.radio("Units", ["Metric", "Imperial"])

# Configure Gemini
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel("gemini-pro")

# Chat memory (REQUIRED)
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

st.subheader("Chat")
user_input = st.text_input("Ask a weather-related question:")

if st.button("Ask"):
    if user_input.strip():
        prompt = f"""
        You are a helpful weather assistant.
        Location: {city}
        Units: {units}
        Question: {user_input}
        Provide general weather advice without real-time data.
        """
        try:
            response = model.generate_content(prompt)
            st.session_state.chat_history.append(("You", user_input))
            st.session_state.chat_history.append(("AI", response.text))
        except Exception as e:
            st.error(f"AI Error: {e}")

# Display conversation
for speaker, msg in st.session_state.chat_history:
    st.markdown(f"**{speaker}:** {msg}")
