# API Key Management

Need to give different people access to your API? Here's how to manage multiple keys without making a mess of things.

## Current setup

Right now you've got one API key in the `ACME_API_KEY` environment variable. That's fine for getting started, but you'll probably need more.

## Adding multiple API keys

### Quick and dirty: Comma-separated keys

1. **Update your .env file**:
   ```bash
   ACME_API_KEY=key1,key2,key3,key4
   ```

2. **Modify api/main.py** to check against multiple keys:
   ```python
   async def verify_api_key(
       credentials: HTTPAuthorizationCredentials = Security(security)
   ) -> str:
       """Verify API key with support for multiple keys"""
       expected_keys = os.getenv("ACME_API_KEY", "").split(",")
       expected_keys = [k.strip() for k in expected_keys if k.strip()]
       
       if not expected_keys:
           logger.error("ACME_API_KEY not configured")
           raise HTTPException(status_code=500, detail="Server configuration error")
       
       if credentials.credentials not in expected_keys:
           logger.warning(f"Invalid API key attempt")
           raise HTTPException(status_code=403, detail="Invalid API Key")
       
       # ... rest of rate limiting code
   ```

3. **Deploy with multiple keys**:
   - Development: `ACME_API_KEY=dev_key_123,test_key_456`
   - Production: `ACME_API_KEY=prod_key_abc,partner_key_xyz,dashboard_key_789`

### Proper solution: Key management system

When you need to track who's using what:

1. **Create a keys table/file** (`api/data/api_keys.json`):
   ```json
   {
     "prod_key_abc": {
       "name": "Production Dashboard",
       "created": "2024-01-01",
       "rate_limit": 60,
       "active": true
     },
     "partner_key_xyz": {
       "name": "HappyRobot Integration",
       "created": "2024-01-01",
       "rate_limit": 100,
       "active": true
     }
   }
   ```

2. **Create key management endpoints**:
   ```python
   @app.post("/admin/keys/create")
   async def create_api_key(name: str, admin_key: str):
       # Verify admin key
       # Generate new key
       # Store in database/file
       # Return new key
   ```

### Easy mode: Use Railway's dashboard

If you're deploying to Railway, manage keys through their UI:

1. **Go to Railway Dashboard** → Your Project → Variables
2. **Update ACME_API_KEY** with comma-separated values
3. **Redeploy** - changes take effect immediately

## Tips from the trenches

1. **Name your keys properly**
   - `prod_` for production (don't mess these up)
   - `dev_` for development (go wild)
   - `test_` for testing (break things here)
   - `client_[name]_` for specific partners

2. **Rotate keys before they get stale**
   - Keep old keys working for 30 days during transition
   - Tell people before you kill their keys (they hate surprises)

3. **Watch what's happening**
   - Log which keys are being used
   - Look for weird patterns (like 10,000 calls at 3am)
   - Give different rate limits to different keys

## Quick start: Add a new key in 30 seconds

1. **Local development**:
   ```bash
   # Before
   ACME_API_KEY=acme_dev_test_key_123
   
   # After (just add a comma)
   ACME_API_KEY=acme_dev_test_key_123,new_client_key_456
   ```

2. **Production (Railway)**:
   - Go to Variables tab
   - Edit ACME_API_KEY
   - Add comma and new key
   - Save (deploys automatically)

3. **Make sure it works**:
   ```bash
   curl -H "Authorization: Bearer new_client_key_456" \
     https://acme-logistics-api.up.railway.app/healthcheck
   ```

## Don't be that person who...

- Commits API keys to Git (seriously, don't)
- Hardcodes keys in the app
- Never rotates keys
- Doesn't monitor key usage
- Forgets to tell people before killing their keys