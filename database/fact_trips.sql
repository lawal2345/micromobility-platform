CREATE TABLE IF NOT EXISTS processed.fact_trips (
    trip_id             STRING NOT NULL,
    vehicle_id          STRING NOT NULL,
    user_id             STRING NOT NULL,
    start_location_id   STRING,
    end_location_id     STRING,
    started_at          TIMESTAMP NOT NULL,
    ended_at            TIMESTAMP NOT NULL,
    duration_minutes    FLOAT64 NOT NULL,
    distance_km         FLOAT64 NOT NULL,
    battery_start       INT64,
    battery_end         INT64,
    battery_consumed    INT64,
    avg_speed_kmh       FLOAT64,
    trip_date           DATE NOT NULL
)
PARTITION BY trip_date
CLUSTER BY vehicle_id;