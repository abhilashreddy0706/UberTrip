import sys
import json
import pickle
import warnings

# Suppress sklearn feature names warnings
warnings.filterwarnings("ignore", category=UserWarning)

# Configurable fare reduction multiplier
# - 0.60 matches Uber Go (Cabs)
# - 0.45 matches Uber Auto (Autos)
# - 0.30 matches Uber Moto (Bikes)
FARE_REDUCTION_MULTIPLIER = 0.45

# ==========================
# LOAD PICKLE FILES ONCE
# ==========================
try:
    with open("models/fare_model.pkl",    "rb") as f: fare_model   = pickle.load(f)
    with open("models/demand_model.pkl",  "rb") as f: demand_model = pickle.load(f)
    with open("models/scaler.pkl",        "rb") as f: scaler       = pickle.load(f)
    with open("models/le_pickup.pkl",     "rb") as f: le_pickup    = pickle.load(f)
    with open("models/le_drop.pkl",       "rb") as f: le_drop      = pickle.load(f)
    with open("models/le_weather.pkl",    "rb") as f: le_weather   = pickle.load(f)
    with open("models/le_demand.pkl",     "rb") as f: le_demand    = pickle.load(f)
except Exception as e:
    print(json.dumps({"error": f"Failed to load pickle models: {str(e)}"}))
    sys.stdout.flush()
    sys.exit(1)

# ==========================
# LOOP FOR PREDICTIONS
# ==========================
for line in sys.stdin:
    line = line.strip()
    if not line:
        continue
    try:
        data = json.loads(line)

        # Encode string names → numeric IDs
        pickup_id  = le_pickup.transform([data["pickup_location"]])[0]
        dropoff_id = le_drop.transform([data["dropoff_location"]])[0]
        weather_id = le_weather.transform([data["weather_condition"]])[0]

        features = [[
            data["hour"], data["day"], data["month"], data["weekday"], data["year"],
            data["trip_distance_km"], data["trip_duration_min"],
            data["surge_multiplier"], data["driver_utilization_percent"],
            pickup_id, dropoff_id, weather_id
        ]]

        X_scaled       = scaler.transform(features)
        raw_fare       = float(fare_model.predict(X_scaled)[0])
        fare           = round(raw_fare * FARE_REDUCTION_MULTIPLIER, 2)
        demand_id_pred = demand_model.predict(X_scaled)[0]
        demand         = le_demand.inverse_transform([demand_id_pred])[0]

        print(json.dumps({"fare": fare, "demand": demand}))
        sys.stdout.flush()

    except Exception as e:
        print(json.dumps({"error": str(e)}))
        sys.stdout.flush()
