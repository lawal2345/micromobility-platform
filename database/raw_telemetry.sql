CREATE TABLE IF NOT EXISTS raw.raw_telemetry (
    event_id        STRING NOT NULL,
    vehicle_id      STRING NOT NULL,
    timestamp       TIMESTAMP NOT NULL,
    latitude        FLOAT64 NOT NULL,
    longitude       FLOAT64 NOT NULL,
    speed_kmh       FLOAT64,
    battery_level   INT64,
    event_type      STRING NOT NULL,
    raw_payload     STRING,
    loaded_at       TIMESTAMP NOT NULL
);