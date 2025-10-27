#!/bin/bash
# Fly.io Deployment Script for Acme Logistics API
# Pure shell script deployment - no Terraform needed!

set -e  # Exit on error

echo "🚁 Fly.io Deployment Script for Acme Logistics API"
echo "=================================================="
echo ""

# Configuration
APP_NAME="acme-logistics-api-$(date +%s | tail -c 5)"  # Unique name with timestamp
REGION="iad"  # US East (Virginia) - change if needed

# Check if flyctl is installed
if ! command -v flyctl &> /dev/null; then
    echo "❌ Fly CLI (flyctl) not found. Installing it now..."
    curl -L https://fly.io/install.sh | sh
    export PATH="$HOME/.fly/bin:$PATH"
fi

# Check if user is logged in to Fly.io
echo "🔐 Checking Fly.io authentication..."
if ! flyctl auth whoami &> /dev/null; then
    echo "📝 Please log in to Fly.io:"
    flyctl auth login
fi

echo "✅ Authenticated with Fly.io"
echo ""

# Create the app (skip if already exists)
echo "🚀 Creating Fly.io app: $APP_NAME in region $REGION"
if ! flyctl apps list | grep -q $APP_NAME; then
    flyctl apps create $APP_NAME --machines --org personal
else
    echo "   App already exists, skipping creation"
fi

# Set secrets
echo "🔐 Setting environment secrets..."
flyctl secrets set \
  ACME_API_KEY="acme_dev_test_key_123" \
  FMCSA_API_KEY="cdc33e44d693a3a58451898d4ec9df862c65b954" \
  --app $APP_NAME

# Deploy the Docker container
echo ""
echo "🐳 Deploying Docker container..."
echo "   This will build and deploy our Dockerfile"
echo ""

flyctl deploy \
  --app $APP_NAME \
  --ha=false \
  --strategy immediate \
  --now

# Allocate an IPv4 address (skip if already allocated)
echo ""
echo "🌐 Checking IPv4 address..."
if ! flyctl ips list --app $APP_NAME | grep -q "v4"; then
    echo "   Allocating new IPv4 address..."
    flyctl ips allocate-v4 --app $APP_NAME
else
    echo "   IPv4 address already allocated"
fi

# Create persistent volume for data (skip if already exists)
echo ""
echo "💾 Checking persistent storage..."
if ! flyctl volumes list --app $APP_NAME | grep -q "acme_data"; then
    echo "   Creating persistent volume for data..."
    flyctl volumes create acme_data --size 1 --region $REGION --app $APP_NAME
else
    echo "   Persistent volume already exists"
fi

# Get the app URL
APP_URL="https://$APP_NAME.fly.dev"

# Scale to ensure it's running
echo ""
echo "⚡ Ensuring app is running..."
flyctl scale count 1 --app $APP_NAME

# Wait for health check
echo "⏳ Waiting for app to be healthy..."
sleep 10

# Check status
flyctl status --app $APP_NAME

echo ""
echo "✅ Deployment Complete!"
echo "====================="
echo ""
echo "🌐 API URL: $APP_URL"
echo "📊 API Docs: $APP_URL/docs"
echo "🔧 Health Check: $APP_URL/healthcheck"
echo ""
echo "🔑 API Key: acme_dev_test_key_123"
echo ""
echo "📦 What was deployed:"
echo "   - Our Dockerized API (built from Dockerfile)"
echo "   - Includes all 10 freight loads from loads.json"
echo "   - FMCSA integration configured"
echo "   - Auto-scaling enabled (scales to zero when idle)"
echo ""
echo "📊 Useful commands:"
echo "   flyctl status --app $APP_NAME"
echo "   flyctl logs --app $APP_NAME"
echo "   flyctl ssh console --app $APP_NAME"
echo ""
echo "🔄 To redeploy after code changes:"
echo "   flyctl deploy --app $APP_NAME"
echo ""
echo "🗑️  To destroy this deployment:"
echo "   flyctl apps destroy $APP_NAME"
echo ""
echo "💾 Save this app name for future reference: $APP_NAME"

# Save deployment info
echo "$APP_NAME" > .fly-app-name
echo "App name saved to .fly-app-name"