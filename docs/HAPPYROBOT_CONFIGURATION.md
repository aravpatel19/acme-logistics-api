# HappyRobot Voice Agent Configuration

Configure your HappyRobot inbound campaign with these API endpoints and prompts.

## API Endpoints

### 1. Verify Carrier (CALL FIRST)
```
GET https://acme-logistics-api-3534.fly.dev/api/v1/carriers/find
Parameters: mc={mc_number} OR dot={dot_number}
Headers: Authorization: Bearer acme_dev_test_key_123
```

### 2. Search Loads
```
GET https://acme-logistics-api-3534.fly.dev/api/v1/loads
Parameters: 
  - origin_city OR origin_state (required)
  - destination_city, destination_state (optional)
  - equipment_type (optional)
Headers: Authorization: Bearer acme_dev_test_key_123
```

### 3. Log Call Outcome
```
POST https://acme-logistics-api-3534.fly.dev/api/v1/offers/log
Headers: 
  - Authorization: Bearer acme_dev_test_key_123
  - Content-Type: application/json
Body: {
  "load_id": "LOAD-XXX",
  "mc_number": "1234567",
  "carrier_name": "Company Name",
  "carrier_offer": 3500,
  "outcome": "booked|no_agreement|not_interested|carrier_not_eligible|already_booked",
  "sentiment": "positive|neutral|negative",
  "negotiation_rounds": 1,
  "call_duration": 120,
  "notes": "Additional details"
}
```

## Voice Agent Prompt

```
You are an AI assistant for Acme Logistics helping carriers find and book freight loads.

CALL FLOW:
1. Greet the carrier and ask for their MC number
2. Verify their eligibility using the carriers/find endpoint
3. If eligible, ask for their current location (city/state) and equipment type
4. Search for available loads using the loads endpoint
5. Present the best matching load with all details
6. If interested, negotiate price (up to 3 rounds, stay within max_buy limit)
7. Log the call outcome using the offers/log endpoint
8. If price agreed, transfer to sales rep

IMPORTANT:
- Always verify carrier FIRST before searching loads
- Use the 'notes' field from loads for natural conversation
- Be friendly but professional
- Track negotiation rounds carefully
- Log ALL calls, even if carrier not eligible
```

## Response Handling

All endpoints return this format:
```json
{
  "statusCode": 200,
  "body": {
    // Response data here
  }
}
```

- Status 200 with nested statusCode 409 = Load already booked
- Status 200 with nested statusCode 201 = Success
- Check carrier.eligible boolean for verification
- Use load.max_buy as your negotiation ceiling

## Testing

Use web call trigger (no phone number needed). Test scenarios:
1. MC 1234567 - Eligible carrier
2. MC 9999999 - Ineligible carrier
3. Already booked loads show in dashboard