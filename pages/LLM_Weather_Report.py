import streamlit as st
import requests
from datetime import date, timedelta
from google import genai

st.set_page_config(page_title="AI Weather Report", page_icon="📝", layout="centered")
st.title("📝 AI‑Generated Weather Report")

# --- API KEY ---
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except Exception:
    st.error("Missing Gemini API key.")
    st.stop()

client = genai.Client(api_key=api_key)

# --- USER INPUTS ---
st.subheader("Report Settings")
city = st.text_input("City", value="Atlanta")
days_back = st.slider("Number of past days to summarize", 3, 7, 3)
tone = st.selectbox("Writing Style", ["Informative", "Friendly", "Professional Forecast"])

# --- GEOCODING ---
geo_url = "https://geocoding-api.open-meteo.com/v1/search"
geo = requests.get(geo_url, params={"name": city, "count": 1}).json()

if geo.get("results") is None:
    st.error("City not found.")
    st.stop()

loc = geo["results"][0]
lat, lon = loc["latitude"], loc["longitude"]
place = f"{loc['name']}, {loc.get('country','')}"

# --- DATE RANGE ---
end = date.today()
start = end - timedelta(days=days_back)

# --- FETCH WEATHER DATA ---
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

temps = data["hourly"]["temperature_2m"]
winds = data["hourly"]["wind_speed_10m"]

avg_temp = round(sum(temps) / len(temps), 1)
max_temp = round(max(temps), 1)
avg_wind = round(sum(winds) / len(winds), 1)

# --- BUTTON ---
if st.button("Generate Weather Report"):
    prompt = (
        "You are a student‑friendly weather report writer.\n"
        "Do not claim real‑time accuracy.\n\n"
        f"Location: {place}\n"
        f"Date Range: {start} to {end}\n"
        f"Average Temperature: {avg_temp}°C\n"
        f"Maximum Temperature: {max_temp}°C\n"
        f"Average Wind Speed: {avg_wind} m/s\n\n"
        f"Write a {tone.lower()} weather report that summarizes conditions "
        "and briefly suggests appropriate activities or precautions."
    )

    try:
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=prompt
        )
        st.subheader("📄 Generated Report")
        st.write(response.text)
    except Exception:
        st.error("Error generating report.")
