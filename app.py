import pickle
import json
from flask import Flask, request, jsonify, render_template

app = Flask(__name__)

# ==========================
# LOAD PICKLE FILES ONCE
# ==========================
with open("models/fare_model.pkl",    "rb") as f: fare_model   = pickle.load(f)
with open("models/demand_model.pkl",  "rb") as f: demand_model = pickle.load(f)
with open("models/scaler.pkl",        "rb") as f: scaler       = pickle.load(f)
with open("models/le_pickup.pkl",     "rb") as f: le_pickup    = pickle.load(f)
with open("models/le_drop.pkl",       "rb") as f: le_drop      = pickle.load(f)
with open("models/le_weather.pkl",    "rb") as f: le_weather   = pickle.load(f)
with open("models/le_demand.pkl",     "rb") as f: le_demand    = pickle.load(f)

with open("models/classes.json", "r") as f:
    classes = json.load(f)

print("✅ Models loaded successfully!")

# ==========================
# ROUTES
# ==========================
@app.route("/")
def index():
    return render_template("index.html", classes=classes)


@app.route("/predict", methods=["POST"])
def predict():
    try:
        data = request.get_json()

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
        fare           = round(float(fare_model.predict(X_scaled)[0]), 2)
        demand_id_pred = demand_model.predict(X_scaled)[0]
        demand         = le_demand.inverse_transform([demand_id_pred])[0]

        return jsonify({"fare": fare, "demand": demand})

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# ==========================
# RUN
# ==========================
if __name__ == "__main__":
    app.run(debug=True, port=5000)