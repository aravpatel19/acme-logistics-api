from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ============================================================================
# CARRIER VERIFICATION MODELS
# ============================================================================

class CarrierVerifyRequest(BaseModel):
    mc_number: str = Field(..., description="Motor Carrier number")


class CarrierVerifyResponse(BaseModel):
    eligible: bool
    carrier_name: str
    allowed_to_operate: str
    status_code: str
    out_of_service: str
    carrier_operation: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = None
    dot_number: Optional[str] = None
    message: str


# ============================================================================
# LOAD SEARCH MODELS (UPDATED - Origin required)
# ============================================================================

class LoadSearchRequest(BaseModel):
    """
    Search request for loads
    
    REQUIRED: origin_city OR origin_state (at least one)
    OPTIONAL: destination, equipment_type, pickup_date
    """
    # REQUIRED: At least one origin field
    origin_city: Optional[str] = Field(None, description="Origin city (required: city OR state)")
    origin_state: Optional[str] = Field(None, description="Origin state (required: city OR state)")
    
    # OPTIONAL: Destination
    destination_city: Optional[str] = Field(None, description="Destination city (optional)")
    destination_state: Optional[str] = Field(None, description="Destination state (optional)")
    
    # OPTIONAL: Equipment type (was required, now optional)
    equipment_type: Optional[str] = Field(None, description="Type of equipment (optional)")
    
    # OPTIONAL: Timing
    pickup_date: Optional[str] = Field(None, description="Preferred pickup date (YYYY-MM-DD)")
    
    # Control
    max_results: int = Field(default=10, le=20, description="Maximum loads to return")
    
    class Config:
        json_schema_extra = {
            "example": {
                "origin_city": "Los Angeles",
                "destination_city": "Chicago",
                "equipment_type": "Dry Van",
                "max_results": 10
            }
        }


class LoadDetail(BaseModel):
    load_id: str
    reference_number: str
    route: str
    origin: str
    destination: str
    rate: float
    miles: int
    pickup: str
    delivery: str
    equipment: str
    weight: int
    commodity: str


class LoadSearchResponse(BaseModel):
    loads: list[LoadDetail]
    count: int


# ============================================================================
# CALL LOGGING MODELS
# ============================================================================

class CallOutcome(str, Enum):
    booked = "booked"
    not_interested = "not_interested"
    no_agreement = "no_agreement"
    carrier_not_eligible = "carrier_not_eligible"
    already_booked = "already_booked"
    offer_made = "offer_made"  # Legacy, kept for compatibility


class CallSentiment(str, Enum):
    positive = "positive"
    neutral = "neutral"
    negative = "negative"


class CallLogRequest(BaseModel):
    call_id: str
    mc_number: str
    carrier_name: Optional[str] = None
    load_id: Optional[str] = None
    outcome: CallOutcome
    sentiment: CallSentiment
    agreed_rate: Optional[float] = None
    negotiation_rounds: int = 0
    call_duration_seconds: Optional[int] = None
    notes: Optional[str] = None


# ============================================================================
# METRICS MODELS
# ============================================================================

class MetricsResponse(BaseModel):
    total_calls: int
    successful_bookings: int
    success_rate: float
    avg_negotiation_rounds: float
    total_revenue: float
    calls_by_outcome: dict
    sentiment_breakdown: dict
    recent_calls: list


# ============================================================================
# HAPPYROBOT API FORMAT MODELS
# ============================================================================

class OfferLogRequest(BaseModel):
    """Request body for logging carrier offers/calls"""
    load_id: Optional[str] = Field(None, description="Load ID if discussing specific load")
    mc_number: str = Field(..., description="Carrier's MC number")
    carrier_name: Optional[str] = Field(None, description="Carrier company name")
    carrier_offer: Optional[float] = Field(None, description="Price offered by carrier")
    outcome: CallOutcome = Field(..., description="Call outcome")
    sentiment: CallSentiment = Field(CallSentiment.neutral, description="Call sentiment")
    negotiation_rounds: int = Field(0, description="Number of negotiation rounds")
    call_duration: int = Field(0, description="Call duration in seconds")
    notes: Optional[str] = Field(None, description="Additional notes about the call")
    
    class Config:
        json_schema_extra = {
            "examples": [
                {
                    "load_id": "LOAD-001",
                    "mc_number": "123456",
                    "carrier_name": "ABC Trucking",
                    "carrier_offer": 3650.00,
                    "outcome": "booked",
                    "sentiment": "positive",
                    "negotiation_rounds": 2,
                    "call_duration": 240,
                    "notes": "Carrier accepted after negotiation"
                },
                {
                    "mc_number": "999999",
                    "carrier_name": "Unknown Carrier",
                    "outcome": "carrier_not_eligible",
                    "sentiment": "neutral",
                    "call_duration": 45,
                    "notes": "Carrier not found in FMCSA database"
                }
            ]
        }


class HappyRobotResponse(BaseModel):
    """Standard HappyRobot API response format"""
    statusCode: int = Field(200, description="HTTP status code")
    body: Dict[str, Any] = Field(..., description="Response data")


class LoadLocation(BaseModel):
    """Location details for load stops"""
    city: str
    state: str
    zip: str = ""
    country: str = "US"


class LoadStop(BaseModel):
    """Stop information for loads"""
    type: str = Field(..., description="Stop type: origin or destination")
    location: LoadLocation
    stop_timestamp_open: str
    stop_timestamp_close: str
    is_appointment_required: bool = False


class LoadContact(BaseModel):
    """Contact information for loads"""
    name: str = "Dispatch"
    email: str = "dispatch@acmelogistics.com"
    phone: str = "18005551234"
    extension: str = ""
    type: str = "dispatch"


class LoadResponse(BaseModel):
    """Individual load in HappyRobot format"""
    reference_number: str
    load_id: str
    contact: LoadContact
    type: str = "can_get"
    status: str = Field(..., description="available or booked")
    is_partial: bool = False
    stops: List[LoadStop]
    origin: str
    destination: str
    miles: int
    equipment_type: str
    weight: int
    posted_carrier_rate: float
    loadboard_rate: float
    rate_per_mile: float
    max_buy: float = Field(..., description="Maximum we'll pay (5% over posted rate)")
    pickup_datetime: str
    delivery_datetime: str
    commodity_type: str
    notes: str
    sale_notes: str
    branch: str = "Main"
    bridge: Dict[str, str]


class CarrierResponse(BaseModel):
    """Carrier information in HappyRobot format"""
    carrier_id: str
    carrier_name: str
    status: str
    dot_number: str
    mc_number: str
    contacts: List = []
    insurance_on_file: Optional[float] = None
    bridge: Dict[str, str]