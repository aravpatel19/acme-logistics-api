# Terraform configuration for Railway deployment
# This sets up the Acme Logistics API with automatic HTTPS

terraform {
  required_providers {
    railway = {
      source  = "terraform-community-providers/railway"
      version = "0.6.0"
    }
  }
}

# Configure the Railway provider
# You'll need to set the RAILWAY_TOKEN environment variable
# Get your token from: https://railway.app/account/tokens
provider "railway" {
  # Token is read from RAILWAY_TOKEN env var
}

# Create the main project
resource "railway_project" "acme_logistics" {
  name        = "acme-logistics-api"
  description = "Automated inbound carrier sales API for Acme Logistics"
  private     = true  # Keep project private
}

# Create the API service
resource "railway_service" "api" {
  name       = "api"
  project_id = railway_project.acme_logistics.id
  
  # Railway will automatically detect and use our Dockerfile
  source_repo        = "https://github.com/aravpatel19/acme-logistics-api"
  source_repo_branch = "main"
  
  # If you're not using GitHub, you can deploy from local with Railway CLI instead
}

# Create persistent volume for metrics data
resource "railway_volume" "metrics_storage" {
  name       = "metrics-data"
  project_id = railway_project.acme_logistics.id
  service_id = railway_service.api.id
  mount_path = "/app/api/data"
  size_gb    = 1  # 1GB is plenty for JSON metrics
}

# Create the dashboard service (optional)
resource "railway_service" "dashboard" {
  name       = "dashboard"
  project_id = railway_project.acme_logistics.id
  
  source_repo        = "https://github.com/aravpatel19/acme-logistics-api"
  source_repo_branch = "main"
  root_directory     = "dashboard"  # Dashboard is in a subdirectory
}

# Configure environment variables for the API service
resource "railway_variable_collection" "api_env" {
  environment_id = railway_project.acme_logistics.default_environment.id
  service_id     = railway_service.api.id

  variables = [
    {
      name  = "ACME_API_KEY"
      value = var.acme_api_key  # We'll define this as a variable
    },
    {
      name  = "FMCSA_API_KEY"
      value = var.fmcsa_api_key
    },
    {
      name  = "FMCSA_BASE_URL"
      value = "https://mobile.fmcsa.dot.gov/qc/services"
    },
    {
      name  = "PORT"
      value = "8000"
    },
    {
      name  = "HOST"
      value = "0.0.0.0"
    }
  ]
}

# Create a Railway subdomain for the API
# This automatically gets HTTPS with Let's Encrypt!
resource "railway_service_domain" "api_domain" {
  subdomain      = "acme-logistics-api"  # Will be: acme-logistics-api.up.railway.app
  environment_id = railway_project.acme_logistics.default_environment.id
  service_id     = railway_service.api.id
}

# Create a Railway subdomain for the dashboard
resource "railway_service_domain" "dashboard_domain" {
  subdomain      = "acme-logistics-dashboard"
  environment_id = railway_project.acme_logistics.default_environment.id
  service_id     = railway_service.dashboard.id
}

# Optional: Add a custom domain if you have one
# resource "railway_custom_domain" "api_custom" {
#   domain         = "api.acme-logistics.com"
#   environment_id = railway_project.acme_logistics.default_environment.id
#   service_id     = railway_service.api.id
# }

# Outputs - these will show after terraform apply
output "api_url" {
  value       = "https://${railway_service_domain.api_domain.domain}"
  description = "The HTTPS URL for your API (automatically secured with Let's Encrypt)"
}

output "dashboard_url" {
  value       = "https://${railway_service_domain.dashboard_domain.domain}"
  description = "The HTTPS URL for your dashboard"
}

output "project_id" {
  value       = railway_project.acme_logistics.id
  description = "Railway project ID"
}