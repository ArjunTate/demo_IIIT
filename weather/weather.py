import requests
import os
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("OPENWEATHER_API_KEY")
BASE_URL = "https://api.openweathermap.org"


# ─────────────────────────────────────────
#  HELPER — build (lat, lon) from either
#           city name or coordinates
# ─────────────────────────────────────────

def get_coordinates(city=None, lat=None, lon=None):
    """Return (lat, lon) from city name or direct coordinates."""
    if lat is not None and lon is not None:
        return lat, lon

    if city:
        url = f"{BASE_URL}/geo/1.0/direct"
        params = {"q": city, "limit": 1, "appid": API_KEY}
        response = requests.get(url, params=params)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"City '{city}' not found.")
        return data[0]["lat"], data[0]["lon"]

    raise ValueError("Provide either a city name or lat/lon coordinates.")


# ─────────────────────────────────────────
#  1. CURRENT WEATHER
# ─────────────────────────────────────────

def get_current_weather(city=None, lat=None, lon=None, units="metric"):
    """
    Fetch current weather.
    units: 'metric' (°C), 'imperial' (°F), 'standard' (K)
    """
    lat, lon = get_coordinates(city, lat, lon)

    url = f"{BASE_URL}/data/2.5/weather"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": units,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    return {
        "city": data["name"],
        "country": data["sys"]["country"],
        "temperature": data["main"]["temp"],
        "feels_like": data["main"]["feels_like"],
        "humidity": data["main"]["humidity"],
        "description": data["weather"][0]["description"].capitalize(),
        "wind_speed": data["wind"]["speed"],
        "units": units,
    }


# ─────────────────────────────────────────
#  2. 5-DAY FORECAST (every 3 hours)
# ─────────────────────────────────────────

def get_forecast(city=None, lat=None, lon=None, units="metric"):
    """
    Fetch 5-day / 3-hour forecast.
    Returns a list of up to 40 forecast entries.
    """
    lat, lon = get_coordinates(city, lat, lon)

    url = f"{BASE_URL}/data/2.5/forecast"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "units": units,
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    forecast_list = []
    for entry in data["list"]:
        forecast_list.append({
            "datetime": entry["dt_txt"],
            "temperature": entry["main"]["temp"],
            "feels_like": entry["main"]["feels_like"],
            "humidity": entry["main"]["humidity"],
            "description": entry["weather"][0]["description"].capitalize(),
            "wind_speed": entry["wind"]["speed"],
        })

    return {
        "city": data["city"]["name"],
        "country": data["city"]["country"],
        "units": units,
        "forecast": forecast_list,
    }


# ─────────────────────────────────────────
#  3. WEATHER ALERTS  (requires One Call API)
# ─────────────────────────────────────────

def get_weather_alerts(city=None, lat=None, lon=None):
    """
    Fetch active weather alerts via One Call API 3.0.
    Note: Requires a paid/subscribed OpenWeather plan.
    """
    lat, lon = get_coordinates(city, lat, lon)

    url = f"{BASE_URL}/data/3.0/onecall"
    params = {
        "lat": lat,
        "lon": lon,
        "appid": API_KEY,
        "exclude": "current,minutely,hourly,daily",  # only fetch alerts
    }
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    alerts = data.get("alerts", [])
    if not alerts:
        return {"alerts": [], "message": "No active alerts for this location."}

    parsed_alerts = []
    for alert in alerts:
        parsed_alerts.append({
            "sender": alert.get("sender_name", "Unknown"),
            "event": alert.get("event", "N/A"),
            "start": alert.get("start"),
            "end": alert.get("end"),
            "description": alert.get("description", ""),
        })

    return {"alerts": parsed_alerts}


# ─────────────────────────────────────────
#  4. AIR QUALITY INDEX (AQI)
# ─────────────────────────────────────────

AQI_LABELS = {
    1: "Good",
    2: "Fair",
    3: "Moderate",
    4: "Poor",
    5: "Very Poor",
}

