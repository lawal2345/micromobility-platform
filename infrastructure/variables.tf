variable "project_id" {
    description = "GCP project ID"
    type        = string
}

variable "region" {
    description = "GCP region"
    type        = string
    default     = "europe-west2"
}

variable "data_bucket_name" {
    description = "Cloud Storage bucket for raw telemetry data"
    type        = string
}

# We use europe-west2 (London) because we're in Derby