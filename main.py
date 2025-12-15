from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import csv
from collections import defaultdict
from datetime import datetime
import os
import asyncio

app = FastAPI()

# ---------- CORS ----------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------- CONFIG ----------
CSV_FILE = "/tmp/sensor_data.csv"   # Render-safe writable path
KG_TO_MG = 1_000_000
MAX_MINUTES = 100                   # ✅ SHOW LAST 100 MINUTES ONLY

# ---------- CACHE ----------
cached_minute_data = []


# --------
