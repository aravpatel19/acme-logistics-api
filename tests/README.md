# Acme Logistics Test Suite

## Test Organization

### Core Tests

1. **final_integration_test.py** - Complete system integration test
   - Tests all API endpoints
   - Verifies authentication
   - Tests booking workflow
   - Checks metrics
   - Error handling validation
   - 16 comprehensive tests
   ```bash
   python tests/final_integration_test.py
   ```

2. **manual_system_test.py** - Step-by-step system verification
   - Manual walkthrough of all functionality
   - Good for debugging issues
   - Includes double-booking prevention test
   ```bash
   python tests/manual_system_test.py
   ```

### Demo Scripts

3. **mock_call_flow.py** - Simulates a complete carrier call
   - Shows the full conversation flow
   - Good for understanding the system
   ```bash
   python tests/mock_call_flow.py
   ```

4. **demo_carrier_rejection_flow.py** - Demonstrates rejection scenarios
   - Shows how to handle failed verifications
   - Logs different rejection types
   ```bash
   python tests/demo_carrier_rejection_flow.py
   ```

### Utility Scripts

5. **check_api_docs_accuracy.py** - Validates API documentation
   - Compares actual API responses with docs
   - Identifies documentation issues
   ```bash
   python tests/check_api_docs_accuracy.py
   ```

## Running Tests

### Prerequisites

1. Start the API server:
   ```bash
   cd api && python main.py
   ```

2. Start the dashboard server:
   ```bash
   cd dashboard && python -m http.server 8001
   ```

### Quick Test

For a quick system check:
```bash
python tests/final_integration_test.py
```

### Full Test Suite

For comprehensive testing:
```bash
# 1. Reset demo data
cd api && python reset_demo.py

# 2. Run integration tests
python tests/final_integration_test.py

# 3. Run manual system test
python tests/manual_system_test.py

# 4. Check API documentation
python tests/check_api_docs_accuracy.py
```

## Test Coverage

- ✅ API Authentication
- ✅ Carrier Verification (FMCSA)
- ✅ Load Search (city, state, equipment)
- ✅ Booking Flow
- ✅ Double-booking Prevention
- ✅ Call Outcome Logging
- ✅ Metrics Tracking
- ✅ Error Handling
- ✅ Dashboard Integration

## Adding New Tests

When adding new tests:
1. Use the existing test structure
2. Include clear test descriptions
3. Handle both success and failure cases
4. Update this README