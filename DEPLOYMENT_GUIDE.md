# Deployment Guide

This guide covers deploying the Acme Logistics API using Docker and Fly.io.

## Prerequisites

1. **Fly.io Account** - Sign up at https://fly.io
2. **Docker** - For local testing
3. **Git** - For version control

## Quick Deploy

```bash
# One-command deployment
./deploy-to-flyio.sh
```

## Docker Overview

Our Dockerfile implements production best practices:
- Multi-stage build (reduces size to ~200MB)
- Non-root user for security
- Health checks included
- All data files included

### What Gets Containerized
- FastAPI application
- 10 pre-loaded freight loads
- Dashboard files
- All dependencies

### Local Testing
```bash
# Build
docker build -t acme-api .

# Run
docker run -p 8000:8000 \
  -e ACME_API_KEY="acme_dev_test_key_123" \
  -e FMCSA_API_KEY="your_key" \
  acme-api

# Test
curl http://localhost:8000/healthcheck
```

## Manual Deployment Steps

1. **Install Fly CLI**
   ```bash
   curl -L https://fly.io/install.sh | sh
   ```

2. **Login**
   ```bash
   flyctl auth login
   ```

3. **Create App**
   ```bash
   flyctl apps create acme-logistics-api
   ```

4. **Set Secrets**
   ```bash
   flyctl secrets set \
     ACME_API_KEY="acme_dev_test_key_123" \
     FMCSA_API_KEY="your_fmcsa_key"
   ```

5. **Deploy**
   ```bash
   flyctl deploy
   ```

6. **Create Volume** (for persistence)
   ```bash
   flyctl volumes create acme_data --size 1 --region iad
   ```

## Configuration

### Environment Variables
- `ACME_API_KEY` - API authentication
- `FMCSA_API_KEY` - FMCSA service key
- `PORT` - Server port (default: 8000)

### fly.toml Settings
- `auto_stop_machines = false` - Keeps app running
- `min_machines_running = 1` - No scale to zero
- Persistent volume mounted at `/app/api/data`

## Management

```bash
# View logs
flyctl logs --app acme-logistics-api-3534

# Check status
flyctl status --app acme-logistics-api-3534

# SSH access
flyctl ssh console --app acme-logistics-api-3534

# Redeploy
flyctl deploy --app acme-logistics-api-3534
```

## Troubleshooting

### Data Not Persisting
- Ensure volume is mounted in fly.toml
- Check `min_machines_running = 1`

### API Not Accessible
- Verify app is running: `flyctl status`
- Check logs for errors: `flyctl logs`

### Reset Demo Data
```bash
curl -X POST -H "Authorization: Bearer acme_dev_test_key_123" \
  https://your-app.fly.dev/metrics/reset
```

## Alternative Platforms

This Docker image works on any platform:
- **AWS ECS/Fargate**
- **Google Cloud Run**
- **Azure Container Instances**
- **Heroku** (with container registry)
- **DigitalOcean App Platform**

## Cost

Current Fly.io deployment:
- **Free tier eligible**
- 1 shared VM (256MB)
- 1GB persistent storage
- Expected: $0/month