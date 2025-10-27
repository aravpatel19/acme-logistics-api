import json
import os
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class LoadService:
    """Service for managing and searching freight loads"""
    
    def __init__(self, loads: List[Dict]):
        self.loads = loads
        self.booked_loads = set()  # Track booked load IDs in memory
        logger.info(f"LoadService initialized with {len(loads)} loads")
    
    @classmethod
    async def initialize(cls, data_path: str = "data/loads.json"):
        """Load freight data from JSON file"""
        try:
            with open(data_path, 'r') as f:
                loads = json.load(f)
            logger.info(f"Successfully loaded {len(loads)} loads from {data_path}")
            return cls(loads)
        except FileNotFoundError:
            logger.error(f"Load data file not found: {data_path}")
            return cls([])
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in load data file: {e}")
            return cls([])
    
    async def search(
        self,
        origin_city: Optional[str] = None,
        origin_state: Optional[str] = None,
        destination_city: Optional[str] = None,
        destination_state: Optional[str] = None,
        equipment_type: Optional[str] = None,  # NOW OPTIONAL
        pickup_date: Optional[str] = None,
        max_results: int = 10,
        include_booked: bool = False
    ) -> List[Dict]:
        """
        Search for loads - ORIGIN is required, everything else optional
        
        Business logic:
        1. MUST have origin (city OR state)
        2. Filter by equipment if provided
        3. Filter by destination if provided
        4. Filter by pickup date if provided
        5. Sort by rate (highest first)
        """
        
        # If no search parameters provided, return all loads
        if not origin_city and not origin_state:
            if include_booked:
                logger.info("No origin filter provided - returning ALL loads (including booked)")
                # Return ALL loads with booking status
                all_with_status = []
                for load in self.loads:
                    load_with_status = load.copy()
                    load_with_status["is_booked"] = load.get("load_id") in self.booked_loads
                    all_with_status.append(load_with_status)
                return sorted(all_with_status, key=lambda x: x.get("loadboard_rate", 0), reverse=True)
            else:
                logger.info("No origin filter provided - returning all available loads")
                # Filter out booked loads and sort by rate (highest first)
                available_loads = [load for load in self.loads if load.get("load_id") not in self.booked_loads]
                return sorted(available_loads, key=lambda x: x.get("loadboard_rate", 0), reverse=True)
        
        results = []
        
        for load in self.loads:
            # Skip booked loads unless explicitly included
            if not include_booked and load.get("load_id") in self.booked_loads:
                continue
                
            load_origin = load.get("origin", "").lower()
            
            # REQUIRED: Origin must match
            origin_matches = False
            
            if origin_city and origin_city.lower() in load_origin:
                origin_matches = True
            
            if origin_state and origin_state.lower() in load_origin:
                origin_matches = True
            
            if not origin_matches:
                continue
            
            # OPTIONAL: Equipment type filter
            if equipment_type:
                load_equipment = load.get("equipment_type", "").lower()
                if equipment_type.lower() != load_equipment:
                    continue
            
            # OPTIONAL: Destination filter
            if destination_city or destination_state:
                load_destination = load.get("destination", "").lower()
                
                destination_matches = False
                
                if destination_city and destination_city.lower() in load_destination:
                    destination_matches = True
                
                if destination_state and destination_state.lower() in load_destination:
                    destination_matches = True
                
                if not destination_matches:
                    continue
            
            # OPTIONAL: Pickup date filter
            if pickup_date:
                try:
                    load_pickup = load.get("pickup_datetime", "")
                    load_date = load_pickup.split("T")[0]
                    search_date = pickup_date.split("T")[0]
                    if load_date != search_date:
                        continue
                except (IndexError, ValueError):
                    pass
            
            # This load matches all criteria
            if include_booked:
                # Add booking status when including booked loads
                load_with_status = load.copy()
                load_with_status["is_booked"] = load.get("load_id") in self.booked_loads
                results.append(load_with_status)
            else:
                results.append(load)
        
        # Sort by rate (highest paying loads first)
        results.sort(key=lambda x: x.get("loadboard_rate", 0), reverse=True)
        
        logger.info(f"Search returned {len(results)} loads (showing top {max_results})")
        
        # Return top N results
        return results[:max_results]
    
    def generate_load_notes(self, load: Dict) -> str:
        """
        Generate brief, natural notes about the load
        
        Simple one-sentence summary with key facts
        """
        equipment = load["equipment_type"]
        origin = load["origin"]
        destination = load["destination"]
        miles = load["miles"]
        rate = load["loadboard_rate"]
        weight = load["weight"]
        commodity = load["commodity_type"]
        
        notes = (
            f"{equipment} load from {origin} to {destination}, "
            f"{miles} miles at ${rate:,.0f}, "
            f"hauling {weight:,} lbs of {commodity}"
        )
        
        return notes
    
    async def get_by_id(self, load_id: str) -> Optional[Dict]:
        """Get a specific load by ID"""
        for load in self.loads:
            if load.get("load_id") == load_id:
                return load
        return None
    
    async def get_all(self) -> List[Dict]:
        """Get all available loads"""
        return self.loads
    
    async def reload(self, data_path: str = "api/data/loads.json"):
        """Reload loads from file (useful for admin/demo)"""
        try:
            with open(data_path, 'r') as f:
                self.loads = json.load(f)
            logger.info(f"Reloaded {len(self.loads)} loads from {data_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to reload loads: {e}")
            return False
    
    def mark_as_booked(self, load_id: str) -> bool:
        """Mark a load as booked"""
        if load_id not in self.booked_loads:
            self.booked_loads.add(load_id)
            logger.info(f"Load {load_id} marked as booked")
            return True
        return False
    
    def is_load_available(self, load_id: str) -> bool:
        """Check if a load is available (not booked)"""
        return load_id not in self.booked_loads