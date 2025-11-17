# single-file Streamlit UI for AirAware dashboard with custom CSS
# Save as: src/dashboard/app_ui_only.py
# Run: streamlit run src/dashboard/app_ui_only.py
#
# This file contains only UI + styling + synthetic sample data so you can run it as-is.

import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import plotly.graph_objects as go
import plotly.express as px
import os

st.set_page_config(layout="wide", page_title="AirAware — Smart AQ Prediction (UI)")

# -------------------------
# Embedded CSS to match screenshot-like teal left menu + modern cards
# -------------------------
st.markdown(
    """
    <style>
    /* Page background */
    .reportview-container {
        background: #0f1720;  /* subtle dark behind the app frame */
    }

    /* Container adjustments */
    .stApp {
        background: #fafafa;
        color: #0b1720;
    }

    /* Left "teal" vertical menu style - mimic screenshot column */
    .left-menu {
        background: linear-gradient(180deg, #0fb39b 0%, #13a69a 100%);
        color: white;
        padding: 22px 18px;
        border-radius: 8px;
        min-height: 180px;
    }
    .left-menu h2 {
        margin: 0;
        font-size: 20px;
        letter-spacing: 0.4px;
    }
    .left-menu p { margin: 6px 0 0 0; opacity: .95; }

    /* Card tiles */
    .kpi {
        background: white;
        padding: 14px;
        border-radius: 10px;
        box-shadow: 0 4px 12px rgba(20,20,20,0.06);
        text-align: center;
    }
    .kpi .label { font-size: 13px; color:#666; }
    .kpi .value { font-size: 22px; font-weight: 700; margin-top:6px; }

    /* Smaller muted footer */
    .muted { color: #6b7280; font-size: 13px; }

    /* Make Plotly charts have rounded cards */
    .chart-card {
        background: white;
        padding: 12px;
        border-radius: 10px;
        box-shadow: 0 6px 18px rgba(11,22,34,0.06);
    }

    /* Report timestamp style */
    .report-ts {
        font-size: 13px;
        color: #374151;
        background: #eef2ff;
        padding: 8px 12px;
        border-radius: 8px;
        display: inline-block;
    }

    /* Responsive tweaks */
    @media (max-width: 900px) {
        .left-menu { margin-bottom: 12px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)

# -------------------------
# Synthetic / sample data generator (hourly PM2.5) - UI only
# -------------------------
def generate_sample_hourly(hours=24 * 7):
    now = datetime.now().replace(minute=0, second=0, microsecond=0)
    times = [now - timedelta(hours=i) for i in range(hours)][::-1]
    base = 60 + 20 * np.sin(np.linspace(0, 6.28 * 3, len(times)))
    diurnal = 15 * np.sin(np.linspace(0, 6.28 * (len(times)/24), len(times)))
    trend = np.linspace(0, 8, len(times))
    noise = np.random.normal(0, 5, len(times))
    pm25 = np.clip(base + diurnal + trend + noise, 5, 500)
    df = pd.DataFrame({"ds": times, "pm25": np.round(pm25, 2)})
    df = df.set_index("ds")
    return df

# create a small processed dataframe for the UI (last 7 days hourly)
df = generate_sample_hourly(24 * 7)

# Compute some derived statistics for KPIs and charts
min_aqi = df["pm25"].min()
max_aqi = df["pm25"].max()
cur_aqi = df["pm25"].iloc[-1]
last24 = df["pm25"].tail(24)

# Small synthetic pollutant composition (for pie)
pollutants = {"PM2.5": 62, "NO2": 18, "CO2": 12, "O3": 8}

# Synthetic long-term trend (past 9 years)
years = list(range(datetime.now().year - 8, datetime.now().year + 1))
index_vals = np.linspace(380, 460, len(years)) + np.random.normal(0, 4, len(years))
trend_df = pd.DataFrame({"year": years, "index_val": np.round(index_vals, 2)})

# -------------------------
# Layout: left menu column + main content
# -------------------------
left_col, main_col = st.columns([1, 3])

with left_col:
    st.markdown('<div class="left-menu">', unsafe_allow_html=True)
    st.markdown("<h2>AirAware<br><small class='muted'>Maharashtra</small></h2>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Smart AQ Prediction — demo UI</p>", unsafe_allow_html=True)
    st.markdown("---", unsafe_allow_html=True)
    st.markdown("<p class='muted'><strong>Station:</strong><br>Pune — Demo</p>", unsafe_allow_html=True)
    st.markdown("<p class='muted'><strong>Pollutants:</strong><br>PM2.5 · NO2 · CO2 · O3</p>", unsafe_allow_html=True)
    st.markdown("<p class='muted'>Click controls on the main panel to adjust report date/time.</p>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

with main_col:
    # Header + report timestamp control
    st.markdown("<div style='display:flex;justify-content:space-between;align-items:baseline;'>", unsafe_allow_html=True)
    st.markdown("<h1 style='margin:0 0 6px 0;'>AirAware — Smart AQ Prediction System</h1>", unsafe_allow_html=True)

    report_date = st.date_input("Report date", value=df.index.max().date())
    report_time = st.time_input("Report time", value=df.index.max().to_pydatetime().time())
    report_ts = datetime.combine(report_date, report_time)
    st.markdown(f"<div class='report-ts'>Report generated on: {report_ts.strftime('%Y-%m-%d %H:%M:%S')}</div>", unsafe_allow_html=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # KPI row
    k1, k2, k3, spacer = st.columns([1,1,1,2])
    with k1:
        st.markdown('<div class="kpi"><div class="label">Min AQI</div><div class="value">{:.0f}</div></div>'.format(min_aqi), unsafe_allow_html=True)
    with k2:
        st.markdown('<div class="kpi"><div class="label">Current AQI</div><div class="value">{:.0f}</div></div>'.format(cur_aqi), unsafe_allow_html=True)
    with k3:
        st.markdown('<div class="kpi"><div class="label">Max AQI</div><div class="value">{:.0f}</div></div>'.format(max_aqi), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Two-column charts: Left big, Right side bars & accuracy
    left_area, right_area = st.columns([2.2, 1])

    with left_area:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Hourly AQI (last 24h)")
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=last24.index,
            y=last24.values,
            mode="lines+markers",
            line=dict(width=2),
            fill="tozeroy",
            name="PM2.5"
        ))
        fig.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=320, template="seaborn",
                          xaxis_tickformat="%d %b\n%H:%M")
        st.plotly_chart(fig, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        # Pollutant composition
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Pollutant Composition")
        pie = go.Figure(data=[go.Pie(labels=list(pollutants.keys()), values=list(pollutants.values()), hole=.45)])
        pie.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=300)
        st.plotly_chart(pie, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with right_area:
        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Prediction — Now / 1Y / 5Y")
        preds = {"Now": cur_aqi, "1 Year": cur_aqi * 1.05, "5 Year": cur_aqi * 1.12}
        bar = px.bar(x=list(preds.keys()), y=list(preds.values()), text=[f"{v:.0f}" for v in preds.values()])
        bar.update_layout(margin=dict(l=10, r=10, t=30, b=10), height=360, showlegend=False)
        st.plotly_chart(bar, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        st.markdown('<div class="chart-card">', unsafe_allow_html=True)
        st.subheader("Model accuracy (sample)")
        acc1, acc2, acc3 = st.columns(3)
        acc1.metric("RF", "89%")
        acc2.metric("GBM", "91%")
        acc3.metric("LSTM", "93%")
        st.markdown("</div>", unsafe_allow_html=True)

    # Long-term trend area (past 9 years)
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="chart-card">', unsafe_allow_html=True)
    st.subheader("Past 9 Years — Trend (Area)")
    fig2 = go.Figure()
    fig2.add_trace(go.Scatter(
        x=trend_df["year"],
        y=trend_df["index_val"],
        mode="lines",
        fill="tozeroy",
        line=dict(width=2)
    ))
    fig2.update_layout(margin=dict(l=10, r=10, t=20, b=10), height=360, xaxis_title="Year", yaxis_title="Index")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("</div>", unsafe_allow_html=True)

    # Footer notes
    st.markdown("<br>", unsafe_allow_html=True)
    footer_col1, footer_col2 = st.columns([3,1])
    footer_col1.markdown("**Notes:** This is a UI-only prototype. Replace synthetic data with your real processed data for live demo.")
    footer_col2.markdown("<div class='muted'>Team: Infosys Spring — AirAware</div>", unsafe_allow_html=True)

# End of file