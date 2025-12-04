resource "google_service_account" "data_formulator_sa" {
  account_id   = "data-formulator-sa"
  display_name = "Data Formulator Cloud Run Service Account"
}