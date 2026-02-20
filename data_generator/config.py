# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# GCP settings
GCP_PROJECT_ID = os.getenv("GCP_PROJECT_ID")
GCS_BUCKET_NAME = os.getenv("GCS_BUCKET_NAME")

# Fleet settings
FLEET_SIZE = 20
VEHICLE_TYPES = ["e-scooter", "e-bike"]

# Geographic bounds — Derby city centre area
# These are real coordinates for Derby, UK 
LAT_MIN = 52.900
LAT_MAX = 52.940
LON_MIN = -1.510
LON_MAX = -1.450

# Simulation settings
PING_INTERVAL_SECONDS = 5      # how often each vehicle sends a location update
TRIP_DURATION_MIN = 5          # minimum trip length in minutes
TRIP_DURATION_MAX = 30         # maximum trip length in minutes
BATTERY_DRAIN_PER_MINUTE = 1   # battery % consumed per minute of riding