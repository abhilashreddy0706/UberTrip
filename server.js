const express = require('express');
const nunjucks = require('nunjucks');
const fs = require('fs');
const path = require('path');
const predictor = require('./predictor');

const app = express();
app.use(express.json());

// Load dynamic classes list for the template dropdowns
const classesPath = path.join(__dirname, 'models', 'classes.json');
let classes = {};

try {
    const rawData = fs.readFileSync(classesPath, 'utf8');
    classes = JSON.parse(rawData);
    console.log("✅ Models and classes configuration loaded successfully!");
} catch (err) {
    console.error("❌ Failed to read classes.json configuration file:", err);
}

// Configure Nunjucks template engine
nunjucks.configure('templates', {
    autoescape: true,
    express: app
});

// GET route for frontend web interface
app.get('/', (req, res) => {
    res.render('index.html', { classes });
});

// POST route for prediction
app.post('/predict', async (req, res) => {
    try {
        const data = req.body;
        
        // Input validation & type conversion to match model requirements
        const payload = {
            hour: parseInt(data.hour, 10),
            day: parseInt(data.day, 10),
            month: parseInt(data.month, 10),
            weekday: parseInt(data.weekday, 10),
            year: parseInt(data.year, 10),
            trip_distance_km: parseFloat(data.trip_distance_km),
            trip_duration_min: parseFloat(data.trip_duration_min),
            surge_multiplier: parseFloat(data.surge_multiplier),
            driver_utilization_percent: parseFloat(data.driver_utilization_percent),
            pickup_location: String(data.pickup_location),
            dropoff_location: String(data.dropoff_location),
            weather_condition: String(data.weather_condition)
        };

        // Validate that no payload values are NaN or invalid
        for (const [key, value] of Object.entries(payload)) {
            if (value === undefined || value === null || (typeof value === 'number' && isNaN(value))) {
                return res.status(400).json({ error: `Invalid or missing parameter: ${key}` });
            }
        }

        // Validate that pickup and dropoff locations are different
        if (payload.pickup_location === payload.dropoff_location) {
            return res.status(400).json({ error: "Pickup and Dropoff locations cannot be the same." });
        }

        // Delegate prediction to python subprocess
        const prediction = await predictor.predict(payload);
        res.json(prediction);

    } catch (err) {
        console.error("Prediction endpoint error:", err.message);
        res.status(500).json({ error: err.message });
    }
});

// Set up server port and run
const PORT = process.env.PORT || 5000;
app.listen(PORT, () => {
    console.log(`🚀 Node.js Backend Server active on port ${PORT}`);
    console.log(`🔗 Access the web app at http://localhost:${PORT}`);
});
