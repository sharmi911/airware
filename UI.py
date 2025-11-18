import streamlit as st
import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# -----------------------------------
# Helper — Random Data Generator
# -----------------------------------
def random_data(n, min_val=40, max_val=120):
    return np.random.randint(min_val, max_val, size=n)

# -----------------------------------
# PAGE SETTINGS
# -----------------------------------
st.set_page_config(
    page_title="AirAware - Smart AQI Dashboard",
    layout="wide",
)

st.title("AirAware — Smart AQI Prediction (India)")

# -----------------------------------
# SIDEBAR
# -----------------------------------
states = [
    "Andhra Pradesh","Arunachal Pradesh","Assam","Bihar","Chhattisgarh",
    "Goa","Gujarat","Haryana","Himachal Pradesh","Jharkhand","Karnataka",
    "Kerala","Madhya Pradesh","Maharashtra","Manipur","Meghalaya","Mizoram",
    "Nagaland","Odisha","Punjab","Rajasthan","Sikkim","Tamil Nadu",
    "Telangana","Tripura","Uttar Pradesh","Uttarakhand","West Bengal"
]

state = st.sidebar.selectbox("Select State", states)

st.sidebar.header("Navigation")
st.sidebar.button("Home")
st.sidebar.button("Hourly AQI")
st.sidebar.button("Daily AQI")
st.sidebar.button("Monthly AQI")
st.sidebar.button("Prediction")

st.sidebar.markdown("---")
st.sidebar.error("Logout")

# -----------------------------------
# AQI SUMMARY
# -----------------------------------
col1, col2 = st.columns(2)

with col1:
    st.subheader("AQI Summary")
    minAQI = random_data(1)[0]
    currAQI = random_data(1)[0]
    maxAQI = random_data(1)[0]

    st.write(f"**Min AQI:** {minAQI}")
    st.write(f"**Current AQI:** {currAQI}")
    st.write(f"**Max AQI:** {maxAQI}")

# -----------------------------------
# POLLUTANT COMPOSITION PIE CHART
# -----------------------------------
with col2:
    st.subheader("Pollutant Composition")

    pollutants = ["PM2.5", "CO2", "NO2", "SO2"]
    values = random_data(4)

    fig_pie = px.pie(
        names=pollutants,
        values=values,
        color_discrete_sequence=["#0099cc", "#33cc33", "#ff9933", "#ff6666"]
    )
    st.plotly_chart(fig_pie, use_container_width=True)

# -----------------------------------
# HOURLY AQI (24 HR)
# -----------------------------------
st.subheader("Hourly AQI (Last 24 Hours)")

hours = [f"{h}:00" for h in range(24)]
hourly_values = random_data(24)

fig_hourly = go.Figure()
fig_hourly.add_trace(go.Scatter(
    x=hours,
    y=hourly_values,
    mode="lines+markers",
    line=dict(color="#0088aa"),
    name="AQI"
))

st.plotly_chart(fig_hourly, use_container_width=True)

# -----------------------------------
# PREDICTION CHART (NOW / 1 YEAR / 5 YEARS)
# -----------------------------------
st.subheader("Prediction (Now / 1Y / 5Y)")

labels = ["Now", "1 Year", "5 Years"]
values = [72, 90, 118]

fig_pred = px.bar(
    x=labels,
    y=values,
    color=labels,
    color_discrete_sequence=["#0077aa", "#33c3ff", "#ffcc00"],
    labels={"x": "", "y": "AQI"}
)

st.plotly_chart(fig_pred, use_container_width=True)

# -----------------------------------
# 5-YEAR TREND AREA CHART
# -----------------------------------
st.subheader("Past 5 Years — Trend (Area)")

years = ["2019", "2020", "2021", "2022", "2023"]
trend = [60, 80, 95, 110, 125]

fig_area = go.Figure()
fig_area.add_trace(go.Scatter(
    x=years,
    y=trend,
    fill='tozeroy',
    name="AQI Trend",
    line=dict(color="#0099cc"),
    fillcolor="rgba(0,150,200,0.3)"
))

st.plotly_chart(fig_area, use_container_width=True)