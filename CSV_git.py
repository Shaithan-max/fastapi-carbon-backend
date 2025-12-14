import serial
import time
import csv
import os
import subprocess
import sys
import shutil  # to check if git exists

# ---------- CONFIG ----------
SERIAL_PORT = 'COM5'         # replace with your ESP32 port
BAUD_RATE = 115200
CSV_FILENAME = r"C:\Users\25sam\OneDrive\Desktop\GIT\sensor_data.csv"
DURATION = 10              # 60 seconds
# Optional: full path to git if not in PATH
GIT_PATH = r"C:\Program Files\Git\cmd\git.exe"  # adjust if needed
# ----------------------------

# -------- OPEN SERIAL --------
ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
print("Waiting for ESP32 to reboot...")
time.sleep(5)
ser.reset_input_buffer()

# -------- FILE CHECK --------
file_exists = os.path.isfile(CSV_FILENAME)

with open(CSV_FILENAME, 'a', newline='') as csvfile:
    csvwriter = csv.writer(csvfile)

    if not file_exists:
        csvwriter.writerow([
            'time',
            'current_A',
            'temp_C',
            'pressure_pct',
            'co2_shredding',
            'co2_heating',
            'co2_moulding',
            'co2_total'
        ])

    print(f"Recording started for {DURATION} seconds...")
    start_time = time.time()

    while time.time() - start_time < DURATION:
        line = ser.readline().decode('utf-8', errors='ignore').strip()
        if not line or line.startswith("time"):
            continue
        data = line.split(',')
        csvwriter.writerow(data)
        print(data)

        # --------- PROGRESS BAR ----------
        elapsed = int(time.time() - start_time)
        progress = int((elapsed / DURATION) * 50)
        bar = "[" + "#" * progress + "-" * (50 - progress) + "]"
        sys.stdout.write(f"\r{bar} {elapsed}/{DURATION} sec")
        sys.stdout.flush()

ser.close()
print("\nRecording finished.")

# ---------- PUSH TO GITHUB ----------
# Check if git exists
git_cmd = shutil.which("git") or GIT_PATH
if not git_cmd or not os.path.isfile(git_cmd):
    print("\nGit executable not found. Install Git or update PATH.")
else:
    try:
        subprocess.run([git_cmd, "add", CSV_FILENAME], check=True)
        subprocess.run([git_cmd, "commit", "-m", "Auto-update sensor data"], check=True)
        subprocess.run([git_cmd, "push", "origin", "main"], check=True)  # change branch if needed
        print("CSV updated and pushed to GitHub successfully!")
    except subprocess.CalledProcessError:
        print("Git push failed. Make sure repo is initialized and authentication is set up.")

