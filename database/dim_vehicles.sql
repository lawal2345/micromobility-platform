CREATE TABLE IF NOT EXISTS processed.dim_vehicles (
    vehicle_id          STRING NOT NULL,
    vehicle_type        STRING NOT NULL,
    model               STRING,
    manufacture_year    INT64,
    registered_date     DATE NOT NULL,
    status              STRING NOT NULL,
    current_battery     INT64,
    last_seen_at        TIMESTAMP,
    last_latitude       FLOAT64,
    last_longitude      FLOAT64
);