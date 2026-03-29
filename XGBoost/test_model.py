import pickle
import pandas as pd

# ---- LOAD MODELS ----
with open("flood_model.pkl", "rb") as f:
    flood_model = pickle.load(f)

with open("heat_model.pkl", "rb") as f:
    heat_model = pickle.load(f)

# ---- FUNCTION TO PREDICT ----
def predict_risk(city_name, temperature, humidity,
                 precipitation, rain, wind_speed,
                 pressure, soil_moisture_top, soil_moisture_deep):

    sample = pd.DataFrame([{
        'temperature': temperature,
        'humidity': humidity,
        'precipitation': precipitation,
        'rain': rain,
        'wind_speed': wind_speed,
        'pressure': pressure,
        'soil_moisture_top': soil_moisture_top,
        'soil_moisture_deep': soil_moisture_deep
    }])

    # ← changed from predict_proba to predict
    flood_prob = float(flood_model.predict(sample)[0])
    heat_prob  = float(heat_model.predict(sample)[0])
    overall    = (flood_prob + heat_prob) / 2

    def get_level(score):
        if score > 70: return "🔴 CRITICAL"
        elif score > 50: return "🟠 HIGH"
        elif score > 30: return "🟡 MEDIUM"
        else: return "🟢 LOW"

    print(f"\n{'='*40}")
    print(f"  City         : {city_name}")
    print(f"  Temperature  : {temperature}°C")
    print(f"  Humidity     : {humidity}%")
    print(f"  Rain         : {rain}mm")
    print(f"{'='*40}")
    print(f"  Flood Risk   : {flood_prob:.1f}/100")
    print(f"  Heat Risk    : {heat_prob:.1f}/100")
    print(f"  Overall Risk : {overall:.1f}/100")
    print(f"  Risk Level   : {get_level(overall)}")
    print(f"{'='*40}")

# ---- TEST CITIES ----
predict_risk("Mumbai (Monsoon)", 29, 92, 18, 15, 25, 1004, 0.42, 0.38)
predict_risk("Delhi (Heatwave)", 45, 20, 0, 0, 10, 1002, 0.10, 0.12)
predict_risk("Jamnagar (Normal)", 28, 55, 0, 0, 12, 1013, 0.22, 0.25)
predict_risk("Chennai (Cyclone)", 31, 95, 25, 22, 65, 998, 0.45, 0.40)