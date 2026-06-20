# UberTrip: Flask to Node.js Migration & ML Prediction System

This project contains the migrated backend prediction system from a Python Flask application to a Node.js Express application.

## Key Changes

1. **Express & Nunjucks Integration:**
   - `server.js` serves as the new entry point.
   - We used the Nunjucks template engine, which supports Jinja's exact layout syntax, enabling us to keep `templates/index.html` completely untouched.

2. **Persistent ML Predictions:**
   - Running Python ML models directly in Node is slow if the python interpreter and models are reloaded on each request.
   - We implemented a persistent background process `predict_worker.py` that loads the ML models once.
   - `predictor.js` acts as a Node.js wrapper that feeds predictions to the worker process via stdin and listens for outputs via stdout in line-delimited JSON. This yields sub-millisecond prediction response times.
   - If the Python worker crashes for any reason, the Node wrapper automatically restarts it.

3. **Same Location Validation & UI Prevention:**
   - **Client-Side:** In `index.html`, the `updateRouteInfo` function dynamically disables the selected location in the opposing dropdown (e.g., selecting `Ameerpet` as pickup disables `Ameerpet` in the dropoff list). On page load, it dynamically shifts the dropoff location to the next option so they never load with matching values.
   - **Server-Side:** Added a validation check in `server.js` to reject any direct `/predict` POST request with identical pickup and dropoff locations with a `400 Bad Request` response.

4. **Configurable Fare Reduction:**
   - Introduced a `FARE_REDUCTION_MULTIPLIER = 0.45` constant in `predict_worker.py` to scale down high fare model outputs (applying a 55% reduction to match real-world budget options like Uber Auto/Moto in Hyderabad).

---

## How to Run & Verify

1. **Ensure dependencies are installed:**
   ```bash
   npm install
   ```

2. **Start the Node.js server:**
   ```bash
   node server.js
   ```

3. **Verify the website:**
   Open a browser and navigate to `http://localhost:5000`.

4. **Verify Prediction Endpoint:**
   To test via shell/terminal (PowerShell):
   ```powershell
   Invoke-RestMethod -Uri "http://localhost:5000/predict" -Method Post -ContentType "application/json" -Body '{"hour": 14, "day": 15, "month": 6, "weekday": 2, "year": 2026, "trip_distance_km": 8.5, "trip_duration_min": 25, "surge_multiplier": 1.5, "driver_utilization_percent": 75, "pickup_location": "Begumpet", "dropoff_location": "Ameerpet", "weather_condition": "Clear"}'
   ```
   **Expected Response:**
   ```json
   {
       "fare": 139.72,
       "demand": "Medium"
   }
   ```
