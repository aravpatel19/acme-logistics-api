# Acme Logistics API Documentation

## Table of Contents
1. [Overview](#overview)
2. [Architecture](#architecture)
3. [API Design Principles](#api-design-principles)
4. [Authentication](#authentication)
5. [API Endpoints](#api-endpoints)
6. [Data Models](#data-models)
7. [Business Logic](#business-logic)
8. [Error Handling](#error-handling)
9. [Testing](#testing)
10. [Deployment](#deployment)

---

## Overview

The Acme Logistics API is a FastAPI-based service designed specifically for integration with HappyRobot's voice AI platform. It enables automated carrier sales by handling inbound calls from trucking companies looking to book freight loads.

### Key Features
- Real-time FMCSA carrier verification
- Intelligent load search and matching
- Double-booking prevention
- Comprehensive call tracking and metrics
- HappyRobot-compatible response format
- Real-time dashboard for monitoring

### Technology Stack
- **Framework**: FastAPI (Python 3.10+)
- **Storage**: JSON files (demo mode)
- **Authentication**: Bearer token
- **External APIs**: FMCSA (carrier verification)
- **Dashboard**: Vanilla JavaScript + Chart.js

---

## Architecture

### High-Level Architecture
```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  HappyRobot AI  │────▶│  Acme API       │────▶│  FMCSA API      │
│  Voice Agent    │◀────│  (FastAPI)      │◀────│  (Verification) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  Dashboard      │
                        │  (Port 8001)    │
                        └─────────────────┘
```

### Directory Structure
```
api/
├── main.py              # FastAPI application and endpoints
├── models.py            # Pydantic models for validation
├── services/            # Business logic layer
│   ├── fmcsa.py        # FMCSA integration service
│   ├── loads.py        # Load management service
│   └── metrics.py      # Call tracking service
└── data/               # JSON data storage
    ├── loads.json      # Freight load database
    └── metrics.json    # Call logs and metrics
```

### Service Architecture

#### 1. **LoadService** (`services/loads.py`)
- Manages freight load inventory
- Tracks booking status in memory
- Implements search with filtering
- Prevents double bookings

#### 2. **FMCSAService** (`services/fmcsa.py`)
- Integrates with government FMCSA API
- Verifies carrier authorization
- Checks insurance and operating status
- Returns eligibility determination

#### 3. **MetricsService** (`services/metrics.py`)
- Tracks all carrier interactions
- Calculates success rates
- Provides dashboard analytics
- Persists call history to JSON

---

## API Design Principles

### 1. HappyRobot Compatibility
All responses follow HappyRobot's expected format:
```json
{
  "statusCode": 200,
  "body": {
    // Response data here
  }
}
```

### 2. Stateless Design
- Each request is independent
- No session management required
- In-memory state only for booking tracking

### 3. RESTful Conventions
- GET for queries (carrier verification, load search)
- POST for actions (logging calls)
- Predictable URL patterns
- HTTP status codes for state communication

### 4. Fail-Safe Approach
- Comprehensive error handling
- Graceful degradation
- Always return valid JSON
- Log errors without exposing internals

---

## Authentication

### Bearer Token Authentication
All API endpoints (except `/healthcheck`) require authentication:

```bash
Authorization: Bearer {ACME_API_KEY}
```

### Implementation Details
- Token validated on every request
- 403 returned for invalid tokens
- Rate limiting: 60 requests/minute per token
- Token stored in environment variable

### Example
```bash
curl -H "Authorization: Bearer acme_dev_test_key_123" \
     http://localhost:8000/api/v1/loads?origin_city=Chicago
```

---

## API Endpoints

### 1. GET `/api/v1/carriers/find`
**Purpose**: Verify carrier eligibility through FMCSA database

**Required Parameters**:
- `mc` (string) - Motor Carrier number OR
- `dot` (string) - DOT number

**Response (200 - Eligible)**:
```json
{
  "statusCode": 200,
  "body": {
    "carrier": {
      "carrier_id": "CAR-123456",
      "carrier_name": "ABC TRUCKING LLC",
      "status": "active",
      "dot_number": "789012",
      "mc_number": "123456",
      "contacts": [],
      "bridge": {
        "status": "success",
        "bridge_carrier_id": "BRK-123456"
      }
    }
  }
}
```

**Response (404 - Not Eligible)**:
```json
{
  "statusCode": 404,
  "body": {
    "error": "Carrier not found with the specified identifiers"
  }
}
```

**Business Logic**:
1. Query FMCSA API with MC/DOT number
2. Check if carrier is authorized to operate
3. Verify insurance on file
4. Ensure not out of service
5. Log failed verifications automatically

---

### 2. GET `/api/v1/loads`
**Purpose**: Search for available freight loads

**Parameters**:
- `origin_city` (string, optional) - Origin city
- `origin_state` (string, optional) - Origin state
- `destination_city` (string, optional) - Destination city
- `destination_state` (string, optional) - Destination state
- `equipment_type` (string, optional) - Equipment type (Dry Van, Reefer, Flatbed)
- `pickup_date` (string, optional) - ISO 8601 date
- `include_booked` (boolean, optional) - Include booked loads (for dashboard)

**Note**: At least one origin parameter (city OR state) should be provided for carrier searches

**Response**:
```json
{
  "statusCode": 200,
  "body": {
    "loads": [
      {
        "reference_number": "LOAD-001",
        "load_id": "LOAD-001",
        "contact": {
          "name": "Dispatch",
          "email": "dispatch@acmelogistics.com",
          "phone": "18005551234",
          "extension": "",
          "type": "dispatch"
        },
        "type": "can_get",
        "status": "available",
        "is_partial": false,
        "stops": [
          {
            "type": "origin",
            "location": {
              "city": "Chicago",
              "state": "IL",
              "zip": "",
              "country": "US"
            },
            "stop_timestamp_open": "2024-01-15T08:00:00",
            "stop_timestamp_close": "2024-01-15T08:00:00"
          },
          {
            "type": "destination",
            "location": {
              "city": "Atlanta",
              "state": "GA",
              "zip": "",
              "country": "US"
            },
            "stop_timestamp_open": "2024-01-16T14:00:00",
            "stop_timestamp_close": "2024-01-16T14:00:00"
          }
        ],
        "origin": "Chicago, IL",
        "destination": "Atlanta, GA",
        "miles": 716,
        "equipment_type": "Dry Van",
        "weight": 42000,
        "posted_carrier_rate": 3500.00,
        "max_buy": 3675.00,
        "rate_per_mile": 4.89,
        "pickup_datetime": "2024-01-15T08:00:00",
        "delivery_datetime": "2024-01-16T14:00:00",
        "commodity_type": "General Freight",
        "notes": "AVAILABLE: Chicago, IL to Atlanta, GA | 716 miles | Dry Van | $3,500 (that's $4.89 per mile) | Pickup Monday",
        "sale_notes": "",
        "branch": "Main",
        "bridge": {
          "status": "success",
          "bridge_load_id": "BRK-LOAD-001"
        }
      }
    ]
  }
}
```

**Filtering Logic**:
1. Filter by origin (required for carriers)
2. Filter by destination if provided
3. Filter by equipment type if specified
4. Exclude booked loads (unless include_booked=true)
5. Sort by rate (highest first)
6. Return up to 10 loads

---

### 3. POST `/api/v1/offers/log`
**Purpose**: Log carrier interactions and booking outcomes

**Request Body**:
```json
{
  "load_id": "LOAD-001",           // Optional if no specific load discussed
  "mc_number": "123456",           // Required
  "carrier_name": "ABC Trucking",  // Optional
  "carrier_offer": 3650.00,        // Optional - final agreed rate if booked
  "outcome": "booked",             // Required - see enum values below
  "sentiment": "positive",         // Required - positive/neutral/negative
  "negotiation_rounds": 2,         // Optional - number of price negotiations
  "call_duration": 180,            // Optional - call duration in seconds
  "notes": "Carrier accepted after negotiation"  // Optional
}
```

**Outcome Values**:
- `booked` - Load successfully booked
- `not_interested` - Carrier declined the opportunity
- `no_agreement` - Could not agree on price
- `carrier_not_eligible` - Failed FMCSA verification
- `already_booked` - Load was already taken

**Response (Success)**:
```json
{
  "statusCode": 201,
  "body": {
    "message": "Call logged successfully",
    "call_id": "call_LOAD-001_123456_20240115143052"
  }
}
```

**Response (409 - Double Booking)**:
```json
{
  "statusCode": 409,
  "body": {
    "error": "Load already booked",
    "message": "Load LOAD-001 has already been booked by another carrier"
  }
}
```

**Business Logic**:
1. Validate load exists (if load_id provided)
2. Check if load already booked
3. Log the interaction with all details
4. If outcome="booked", mark load as unavailable
5. Update metrics for dashboard

---

### 4. GET `/healthcheck`
**Purpose**: API health status (no auth required)

**Response**:
```json
{
  "status": "healthy",
  "loads_available": 10,
  "loads_booked": 3,
  "booked_load_ids": ["LOAD-001", "LOAD-003", "LOAD-005"],
  "services": {
    "fmcsa": "operational",
    "loads": "operational", 
    "metrics": "operational"
  }
}
```

---

### 5. GET `/metrics`
**Purpose**: Dashboard metrics and analytics

**Response**:
```json
{
  "total_calls": 45,
  "successful_bookings": 12,
  "success_rate": 26.7,
  "avg_negotiation_rounds": 1.8,
  "total_revenue": 42500.00,
  "calls_by_outcome": {
    "booked": 12,
    "not_interested": 8,
    "no_agreement": 5,
    "carrier_not_eligible": 15,
    "already_booked": 5
  },
  "sentiment_breakdown": {
    "positive": 12,
    "neutral": 20,
    "negative": 13
  },
  "recent_calls": [
    {
      "call_id": "call_LOAD-001_123456_20240115143052",
      "mc_number": "123456",
      "carrier_name": "ABC Trucking",
      "load_id": "LOAD-001",
      "outcome": "booked",
      "sentiment": "positive",
      "agreed_rate": 3650.00,
      "negotiation_rounds": 2,
      "call_duration_seconds": 180,
      "notes": "Carrier accepted after negotiation",
      "timestamp": "2024-01-15T14:30:52.123456"
    }
  ]
}
```

---

## Data Models

### Core Enums

```python
class CallOutcome(str, Enum):
    booked = "booked"
    not_interested = "not_interested"
    no_agreement = "no_agreement"
    carrier_not_eligible = "carrier_not_eligible"
    already_booked = "already_booked"

class CallSentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"
```

### Request Models

```python
class OfferLogRequest(BaseModel):
    load_id: Optional[str] = None
    mc_number: str
    carrier_name: Optional[str] = None
    carrier_offer: Optional[float] = None
    outcome: CallOutcome
    sentiment: CallSentiment = CallSentiment.neutral
    negotiation_rounds: int = 0
    call_duration: int = 0
    notes: Optional[str] = None
```

### Response Models

```python
class HappyRobotResponse(BaseModel):
    statusCode: int = 200
    body: Dict[str, Any]
```

---

## Business Logic

### Load Booking Flow
1. **Carrier Verification** → Must pass FMCSA check
2. **Load Search** → Based on carrier location/equipment
3. **Price Negotiation** → Within max_buy limits (5% over posted rate)
4. **Booking** → Atomic operation with double-booking prevention
5. **Logging** → Every interaction tracked for analytics

### Double-Booking Prevention
- In-memory `booked_loads` set tracks booked load IDs
- Check performed before allowing new booking
- Returns 409 Conflict if already booked
- Alternative: Log as "already_booked" outcome

### Pricing Logic
- **Posted Rate**: What we advertise to carriers
- **Max Buy**: Maximum we'll pay (posted rate + 5%)
- **Rate Per Mile**: Calculated for carrier reference
- Negotiation happens outside API (in voice agent)

### Search Prioritization
1. Exact city match preferred
2. State match as fallback
3. Equipment type must match if specified
4. Sort by rate descending (best opportunities first)
5. Limit results to maintain conversation flow

---

## Error Handling

### Error Response Format
```json
{
  "statusCode": 400,
  "body": {
    "error": "Brief error message",
    "message": "Detailed explanation for debugging"
  }
}
```

### Common Error Scenarios
- **400**: Missing required parameters
- **401/403**: Invalid or missing API key
- **404**: Resource not found (carrier, load)
- **409**: Conflict (double booking)
- **422**: Validation error (invalid enum values)
- **429**: Rate limit exceeded
- **500**: Internal server error

### Error Handling Strategy
1. Validate inputs early
2. Use Pydantic for automatic validation
3. Catch and log all exceptions
4. Never expose internal details
5. Always return valid JSON

---

## Testing

### Test Coverage
- **Unit Tests**: Service-level logic
- **Integration Tests**: Full API flow
- **Scenario Tests**: Real-world use cases
- **Performance Tests**: Concurrent bookings
- **Documentation Tests**: API accuracy

### Key Test Files
1. `final_integration_test.py` - 16 comprehensive tests
2. `manual_system_test.py` - Step-by-step verification
3. `mock_call_flow.py` - Simulated carrier interaction
4. `demo_carrier_rejection_flow.py` - Rejection scenarios
5. `check_api_docs_accuracy.py` - Documentation validation

### Testing Best Practices
- Reset data before test runs
- Test both success and failure paths
- Verify state changes (bookings)
- Check metrics updates
- Validate error responses

---

## Deployment

### Environment Variables
```bash
# Required
ACME_API_KEY=your_api_key_here
FMCSA_API_KEY=your_fmcsa_key
FMCSA_BASE_URL=https://mobile.fmcsa.dot.gov/qc/services

# Optional
HOST=0.0.0.0
PORT=8000
LOG_LEVEL=INFO
```

### Running Locally
```bash
# Start API
cd api && python main.py

# Start Dashboard
cd dashboard && python -m http.server 8001

# Or use the convenience script
./start_servers.sh
```

### Docker Deployment
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY api/requirements.txt .
RUN pip install -r requirements.txt
COPY api/ .
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Production Considerations
1. Use PostgreSQL instead of JSON files
2. Implement proper logging (CloudWatch, etc.)
3. Add monitoring (Datadog, New Relic)
4. Use Redis for booking state
5. Implement proper rate limiting
6. Add request ID tracking
7. Use environment-specific configs

---

## Integration with HappyRobot

### Call Flow
1. **Greeting** → Get MC number from carrier
2. **Verification** → Call `/api/v1/carriers/find`
3. **Location** → Get carrier's current city
4. **Search** → Call `/api/v1/loads` with location
5. **Present** → Read load details to carrier
6. **Negotiate** → Handle price discussion
7. **Book** → Call `/api/v1/offers/log` with outcome
8. **Transfer** → Hand off to human agent if booked

### Best Practices
- Always verify carrier first
- Keep searches focused (use filters)
- Present one load at a time
- Log every interaction
- Handle all outcome types
- Gracefully handle API errors

### Voice Agent Prompts
Use the `notes` field from load responses for natural language:
```
"AVAILABLE: Chicago, IL to Atlanta, GA | 716 miles | 
Dry Van | $3,500 (that's $4.89 per mile) | Pickup Monday"
```

---

## Monitoring & Analytics

### Dashboard Features
- Real-time metrics (15s refresh)
- Call outcome distribution
- Success rate tracking
- Recent calls table
- Load availability status

### Key Metrics
- **Total Calls**: All carrier interactions
- **Success Rate**: Bookings / Total Calls
- **Average Negotiation**: Rounds per booking
- **Revenue**: Sum of agreed rates
- **Sentiment**: Carrier satisfaction trends

### Performance Metrics
- API response time < 200ms
- Dashboard refresh every 15s
- No database = instant booking checks
- Concurrent call handling
- Automatic state persistence

---

## Security Considerations

### Current Implementation
- Bearer token authentication
- Rate limiting (60 req/min)
- CORS configured for specific origins
- No sensitive data in responses
- Input validation on all endpoints

### Production Enhancements Needed
- HTTPS only (TLS 1.3)
- API key rotation
- Request signing
- Audit logging
- PCI compliance for payments
- GDPR compliance for EU carriers

---

## Troubleshooting

### Common Issues

1. **No loads showing**
   - Check origin parameters
   - Verify loads aren't all booked
   - Check JSON file integrity

2. **Double booking allowed**
   - API server restarted (in-memory state lost)
   - Check response status codes

3. **FMCSA verification failing**
   - Check API key is valid
   - Verify carrier MC/DOT is correct
   - Check FMCSA API status

4. **Dashboard not updating**
   - Verify API is running
   - Check browser console
   - Ensure CORS is configured

### Debug Endpoints
- `/healthcheck` - System status
- `/metrics` - Detailed analytics
- `/docs` - Auto-generated API docs

---

## Future Enhancements

### Phase 2 (Current)
- ngrok integration
- HappyRobot configuration
- End-to-end testing

### Phase 3
- Docker containerization
- Railway deployment
- Production environment

### Future Features
- PostgreSQL database
- Redis for state management
- Webhook notifications
- SMS confirmations
- Driver mobile app
- Real-time tracking
- Payment processing
- Multi-tenant support