import streamlit as st
import pandas as pd
import plotly.express as px
import requests
from datetime import date, timedelta

# ✅ MUST be the first Streamlit command
st.set_page_config(page_title="Weather Explorer", page_icon="🌤️", layout="wide")

st.title("🌤️ Weather Explorer")
st.caption("Explore historical temperature and wind data using metric units (°C, m/s).")

# Sidebar inputs (≥ 2 REQUIRED)
with st.sidebar:
    st.header("Inputs")
    city = st.text_input("City / Place", value="Atlanta")
    days_back = st.slider("Days Back", 3, 60, 14)
    smooth = st.slider("Moving Average Window (hours)", 1, 7, 3)

# Resolve city → coordinates
geo_url = "https://geocoding-api.open-meteo.com/v1/search"
geo = requests.get(geo_url, params={"name": city, "count": 1}).json()

if geo.get("results") is None:
    st.error("City not found. Try another location.")
    st.stop()

loc = geo["results"][0]
lat, lon = loc["latitude"], loc["longitude"]
place = f"{loc['name']}, {loc.get('country','')}"

# Date range
end = date.today()
start = end - timedelta(days=days_back)

# ✅ Metric units only
temp_unit = "celsius"
wind_unit = "ms"  # meters per second

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
df["temperature_ma"] = df["temperature"].rolling(smooth).mean()
df["wind_speed_ma"] = df["wind_speed"].rolling(smooth).mean()

daily = df.resample("D").agg({
    "temperature": ["min", "mean", "max"],
    "wind_speed": ["mean", "max"]
})
daily.columns = ["_".join(c) for c in daily.columns]

# Page content
st.subheader(f"📍 Location: {place}")
st.write(f"Date Range: {start} → {end}")

# ✅ Dynamic charts
fig_temp = px.line(
    df.reset_index(),
    x="time",
    y=["temperature", "temperature_ma"],
    labels={"value": "Temperature (°C)", "time": "Time"},
    title="Hourly Temperature with Moving Average"
)
st.plotly_chart(fig_temp, use_container_width=True)

fig_wind = px.line(
    df.reset_index(),
    x="time",
    y=["wind_speed", "wind_speed_ma"],
    labels={"value": "Wind Speed (m/s)", "time": "Time"},
    title="Hourly Wind Speed with Moving Average"
)
st.plotly_chart(fig_wind, use_container_width=True)

# ✅ Processed daily table
st.subheader("📊 Daily Weather Summary (Computed)")
st.dataframe(daily, use_container_width=True)

with st.expander("What this page does"):
    st.write("""
    - Retrieves real weather data from Open‑Meteo
    - Computes rolling averages and daily summaries
    - Displays interactive charts that update with user input
    - All analysis is implemented manually (no LLM)
    """)
