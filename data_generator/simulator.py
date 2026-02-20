# simulator.py
import json
import time
import random
from datetime import datetime, timezone
from google.cloud import storage
from vehicles import Vehicle
from config import (
    GCP_PROJECT_ID, GCS_BUCKET_NAME, FLEET_SIZE,
    PING_INTERVAL_SECONDS, TRIP_DURATION_MIN, TRIP_DURATION_MAX
)

def upload_to_gcs(bucket, events):
    """Write a batch of events as a JSON file to Cloud Storage"""
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    filename = f"telemetry/raw_{timestamp}.json"
    blob = bucket.blob(filename)
    blob.upload_from_string(
        json.dumps(events, indent=2),
        content_type="application/json"
    )
    print(f"Uploaded {len(events)} events to gs://{GCS_BUCKET_NAME}/{filename}")

def run_simulation():
    # Connect to GCS
    client = storage.Client(project=GCP_PROJECT_ID)
    bucket = client.bucket(GCS_BUCKET_NAME)

    # Create the fleet
    fleet = [Vehicle(f"V{str(i).zfill(3)}") for i in range(1, FLEET_SIZE + 1)]
    trip_timers = {v.vehicle_id: 0 for v in fleet}

    print(f"Starting simulation with {FLEET_SIZE} vehicles...")

    while True:
        batch = []

        for vehicle in fleet:
            if vehicle.status == "available":
                # 20% chance a trip starts each cycle
                if random.random() < 0.2 and vehicle.battery > 20:
                    event = vehicle.start_trip()
                    trip_timers[vehicle.vehicle_id] = random.randint(
                        TRIP_DURATION_MIN * 12,
                        TRIP_DURATION_MAX * 12
                    )
                    batch.append(event)

            elif vehicle.status == "in_use":
                # Move the vehicle and record location
                event = vehicle.move()
                batch.append(event)

                # Count down trip timer
                trip_timers[vehicle.vehicle_id] -= 1
                if trip_timers[vehicle.vehicle_id] <= 0:
                    end_event = vehicle.end_trip()
                    batch.append(end_event)

        if batch:
            upload_to_gcs(bucket, batch)

        time.sleep(PING_INTERVAL_SECONDS)

if __name__ == "__main__":
    run_simulation()