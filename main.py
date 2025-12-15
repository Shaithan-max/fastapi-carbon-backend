from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from collections import defaultdict
from datetime import datetime
import os
import asyncio

app = FastAPI()

# -------- CORS --------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------- CSV PATH --------
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")

# -------- CACHE --------
cached_minute_data = []


# -------- SENSOR DATA MODEL --------
class SensorData(BaseModel):
    time: int
    current_A: float
    temp_C: float
    pressure: float
    co2_shred: float
    co2_heating: float
    co2_mould: float
    co2_total: float


# -------- READ & AGGREGATE (MINUTE-WISE) --------
def read_and_process_csv():
    minute_data = defaultdict(lambda: {
        "shred_cf": 0.0,
        "heat_cf": 0.0,
        "pressure_cf": 0.0
    })

    if not os.path.exists(CSV_FILE):
        return []

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            timestamp = int(row["time"])
            minute = datetime.fromtimestamp(timestamp).replace(
                second=0, microsecond=0
            )

            minute_data[minute]["shred_cf"] += float(row["co2_shred"])
            minute_data[minute]["heat_cf"] += float(row["co2_heating"])
            minute_data[minute]["pressure_cf"] += float(row["co2_mould"])

    result = []
    for minute, values in sorted(minute_data.items()):
        total = (
            values["shred_cf"]
            + values["heat_cf"]
            + values["pressure_cf"]
        )

        result.append({
            "minute": minute.strftime("%Y-%m-%d %H:%M"),
            "shredding_carbon": round(values["shred_cf"], 6),
            "heating_carbon": round(values["heat_cf"], 6),
            "pressure_carbon": round(values["pressure_cf"], 6),
            "total_carbon": round(total, 6)
        })

    return result


# -------- RECEIVE SENSOR DATA --------
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

    return {"status": "minute data saved"}


# -------- BACKGROUND CACHE UPDATE --------
async def update_cache_every_minute():
    global cached_minute_data
    while True:
        cached_minute_data = read_and_process_csv()
        await asyncio.sleep(60)


@app.on_event("startup")
async def startup_event():
    asyncio.create_task(update_cache_every_minute())


# -------- API --------
@app.get("/")
def root():
    return {"status": "Carbon Footprint API running (minute-wise)"}


@app.get("/carbon-footprint/minute")
def get_minute_carbon():
    return {
        "unit": "kg CO2",
        "updated_every": "1 minute",
        "data": cached_minute_data
    }
