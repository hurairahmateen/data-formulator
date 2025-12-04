resource "google_cloud_run_v2_service" "data_formulator" {
  name     = var.service_name
  location = var.region

  template {
    service_account = google_service_account.data_formulator_sa.email

    containers {
        image = var.image

        ports {
            container_port = 5000
        }

        env {
            name  = "FLASK_RUN_HOST"
            value = "0.0.0.0"
        }

        env {
            name  = "FLASK_RUN_PORT"
            value = "5000"
        }
    }
  }

  ingress = "INGRESS_TRAFFIC_ALL"
  
  depends_on = [
    google_project_service.required_apis,
    google_service_account.data_formulator_sa
  ]
}
