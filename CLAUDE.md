# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is an **automated inbound carrier sales system** for Acme Logistics that integrates with HappyRobot's voice AI platform. The system handles inbound carrier calls following this workflow:

1. **Verify carrier credentials FIRST** using FMCSA database
2. **Search available freight** based on verified carrier's location and equipment  
3. **Negotiate pricing** (up to 3 rounds) within max_buy limits
4. **Log comprehensive call data** (outcome, sentiment, negotiation details)
5. **Transfer to sales rep** after agreement

**Current Status:** Core API complete with in-memory booking tracking, dashboard implemented, ready for HappyRobot integration

## Common Development Commands

### Running the API
```bash
# Start the API server (from project root)
python api/main.py

# The API will be available at http://localhost:8000
# API documentation available at http://localhost:8000/docs
```

### Running Tests
```bash
# Run comprehensive integration test suite
python tests/final_integration_test.py

# Test call flow scenarios
python tests/mock_call_flow.py

# Test carrier rejection flow
python tests/demo_carrier_rejection_flow.py

# Manual system test
python tests/manual_system_test.py

# Check API documentation accuracy
python tests/check_api_docs_accuracy.py
```

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # On macOS/Linux
# or
venv\Scripts\activate  # On Windows

# Install dependencies
pip install -r api/requirements.txt
```

### Docker Commands (when Dockerfile exists)
```bash
# Build Docker image
docker build -t acme-logistics-api .

# Run with Docker
docker run -p 8000:8000 --env-file .env acme-logistics-api

# Using Docker Compose (when docker-compose.yml exists)
docker-compose up
docker-compose down
```

### Quick Testing with ngrok
```bash
# Terminal 1: Start both servers
./start_servers.sh
# OR manually:
# API: cd api && python main.py
# Dashboard: cd dashboard && python -m http.server 8001

# Terminal 2: Expose to internet
ngrok http 8000
# Copy the https URL for HappyRobot integration
```

## High-Level Architecture

### API Structure
The FastAPI application follows a service-oriented architecture:

```
api/
├── main.py          # FastAPI application and endpoints
├── models.py        # Pydantic data models
├── services/        # Business logic layer
│   ├── loads.py     # Load search and management
│   ├── fmcsa.py     # FMCSA carrier verification
│   └── metrics.py   # Call tracking and metrics
└── data/           # JSON data storage
    ├── loads.json   # Freight load data
    └── metrics.json # Call metrics and logs
```

### Key API Endpoints

**Working Endpoints:**

1. **GET /api/v1/carriers/find** - Verify carrier through FMCSA (CALL THIS FIRST)
   - REQUIRES: `mc` (MC number) OR `dot` (DOT number)
   - Checks authorization, insurance, and active status
   - Returns carrier eligibility in HappyRobot format

2. **GET /api/v1/loads** - Search for available loads
   - REQUIRES: `origin_city` OR `origin_state` (at least one)
   - OPTIONAL: `equipment_type`, `destination_city`, `destination_state`, `pickup_date`
   - Returns loads sorted by rate (highest first)
   - Includes `max_buy` field (5% over posted rate)
   - Automatically filters out booked loads

3. **POST /api/v1/offers/log** - Log carrier offers (FULLY IMPLEMENTED)
   - Accepts: `load_id`, `mc_number`, `carrier_name`, `carrier_offer`, `outcome`, `sentiment`, `negotiation_rounds`, `call_duration`, `notes`
   - Automatically marks loads as booked when outcome="booked"
   - Returns 409 if load already booked
   - Updates call to "already_booked" outcome if attempted

4. **GET /healthcheck** - API health status
5. **GET /metrics** - Dashboard metrics with aggregated data

### Authentication
All API endpoints (except healthcheck) require Bearer token authentication:
```
Authorization: Bearer {ACME_API_KEY}
```

### Correct Call Flow (IMPORTANT)
1. **Carrier calls in** → HappyRobot AI answers
2. **Get MC number FIRST** → Call `/api/v1/carriers/find` to verify eligibility
3. **If verified** → Ask for location and equipment type
4. **Search loads** → Call `/api/v1/loads` with carrier's criteria
5. **Present load** → Use the `notes` field for natural pitch
6. **Handle negotiation** → Need `/api/v1/offers/evaluate` endpoint (MISSING)
7. **Log the call** → Call `/api/v1/offers/log` with complete data
8. **Transfer to human** → If price agreed, transfer to sales rep

### Key Design Decisions

- **Origin-Required Search**: Matches real-world carrier behavior (carriers always know their location)
- **Flat JSON Structure**: Optimized for AI parsing with calculated fields like `rate_per_mile`
- **Real-time FMCSA Verification**: Ensures compliance with live government database checks
- **File-based Storage**: Uses JSON files for demo simplicity (production would use database)
- **In-Memory Booking State**: Uses Python sets to track booked loads, preventing double booking
- **HappyRobot Response Format**: All endpoints return standardized `{statusCode, body}` structure
- **Web Call Trigger**: Uses web hooks instead of phone numbers (per requirements)

### Testing Philosophy
The project includes comprehensive test coverage:
- Unit tests for individual services
- Integration tests for full API flows
- Scenario tests simulating real carrier searches
- Shell script for endpoint validation

When making changes, ensure all existing tests pass and add new tests for new functionality.

### Environment Variables
Required in `.env` file:
- `ACME_API_KEY` - API authentication key
- `FMCSA_API_KEY` - FMCSA API credentials
- `FMCSA_BASE_URL` - FMCSA API endpoint
- `HOST` - Server host (default: 0.0.0.0)
- `PORT` - Server port (default: 8000)

## Key Components Implemented

### 1. Booking System
- In-memory tracking using LoadService.booked_loads set
- Automatic booking when outcome="booked" in log call
- 409 Conflict response for double booking attempts
- Updates call to "already_booked" outcome

### 2. Dashboard (dashboard/)
- Real-time metrics visualization with Chart.js
- Shows: call volume, success rates, sentiment analysis, recent calls
- Auto-refreshes every 30 seconds
- Mobile responsive design

### 3. Enhanced Call Logging
- Complete outcome tracking: `booked`, `no_agreement`, `not_interested`, `carrier_not_eligible`, `already_booked`
- Sentiment analysis: `positive`, `neutral`, `negative`
- Tracks negotiation rounds and call duration

### 4. Test Suite
- Comprehensive integration tests (final_integration_test.py)
- Mock call flow testing
- API documentation accuracy checks
- Manual system testing utilities

## Deployment Options

### Quick Deployment with ngrok (Testing)
```bash
python api/main.py
ngrok http 8000
```

### Cloud Deployment Options
- **Railway**: Connect GitHub repo, auto-deploy on push
- **Render**: Add render.yaml, set env vars
- **Fly.io**: Use fly launch, configure fly.toml

### HappyRobot Integration Steps
1. Deploy API and get public URL (use ngrok for testing)
2. Configure inbound campaign in HappyRobot
3. Set up web call trigger (no phone number needed)
4. Configure API endpoints in voice agent (see HAPPYROBOT_API_ENDPOINTS.md)
5. Use prompt from HAPPYROBOT_COMPLETE_SETUP.md
6. Test end-to-end flow

## Important Instructions

- NEVER create files unless they're absolutely necessary
- ALWAYS prefer editing existing files to creating new ones  
- NEVER proactively create documentation files (*.md) unless explicitly requested
- When testing, ALWAYS run the lint/typecheck commands if provided
- NEVER commit changes unless explicitly asked by the user