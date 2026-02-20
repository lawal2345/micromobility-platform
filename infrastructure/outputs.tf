output "bucket_name" {
  value       = google_storage_bucket.raw_data.name
  description = "Cloud Storage bucket for raw data"
}

output "service_account_email" {
  value       = google_service_account.micromobility_sa.email
  description = "Service account email"
}