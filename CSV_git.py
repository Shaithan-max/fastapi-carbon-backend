import serial
import time
import csv
import os
import subprocess
import sys
import shutil

# ---------- CONFIG ----------
SERIAL_PORT = 'COM5'  # replace with your ESP32 port
BAUD_RATE = 115200
CSV_FILENAME = r"C:\Users\25sam\OneDrive\Desktop\GIT\sensor_data.csv"
DURATION = 5  # seconds to log
BRANCH_NAME = "master"  # use master branch
GIT_PATH = r"C:\Program Files\Git\cmd\git.exe"  # optional: full path to git
# ----------------------------

# -------- OPEN SERIAL --------
try:
    ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=2)
except Exception as e:
    print(f"Error opening serial port: {e}")
    sys.exit(1)

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
git_cmd = shutil.which("git") or GIT_PATH
if not git_cmd or not os.path.isfile(git_cmd):
    print("Git executable not found. Install Git or update PATH.")
else:
    try:
        # Add and commit CSV changes
        subprocess.run([git_cmd, "add", CSV_FILENAME], check=True)
        subprocess.run([git_cmd, "commit", "-m", "Auto-update sensor data"], check=True)
        # Push to master
        subprocess.run([git_cmd, "push", "origin", BRANCH_NAME], check=True)
        print("CSV updated and pushed to GitHub successfully!")
    except subprocess.CalledProcessError:
        print("Git push failed. Make sure the repository is initialized, branch exists, and authentication is set up.")
