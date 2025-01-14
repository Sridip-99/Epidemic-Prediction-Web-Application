import requests

def fetch_weather(place, date):
    api_key = "a1f7012061eb4195be2114511241111"  # Replace with your API key
    base_url = "https://api.weatherapi.com/v1/history.json"
    params = {
        "key": api_key,
        "q": place,
        "dt": date
    }
    response = requests.get(base_url, params=params)
    if response.status_code == 200:
        return response.json()  # Return parsed JSON data
    else:
        return {"error": "Unable to fetch weather data"}


def fetch_unwto_data(place, date):
    # Replace this with the actual UNWTO API endpoint and your API key
    api_url = "https://api.unwto.org/v1/to    urism-data"
    api_key = "your_api_key_here"

    params = {
        "place": place,
        "date": date,
    }

    response = requests.get(api_url, headers={"Authorization": f"Bearer {api_key}"}, params=params)

    if response.status_code == 200:
        data = response.json()
        return {
            "resident_ratio": data.get("resident_ratio", 0),
            "traveler_ratio": data.get("traveler_ratio", 0),
        }
    else:
        return None #{"error": "Failed to fetch data from UNWTO API"}

