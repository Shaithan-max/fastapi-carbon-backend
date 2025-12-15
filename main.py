from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
import os
from datetime import datetime

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CONFIG ----------
CSV_FILE = "/tmp/sensor_data.csv"   # Render writable path
KG_TO_MG = 1_000_000


# ---------- DATA MODEL ----------
class SensorData(BaseModel):
    time: int
    current_A: float
    temp_C: float
    pressure: float
    co2_shred: float
    co2_heating: float
    co2_mould: float
    co2_total: float


# ---------- RECEIVE SENSOR DATA ----------
@app.post("/sensor-data")
def receive_sensor_data(data: SensorData):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as file:
        writer = csv.writer(file)

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


# ---------- GET ALL DATA ----------
@app.get("/carbon-footprint")
def get_all_data():
    if not os.path.exists(CSV_FILE):
        return {"unit": "mg CO2", "data": []}

    result = []

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            ts = int(row["time"])

            # skip invalid timestamps
            if ts < 1_000_000_000:
                continue

            result.append({
                "time": datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M:%S"),
                "shredding_carbon_mg": float(row["co2_shred"]) * KG_TO_MG,
                "heating_carbon_mg": float(row["co2_heating"]) * KG_TO_MG,
                "pressure_carbon_mg": float(row["co2_mould"]) * KG_TO_MG,
                "total_carbon_mg": float(row["co2_total"]) * KG_TO_MG
            })

    return {"unit": "mg CO2", "data": result}


# ---------- ROOT ----------
@app.get("/")
def root():
    return {"status": "Carbon Footprint API running"}
