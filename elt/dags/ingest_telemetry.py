# ingest_telemetry.py
import os
import json
import logging
from datetime import datetime, timedelta
from google.cloud import storage, bigquery

from airflow import DAG
from airflow.operators.python import PythonOperator

# ── Configuration ──────────────────────────────────────────────
PROJECT_ID   = os.environ["GCP_PROJECT_ID"]
BUCKET_NAME  = os.environ["GCS_BUCKET_NAME"]
DATASET      = os.environ["BIGQUERY_DATASET"]
TABLE        = "raw_telemetry"
SOURCE_PREFIX = "telemetry/"
ARCHIVE_PREFIX = "processed/"

# ── Helper Functions ────────────────────────────────────────────

def list_new_files(**context):
    """Task 1: Scan Cloud Storage for unprocessed files"""
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    
    blobs = list(bucket.list_blobs(prefix=SOURCE_PREFIX))
    # Only pick up .json files
    files = [b.name for b in blobs if b.name.endswith(".json")]
    
    logging.info(f"Found {len(files)} files to process")
    
    # Pass file list to next task via XCom
    context["ti"].xcom_push(key="files_to_process", value=files)


def load_files_to_bigquery(**context):
    """Task 2: Load each JSON file into BigQuery raw_telemetry table"""
    files = context["ti"].xcom_pull(key="files_to_process")
    
    if not files:
        logging.info("No files to process. Skipping.")
        return
    
    storage_client = storage.Client(project=PROJECT_ID)
    bq_client = bigquery.Client(project=PROJECT_ID)
    bucket = storage_client.bucket(BUCKET_NAME)
    
    table_ref = f"{PROJECT_ID}.{DATASET}.{TABLE}"
    
    # Define the BigQuery schema matching our raw_telemetry table
    job_config = bigquery.LoadJobConfig(
        schema=[
            bigquery.SchemaField("event_id",      "STRING",    mode="REQUIRED"),
            bigquery.SchemaField("vehicle_id",    "STRING",    mode="REQUIRED"),
            bigquery.SchemaField("trip_id",       "STRING",    mode="NULLABLE"),
            bigquery.SchemaField("timestamp",     "TIMESTAMP", mode="REQUIRED"),
            bigquery.SchemaField("latitude",      "FLOAT64",   mode="REQUIRED"),
            bigquery.SchemaField("longitude",     "FLOAT64",   mode="REQUIRED"),
            bigquery.SchemaField("speed_kmh",     "FLOAT64",   mode="NULLABLE"),
            bigquery.SchemaField("battery_level", "INTEGER",   mode="NULLABLE"),
            bigquery.SchemaField("event_type",    "STRING",    mode="REQUIRED"),
            bigquery.SchemaField("vehicle_type",  "STRING",    mode="NULLABLE"),
        ],
        source_format=bigquery.SourceFormat.NEWLINE_DELIMITED_JSON,
        write_disposition=bigquery.WriteDisposition.WRITE_APPEND,
    )
    
    rows_loaded = 0
    for filename in files:
        # Read the file from Cloud Storage
        blob = bucket.blob(filename)
        content = json.loads(blob.download_as_text())
        
        # BigQuery expects newline-delimited JSON, not a JSON array
        # So we convert the array into one JSON object per line
        ndjson = "\n".join(json.dumps(row) for row in content)
        
        # Load into BigQuery
        job = bq_client.load_table_from_file(
            file_obj=__import__('io').StringIO(ndjson),
            destination=table_ref,
            job_config=job_config
        )
        job.result()  # Wait for job to complete
        rows_loaded += len(content)
        logging.info(f"Loaded {filename} → {len(content)} rows")
    
    logging.info(f"Total rows loaded: {rows_loaded}")
    context["ti"].xcom_push(key="files_processed", value=files)


def archive_files(**context):
    """Task 3: Move processed files to archive folder"""
    files = context["ti"].xcom_pull(key="files_processed")
    
    if not files:
        return
    
    client = storage.Client(project=PROJECT_ID)
    bucket = client.bucket(BUCKET_NAME)
    
    for filename in files:
        # Copy to processed/ folder
        source_blob = bucket.blob(filename)
        new_name = filename.replace(SOURCE_PREFIX, ARCHIVE_PREFIX)
        bucket.copy_blob(source_blob, bucket, new_name)
        # Delete original
        source_blob.delete()
        logging.info(f"Archived {filename} → {new_name}")


# ── DAG Definition ──────────────────────────────────────────────

default_args = {
    "owner": "lawal",
    "retries": 1,
    "retry_delay": timedelta(minutes=2),
}

with DAG(
    dag_id="ingest_telemetry",
    description="Load raw telemetry from Cloud Storage into BigQuery",
    schedule_interval="*/5 * * * *",  # every 5 minutes
    start_date=datetime(2026, 2, 14),
    catchup=False,
    default_args=default_args,
) as dag:

    task_list_files = PythonOperator(
        task_id="list_new_files",
        python_callable=list_new_files,
    )

    task_load_bq = PythonOperator(
        task_id="load_to_bigquery",
        python_callable=load_files_to_bigquery,
    )

    task_archive = PythonOperator(
        task_id="archive_files",
        python_callable=archive_files,
    )

    # Define the order
    task_list_files >> task_load_bq >> task_archive