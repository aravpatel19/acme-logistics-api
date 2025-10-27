# Acme Logistics API

A production-ready API that automates inbound carrier sales calls for freight brokers. Built to integrate seamlessly with HappyRobot's voice AI platform, this system handles everything from carrier verification to price negotiation - turning phone calls into booked loads.

## What it does

When carriers call in, the system automatically:
- Verifies their credentials through the FMCSA database
- Matches them with available freight based on location and equipment
- Negotiates pricing within your approved limits
- Tracks every interaction with detailed analytics
- Transfers qualified carriers to your sales team

The result? Your sales team only talks to verified, interested carriers who've already agreed on pricing.

## Built with

- **Backend**: FastAPI (Python 3.11) - Fast, modern, and built for APIs
- **Dashboard**: Vanilla JavaScript with Chart.js - No framework bloat
- **External APIs**: FMCSA for carrier verification, HappyRobot for voice AI
- **Deployment**: Docker + Railway with automatic HTTPS

## Quick Start

### Prerequisites
- Python 3.10+
- FMCSA API key
- ngrok (for local testing)

### Installation

```bash
# Clone and setup
git clone https://github.com/aravpatel19/acme-logistics-api.git
cd acme-logistics-api

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r api/requirements.txt

# Configure environment
cp .env.example .env
# Edit .env with your API keys

# Note: metrics.json will be created automatically on first run
```

### Running Locally

```bash
# Start both servers
./start_servers.sh

# Or manually:
# Terminal 1 - API
python api/main.py

# Terminal 2 - Dashboard
cd dashboard && python -m http.server 8001

# Terminal 3 - Expose for webhooks
ngrok http 8000
```

Access:
- API: http://localhost:8000
- Dashboard: http://localhost:8001
- API Docs: http://localhost:8000/docs

## API Endpoints

All endpoints require Bearer token authentication:
```
Authorization: Bearer {ACME_API_KEY}
```

### Core Endpoints

1. **GET /api/v1/carriers/find** - Verify carrier through FMCSA
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" \
     "http://localhost:8000/api/v1/carriers/find?mc=999999"
   ```

2. **GET /api/v1/loads** - Search available freight
   ```bash
   curl -H "Authorization: Bearer YOUR_KEY" \
     "http://localhost:8000/api/v1/loads?origin_state=TX&equipment_type=Dry Van"
   ```

3. **POST /api/v1/offers/log** - Log call outcomes
   ```bash
   curl -X POST -H "Authorization: Bearer YOUR_KEY" \
     -H "Content-Type: application/json" \
     -d '{"mc_number":"999999","outcome":"booked","sentiment":"positive"}' \
     "http://localhost:8000/api/v1/offers/log"
   ```

See [API_DOCUMENTATION.md](API_DOCUMENTATION.md) for complete reference.

## Testing

```bash
# Run all tests
python tests/final_integration_test.py

# Test specific flows
python tests/demo_carrier_rejection_flow.py
python tests/mock_call_flow.py
```

## Project Structure

```
acme-logistics-api/
├── api/
│   ├── main.py              # FastAPI application
│   ├── models.py            # Data models
│   ├── requirements.txt     # Python dependencies
│   └── services/            # Business logic
│       ├── fmcsa.py         # Carrier verification
│       ├── loads.py         # Load management
│       └── metrics.py       # Analytics
├── dashboard/               # Web dashboard
│   ├── index.html
│   └── app.js
├── terraform/              # Infrastructure as Code
│   └── main.tf
├── tests/                  # Test suite
├── Dockerfile             # Container definition
└── start_servers.sh       # Local development script
```

## Documentation

- [API Documentation](API_DOCUMENTATION.md) - Complete API reference
- [HappyRobot Integration](HAPPYROBOT_API_ENDPOINTS.md) - Voice AI setup
- [Deployment Guide](RAILWAY_DEPLOYMENT_GUIDE.md) - Production deployment
- [API Key Management](API_KEY_MANAGEMENT.md) - Managing multiple API keys

## Security

- Bearer token authentication on all endpoints
- Rate limiting (60 requests/minute)
- HTTPS enforced in production
- Environment-based configuration

## Deployment

Deploy to Railway with automatic HTTPS:

```bash
cd terraform
terraform init
terraform apply
```

See [RAILWAY_DEPLOYMENT_GUIDE.md](RAILWAY_DEPLOYMENT_GUIDE.md) for detailed instructions.

## License

Proprietary - HappyRobot
