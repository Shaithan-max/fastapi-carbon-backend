from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from collections import defaultdict
from datetime import datetime

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

KG_TO_MG = 1_000_000

# 🔹 IN-MEMORY STORE
minute_data = defaultdict(lambda: {
    "shred": 0.0,
    "heat": 0.0,
    "pressure": 0.0
})


class SensorData(BaseModel):
    time: int
    current_A: float
    temp_C: float
    pressure: float
    co2_shred: float
    co2_heating: float
    co2_mould: float
    co2_total: float


@app.post("/sensor-data")
def receive_sensor_data(data: SensorData):
    minute = datetime.fromtimestamp(data.time).replace(second=0, microsecond=0)

    minute_data[minute]["shred"] += data.co2_shred
    minute_data[minute]["heat"] += data.co2_heating
    minute_data[minute]["pressure"] += data.co2_mould

    return {"status": "minute data saved"}


@app.get("/carbon-footprint/minute")
def get_minute_carbon():
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

    return {
        "unit": "mg CO2",
        "data": result
    }


@app.delete("/reset-data")
def reset_data():
    minute_data.clear()
    return {"status": "All in-memory data cleared"}


@app.get("/")
def root():
    return {"status": "Carbon Footprint API running (in-memory storage)"}
