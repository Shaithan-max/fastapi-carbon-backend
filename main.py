from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from collections import defaultdict
from datetime import datetime
import os

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")

KG_TO_MG = 1_000_000


class SensorData(BaseModel):
    time: int
    current_A: float
    temp_C: float
    pressure: float
    co2_shred: float
    co2_heating: float
    co2_mould: float
    co2_total: float


def read_and_process_csv():
    minute_data = defaultdict(lambda: {
        "shred": 0.0,
        "heat": 0.0,
        "pressure": 0.0
    })

    if not os.path.exists(CSV_FILE):
        return []

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)
        for row in reader:
            ts = int(row["time"])
            minute = datetime.fromtimestamp(ts).replace(second=0, microsecond=0)

            minute_data[minute]["shred"] += float(row["co2_shred"])
            minute_data[minute]["heat"] += float(row["co2_heating"])
            minute_data[minute]["pressure"] += float(row["co2_mould"])

    result = []
    for minute, v in sorted(minute_data.items()):
        total = v["shred"] + v["heat"] + v["pressure"]

        result.append({
            "minute": minute.strftime("%Y-%m-%d %H:%M"),
            "shredding_carbon_mg": round(v["shred"] * KG_TO_MG, 6),
            "heating_carbon_mg": round(v["heat"] * KG_TO_MG, 6),
            "pressure_carbon_mg": round(v["pressure"] * KG_TO_MG, 6),
            "total_carbon_mg": round(total * KG_TO_MG, 6)
        })

    return result


@app.post("/sensor-data")
def receive_sensor_data(data: SensorData):
    file_exists = os.path.exists(CSV_FILE)

    with open(CSV_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if not file_exists:
            writer.writerow([
                "time", "current_A", "temp_C", "pressure",
                "co2_shred", "co2_heating", "co2_mould", "co2_total"
            ])
        writer.writerow([
            data.time, data.current_A, data.temp_C, data.pressure,
            data.co2_shred, data.co2_heating, data.co2_mould, data.co2_total
        ])

    return {"status": "minute data saved"}


@app.get("/carbon-footprint/minute")
def get_minute_carbon():
    return {
        "unit": "mg CO2",
        "data": read_and_process_csv()
    }


@app.get("/")
def root():
    return {"status": "Carbon Footprint API running (live CSV read)"}
