import streamlit as st
import requests
from datetime import date, timedelta
from google import genai

st.set_page_config(page_title="Weather Chatbot Pro", page_icon="💬")
st.title("💬 Weather Chatbot (API‑Powered)")

# --- API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing Gemini API key.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- USER INPUT ---
city = st.text_input("City for weather context", value="Atlanta")

# --- GEOCODE ---
geo_url = "https://geocoding-api.open-meteo.com/v1/search"
geo = requests.get(geo_url, params={"name": city, "count": 1}).json()

if geo.get("results") is None:
    st.error("City not found.")
    st.stop()

loc = geo["results"][0]
lat, lon = loc["latitude"], loc["longitude"]
place = f"{loc['name']}, {loc.get('country','')}"

# --- WEATHER DATA ---
end = date.today()
start = end - timedelta(days=3)

weather_url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["temperature_2m", "wind_speed_10m"],
    "start_date": start.isoformat(),
    "end_date": end.isoformat(),
    "temperature_unit": "celsius",
    "wind_speed_unit": "ms",
    "timezone": "auto",
}

data = requests.get(weather_url, params=params).json()

avg_temp = round(sum(data["hourly"]["temperature_2m"]) / len(data["hourly"]["temperature_2m"]), 1)
max_wind = round(max(data["hourly"]["wind_speed_10m"]), 1)

# --- CHAT HISTORY ---
if "messages" not in st.session_state:
    st.session_state.messages = [{
        "role": "assistant",
        "content": "Hi! Ask me weather‑related questions using recent data."
    }]

for m in st.session_state.messages:
    with st.chat_message(m["role"]):
        st.write(m["content"])

# --- CHAT INPUT ---
user_input = st.chat_input("Ask a weather question...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})

    context = (
        f"Recent weather data for {place}:\n"
        f"- Average temperature: {avg_temp}°C\n"
        f"- Maximum wind speed: {max_wind} m/s\n"
        "Data is historical, not live.\n"
    )

    conversation = ""
    for msg in st.session_state.messages:
        conversation += f"{msg['role']}: {msg['content']}\n"

    prompt = (
        "You are a helpful weather chatbot for a CS 1301 project.\n"
        "Only answer weather‑related questions.\n"
        "Be clear and student‑appropriate.\n\n"
        f"{context}\n"
        f"Conversation:\n{conversation}"
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        bot_reply = response.text
    except Exception:
        bot_reply = "Sorry, I had trouble answering that."

    st.session_state.messages.append({"role": "assistant", "content": bot_reply})
    with st.chat_message("assistant"):
        st.write(bot_reply)
