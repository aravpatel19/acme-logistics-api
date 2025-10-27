from fastapi import FastAPI, HTTPException, Depends, Security, Query, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from typing import Optional
import httpx
import os
from dotenv import load_dotenv
import logging
from datetime import datetime, timedelta
from collections import defaultdict

# Import our services
from services.fmcsa import FMCSAService
from services.loads import LoadService
from services.metrics import MetricsService

# Import our models
from models import (
    OfferLogRequest, HappyRobotResponse, CallOutcome, CallSentiment,
    LoadResponse, CarrierResponse
)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Async context manager for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifecycle"""
    # Startup
    logger.info("Starting Acme Logistics API...")
    
    # Initialize HTTP client
    app.state.http_client = httpx.AsyncClient(timeout=15.0)
    
    # Initialize services
    app.state.loads = await LoadService.initialize()
    app.state.metrics = MetricsService()
    
    logger.info(f"✅ Loaded {len(app.state.loads.loads)} freight loads")
    logger.info(f"✅ Metrics service initialized")
    logger.info("🚀 API is ready!")
    
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await app.state.http_client.aclose()
    await app.state.metrics.save()
    logger.info("👋 Goodbye!")

# Create FastAPI app
app = FastAPI(
    title="Acme Logistics Bridge API",
    description="API for HappyRobot voice agent integration",
    version="1.0.0",
    lifespan=lifespan
)

# CORS - Configured for demo (specify your HappyRobot domain in production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:8000",
        "http://localhost:8001",  # Dashboard
        "https://*.happyrobot.ai",
        "https://*.ngrok.io",  # For testing with ngrok
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

# Security
security = HTTPBearer()

# Simple in-memory rate limiting for demo
from collections import defaultdict
from datetime import datetime, timedelta

rate_limit_storage = defaultdict(list)
RATE_LIMIT_REQUESTS = 60  # requests per minute

async def verify_api_key(
    credentials: HTTPAuthorizationCredentials = Security(security)
) -> str:
    """Verify API key with rate limiting"""
    expected_key = os.getenv("ACME_API_KEY")
    
    if not expected_key:
        logger.error("ACME_API_KEY not configured")
        raise HTTPException(status_code=500, detail="Server configuration error")
    
    if credentials.credentials != expected_key:
        logger.warning(f"Invalid API key attempt")
        raise HTTPException(status_code=403, detail="Invalid API Key")
    
    # Simple rate limiting
    now = datetime.now()
    minute_ago = now - timedelta(minutes=1)
    
    # Clean old entries
    rate_limit_storage[credentials.credentials] = [
        timestamp for timestamp in rate_limit_storage[credentials.credentials]
        if timestamp > minute_ago
    ]
    
    # Check rate limit
    if len(rate_limit_storage[credentials.credentials]) >= RATE_LIMIT_REQUESTS:
        raise HTTPException(status_code=429, detail="Rate limit exceeded")
    
    # Record this request
    rate_limit_storage[credentials.credentials].append(now)
    
    return credentials.credentials


# ============================================================================
# HAPPYROBOT-COMPATIBLE ENDPOINTS
# ============================================================================

@app.get("/api/v1/loads", response_model=HappyRobotResponse)
async def get_loads(
    # REQUIRED: At least one origin parameter
    origin_city: Optional[str] = Query(None, description="Origin city (required: city OR state)"),
    origin_state: Optional[str] = Query(None, description="Origin state (required: city OR state)"),
    
    # OPTIONAL: Everything else
    destination_city: Optional[str] = Query(None, description="Destination city (optional)"),
    destination_state: Optional[str] = Query(None, description="Destination state (optional)"),
    equipment_type: Optional[str] = Query(None, description="Equipment type (optional)"),
    pickup_date: Optional[str] = Query(None, description="Pickup date ISO 8601 (optional)"),
    include_booked: bool = Query(False, description="Include booked loads in results"),
    
    api_key: str = Depends(verify_api_key)
):
    """
    Search for available freight loads
    
    Returns loads matching the search criteria in HappyRobot format.
    Loads are automatically filtered to exclude already booked loads unless include_booked=true.
    
    **REQUIRED**: Must provide either origin_city OR origin_state (carriers always know their location)
    
    **Response includes:**
    - Load details with origin/destination
    - Equipment type and commodity
    - Posted rate and max_buy (5% over posted rate)
    - Pickup/delivery dates
    - Notes for the voice agent to use
    
    Loads are sorted by rate (highest first) to present best opportunities.
    """
    
    # If no parameters provided, return all loads
    # This is useful for dashboard views
    
    logger.info(f"🔍 Load search: origin={origin_city or origin_state}, "
                f"dest={destination_city or destination_state or 'any'}, "
                f"equipment={equipment_type or 'any'}, "
                f"include_booked={include_booked}")
    
    try:
        # Search loads
        if include_booked:
            # Special case for dashboard - get ALL loads regardless of booking status
            results = await app.state.loads.search(
                origin_city=origin_city,
                origin_state=origin_state,
                destination_city=destination_city,
                destination_state=destination_state,
                equipment_type=equipment_type,
                pickup_date=pickup_date,
                max_results=100,  # Get more loads when including booked
                include_booked=True
            )
        else:
            # Normal search - exclude booked loads (for HappyRobot)
            results = await app.state.loads.search(
                origin_city=origin_city,
                origin_state=origin_state,
                destination_city=destination_city,
                destination_state=destination_state,
                equipment_type=equipment_type,
                pickup_date=pickup_date,
                max_results=10
            )
        
        # Format for HappyRobot - SIMPLIFIED FLAT STRUCTURE
        formatted_loads = []
        for load in results:
            # Parse origin
            origin_parts = load["origin"].split(",")
            origin_city_parsed = origin_parts[0].strip() if len(origin_parts) > 0 else ""
            origin_state_parsed = origin_parts[1].strip() if len(origin_parts) > 1 else ""
            
            # Parse destination
            dest_parts = load["destination"].split(",")
            dest_city_parsed = dest_parts[0].strip() if len(dest_parts) > 0 else ""
            dest_state_parsed = dest_parts[1].strip() if len(dest_parts) > 1 else ""
            
            # Calculate rate per mile
            rate_per_mile = round(load["loadboard_rate"] / load["miles"], 2) if load["miles"] > 0 else 0
            
            # SIMPLE FLAT STRUCTURE
            formatted_loads.append({
                # Identifiers
                "reference_number": load["load_id"],
                "load_id": load["load_id"],
                
                # Contact
                "contact": {
                    "name": "Dispatch",
                    "email": "dispatch@acmelogistics.com",
                    "phone": "18005551234",
                    "extension": "",
                    "type": "dispatch"
                },
                
                # Type and status
                "type": "can_get",
                "status": "booked" if load.get("is_booked", False) else "available",
                "is_partial": False,
                
                # Stops (required by HappyRobot)
                "stops": [
                    {
                        "type": "origin",
                        "location": {
                            "city": origin_city_parsed,
                            "state": origin_state_parsed,
                            "zip": "",
                            "country": "US"
                        },
                        "stop_timestamp_open": load["pickup_datetime"],
                        "stop_timestamp_close": load["pickup_datetime"]
                    },
                    {
                        "type": "destination",
                        "location": {
                            "city": dest_city_parsed,
                            "state": dest_state_parsed,
                            "zip": "",
                            "country": "US"
                        },
                        "stop_timestamp_open": load["delivery_datetime"],
                        "stop_timestamp_close": load["delivery_datetime"]
                    }
                ],
                
                # Route info (flat)
                "origin": load["origin"],
                "destination": load["destination"],
                "miles": load["miles"],
                
                # Equipment and cargo (flat)
                "equipment_type": load["equipment_type"],
                "weight": load["weight"],
                "number_of_pieces": load["num_of_pieces"],
                "commodity_type": load["commodity_type"],
                "dimensions": load.get("dimensions", ""),
                
                # Pricing (flat)
                "posted_carrier_rate": load["loadboard_rate"],
                "max_buy": round(load["loadboard_rate"] * 1.05, 2),
                "rate_per_mile": rate_per_mile,
                
                # Schedule (flat)
                "pickup_datetime": load["pickup_datetime"],
                "delivery_datetime": load["delivery_datetime"],
                "pickup_date": load["pickup_datetime"].split("T")[0],
                "delivery_date": load["delivery_datetime"].split("T")[0],
                
                # Notes
                "notes": app.state.loads.generate_load_notes(load),
                "sale_notes": load.get("notes", ""),
                
                # Metadata
                "branch": "Main",
                "bridge": {
                    "status": "success",
                    "bridge_load_id": f"BRK-{load['load_id']}"
                }
            })
        
        logger.info(f"✅ Found {len(formatted_loads)} matching loads")
        
        # HappyRobot expects this format
        return {
            "statusCode": 200,
            "body": {
                "loads": formatted_loads
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Load search error: {e}")
        return {
            "statusCode": 500,
            "body": {
                "error": f"Load search failed: {str(e)}"
            }
        }


@app.get("/api/v1/carriers/find", response_model=HappyRobotResponse)
async def get_carrier(
    mc: Optional[str] = Query(None, description="Motor Carrier (MC) number"),
    dot: Optional[str] = Query(None, description="DOT number"),
    api_key: str = Depends(verify_api_key)
):
    """
    Verify carrier eligibility through FMCSA database
    
    This endpoint checks if a carrier is authorized to operate by verifying:
    - Active FMCSA authority
    - Valid insurance on file
    - Not out of service
    
    Returns carrier details if found and eligible.
    Returns 404 if carrier not found or not eligible.
    """
    logger.info(f"📞 Carrier lookup: MC={mc}, DOT={dot}")
    
    # Validation
    if not mc and not dot:
        return {
            "statusCode": 400,
            "body": {
                "error": "Either mc or dot must be provided"
            }
        }
    
    try:
        # Get environment variables
        fmcsa_api_key = os.getenv("FMCSA_API_KEY")
        fmcsa_base_url = os.getenv(
            "FMCSA_BASE_URL",
            "https://mobile.fmcsa.dot.gov/qc/services"
        )
        
        if not fmcsa_api_key:
            return {
                "statusCode": 500,
                "body": {
                    "error": "FMCSA API key not configured"
                }
            }
        
        # Create FMCSA service and verify
        fmcsa_service = FMCSAService(
            app.state.http_client,
            fmcsa_api_key,
            fmcsa_base_url
        )
        
        # Use MC number if provided, otherwise DOT
        lookup_number = mc or dot
        result = await fmcsa_service.verify_carrier(lookup_number)
        
        # Log verification attempt if not eligible
        if not result["eligible"]:
            await app.state.metrics.log_call(
                call_id=f"call_verify_{mc or dot}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                mc_number=mc or dot,
                carrier_name=result.get("carrier_name", "Unknown Carrier"),
                load_id=None,
                outcome="carrier_not_eligible",
                sentiment="negative",
                agreed_rate=None,
                negotiation_rounds=0,
                call_duration_seconds=30,  # Assume short call for failed verification
                notes=result.get("message", "Not eligible")
            )
            logger.info(f"❌ Carrier not eligible: MC/DOT {mc or dot} - {result.get('message', 'Unknown reason')}")
        else:
            logger.info(f"✅ Carrier found and eligible: {result['carrier_name']}")
        
        # Always format and return carrier information
        carrier_response = {
            "carrier_id": f"CAR-{mc or dot}",
            "carrier_name": result["carrier_name"],
            "mc_number": result.get("mc_number", mc or ""),
            "dot_number": result.get("dot_number", dot or ""),
            "eligible": result["eligible"],
            "status": "active" if result["status_code"] == "A" else "inactive",
            "status_code": result["status_code"],
            "status_description": result.get("status_description", ""),
            "allowed_to_operate": result["allowed_to_operate"],
            "out_of_service": result["out_of_service"],
            "carrier_operation": result.get("carrier_operation", ""),
            "city": result.get("city", ""),
            "state": result.get("state", ""),
            "address": result.get("address", ""),
            "zip_code": result.get("zip_code", ""),
            "phone": result.get("phone", ""),
            "insurance_on_file": result.get("insurance_on_file", 0),
            "insurance_required": result.get("insurance_required", 0),
            "message": result["message"],
            "notes": result["message"],  # Duplicate message in notes field for easier parsing
            "contacts": [],  # We don't have contact info from FMCSA
            "bridge": {
                "status": "success",
                "bridge_carrier_id": f"BRK-{mc or dot}"
            }
        }
        
        # Always return 200 with carrier information
        return {
            "statusCode": 200,
            "body": {
                "carrier": carrier_response
            }
        }
        
    except Exception as e:
        logger.error(f"❌ Carrier lookup error: {e}")
        return {
            "statusCode": 500,
            "body": {
                "error": f"Carrier lookup failed: {str(e)}"
            }
        }


@app.post("/api/v1/offers/log", response_model=HappyRobotResponse)
async def log_offer(
    request: OfferLogRequest = Body(..., 
        description="Call/offer details to log",
        openapi_examples={
            "successful_booking": {
                "summary": "Successful booking",
                "value": {
                    "load_id": "LOAD-001",
                    "mc_number": "123456",
                    "carrier_name": "ABC Trucking",
                    "carrier_offer": 3650.00,
                    "outcome": "booked",
                    "sentiment": "positive",
                    "negotiation_rounds": 2,
                    "call_duration": 240,
                    "notes": "Carrier accepted after negotiation"
                }
            },
            "carrier_rejected": {
                "summary": "Carrier not eligible",
                "value": {
                    "mc_number": "999999",
                    "carrier_name": "Unknown Carrier",
                    "outcome": "carrier_not_eligible",
                    "sentiment": "neutral",
                    "call_duration": 45,
                    "notes": "Carrier not found in FMCSA database"
                }
            }
        }
    ),
    api_key: str = Depends(verify_api_key)
):
    """
    Log carrier call outcomes and offers
    
    This endpoint is used to track all carrier interactions including:
    - Successful bookings
    - Failed verifications
    - Rejected offers
    - Price negotiations
    - Already booked loads
    
    The outcome field is critical for tracking call results.
    """
    logger.info(f"📝 Logging offer: Load {request.load_id}, MC {request.mc_number}, Outcome: {request.outcome}")
    
    try:
        # Validate load exists (only if load_id is provided)
        if request.load_id:
            load = await app.state.loads.get_by_id(request.load_id)
            if not load:
                return HappyRobotResponse(
                    statusCode=404,
                    body={
                        "error": f"Load with ID {request.load_id} not found"
                    }
                )
        
        # Check if load is already booked
        if request.load_id and request.outcome == "booked":
            if not app.state.loads.is_load_available(request.load_id):
                logger.warning(f"⚠️ Attempt to book already booked load: {request.load_id}")
                # Log the failed attempt
                await app.state.metrics.log_call(
                    call_id=f"call_{request.load_id}_{request.mc_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}",
                    mc_number=request.mc_number,
                    carrier_name=request.carrier_name,
                    load_id=request.load_id,
                    outcome="already_booked",
                    sentiment="negative",
                    agreed_rate=None,
                    negotiation_rounds=request.negotiation_rounds,
                    call_duration_seconds=request.call_duration,
                    notes="Load was already booked by another carrier"
                )
                return HappyRobotResponse(
                    statusCode=409,  # Conflict
                    body={
                        "error": "Load already booked",
                        "message": f"Load {request.load_id} has already been booked by another carrier"
                    }
                )
        
        # Log the offer as a call with enhanced data
        call_id = f"call_{request.load_id}_{request.mc_number}_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        await app.state.metrics.log_call(
            call_id=call_id,
            mc_number=request.mc_number,
            carrier_name=request.carrier_name,
            load_id=request.load_id,
            outcome=request.outcome.value,
            sentiment=request.sentiment.value,
            agreed_rate=request.carrier_offer if request.outcome == CallOutcome.booked else None,
            negotiation_rounds=request.negotiation_rounds,
            call_duration_seconds=request.call_duration,
            notes=request.notes
        )
        
        # If the outcome is "booked", mark the load as unavailable
        if request.outcome == CallOutcome.booked and request.load_id:
            app.state.loads.mark_as_booked(request.load_id)
            logger.info(f"✅ Load {request.load_id} marked as booked")
        
        logger.info(f"✅ Call logged: {request.outcome.value} - MC {request.mc_number}")
        
        # Return HappyRobot format
        return HappyRobotResponse(
            statusCode=201,
            body={
                "message": "Call logged successfully",
                "call_id": call_id
            }
        )
        
    except Exception as e:
        logger.error(f"❌ Offer logging error: {e}")
        return HappyRobotResponse(
            statusCode=500,
            body={
                "error": "Internal server error"
            }
        )


# ============================================================================
# DASHBOARD
# ============================================================================

# Mount dashboard static files
dashboard_path = os.path.join(os.path.dirname(__file__), "..", "dashboard")
if os.path.exists(dashboard_path):
    app.mount("/static", StaticFiles(directory=dashboard_path), name="static")

@app.get("/dashboard")
async def dashboard():
    """Serve the dashboard HTML"""
    dashboard_file = os.path.join(dashboard_path, "index.html")
    if os.path.exists(dashboard_file):
        return FileResponse(dashboard_file)
    else:
        raise HTTPException(status_code=404, detail="Dashboard not found")

# ============================================================================
# ADMIN/DEBUG ENDPOINTS
# ============================================================================

@app.get("/")
async def root():
    """Health check"""
    return {
        "service": "Acme Logistics Bridge API",
        "status": "operational",
        "version": "1.0.0",
        "dashboard": "/dashboard"
    }


@app.get("/healthcheck")
async def healthcheck():
    """Detailed health check"""
    return {
        "status": "healthy",
        "loads_available": len(app.state.loads.loads),
        "loads_booked": len(app.state.loads.booked_loads),
        "booked_load_ids": list(app.state.loads.booked_loads),
        "services": {
            "fmcsa": "operational",
            "loads": "operational",
            "metrics": "operational"
        }
    }


@app.get("/metrics")
async def get_metrics(api_key: str = Depends(verify_api_key)):
    """Get dashboard metrics"""
    try:
        metrics = await app.state.metrics.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/metrics/reset")
async def reset_metrics(api_key: str = Depends(verify_api_key)):
    """Reset all metrics data (useful for demos)"""
    try:
        # Clear the metrics
        app.state.metrics.calls = []
        await app.state.metrics.save()
        
        # Also clear booked loads tracking
        app.state.loads.booked_loads.clear()
        
        logger.info("🧹 Metrics and booking data reset")
        
        return {
            "status": "success",
            "message": "All metrics and booking data have been reset"
        }
    except Exception as e:
        logger.error(f"Failed to reset metrics: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Removed unnecessary endpoints:
# - /loads (debug endpoint not needed)
# - /loads/{load_id} (not used by HappyRobot)  
# - /api/v1/loads/{load_id}/status (not used by HappyRobot)


# ============================================================================
# ERROR HANDLERS
# ============================================================================

@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc):
    """Custom HTTP exception handler"""
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "status_code": exc.status_code
        }
    )


@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    """Catch-all exception handler"""
    logger.error(f"Unhandled exception: {exc}")
    # Don't leak exception details in production
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "message": "An unexpected error occurred. Please try again later."
        }
    )


# ============================================================================
# RUN SERVER
# ============================================================================

if __name__ == "__main__":
    import uvicorn
    
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    logger.info(f"🚀 Starting server on {host}:{port}")
    
    uvicorn.run(
        app,
        host=host,
        port=port,
        reload=False
    )