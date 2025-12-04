resource "google_artifact_registry_repository" "repo" {
  provider      = google
  location      = var.region
  repository_id = local.artifact_repo
  description   = "Docker repo for Data Formulator"
  format        = "DOCKER"
}