import pandas as pd
import numpy as np
import xgboost as xgb
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import pickle

print("Loading dataset...")
data = pd.read_csv("full_dataset.csv")

features = [
    'temperature', 'humidity', 'precipitation',
    'rain', 'wind_speed', 'pressure',
    'soil_moisture_top', 'soil_moisture_deep'
]

X = data[features]

# ---- TRAIN FLOOD SCORE MODEL (regression) ----
print("\n--- Training Flood Score Model ---")
y_flood = data['flood_score']

X_train, X_test, y_train, y_test = train_test_split(
    X, y_flood, test_size=0.2, random_state=42
)

flood_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
flood_model.fit(X_train, y_train)
preds = flood_model.predict(X_test)
print(f"MAE: {mean_absolute_error(y_test, preds):.2f}")
print(f"R2:  {r2_score(y_test, preds):.4f}")

# ---- TRAIN HEAT SCORE MODEL (regression) ----
print("\n--- Training Heat Score Model ---")
y_heat = data['heat_score']

X_train2, X_test2, y_train2, y_test2 = train_test_split(
    X, y_heat, test_size=0.2, random_state=42
)

heat_model = xgb.XGBRegressor(
    n_estimators=100,
    max_depth=6,
    learning_rate=0.1,
    random_state=42
)
heat_model.fit(X_train2, y_train2)
preds2 = heat_model.predict(X_test2)
print(f"MAE: {mean_absolute_error(y_test2, preds2):.2f}")
print(f"R2:  {r2_score(y_test2, preds2):.4f}")

# ---- SAVE ----
with open("flood_model.pkl", "wb") as f:
    pickle.dump(flood_model, f)
with open("heat_model.pkl", "wb") as f:
    pickle.dump(heat_model, f)

print("\n✅ flood_model.pkl saved")
print("✅ heat_model.pkl saved")