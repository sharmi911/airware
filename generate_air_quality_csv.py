import csv
import datetime as dt
import os
import random
import requests

OWM_API_KEY = "c65a7f0b5a35652c9fae2b15734ce1aa"

STATE_LOCATIONS = {
    "Andhra Pradesh":      {"city": "Vijayawada", "lat": 16.5062, "lon": 80.6480},
    "Arunachal Pradesh":   {"city": "Itanagar", "lat": 27.0844, "lon": 93.6053},
    "Assam":               {"city": "Dispur", "lat": 26.1408, "lon": 91.7898},
    "Bihar":               {"city": "Patna", "lat": 25.5941, "lon": 85.1376},
    "Chhattisgarh":        {"city": "Raipur", "lat": 21.2514, "lon": 81.6296},
    "Goa":                 {"city": "Panaji", "lat": 15.4909, "lon": 73.8278},
    "Gujarat":             {"city": "Gandhinagar", "lat": 23.2156, "lon": 72.6369},
    "Haryana":             {"city": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "Himachal Pradesh":    {"city": "Shimla", "lat": 31.1048, "lon": 77.1734},
    "Jharkhand":           {"city": "Ranchi", "lat": 23.3441, "lon": 85.3096},
    "Karnataka":           {"city": "Bengaluru", "lat": 12.9716, "lon": 77.5946},
    "Kerala":              {"city": "Thiruvananthapuram", "lat": 8.5241, "lon": 76.9366},
    "Madhya Pradesh":      {"city": "Bhopal", "lat": 23.2599, "lon": 77.4126},
    "Maharashtra":         {"city": "Mumbai", "lat": 19.0760, "lon": 72.8777},
    "Manipur":             {"city": "Imphal", "lat": 24.8170, "lon": 93.9368},
    "Meghalaya":           {"city": "Shillong", "lat": 25.5788, "lon": 91.8933},
    "Mizoram":             {"city": "Aizawl", "lat": 23.7271, "lon": 92.7176},
    "Nagaland":            {"city": "Kohima", "lat": 25.6751, "lon": 94.1086},
    "Odisha":              {"city": "Bhubaneswar", "lat": 20.2961, "lon": 85.8245},
    "Punjab":              {"city": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "Rajasthan":           {"city": "Jaipur", "lat": 26.9124, "lon": 75.7873},
    "Sikkim":              {"city": "Gangtok", "lat": 27.3389, "lon": 88.6065},
    "Tamil Nadu":          {"city": "Chennai", "lat": 13.0827, "lon": 80.2707},
    "Telangana":           {"city": "Hyderabad", "lat": 17.3850, "lon": 78.4867},
    "Tripura":             {"city": "Agartala", "lat": 23.8315, "lon": 91.2868},
    "Uttar Pradesh":       {"city": "Lucknow", "lat": 26.8467, "lon": 80.9462},
    "Uttarakhand":         {"city": "Dehradun", "lat": 30.3165, "lon": 78.0322},
    "West Bengal":         {"city": "Kolkata", "lat": 22.5726, "lon": 88.3639},
    "Delhi":               {"city": "Delhi", "lat": 28.7041, "lon": 77.1025},
    "Puducherry":          {"city": "Puducherry", "lat": 11.9139, "lon": 79.8145},
    "Chandigarh":          {"city": "Chandigarh", "lat": 30.7333, "lon": 76.7794},
    "Andaman and Nicobar Islands": {"city": "Port Blair", "lat": 11.6234, "lon": 92.7265},
    "Ladakh":              {"city": "Leh", "lat": 34.1526, "lon": 77.5771},
    "Jammu and Kashmir":   {"city": "Srinagar", "lat": 34.0837, "lon": 74.7973},
}

def get_category(aqi):
    return {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor"
    }.get(int(aqi), "Unknown")

def fetch_realtime(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": OWM_API_KEY}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    js = r.json()
    return js["list"][0]

def generate_history(base_value, percent=15):
    """Generate a synthetic daily variation ±percent%."""
    up_down = 1 + random.uniform(-percent/100, percent/100)
    value = max(1, base_value * up_down)
    return round(value, 2)

def generate_pollutant(base, scale=0.25):
    return round(max(1, base * random.uniform(1-scale, 1+scale)), 2)

def main():
    rows = []
    now = dt.datetime.utcnow()
    id_counter = 1

    for state, info in STATE_LOCATIONS.items():
        city = info["city"]
        lat, lon = info["lat"], info["lon"]

        try:
            real = fetch_realtime(lat, lon)
        except:
            print(f"[ERROR] Could not fetch for {state}")
            continue

        real_aqi = real["main"]["aqi"]
        comps = real["components"]

        # Create 7 days of history • 3-hour intervals = 56 samples
        for day_offset in range(7):
            for hour in range(0, 24, 3):  # 0,3,6,...21
                timestamp = now - dt.timedelta(days=day_offset, hours=hour)

                synthetic_aqi = generate_history(real_aqi, percent=40)
                synthetic_aqi = min(max(synthetic_aqi, 1), 5)   # clamp 1–5 scale

                rows.append({
                    "id": id_counter,
                    "state": state,
                    "city": city,
                    "station": f"{city} Center",
                    "latitude": lat,
                    "longitude": lon,
                    "datetime": timestamp.isoformat(),

                    "aqi": synthetic_aqi,
                    "category": get_category(round(synthetic_aqi)),

                    "temperature_c": generate_history(25, percent=20),
                    "pm25": generate_pollutant(comps["pm2_5"]),
                    "pm10": generate_pollutant(comps["pm10"]),
                    "no2": generate_pollutant(comps["no2"]),
                    "so2": generate_pollutant(comps["so2"]),
                    "co": generate_pollutant(comps["co"]),
                    "o3": generate_pollutant(comps["o3"]),
                })
                id_counter += 1

    os.makedirs("data", exist_ok=True)
    out = "data/air_quality.csv"

    with open(out, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    print(f"[OK] Wrote {len(rows)} rows to {out}")

if __name__ == "__main__":
    main()
