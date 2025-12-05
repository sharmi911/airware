import requests

OWM_API_KEY = "c65a7f0b5a35652c9fae2b15734ce1aa"  # paste from OWM dashboard

def test_weather():
    url = "https://api.openweathermap.org/data/2.5/weather"
    params = {
        "q": "Delhi,IN",
        "appid": OWM_API_KEY,
        "units": "metric"
    }
    r = requests.get(url, params=params)
    print("Status code:", r.status_code)
    print("URL:", r.url)
    print("Response:", r.text[:300])  # first 300 chars

if __name__ == "__main__":
    test_weather()
