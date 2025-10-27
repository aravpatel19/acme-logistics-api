# HappyRobot API Endpoints Configuration

## Current API Details
- **Base URL**: `https://nonpecuniary-scoldable-latesha.ngrok-free.dev`
- **API Key**: `acme_dev_test_key_123`
- **Status**: ✅ Live (via ngrok)

---

## Tool 1: Verify Carrier (Webhook GET)

### Configuration
- **URL**: `https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/carriers/find?mc={{mc}}`
- **Method**: GET
- **Headers**:
  - Key: `Authorization`
  - Value: `Bearer acme_dev_test_key_123`
- **Content Type**: Not needed for GET
- **Authorization**: No Auth (handled via headers)

### Testing
Test with MC number: `383025` or `123456`

### Expected Response (200 - Success)
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

### Expected Response (404 - Not Found)
```json
{
  "statusCode": 404,
  "body": {
    "error": "Carrier not found with the specified identifiers"
  }
}
```

---

## Tool 2: Search Loads (Webhook GET)

### Configuration
- **URL**: `https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/loads`
- **Method**: GET
- **Headers**:
  - Key: `Authorization`
  - Value: `Bearer acme_dev_test_key_123`
- **Query Parameters** (built from tool parameters):
  - `origin_city={{origin_city}}` (if provided)
  - `origin_state={{origin_state}}` (if provided)
  - `equipment_type={{equipment_type}}` (if provided)

### URL Construction
The URL should include parameters dynamically:
```
https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/loads?origin_city={{origin_city}}&equipment_type={{equipment_type}}
```

### Testing
- Origin city: `Chicago`
- Equipment type: `Dry Van`

### Expected Response
```json
{
  "statusCode": 200,
  "body": {
    "loads": [
      {
        "load_id": "LOAD-001",
        "origin": "Chicago, IL",
        "destination": "Atlanta, GA",
        "miles": 716,
        "equipment_type": "Dry Van",
        "posted_carrier_rate": 3500.00,
        "max_buy": 3675.00,
        "rate_per_mile": 4.89,
        "pickup_datetime": "2024-01-15T08:00:00",
        "notes": "AVAILABLE: Chicago, IL to Atlanta, GA | 716 miles | Dry Van | $3,500 (that's $4.89 per mile) | Pickup Monday",
        // ... additional fields
      }
    ]
  }
}
```

---

## Tool 3: Log Call (Webhook POST)

### Configuration
- **URL**: `https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/offers/log`
- **Method**: POST
- **Headers**:
  - Key: `Authorization`
  - Value: `Bearer acme_dev_test_key_123`
- **Content Type**: `application/json`
- **Authorization**: No Auth (handled via headers)
- **Error Handling**: Gracefully handle 5XX errors

### Body Structure
The body is automatically built from tool parameters:
```json
{
  "mc_number": "{{mc_number}}",
  "outcome": "{{outcome}}",
  "load_id": "{{load_id}}",
  "carrier_name": "{{carrier_name}}",
  "carrier_offer": {{carrier_offer}},
  "sentiment": "{{sentiment}}",
  "negotiation_rounds": {{negotiation_rounds}},
  "notes": "{{notes}}"
}
```

### Testing Body Example
```json
{
  "mc_number": "123456",
  "carrier_name": "Test Carrier LLC",
  "load_id": "LOAD-001",
  "carrier_offer": 3550,
  "outcome": "booked",
  "sentiment": "positive",
  "negotiation_rounds": 2,
  "notes": "Carrier accepted after negotiation"
}
```

### Expected Response (201 - Success)
```json
{
  "statusCode": 201,
  "body": {
    "message": "Call logged successfully",
    "call_id": "call_LOAD-001_123456_20240115143052"
  }
}
```

### Expected Response (409 - Conflict)
```json
{
  "statusCode": 409,
  "body": {
    "error": "Load already booked",
    "message": "Load LOAD-001 has already been booked by another carrier"
  }
}
```

---

## Important Configuration Notes

### 1. Variable Syntax in HappyRobot
- Use `{{parameter_name}}` in webhook URLs and bodies
- Parameters come from the tool's defined parameters
- Empty optional parameters are omitted

### 2. Authentication
- Always use Bearer token in Authorization header
- Never put API key in URL
- Headers are configured in the webhook action, not the tool

### 3. Error Handling
- Enable "Gracefully handle 5XX errors" on all webhooks
- This prevents workflow failures on API errors
- Agent can respond appropriately to errors

### 4. Testing Individual Endpoints

**Verify Carrier**:
```bash
curl -H "Authorization: Bearer acme_dev_test_key_123" \
  "https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/carriers/find?mc=383025"
```

**Search Loads**:
```bash
curl -H "Authorization: Bearer acme_dev_test_key_123" \
  "https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/loads?origin_city=Chicago&equipment_type=Dry%20Van"
```

**Log Call**:
```bash
curl -X POST \
  -H "Authorization: Bearer acme_dev_test_key_123" \
  -H "Content-Type: application/json" \
  -d '{
    "mc_number": "123456",
    "outcome": "not_interested",
    "sentiment": "neutral",
    "notes": "Testing webhook"
  }' \
  "https://nonpecuniary-scoldable-latesha.ngrok-free.dev/api/v1/offers/log"
```

---

## Monitoring & Debugging

### ngrok Web Interface
- URL: http://127.0.0.1:4040
- Shows all requests/responses
- Helps debug webhook calls

### Dashboard
- URL: http://localhost:8001
- Shows logged calls
- Verifies data is being saved

### Common Issues

1. **401/403 Errors**
   - Check Authorization header format
   - Verify API key is correct

2. **Empty Responses**
   - Ensure parameters are being passed
   - Check variable names match exactly

3. **Connection Errors**
   - Verify ngrok is still running
   - Check API server is running

4. **No Loads Found**
   - Try different cities (Chicago, Houston, Miami)
   - Check if loads are already booked