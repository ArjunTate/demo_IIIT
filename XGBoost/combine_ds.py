import pandas as pd
import os

# ---- CORRECT FOLDER PATH ----
folder = r"D:\TechVortex_IIIT\DATASET FOR WETHER SOIL PREDICTION"
# ⚠️ Run this in terminal to get exact name:
# cd D:\TechVortex_IIIT
# dir

cities = ['mumbai', 'punr', 'delhi', 
          'jamnagar', 'gwalior', 
          'chennai', 'kolkata']

all_data = []

for city in cities:
    path = os.path.join(folder, f"{city}.csv")
    
    # skip first 3 rows (lat/long metadata)
    df = pd.read_csv(path, skiprows=3)  
    df['city'] = city
    all_data.append(df)
    print(f"✅ Loaded {city} - {len(df)} rows") 

# ---- COMBINE ALL ----
data = pd.concat(all_data, ignore_index=True)

# ---- RENAME COLUMNS (shorter names) ----
data = data.rename(columns={
    'time': 'time',
    'temperature_2m (°C)': 'temperature',
    'relative_humidity_2m (%)': 'humidity',
    'precipitation (mm)': 'precipitation',
    'rain (mm)': 'rain', 
    'wind_speed_10m (km/h)': 'wind_speed',
    'surface_pressure (hPa)': 'pressure',
    'soil_moisture_0_to_7cm (m³/m³)': 'soil_moisture_top',
    'soil_moisture_7_to_28cm (m³/m³)': 'soil_moisture_deep'
})

# Flood risk
data['flood_risk'] = (
    (data['rain'] > 2.5) &
    (data['soil_moisture_top'] > 0.30)
).astype(int)

# Heat risk — completely rewritten
data['heat_risk'] = (
    (data['temperature'] > 32) |
    ((data['temperature'] > 28) &
     (data['humidity'] > 70))
).astype(int)

# ---- ADD CONTINUOUS RISK SCORE (0-100) ----
# This is what model will actually predict
data['flood_score'] = (
    (data['rain'] / 50 * 60) +
    (data['soil_moisture_top'] * 40)
).clip(0, 100)

data['heat_score'] = (
    ((data['temperature'] - 20) / 25 * 70) +
    (data['humidity'] / 100 * 30)
).clip(0, 100)

# Overall risk score (0-100)
data['risk_score'] = (
    (data['rain'] * 2) +
    (data['soil_moisture_top'] * 30) +
    (data['temperature'] * 0.5) +
    (data['humidity'] * 0.3)
).clip(0, 100)

print("\n--- COLUMN NAMES ---")
print(data.columns.tolist())
print("\n--- SHAPE ---")
print(data.shape)
print("\n--- FLOOD RISK DISTRIBUTION ---")
print(data['flood_risk'].value_counts())
print("\n--- HEAT RISK DISTRIBUTION ---")
print(data['heat_risk'].value_counts())

data.to_csv("full_dataset.csv", index=False)
print("\n✅ Saved as full_dataset.csv")