from fastapi import FastAPI, HTTPException
from google.cloud import bigquery
from google.oauth2 import service_account
import os

# ── App setup ─────────────────────────────────────────────────────────────────
app = FastAPI(
    title="Micro-Mobility Platform API",
    description="Serves processed telemetry data from BigQuery",
    version="1.0.0"
)

# ── BigQuery client ────────────────────────────────────────────────────────────
KEY_PATH = os.path.join(os.path.dirname(__file__), "..", ".env.json")

if os.path.exists(KEY_PATH):
    # Running locally — use service account file
    credentials = service_account.Credentials.from_service_account_file(KEY_PATH)
    client = bigquery.Client(credentials=credentials, project="micromobility-platform")
else:
    # Running on Cloud Run — use GCP's built-in identity
    client = bigquery.Client(project="micromobility-platform")

DATASET = "processed"   # the dataset where dbt wrote your mart tables

# ── Helper: run a query and return rows as list of dicts ───────────────────────
def run_query(sql: str):
    query_job = client.query(sql)
    results = query_job.result()
    return [dict(row) for row in results]


# ── Routes ─────────────────────────────────────────────────────────────────────

@app.get("/")
def root():
    return {"status": "ok", "message": "Micro-Mobility API is running"}


@app.get("/vehicles")
def get_vehicles():
    """All vehicles with their current status and battery level."""
    sql = f"""
        SELECT
            vehicle_id,
            vehicle_type,
            current_battery_pct,
            current_status,
            CAST(last_seen_at AS STRING) AS last_seen_at
        FROM `micromobility-platform.{DATASET}.dim_vehicles`
        ORDER BY vehicle_id
    """
    return run_query(sql)


@app.get("/trips")
def get_trips(limit: int = 100):
    """Recent trips from the fact table."""
    sql = f"""
        SELECT
            trip_id,
            vehicle_id,
            CAST(trip_start_at AS STRING) AS trip_start_at,
            CAST(trip_end_at   AS STRING) AS trip_end_at,
            duration_minutes,
            avg_speed_kmh,
            max_speed_kmh,
            battery_consumed_pct,
            CAST(trip_date AS STRING) AS trip_date
        FROM `micromobility-platform.{DATASET}.fct_trips`
        ORDER BY trip_start_at DESC
        LIMIT {limit}
    """
    return run_query(sql)


@app.get("/analytics/summary")
def get_summary():
    """High-level KPIs for the dashboard header."""
    sql = f"""
        SELECT
            COUNT(*)                        AS total_trips,
            ROUND(AVG(duration_minutes), 1) AS avg_duration_minutes,
            ROUND(AVG(avg_speed_kmh), 1)    AS avg_speed_kmh,
            ROUND(AVG(battery_consumed_pct),1) AS avg_battery_consumed_pct
        FROM `micromobility-platform.{DATASET}.fct_trips`
    """
    rows = run_query(sql)
    return rows[0] if rows else {}


@app.get("/analytics/demand")
def get_demand_by_hour():
    """Trip count grouped by hour of day — for the demand chart."""
    sql = f"""
        SELECT
            EXTRACT(HOUR FROM trip_start_at) AS hour_of_day,
            COUNT(*)                          AS trip_count
        FROM `micromobility-platform.{DATASET}.fct_trips`
        GROUP BY hour_of_day
        ORDER BY hour_of_day
    """
    return run_query(sql)