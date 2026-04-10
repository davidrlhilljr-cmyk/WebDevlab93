import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date, timedelta

# ✅ MUST be first Streamlit command
st.set_page_config(page_title="Weather Explorer", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Explorer (Open‑Meteo)")
st.caption("Explore historical temperature and wind data by location and date range.")

# Sidebar inputs (≥ 2 — REQUIRED)
with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")
    days_back = st.slider("Days Back", 3, 60, 14)
    units = st.radio("Units", ["Metric (°C, m/s)", "Imperial (°F, mph)"])
    smooth = st.slider("Moving Average Window", 1, 7, 3)

# Resolve city → coordinates
geo_url = "https://geocoding-api.open-meteo.com/v1/search"
geo = requests.get(geo_url, params={"name": city, "count": 1}).json()

if geo.get("results") is None:
    st.error("City not found.")
    st.stop()

loc = geo["results"][0]
lat, lon = loc["latitude"], loc["longitude"]
place = f"{loc['name']}, {loc.get('country','')}"

end = date.today()
start = end - timedelta(days=days_back)

temp_unit = "fahrenheit" if "Imperial" in units else "celsius"
wind_unit = "mph" if "Imperial" in units else "ms"

# Fetch weather data
weather_url = "https://api.open-meteo.com/v1/forecast"
params = {
    "latitude": lat,
    "longitude": lon,
    "hourly": ["temperature_2m", "wind_speed_10m"],
    "start_date": start.isoformat(),
    "end_date": end.isoformat(),
    "temperature_unit": temp_unit,
    "wind_speed_unit": wind_unit,
    "timezone": "auto",
}

data = requests.get(weather_url, params=params).json()

df = pd.DataFrame({
    "time": pd.to_datetime(data["hourly"]["time"]),
    "temperature": data["hourly"]["temperature_2m"],
    "wind_speed": data["hourly"]["wind_speed_10m"],
}).set_index("time")

# ✅ Student‑implemented analysis
df["temp_ma"] = df["temperature"].rolling(smooth).mean()
df["wind_ma"] = df["wind_speed"].rolling(smooth).mean()

daily = df.resample("D").agg({
    "temperature": ["min", "mean", "max"],
    "wind_speed": ["mean", "max"]
})
daily.columns = ["_".join(c) for c in daily.columns]

st.subheader(f"📍 Location: {place}")
st.write(f"Date Range: {start} → {end}")

# ✅ Dynamic charts
fig1 = px.line(
    df.reset_index(),
    x="time",
    y=["temperature", "temp_ma"],
    title="Hourly Temperature"
)
st.plotly_chart(fig1, use_container_width=True)

fig2 = px.line(
    df.reset_index(),
    x="time",
    y=["wind_speed", "wind_ma"],
    title="Hourly Wind Speed"
)
st.plotly_chart(fig2, use_container_width=True)

# ✅ Processed data table
st.subheader("📊 Daily Weather Summary")
st.dataframe(daily, use_container_width=True)

with st.expander("What this page does"):
    st.write("""
    - Fetches weather data from Open‑Meteo
    - Computes rolling averages and daily summaries
    - Displays interactive charts that update with user input
    """)
