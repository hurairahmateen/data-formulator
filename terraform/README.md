# Data Formulator Infrastructure (Terraform Deployment)

This folder contains the Terraform configuration used to deploy **Data Formulator** to **Google Cloud Run**, including all supporting infrastructure such as Artifact Registry, IAM roles, and the service configuration.

---

## Overview

This Terraform setup accomplishes the following:

### 1. Deploys Data Formulator on Google Cloud Run
- Builds and runs a containerized Flask backend with a Vite-built frontend
- Cloud Run executes the container on port **8080** (configurable via `PORT` environment variable)
- Supports both public and private access configurations

### 2. Creates an Artifact Registry repository
Used to store and version Docker images for Cloud Run.

Repository path example:
```
us-central1-docker.pkg.dev/<project-id>/<project-id>-repo/data-formulator
```

### 3. Creates a Cloud Run Service Account
- Service account: `data-formulator-sa`
- Granted permissions:
  - `roles/artifactregistry.reader` - Allows Cloud Run to pull images from Artifact Registry

### 4. Enables required Google Cloud APIs
Terraform automatically enables:
- Cloud Run API (`run.googleapis.com`)
- Artifact Registry API (`artifactregistry.googleapis.com`)
- IAM API (`iam.googleapis.com`)

### 5. Configures IAM access to the deployed service
The service currently allows:
- `domain:napster.com` - Domain-specific access
- `allUsers` - Public access (can be removed for private deployment)

These permissions can be updated later using `gcloud` commands or Terraform.

---

## Prerequisites

1. **Google Cloud Project** with billing enabled
2. **Docker** installed locally
3. **Terraform** >= 1.6.0 installed
4. **gcloud CLI** configured with appropriate permissions:
   ```bash
   gcloud auth login
   gcloud config set project <your-project-id>
   gcloud auth configure-docker us-central1-docker.pkg.dev
   ```

---

## Deployment Steps

### 1. Build the Docker Image
From the project root directory:
```bash
docker build -t data-formulator .
```

### 2. Tag and Push the Image
```bash
# Replace <project-id> with your actual Google Cloud project ID
docker tag data-formulator \
  us-central1-docker.pkg.dev/<project-id>/<project-id>-repo/data-formulator:latest

docker push \
  us-central1-docker.pkg.dev/<project-id>/<project-id>-repo/data-formulator:latest
```

### 3. Configure Terraform Variables
Update `envs/dev/terraform.tfvars` with your project details:
```hcl
project_id   = "your-project-id"
region       = "us-central1"
service_name = "data-formulator"
image        = "us-central1-docker.pkg.dev/your-project-id/your-project-id-repo/data-formulator:latest"
```

### 4. Apply Terraform Configuration
```bash
cd terraform
terraform init
terraform apply -var-file=envs/dev/terraform.tfvars
```

Terraform will:
- Create all necessary resources
- Deploy the Cloud Run service
- Output the service URL

### 5. Access Your Deployment
After successful deployment, access your Data Formulator instance at the URL provided in the Terraform output.

---

## Configuration Files

### `terraform.tfvars`
Contains environment-specific variables:
```hcl
project_id   = "genai-analytics-435321"
region       = "us-central1" 
service_name = "data-formulator"
image        = "us-central1-docker.pkg.dev/genai-analytics-435321/genai-analytics-435321-repo/data-formulator:latest"
```

### `cloudrun.tf`
- Defines Cloud Run service configuration
- Sets ingress rules, ports, and environment variables
- Configures service account and dependencies

### `artifact-registry.tf`
- Creates a Docker-format Artifact Registry repository
- Stores versioned container images

### `iam.tf`
- Creates the Cloud Run service account
- Grants Artifact Registry read access

### `provider.tf`
- Initializes Google Cloud provider
- Enables required Google Cloud APIs

### `outputs.tf`
- Outputs Cloud Run service URL after deployment

---

## Post-Deployment Configuration

### Configure AI Model Access
Set environment variables for AI models:
```bash
gcloud run services update data-formulator \
  --region=us-central1 \
  --set-env-vars="OPENAI_API_KEY=your-key,OPENAI_MODELS=gpt-4,gpt-3.5-turbo"
```

### Monitor the Service
```bash
# Check service status
gcloud run services describe data-formulator --region=us-central1

# View logs
gcloud run services logs tail data-formulator --region=us-central1

# Check IAM policies
gcloud run services get-iam-policy data-formulator --region=us-central1
```

### Make Service Private (Optional)
To restrict access and remove public access:
```bash
# Remove public access
gcloud run services remove-iam-policy-binding data-formulator \
  --region=us-central1 \
  --member="allUsers" \
  --role="roles/run.invoker"

# Update Terraform to use internal-only ingress
# In cloudrun.tf, change: ingress = "INGRESS_TRAFFIC_INTERNAL_ONLY"
```

---

## Troubleshooting

### Common Issues

1. **"No module named data_formulator"**
   - Ensure the Docker image was built correctly with all dependencies
   - Check that `PYTHONPATH` is set correctly in the Dockerfile

2. **Port mismatch errors**
   - Cloud Run expects port 8080 by default
   - Ensure your application respects the `PORT` environment variable

3. **Permission denied errors**
   - Verify service account has correct IAM roles
   - Check that Artifact Registry permissions are properly configured

### Useful Commands
```bash
# View detailed service information
gcloud run services describe data-formulator --region=us-central1

# Test service connectivity
curl -H "Authorization: Bearer $(gcloud auth print-access-token)" \
  https://your-service-url

# View recent logs
gcloud logging read "resource.type=cloud_run_revision AND resource.labels.service_name=data-formulator" --limit=50
```

---

## Cleanup

To destroy all resources created by this Terraform configuration:
```bash
terraform destroy -var-file=envs/dev/terraform.tfvars
```

**Warning**: This will permanently delete all resources including the Cloud Run service, Artifact Registry repository, and service accounts.