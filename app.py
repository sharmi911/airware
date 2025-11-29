from flask import Flask, jsonify, request
import requests
from flask_cors import CORS


app = Flask(__name__)
CORS(app)

# YOUR TOKEN HERE
WAQI_TOKEN = "073c3095deb057487b16bb27f52e8f17643cd6f5"

# Map states → main city for WAQI
STATE_CITY = {
    "Tamil Nadu": "Chennai",
    "Karnataka": "Bengaluru",
    "Maharashtra": "Mumbai",
    "Kerala": "Thiruvananthapuram",
    "Delhi": "Delhi",
    "Chhattisgarh": "Raipur",
    "Andhra Pradesh": "Vijayawada",
    "Telangana": "Hyderabad",
    "Uttar Pradesh": "Lucknow",
    "West Bengal": "Kolkata",
    "Rajasthan": "Jaipur",
    "Punjab": "Ludhiana",
    "Haryana": "Gurugram",
    "Odisha": "Bhubaneswar",
    "Bihar": "Patna",
    "Gujarat": "Ahmedabad",
    "Jharkhand": "Ranchi",
    "Madhya Pradesh": "Bhopal",
    "Uttarakhand": "Dehradun",
    "Goa": "Panaji",
    "Tripura": "Agartala",
    "Manipur": "Imphal",
    "Meghalaya": "Shillong",
    "Nagaland": "Kohima",
    "Mizoram": "Aizawl",
    "Arunachal Pradesh": "Itanagar",
    "Assam": "Guwahati",
    "Himachal Pradesh": "Shimla",
    "Sikkim": "Gangtok",
    "Jammu and Kashmir": "Srinagar",
    "Ladakh": "Leh",
    "Andaman and Nicobar Islands": "Port Blair",
    "Puducherry": "Puducherry",
    "Chandigarh": "Chandigarh"
}

def fetch_waqi(city):
    url = f"https://api.waqi.info/feed/{city}/?token={WAQI_TOKEN}"
    r = requests.get(url).json()

    if r["status"] != "ok":
        return None

    d = r["data"]
    iaqi = d.get("iaqi", {})

    pollutants = {
        "pm25": iaqi.get("pm25", {}).get("v"),
        "pm10": iaqi.get("pm10", {}).get("v"),
        "no2": iaqi.get("no2", {}).get("v"),
        "so2": iaqi.get("so2", {}).get("v"),
        "o3": iaqi.get("o3", {}).get("v"),
        "co": iaqi.get("co", {}).get("v")
    }

    # WAQI may contain forecast for PM10/PM2.5
    forecast = d.get("forecast", {}).get("daily", {})

    # Generate dummy hourly values based on current AQI variations
    curr = d.get("aqi", 0)
    hourly = [{"time": i, "value": curr + (i % 5 - 2) * 4} for i in range(24)]

    # Generate dummy daily values using WAQI forecast (if available)
    daily = []
    if "pm10" in forecast:
        for entry in forecast["pm10"]:
            daily.append({
                "date": entry["day"],
                "value": entry["avg"]
            })

    # Monthly = average of daily
    monthly = sum([x["value"] for x in daily]) / len(daily) if daily else curr

    return {
        "city": d.get("city", {}).get("name", city),
        "current_aqi": curr,
        "pollutant_mix": pollutants,
        "hourly": hourly,
        "daily": daily,
        "monthly": monthly,
        "forecast": forecast
    }

@app.route("/states")
def states():
    return jsonify(sorted(list(STATE_CITY.keys())))

@app.route("/aqi")
def get_aqi():
    state = request.args.get("state")
    if not state:
        return jsonify({"error": "Provide state parameter"}), 400

    city = STATE_CITY.get(state)
    if not city:
        return jsonify({"error": "Invalid state"}), 404

    data = fetch_waqi(city)
    if not data:
        return jsonify({"error": "WAQI error"}), 500

    return jsonify(data)

@app.route("/")
def home():
    return "WAQI Backend Running Successfully!"

if __name__ == "__main__":
    app.run(port=5000, debug=True)

