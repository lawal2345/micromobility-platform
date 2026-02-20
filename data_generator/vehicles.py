# vehicles.py
import uuid
import random
from datetime import datetime, timezone
from config import (
    VEHICLE_TYPES, LAT_MIN, LAT_MAX, LON_MIN, LON_MAX,
    BATTERY_DRAIN_PER_MINUTE
)

class Vehicle:
    def __init__(self, vehicle_id):
        self.vehicle_id = vehicle_id
        self.vehicle_type = random.choice(VEHICLE_TYPES)
        self.battery = random.randint(60, 100)  # start reasonably charged
        self.latitude = random.uniform(LAT_MIN, LAT_MAX)
        self.longitude = random.uniform(LON_MIN, LON_MAX)
        self.status = "available"
        self.trip_id = None

    def start_trip(self):
        """Called when a user unlocks this vehicle"""
        self.status = "in_use"
        self.trip_id = str(uuid.uuid4())
        return self._build_event("trip_start")

    def end_trip(self):
        """Called when a user parks this vehicle"""
        self.status = "available"
        event = self._build_event("trip_end")
        self.trip_id = None
        return event

    def move(self):
        """Simulate movement — small random change in coordinates"""
        self.latitude += random.uniform(-0.001, 0.001)
        self.longitude += random.uniform(-0.001, 0.001)

        # Keep within Derby bounds
        self.latitude = max(LAT_MIN, min(LAT_MAX, self.latitude))
        self.longitude = max(LON_MIN, min(LON_MAX, self.longitude))

        # Drain battery while moving
        self.battery -= BATTERY_DRAIN_PER_MINUTE / 12  # per 5-second ping
        self.battery = max(0, round(self.battery, 1))

        return self._build_event("location_update")

    def _build_event(self, event_type):
        """Build a JSON-ready dictionary for this event"""
        return {
            "event_id": str(uuid.uuid4()),
            "vehicle_id": self.vehicle_id,
            "trip_id": self.trip_id,
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "latitude": round(self.latitude, 6),
            "longitude": round(self.longitude, 6),
            "speed_kmh": round(random.uniform(8, 25), 1) if self.status == "in_use" else 0,
            "battery_level": int(self.battery),
            "event_type": event_type,
            "vehicle_type": self.vehicle_type
        }