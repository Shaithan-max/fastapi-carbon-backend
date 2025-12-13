from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import csv
from collections import defaultdict
from datetime import datetime
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
CSV_FILE = os.path.join(BASE_DIR, "sensor_data.csv")


def read_and_process_csv():
    hourly_data = defaultdict(lambda: {
        "shred_cf": 0.0,
        "heat_cf": 0.0,
        "pressure_cf": 0.0
    })

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)

        for row in reader:
            timestamp = int(row["time"])
            hour = datetime.fromtimestamp(timestamp).replace(
                minute=0, second=0, microsecond=0
            )

            shred_cf = float(row["co2_shred"])
            heat_cf = float(row["co2_heating"])
            pressure_cf = float(row["co2_mould"])

            hourly_data[hour]["shred_cf"] += shred_cf
            hourly_data[hour]["heat_cf"] += heat_cf
            hourly_data[hour]["pressure_cf"] += pressure_cf

    result = []
    for hour, values in sorted(hourly_data.items()):
        total = (
            values["shred_cf"]
            + values["heat_cf"]
            + values["pressure_cf"]
        )

        result.append({
            "hour": hour.strftime("%Y-%m-%d %H:00"),
            "shredding_carbon": round(values["shred_cf"], 6),
            "heating_carbon": round(values["heat_cf"], 6),
            "pressure_carbon": round(values["pressure_cf"], 6),
            "total_carbon": round(total, 6)
        })

    return result


@app.get("/")
def root():
    return {"status": "Carbon Footprint API is running"}


@app.get("/carbon-footprint/hourly")
def get_hourly_carbon():
    return {
        "unit": "kg CO2",
        "data": read_and_process_csv()
    }
