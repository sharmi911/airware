import csv
import datetime as dt
import os
import requests

OWM_API_KEY = "c65a7f0b5a35652c9fae2b15734ce1aa"  # <-- put your key here

STATE_LOCATIONS = {
    "Andhra Pradesh":      {"city": "Vijayawada",          "lat": 16.5062, "lon": 80.6480},
    "Arunachal Pradesh":   {"city": "Itanagar",            "lat": 27.0844, "lon": 93.6053},
    "Assam":               {"city": "Dispur",              "lat": 26.1408, "lon": 91.7898},
    "Bihar":               {"city": "Patna",               "lat": 25.5941, "lon": 85.1376},
    "Chhattisgarh":        {"city": "Raipur",              "lat": 21.2514, "lon": 81.6296},
    "Goa":                 {"city": "Panaji",              "lat": 15.4909, "lon": 73.8278},
    "Gujarat":             {"city": "Gandhinagar",         "lat": 23.2156, "lon": 72.6369},
    "Haryana":             {"city": "Chandigarh",          "lat": 30.7333, "lon": 76.7794},
    "Himachal Pradesh":    {"city": "Shimla",              "lat": 31.1048, "lon": 77.1734},
    "Jharkhand":           {"city": "Ranchi",              "lat": 23.3441, "lon": 85.3096},
    "Karnataka":           {"city": "Bengaluru",           "lat": 12.9716, "lon": 77.5946},
    "Kerala":              {"city": "Thiruvananthapuram",  "lat": 8.5241,  "lon": 76.9366},
    "Madhya Pradesh":      {"city": "Bhopal",              "lat": 23.2599, "lon": 77.4126},
    "Maharashtra":         {"city": "Mumbai",              "lat": 19.0760, "lon": 72.8777},
    "Manipur":             {"city": "Imphal",              "lat": 24.8170, "lon": 93.9368},
    "Meghalaya":           {"city": "Shillong",            "lat": 25.5788, "lon": 91.8933},
    "Mizoram":             {"city": "Aizawl",              "lat": 23.7271, "lon": 92.7176},
    "Nagaland":            {"city": "Kohima",              "lat": 25.6751, "lon": 94.1086},
    "Odisha":              {"city": "Bhubaneswar",         "lat": 20.2961, "lon": 85.8245},
    "Punjab":              {"city": "Chandigarh",          "lat": 30.7333, "lon": 76.7794},
    "Rajasthan":           {"city": "Jaipur",              "lat": 26.9124, "lon": 75.7873},
    "Sikkim":              {"city": "Gangtok",             "lat": 27.3389, "lon": 88.6065},
    "Tamil Nadu":          {"city": "Chennai",             "lat": 13.0827, "lon": 80.2707},
    "Telangana":           {"city": "Hyderabad",           "lat": 17.3850, "lon": 78.4867},
    "Tripura":             {"city": "Agartala",            "lat": 23.8315, "lon": 91.2868},
    "Uttar Pradesh":       {"city": "Lucknow",             "lat": 26.8467, "lon": 80.9462},
    "Uttarakhand":         {"city": "Dehradun",            "lat": 30.3165, "lon": 78.0322},
    "West Bengal":         {"city": "Kolkata",             "lat": 22.5726, "lon": 88.3639},
    "Delhi":               {"city": "Delhi",               "lat": 28.7041, "lon": 77.1025},
    "Puducherry":          {"city": "Puducherry",          "lat": 11.9139, "lon": 79.8145},
    "Chandigarh":          {"city": "Chandigarh",          "lat": 30.7333, "lon": 76.7794},
    "Andaman and Nicobar Islands": {"city": "Port Blair",  "lat": 11.6234, "lon": 92.7265},
    "Ladakh":              {"city": "Leh",                 "lat": 34.1526, "lon": 77.5771},
    "Jammu and Kashmir":   {"city": "Srinagar",            "lat": 34.0837, "lon": 74.7973},
}

def category_from_owm_aqi(aqi_val: int) -> str:
    mapping = {
        1: "Good",
        2: "Fair",
        3: "Moderate",
        4: "Poor",
        5: "Very Poor",
    }
    return mapping.get(int(aqi_val), "Unknown")

def fetch_air_pollution(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": OWM_API_KEY}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def fetch_weather(lat, lon):
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {"lat": lat, "lon": lon, "appid": OWM_API_KEY, "units": "metric"}
    r = requests.get(url, params=params, timeout=10)
    r.raise_for_status()
    return r.json()

def main():
    now = dt.datetime.utcnow().replace(microsecond=0).isoformat()
    rows = []
    row_id = 1

    for state, info in STATE_LOCATIONS.items():
        lat = info["lat"]
        lon = info["lon"]
        city = info["city"]
        station = f"{city} Center"

        try:
            air = fetch_air_pollution(lat, lon)
            weather = fetch_weather(lat, lon)
        except Exception as e:
            print(f"[ERROR] {state} ({city}): {e}")
            continue

        if not air.get("list"):
            print(f"[WARN] No air data for {state} ({city})")
            continue

        air_data = air["list"][0]
        comps = air_data.get("components", {})
        aqi_val = air_data.get("main", {}).get("aqi", None)

        if aqi_val is None:
            print(f"[WARN] No AQI for {state} ({city})")
            continue

        temp_c = None
        if weather.get("main"):
            temp_c = weather["main"].get("temp")

        row = {
            "id": row_id,
            "state": state,
            "city": city,
            "station": station,
            "latitude": lat,
            "longitude": lon,
            "datetime": now,
            "aqi": aqi_val,
            "category": category_from_owm_aqi(aqi_val),
            "temperature_c": temp_c,
            "pm25": comps.get("pm2_5"),
            "pm10": comps.get("pm10"),
            "no2": comps.get("no2"),
            "so2": comps.get("so2"),
            "co": comps.get("co"),
            "o3": comps.get("o3"),
        }
        rows.append(row)
        row_id += 1

    os.makedirs("data", exist_ok=True)
    out_path = os.path.join("data", "air_quality.csv")

    with open(out_path, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "id","state","city","station","latitude","longitude",
                "datetime","aqi","category","temperature_c",
                "pm25","pm10","no2","so2","co","o3"
            ],
        )
        writer.writeheader()
        writer.writerows(rows)

    print(f"[INFO] Wrote {len(rows)} rows to {out_path}")

if __name__ == "__main__":
    main()
