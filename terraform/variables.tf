# Input variables for sensitive data
# These should be provided when running terraform apply

variable "acme_api_key" {
  description = "API key for authenticating requests to the Acme Logistics API"
  type        = string
  sensitive   = true
}

variable "fmcsa_api_key" {
  description = "API key for the FMCSA carrier verification service"
  type        = string
  sensitive   = true
}

# Optional: Railway token (can also be set via RAILWAY_TOKEN env var)
variable "railway_token" {
  description = "Railway API token for deployment"
  type        = string
  sensitive   = true
  default     = ""  # Uses RAILWAY_TOKEN env var if not provided
}