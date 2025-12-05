from flask import Flask, render_template, jsonify, request
import pandas as pd
from sklearn.linear_model import LinearRegression
import numpy as np
import os

app = Flask(__name__)

# ---------- Load data ----------

DATA_PATH = os.path.join("data", "air_quality.csv")
df = pd.read_csv(DATA_PATH, parse_dates=["datetime"])

# Normalize columns (adjust if your column names differ)
df["state"] = df["state"].astype(str)

# 👇 NEW: normalized key for safer matching
df["state_key"] = df["state"].str.strip().str.lower()

df = df.sort_values("datetime")


def get_state_summary(state: str):
    """Return summary + pollutant mix + simple time series for one state."""
    state_key = state.strip().lower()

    sdf = df[df["state_key"] == state_key].copy()
    if sdf.empty:
        return None

    latest = sdf.iloc[-1]

    # temperature
    if "temperature_c" in latest.index:
        temp = float(latest["temperature_c"]) if pd.notna(latest["temperature_c"]) else None
    elif "temperature" in latest.index:
        temp = float(latest["temperature"])
    else:
        temp = None

    curr_aqi = float(latest["aqi"])
    category = latest.get("category")     # 👈 NEW LINE

    sdf_recent = sdf.set_index("datetime").last("7D")
    if sdf_recent.empty:
        sdf_recent = sdf

    min_aqi = float(sdf_recent["aqi"].min())
    max_aqi = float(sdf_recent["aqi"].max())

    pollutant_cols = ["pm25", "pm10", "no2", "so2"]
    pollutant_vals = latest[pollutant_cols].fillna(0)
    total = pollutant_vals.sum()
    if total == 0:
        mix = [25, 25, 25, 25]
    else:
        mix = [round(v / total * 100, 1) for v in pollutant_vals]

    hourly_series = (
        sdf.set_index("datetime")
        .last("1D")
        .resample("3H")["aqi"]
        .mean()
        .dropna()
    )
    hourly = {
        "labels": [d.strftime("%H:%M") for d in hourly_series.index],
        "values": [round(v, 1) for v in hourly_series.values],
    }

    daily_series = (
        sdf.set_index("datetime")
        .last("7D")
        .resample("D")["aqi"]
        .mean()
        .dropna()
    )
    daily = {
        "labels": [d.strftime("%d-%b") for d in daily_series.index],
        "values": [round(v, 1) for v in daily_series.values],
    }

    monthly_series = (
        sdf.set_index("datetime")
        .last("365D")
        .resample("M")["aqi"]
        .mean()
        .dropna()
    )
    monthly = {
        "labels": [d.strftime("%b-%Y") for d in monthly_series.index],
        "values": [round(v, 1) for v in monthly_series.values],
    }

    return {
        "temp": round(temp, 1) if temp is not None else None,
        "min_aqi": round(min_aqi, 1),
        "curr_aqi": round(curr_aqi, 1),
        "max_aqi": round(max_aqi, 1),
        "category": category,         
        "pollutants": mix,
        "hourly": hourly,
        "daily": daily,
        "monthly": monthly,
    }




def predict_yearly_aqi(state: str, years: int = 5):
    """Simple linear regression on yearly average AQI."""
    state_key = state.strip().lower()
    sdf = df[df["state_key"] == state_key].copy()
    if sdf.empty:
        return None


    # Yearly mean AQI
    yearly = (
        sdf.set_index("datetime")
        .resample("Y")["aqi"]
        .mean()
        .dropna()
    )
    if len(yearly) < 2:
        # Not enough data for regression; just repeat last value
        last_year = yearly.index.year.max()
        last_val = yearly.iloc[-1]
        future_years = list(range(last_year + 1, last_year + years + 1))
        preds = [float(last_val)] * years
        return future_years, preds

    X = np.array(yearly.index.year).reshape(-1, 1)
    y = yearly.values

    model = LinearRegression()
    model.fit(X, y)

    last_year = yearly.index.year.max()
    future_years = np.arange(last_year + 1, last_year + years + 1)
    preds = model.predict(future_years.reshape(-1, 1))

    return list(future_years), [round(float(v), 1) for v in preds]


# ---------- Routes ----------

@app.route("/")
def landing():
    # landing.html from templates/
    return render_template("landing.html")


@app.route("/dashboard")
def dashboard():
    # dashboard.html from templates/
    return render_template("dashboard.html")


@app.route("/api/state/<state_name>")
def api_state(state_name):
    summary = get_state_summary(state_name)
    if summary is None:
        return jsonify({"error": "State not found in data"}), 404
    return jsonify(summary)


@app.route("/api/predict")
def api_predict():
    state = request.args.get("state")
    years = int(request.args.get("years", 5))
    if not state:
        return jsonify({"error": "state parameter required"}), 400

    result = predict_yearly_aqi(state, years)
    if result is None:
        return jsonify({"error": "State not found in data"}), 404

    future_years, preds = result
    return jsonify({"years": future_years, "aqi": preds})


if __name__ == "__main__":
    app.run(debug=True)
