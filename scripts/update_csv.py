import csv
import time
import random
import os

FILE = "sensor_data.csv"

file_exists = os.path.exists(FILE)

with open(FILE, "a", newline="") as f:
    writer = csv.writer(f)

    # Write header only once
    if not file_exists:
        writer.writerow([
            "time",
            "current_A",
            "temp_C",
            "pressure_i",
            "co2_shred",
            "co2_heati",
            "co2_mould",
            "co2_total"
        ])

    # Simulated sensor values
    current = round(random.uniform(0.1, 0.6), 3)
    temp = round(random.uniform(31.0, 33.0), 2)
    pressure = random.randint(0, 65)

    # Simple carbon calculations (demo logic)
    co2_shred = round(pressure * 4e-09, 9)
    co2_heati = round(temp * 3.3e-05, 6)
    co2_mould = round(current * 1e-06, 9)
    co2_total = round(co2_shred + co2_heati + co2_mould, 6)

    writer.writerow([
        int(time.time()),
        current,
        temp,
        pressure,
        co2_shred,
        co2_heati,
        co2_mould,
        co2_total
    ])
