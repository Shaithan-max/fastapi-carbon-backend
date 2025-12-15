from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from collections import defaultdict
from datetime import datetime
import os

app = FastAPI()

# ---------------- CORS ----------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------- CONFIG ----------------
CSV_FILE = "/tmp/sensor_data.csv"  # Render-safe path
KG_TO_MG = 1_000_000  # 1 kg = 1,000,000 mg

# ---------------- DATA MODEL ----------------
class SensorData(BaseModel):
    time: int
    current_A: float
    temp_C: float
    pressure: float
    co2_shred: float
    co2_heating: float
    co2_mould: float
    co2_total: float

# ---------------- READ + PROCESS (SECOND-WISE) ----------------
def read_and_process_csv():
    second_data = []

    if not os.path.exists(CSV_FILE):
        return []

    with open(CSV_FILE, newline="") as f:
        reader = csv.DictReader(f)

        for row in reader:
            ts = int(row["time"])
            # Skip invalid timestamps
            if ts < 1_000_000_000:
                continue

            second_data.append({
                "timestamp": ts,
                "shredding_carbon_mg": round(float(row["co2_shred"]) * KG_TO_MG, 6),
                "heating_carbon_mg": round(float(row["co2_heating"]) * KG_TO_MG, 6),
                "pressure_carbon_mg": round(float(row["co2_mould"]) * KG_TO_MG, 6),
                "total_carbon_mg": round(float(row["co2_total"]) * KG_TO_MG, 6),
            })

    # Sort by timestamp
    second_data.sort(key=lambda x: x["timestamp"])

    # Format timestamp for frontend
    for item in second_data:
        item["minute"] = datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    return second_data

# ---------------- RECEIVE SENSOR DATA ----------------
@app.post("/sensor-data")
def receive_sensor_data(data: SensorData):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)

        if not file_exists:
            writer.writerow([
                "time",
                "current_A",
                "temp_C",
                "pressure",
                "co2_shred",
                "co2_heating",
                "co2_mould",
                "co2_total"
            ])

        writer.writerow([
            data.time,
            data.current_A,
            data.temp_C,
            data.pressure,
            data.co2_shred,
            data.co2_heating,
            data.co2_mould,
            data.co2_total
        ])

    return {"status": "sensor data saved"}

# ---------------- API ROUTES ----------------
@app.get("/")
def root():
    return {"status": "Carbon Footprint API running"}

@app.get("/carbon-footprint/minute")
def get_minute_carbon():
    return {
        "unit": "mg CO2",
        "data": read_and_process_csv()
    }
