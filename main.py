from fastapi import FastAPI
import csv
from collections import defaultdict
from datetime import datetime

app = FastAPI()

CSV_FILE = "sensor_data.csv"

HEAT_FACTOR = 0.2
PRESSURE_FACTOR = 0.00005
FLUX_FACTOR = 0.1


def read_and_process_csv():
    hourly_data = defaultdict(lambda: {
        "heat_cf": 0,
        "pressure_cf": 0,
        "flux_cf": 0
    })

    with open(CSV_FILE, newline="") as file:
        reader = csv.DictReader(file)  # ✅ IMPORTANT

        for row in reader:
            timestamp = int(row["timestamp"])
            heat = float(row["heat"])
            pressure = float(row["pressure"])
            flux = float(row["flux"])

            hour = datetime.fromtimestamp(timestamp).strftime("%Y-%m-%d %H:00")

            hourly_data[hour]["heat_cf"] += heat * HEAT_FACTOR
            hourly_data[hour]["pressure_cf"] += pressure * PRESSURE_FACTOR
            hourly_data[hour]["flux_cf"] += flux * FLUX_FACTOR

    result = []
    for hour, values in hourly_data.items():
        result.append({
            "hour": hour,
            "heat_carbon": round(values["heat_cf"], 2),
            "pressure_carbon": round(values["pressure_cf"], 2),
            "flux_carbon": round(values["flux_cf"], 2),
            "total_carbon": round(
                values["heat_cf"]
                + values["pressure_cf"]
                + values["flux_cf"], 2
            )
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
