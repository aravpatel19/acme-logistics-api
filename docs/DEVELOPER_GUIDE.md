# Developer Guide: Safe Code Changes

This guide explains how to safely make changes to the Acme Logistics automation system without breaking functionality.

## System Architecture Overview

The system consists of:
- **FastAPI Backend** (`api/main.py`) - Core API with 3 HappyRobot endpoints + dashboard/metrics endpoints
- **Service Layer** (`api/services/`) - Business logic modules (fmcsa.py, loads.py, metrics.py)
- **Data Models** (`api/models.py`) - Pydantic schemas for validation
- **Dashboard** (`dashboard/`) - Real-time monitoring interface (JavaScript/Chart.js)
- **External Integration** - HappyRobot voice AI platform

## Safe Change Process

### 1. Pre-Change Checklist
- [ ] Understand what you're changing and why
- [ ] Identify which files will be affected
- [ ] Consider downstream impacts (see "Ripple Effects" section)
- [ ] Have a rollback plan

### 2. Making Changes Locally
```bash
# 1. Make your code changes
# 2. Start local servers
./start_servers.sh

# 3. Test immediately
curl -H "Authorization: Bearer acme_dev_test_key_123" \
     "http://localhost:8000/api/v1/carriers/find?mc=123456"
```

### 3. Validation Steps (CRITICAL)
```bash
# Run integration tests
python tests/final_integration_test.py

# Check dashboard functionality
open http://localhost:8001/dashboard

# Verify API documentation
open http://localhost:8000/docs

# Test specific endpoints if needed
curl -H "Authorization: Bearer acme_dev_test_key_123" \
     "http://localhost:8000/api/v1/loads?origin_state=CA"
```

### 4. Deployment
- Test locally first (always)
- Deploy to staging if available
- Monitor logs after deployment
- Keep rollback ready

## Common Change Scenarios

### Business Logic Changes (LOW RISK)

**Examples**: Carrier eligibility criteria, pricing calculations, load matching rules

**Primary Files**:
- `api/services/fmcsa.py` - Carrier verification logic
- `api/services/loads.py` - Load search and matching
- `api/services/metrics.py` - Analytics calculations

**Process**:
1. Modify the specific service function
2. Test the affected endpoint
3. Verify dashboard metrics still work

**Ripple Effects**: Usually none - services are well-isolated

### API Parameter Changes (MEDIUM RISK)

**Examples**: Adding filters, changing required fields, modifying response format

**Primary Files**:
- `api/models.py` - Request/response schemas
- `api/main.py` - Endpoint implementations

**Process**:
1. Update Pydantic models first
2. Modify endpoint logic
3. Test with both old and new parameter combinations
4. Update API documentation if needed

**Ripple Effects**:
- HappyRobot workflows may need updates
- Dashboard JavaScript may need changes
- Integration tests require updates

### Database/Data Structure Changes (HIGH RISK)

**Examples**: Changing load data format, metrics storage structure

**Primary Files**:
- `api/data/loads.json` - Load dataset
- `api/data/metrics.json` - Metrics storage
- Related service files

**Process**:
1. Create data migration script if needed
2. Update all code that reads/writes the data
3. Test with existing data
4. Verify dashboard displays correctly

**Ripple Effects**:
- All endpoints using the data
- Dashboard charts and displays
- Metrics calculations
- Test data files

## Ripple Effect Matrix

When you change X, also check Y:

| Change Type | Also Check/Update |
|-------------|------------------|
| Carrier eligibility logic | Dashboard metrics, test assertions, FMCSA service logic |
| Load search parameters | HappyRobot workflow, API docs, Dashboard load display |
| Response data format | Dashboard JavaScript, integration tests, HappyRobot webhooks |
| API endpoint URLs | HappyRobot configuration, deployment scripts, dashboard API calls |
| Environment variables | Docker files, deployment configs, .env.example |
| Database schema | Migration scripts, all data access code |
| Rate limits | API response times, dashboard refresh intervals |
| Authentication | All API endpoints, dashboard localStorage handling |

## File Dependencies Map

### Core Dependencies
```
api/main.py
├── services/fmcsa.py (carrier verification)
├── services/loads.py (load management)
├── services/metrics.py (analytics)
└── models.py (data validation)

dashboard/app.js
├── Depends on: /api/v1/loads, /metrics endpoints
└── Affects: Real-time data display

tests/final_integration_test.py
├── Tests all API endpoints
└── Must be updated for API changes
```

### Critical Integration Points
- **HappyRobot**: Expects specific response format from all `/api/v1/*` endpoints
- **Dashboard**: Relies on `/metrics` endpoint and load status data
- **FMCSA API**: External dependency - changes here affect carrier verification

## Safety Nets

### 1. Automated Validation
```bash
# Always run before deploying
python tests/final_integration_test.py
```

### 2. Real-time Monitoring
- Dashboard at `/dashboard` shows system health
- Logs in console show request/response flows
- Metrics endpoint shows data integrity

### 3. Error Handling
The system has built-in error handling:
- Invalid API keys return 403
- Missing data returns 404 
- Server errors return 500 with safe messages

## Red Flags - Stop Immediately If You See:

- ❌ Dashboard stops loading or shows empty data
- ❌ Integration tests fail
- ❌ 500 errors in API responses
- ❌ Missing required fields in API docs
- ❌ HappyRobot webhooks returning errors

## Environment-Specific Considerations

### Local Development
- Uses `acme_dev_test_key_123` API key
- Data persists between restarts
- Both API (8000) and dashboard (8001) must run

### Production (Fly.io)
- Uses production API keys from environment
- Data stored in persistent volumes
- Single container runs both services
- HTTPS required for HappyRobot integration

## Emergency Rollback

If something breaks in production:

```bash
# Quick rollback to last working state
git log --oneline -5  # Find last good commit
git checkout <commit-hash>
./deploy-to-flyio.sh  # Redeploy
```

## Best Practices

1. **One change at a time** - Don't modify multiple systems simultaneously
2. **Test locally first** - Never push untested changes
3. **Check the dashboard** - Real-time validation of data flow
4. **Update tests** - Keep integration tests current
5. **Monitor after deployment** - Watch logs for the first few minutes
6. **Document breaking changes** - Update API docs and this guide
7. **Preserve API contracts** - HappyRobot depends on exact response formats
8. **Test data population** - Use `python tests/populate_metrics.py` for demo data

## Getting Help

- **Logs**: Check console output for detailed error messages
- **API Docs**: `/docs` endpoint shows current API contract
- **Test Suite**: `tests/final_integration_test.py` shows expected behavior
- **Dashboard**: Real-time system health at `/dashboard`

Remember: The modular architecture makes most changes safe, but always validate the integration points.