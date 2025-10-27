import json
import os
from typing import Dict, List, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class MetricsService:
    """
    Service for tracking and reporting call metrics
    Simplified version - HappyRobot handles negotiation
    """
    
    def __init__(self, data_path: str = "data/metrics.json"):
        self.data_path = data_path
        self.calls: List[Dict] = []
        self._load()
    
    def _load(self):
        """Load existing metrics from file"""
        try:
            if os.path.exists(self.data_path):
                with open(self.data_path, 'r') as f:
                    self.calls = json.load(f)
                logger.info(f"Loaded {len(self.calls)} call records")
        except Exception as e:
            logger.error(f"Failed to load metrics: {e}")
            self.calls = []
    
    async def save(self):
        """Save metrics to file"""
        try:
            os.makedirs(os.path.dirname(self.data_path), exist_ok=True)
            with open(self.data_path, 'w') as f:
                json.dump(self.calls, f, indent=2)
            logger.info(f"Saved {len(self.calls)} call records")
        except Exception as e:
            logger.error(f"Failed to save metrics: {e}")
    
    async def log_call(
        self,
        call_id: str,
        mc_number: str,
        carrier_name: Optional[str] = None,
        load_id: Optional[str] = None,
        outcome: str = "unknown",
        sentiment: str = "neutral",
        agreed_rate: Optional[float] = None,
        negotiation_rounds: int = 0,
        call_duration_seconds: Optional[int] = None,
        notes: Optional[str] = None
    ):
        """Log a completed call"""
        call_record = {
            "call_id": call_id,
            "mc_number": mc_number,
            "carrier_name": carrier_name,
            "load_id": load_id,
            "outcome": outcome,  # booked, declined, no_suitable_loads, etc.
            "sentiment": sentiment,  # positive, neutral, negative
            "agreed_rate": agreed_rate,
            "negotiation_rounds": negotiation_rounds,
            "call_duration_seconds": call_duration_seconds,
            "notes": notes,
            "timestamp": datetime.now().isoformat()
        }
        
        self.calls.append(call_record)
        await self.save()
        
        logger.info(f"Logged call {call_id}: outcome={outcome}, sentiment={sentiment}")
        
        return call_record
    
    async def get_metrics(self) -> Dict:
        """Get aggregated metrics for dashboard"""
        if not self.calls:
            return {
                "total_calls": 0,
                "successful_bookings": 0,
                "success_rate": 0.0,
                "avg_negotiation_rounds": 0.0,
                "total_booked_value": 0.0,
                "calls_by_outcome": {},
                "sentiment_breakdown": {},
                "recent_calls": []
            }
        
        # Calculate metrics
        total_calls = len(self.calls)
        successful = [c for c in self.calls if c["outcome"] == "booked"]
        successful_count = len(successful)
        success_rate = (successful_count / total_calls * 100) if total_calls > 0 else 0.0
        
        # Average negotiation rounds (only for booked calls)
        if successful:
            avg_rounds = sum(c.get("negotiation_rounds", 0) for c in successful) / len(successful)
        else:
            avg_rounds = 0.0
        
        # Total booked value (sum of all agreed rates for booked loads)
        total_booked_value = sum(c.get("agreed_rate", 0) or 0 for c in successful)
        
        # Breakdown by outcome
        outcomes = {}
        for call in self.calls:
            outcome = call.get("outcome", "unknown")
            outcomes[outcome] = outcomes.get(outcome, 0) + 1
        
        # Breakdown by sentiment
        sentiments = {}
        for call in self.calls:
            sentiment = call.get("sentiment", "neutral")
            sentiments[sentiment] = sentiments.get(sentiment, 0) + 1
        
        # Recent calls (last 10)
        recent = sorted(self.calls, key=lambda x: x["timestamp"], reverse=True)[:10]
        
        return {
            "total_calls": total_calls,
            "successful_bookings": successful_count,
            "success_rate": round(success_rate, 1),
            "avg_negotiation_rounds": round(avg_rounds, 1),
            "total_booked_value": round(total_booked_value, 2),
            "calls_by_outcome": outcomes,
            "sentiment_breakdown": sentiments,
            "recent_calls": recent
        }
    
    async def log_verification(self, mc_number: str, eligible: bool):
        """Log a carrier verification (for debugging)"""
        logger.info(f"Verification: MC {mc_number} - Eligible: {eligible}")