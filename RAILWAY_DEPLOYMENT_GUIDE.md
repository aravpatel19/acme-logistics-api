# Railway Deployment Guide with Terraform

## Overview

This guide explains how to deploy the Acme Logistics API to Railway using Terraform. Railway automatically provides:
- **HTTPS with Let's Encrypt certificates** (no configuration needed!)
- Auto-scaling
- Built-in logging and monitoring
- Automatic deployments from GitHub

## How HTTPS Works on Railway

**You don't need to do anything!** Railway automatically:
1. Provisions a Let's Encrypt SSL certificate for your subdomain
2. Handles certificate renewal (every 90 days)
3. Forces HTTPS redirect for all traffic
4. Provides secure WebSocket connections

Your API will be accessible at:
- `https://acme-logistics-api.up.railway.app` (with automatic HTTPS)

## Prerequisites

1. **Railway Account**: Sign up at [railway.app](https://railway.app)
2. **Railway Token**: Get from [railway.app/account/tokens](https://railway.app/account/tokens)
3. **Terraform**: Install from [terraform.io](https://www.terraform.io/downloads)
4. **Git Repository**: Push your code to GitHub/GitLab (optional, for auto-deploy)

## Step-by-Step Deployment

### 1. Set Up Environment

```bash
# Navigate to terraform directory
cd terraform/

# Create your variables file from the example
cp terraform.tfvars.example terraform.tfvars

# Edit terraform.tfvars with your actual values
# - acme_api_key: Create a secure key (e.g., use `openssl rand -hex 32`)
# - fmcsa_api_key: Your FMCSA API key
```

### 2. Set Railway Token

```bash
# Option 1: Environment variable (recommended)
export RAILWAY_TOKEN="your-railway-token-here"

# Option 2: Add to terraform.tfvars
# railway_token = "your-railway-token-here"
```

### 3. Initialize Terraform

```bash
# Initialize Terraform (downloads Railway provider)
terraform init

# You should see:
# Terraform has been successfully initialized!
```

### 4. Plan Deployment

```bash
# Preview what will be created
terraform plan

# You'll see:
# - railway_project.acme_logistics
# - railway_service.api
# - railway_service.dashboard
# - railway_variable_collection.api_env
# - railway_service_domain.api_domain
# - railway_service_domain.dashboard_domain
```

### 5. Deploy!

```bash
# Apply the configuration
terraform apply

# Type 'yes' when prompted

# After ~2-3 minutes, you'll see:
# Outputs:
# api_url = "https://acme-logistics-api.up.railway.app"
# dashboard_url = "https://acme-logistics-dashboard.up.railway.app"
```

### 6. Verify Deployment

```bash
# Test the API (replace with your API key)
curl -H "Authorization: Bearer your-acme-api-key" \
  https://acme-logistics-api.up.railway.app/healthcheck

# Should return:
# {"status":"healthy","loads_available":50,"loads_booked":0,...}
```

## What Happens Behind the Scenes

1. **Project Creation**: Terraform creates a Railway project
2. **Container Build**: Railway detects the Dockerfile and builds your container
3. **SSL Certificate**: Railway automatically requests a Let's Encrypt certificate
4. **DNS Setup**: Railway configures DNS for your subdomain
5. **Deployment**: Your app starts with HTTPS enabled
6. **Health Checks**: Railway monitors your `/healthcheck` endpoint

## Connecting GitHub for Auto-Deploy

If you want automatic deployments on git push:

1. Go to your Railway project dashboard
2. Click on the API service
3. Go to Settings → Source
4. Click "Connect GitHub"
5. Select your repository
6. Choose the branch (usually `main`)

Now every push to GitHub will automatically deploy!

## Custom Domain (Optional)

To use your own domain (e.g., `api.acme-logistics.com`):

1. Uncomment the `railway_custom_domain` resource in `main.tf`
2. Run `terraform apply`
3. You'll get a CNAME record to add to your DNS:
   ```
   Type: CNAME
   Name: api
   Value: acme-logistics-api.up.railway.app
   ```
4. Railway will automatically provision SSL for your custom domain too!

## Monitoring Your Deployment

1. **Railway Dashboard**: See logs, metrics, and deployments at railway.app
2. **API Logs**: Click on your service → Logs tab
3. **Metrics**: Click on your service → Metrics tab (CPU, Memory, Network)
4. **Healthcheck**: Monitor `https://your-api-url/healthcheck`

## Updating Your Deployment

### Update Environment Variables
```bash
# Edit terraform.tfvars, then:
terraform apply
```

### Update Code
```bash
# If connected to GitHub:
git push origin main  # Auto-deploys

# If not using GitHub:
railway up  # From your project directory
```

### Scale Your Service
```bash
# Edit main.tf to add regions/replicas
# In railway_service "api" block, add:
regions = [{
  region       = "us-west-2"
  num_replicas = 2
}]

terraform apply
```

## Security Notes

✅ **HTTPS is automatic** - All traffic is encrypted with TLS 1.3
✅ **API Key Required** - All endpoints need `Authorization: Bearer {key}`
✅ **Environment Variables** - Sensitive data stored securely in Railway
✅ **Private Project** - Your code and logs are private by default
✅ **Non-root Container** - Dockerfile uses non-root user for security

## Troubleshooting

### "Method Not Allowed" Error
- Make sure your HappyRobot webhook uses the full URL with path
- Example: `https://acme-logistics-api.up.railway.app/api/v1/offers/log`

### "Invalid API Key" Error
- Check that `ACME_API_KEY` environment variable is set correctly
- Verify the Authorization header format: `Bearer your-key-here`

### Build Failures
- Check Railway logs for detailed error messages
- Ensure all files are committed to Git (if using GitHub deploy)

### SSL Certificate Issues
- Railway handles this automatically
- If using custom domain, ensure DNS is configured correctly
- Certificates renew automatically - no action needed

## Cost Estimation

Railway pricing (as of 2024):
- **Hobby Plan**: $5/month (includes $5 of usage)
- **Usage**: ~$0.01/GB RAM/hour
- **Estimated Monthly**: $5-10 for a small API

Your API is lightweight, so costs should be minimal!

## Next Steps

1. ✅ Deploy with Terraform
2. ✅ Verify HTTPS is working
3. ✅ Update HappyRobot webhooks to use new URLs
4. ✅ Test end-to-end flow
5. 📊 Monitor performance in Railway dashboard
6. 🚀 Consider adding custom domain

Congratulations! Your API is now deployed with enterprise-grade security! 🎉