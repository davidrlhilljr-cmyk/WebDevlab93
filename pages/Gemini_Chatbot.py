import streamlit as st
from google import genai

st.title("Weather Chatbot")
st.write("Ask general weather related questions, packing questions, or activity ideas.")

#API KEY SHENANAGIS

try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing Gemini API key. Add GEMINI_API_KEY to your streamlit secerets.")
    st.stop()

client = genai.Client(api_key=api_key)


if"messages" not in st.session_state:
    st.session_state.messages = [{"role":"assistant",
                                  "content":"Hi! I'm your weather chatbot. Ask me about packing, weather safety, outdoor activities, or general weather questions."}]

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.write(message["content"])


user_input = st.chat_input("Type your message here...")

if user_input:
    st.session_state.messages.append({"role":"user","content": user_input})
    with st.chat_message("user"):
        st.write(user_input)
    try:
        conversation_text = ""
        for msg in st.session_state.messages:
            conversation_text += f"{msg['role']}: {msg['content']}\n"

        prompt = (
            "You are a helpful weather-themed chatbot for a CS 1301 Streamlit project. "
            "Answer clearly and briefly. Stay school-appropriate. "
            "Do not claim to know live weather data. "
            "You can help with packing advice, weather safety, seasonal clothing, "
            "and indoor/outdoor activity suggestions.\n\n"
            f"Conversation so far:\n{conversation_text}\n"
            f"User: {user_input}")
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt)
        bot_reply = response.text if response.text else "Sorry, I could not generate a response."

    except Exception:
        bot_reply = "Sorry, I ran into an error while generating a response. Please try again."

    st.session_state.messages.append({"role":"assistant","content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
