terraform {
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Cloud Storage bucket - raw telemetry data lands here
resource "google_storage_bucket" "raw_data" {
  name          = var.data_bucket_name
  location      = "EU"
  force_destroy = true
}

# BigQuery dataset - raw schema (untouched incoming data)
resource "google_bigquery_dataset" "raw" {
  dataset_id  = "raw"
  description = "Raw telemetry data loaded directly from Cloud Storage"
  location    = "EU"
}

# BigQuery dataset - processed schema (clean dbt models)
resource "google_bigquery_dataset" "processed" {
  dataset_id  = "processed"
  description = "Cleaned and transformed data models built by dbt"
  location    = "EU"
}

# Service account for our application
resource "google_service_account" "micromobility_sa" {
  account_id   = "micromobility-sa"
  display_name = "Micro-Mobility Platform Service Account"
}

# Give the service account permissions it needs
resource "google_project_iam_member" "sa_bigquery_admin" {
  project = var.project_id
  role    = "roles/bigquery.admin"
  member  = "serviceAccount:${google_service_account.micromobility_sa.email}"
}

resource "google_project_iam_member" "sa_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.micromobility_sa.email}"
}

# Create and download a key for the service account
resource "google_service_account_key" "micromobility_sa_key" {
  service_account_id = google_service_account.micromobility_sa.name
}

# Save the key locally
resource "local_file" "sa_key_file" {
  content  = base64decode(google_service_account_key.micromobility_sa_key.private_key)
  filename = "${path.module}/../.env.json"
}