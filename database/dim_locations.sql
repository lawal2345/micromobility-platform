CREATE TABLE IF NOT EXISTS processed.dim_locations (
    location_id             STRING NOT NULL,
    zone_name               STRING NOT NULL,
    zone_type               STRING,
    centroid_latitude       FLOAT64 NOT NULL,
    centroid_longitude      FLOAT64 NOT NULL,
    zone_radius_meters      INT64
);