def get_air_quality(city=None, lat=None, lon=None):
    """
    Fetch current air quality index and pollutant levels.
    """
    lat, lon = get_coordinates(city, lat, lon)

    url = f"{BASE_URL}/data/2.5/air_pollution"
    params = {"lat": lat, "lon": lon, "appid": API_KEY}
    response = requests.get(url, params=params)
    response.raise_for_status()
    data = response.json()

    entry = data["list"][0]
    aqi = entry["main"]["aqi"]
    components = entry["components"]

    return {
        "aqi": aqi,
        "aqi_label": AQI_LABELS.get(aqi, "Unknown"),
        "co": components.get("co"),       # Carbon monoxide (μg/m³)
        "no2": components.get("no2"),     # Nitrogen dioxide
        "o3": components.get("o3"),       # Ozone
        "pm2_5": components.get("pm2_5"), # Fine particles
        "pm10": components.get("pm10"),   # Coarse particles
    }


# ─────────────────────────────────────────
#  MAIN — quick demo
# ─────────────────────────────────────────

if __name__ == "__main__":

    print("=" * 45)
    print("       OpenWeather API - Test Tool")
    print("=" * 45)

    # ── Ask user how they want to provide location ──
    print("\nHow do you want to enter the location?")
    print("  1. City name")
    print("  2. Latitude & Longitude")
    choice = input("\nEnter 1 or 2: ").strip()

    city = None
    lat = lon = None

    if choice == "1":
        city = input("Enter city name (e.g. Mumbai, Delhi, London): ").strip()
    elif choice == "2":
        lat = float(input("Enter latitude  (e.g. 19.0760): ").strip())
        lon = float(input("Enter longitude (e.g. 72.8777): ").strip())
    else:
        print("Invalid choice. Defaulting to city input.")
        city = input("Enter city name: ").strip()

    # ── Ask what data to fetch ──
    print("\nWhat data do you want?")
    print("  1. Current weather")
    print("  2. 5-Day forecast")
    print("  3. Air quality")
    print("  4. Weather alerts")
    print("  5. All of the above")
    data_choice = input("\nEnter choice (1-5): ").strip()

    print("\n" + "=" * 45)

    try:
        # Current weather
        if data_choice in ("1", "5"):
            current = get_current_weather(city=city, lat=lat, lon=lon)
            print(f"\n[Current Weather — {current['city']}, {current['country']}]")
            print(f"  {current['description']}")
            print(f"  Temp      : {current['temperature']}°C (feels like {current['feels_like']}°C)")
            print(f"  Humidity  : {current['humidity']}%")
            print(f"  Wind      : {current['wind_speed']} m/s")

        # 5-day forecast
        if data_choice in ("2", "5"):
            forecast = get_forecast(city=city, lat=lat, lon=lon)
            print(f"\n[5-Day Forecast — {forecast['city']}, next 5 slots]")
            for entry in forecast["forecast"][:5]:
                print(f"  {entry['datetime']}  |  {entry['temperature']}°C  |  {entry['description']}")

        # Air quality
        if data_choice in ("3", "5"):
            aqi = get_air_quality(city=city, lat=lat, lon=lon)
            print(f"\n[Air Quality]")
            print(f"  AQI       : {aqi['aqi']} — {aqi['aqi_label']}")
            print(f"  PM2.5     : {aqi['pm2_5']} μg/m³")
            print(f"  PM10      : {aqi['pm10']} μg/m³")
            print(f"  NO₂       : {aqi['no2']} μg/m³")

        # Alerts
        if data_choice in ("4", "5"):
            alerts = get_weather_alerts(city=city, lat=lat, lon=lon)
            print(f"\n[Weather Alerts]")
            if alerts["alerts"]:
                for a in alerts["alerts"]:
                    print(f"  ⚠ {a['event']} — {a['sender']}")
            else:
                print(f"  {alerts['message']}")

    except ValueError as e:
        print(f"\n  Error: {e}")
    except Exception as e:
        print(f"\n  Something went wrong: {e}")