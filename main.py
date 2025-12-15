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

            # Use each timestamp as-is (per second)
            second_data.append({
                "timestamp": ts,
                "shredding_carbon_mg": round(float(row["co2_shred"]) * KG_TO_MG, 6),
                "heating_carbon_mg": round(float(row["co2_heating"]) * KG_TO_MG, 6),
                "pressure_carbon_mg": round(float(row["co2_mould"]) * KG_TO_MG, 6),
                "total_carbon_mg": round(float(row["co2_total"]) * KG_TO_MG, 6)
            })

    # Sort by timestamp
    second_data.sort(key=lambda x: x["timestamp"])

    # Format timestamp as "YYYY-MM-DD HH:MM:SS" for frontend
    for item in second_data:
        item["minute"] = datetime.fromtimestamp(item["timestamp"]).strftime("%Y-%m-%d %H:%M:%S")

    return second_data
