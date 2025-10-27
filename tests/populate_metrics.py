#!/usr/bin/env python3
"""
Populate the API with realistic test metrics data
"""
import requests
import json
import random
import time
from datetime import datetime, timedelta

# API Configuration
API_URL = "https://acme-logistics-api-3534.fly.dev"
API_KEY = "acme_dev_test_key_123"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

# Sample carrier data
carriers = [
    {"mc": "1234567", "name": "Direct Drive Transportation LLC"},
    {"mc": "2345678", "name": "Swift Logistics Inc"},
    {"mc": "3456789", "name": "Eagle Transport Services"},
    {"mc": "4567890", "name": "Prime Movers LLC"},
    {"mc": "5678901", "name": "Reliable Freight Systems"},
    {"mc": "6789012", "name": "Express Carriers Corp"},
    {"mc": "7890123", "name": "National Transport Co"},
    {"mc": "8901234", "name": "Midwest Trucking Inc"},
]

# Load IDs (we know these from loads.json)
load_ids = [
    "LOAD-001", "LOAD-002", "LOAD-003", "LOAD-004", "LOAD-005",
    "LOAD-006", "LOAD-007", "LOAD-008", "LOAD-009", "LOAD-010"
]

# Scenarios to create
scenarios = [
    # Successful bookings
    {"outcome": "booked", "sentiment": "positive", "rounds": 1, "duration": 180, "note": "Accepted first offer"},
    {"outcome": "booked", "sentiment": "positive", "rounds": 2, "duration": 240, "note": "Negotiated and agreed"},
    {"outcome": "booked", "sentiment": "neutral", "rounds": 3, "duration": 300, "note": "After some negotiation"},
    
    # Failed negotiations
    {"outcome": "no_agreement", "sentiment": "negative", "rounds": 3, "duration": 250, "note": "Price too low"},
    {"outcome": "no_agreement", "sentiment": "neutral", "rounds": 2, "duration": 200, "note": "Couldn't meet rate"},
    
    # Not interested
    {"outcome": "not_interested", "sentiment": "neutral", "rounds": 1, "duration": 90, "note": "Wrong equipment type"},
    {"outcome": "not_interested", "sentiment": "negative", "rounds": 1, "duration": 60, "note": "Route not suitable"},
    
    # Carrier not eligible
    {"outcome": "carrier_not_eligible", "sentiment": "neutral", "rounds": 0, "duration": 45, "note": "Failed FMCSA check"},
    
    # Already booked attempts
    {"outcome": "already_booked", "sentiment": "negative", "rounds": 1, "duration": 120, "note": "Load taken by another carrier"},
]

def log_call(load_id, carrier, scenario, offer_adjustment=0):
    """Log a single call to the API"""
    
    # Base rate varies by load
    base_rates = {
        "LOAD-001": 3500, "LOAD-002": 2800, "LOAD-003": 4200,
        "LOAD-004": 2200, "LOAD-005": 5500, "LOAD-006": 1800,
        "LOAD-007": 3200, "LOAD-008": 2600, "LOAD-009": 4800,
        "LOAD-010": 2900
    }
    
    base_rate = base_rates.get(load_id, 3000)
    
    # Adjust offer based on outcome
    if scenario["outcome"] == "booked":
        offer = base_rate + random.randint(-200, 100) + offer_adjustment
    elif scenario["outcome"] == "no_agreement":
        offer = base_rate - random.randint(300, 600) + offer_adjustment
    else:
        offer = base_rate + offer_adjustment
    
    payload = {
        "load_id": load_id,
        "mc_number": carrier["mc"],
        "carrier_name": carrier["name"],
        "carrier_offer": offer,
        "outcome": scenario["outcome"],
        "sentiment": scenario["sentiment"],
        "negotiation_rounds": scenario["rounds"],
        "call_duration": scenario["duration"] + random.randint(-30, 30),
        "notes": scenario["note"]
    }
    
    try:
        response = requests.post(
            f"{API_URL}/api/v1/offers/log",
            headers=headers,
            json=payload
        )
        
        if response.status_code == 201:
            print(f"✓ Logged: {carrier['name']} - {load_id} - {scenario['outcome']}")
        elif response.status_code == 409:
            print(f"✗ Conflict: {load_id} already booked")
            # Update the payload to reflect already booked
            payload["outcome"] = "already_booked"
            payload["notes"] = "Load was already booked by another carrier"
            response = requests.post(
                f"{API_URL}/api/v1/offers/log",
                headers=headers,
                json=payload
            )
            print(f"  → Logged as already_booked")
        else:
            print(f"✗ Error: {response.status_code} - {response.text}")
            
    except Exception as e:
        print(f"✗ Error logging call: {e}")
    
    # Small delay to simulate realistic timing
    time.sleep(0.5)

def main():
    print("🚀 Populating metrics with test data...")
    print(f"   API: {API_URL}")
    print()
    
    # First, let's book some loads
    print("📦 Booking some loads...")
    booked_loads = set()
    
    # Book 4 random loads
    for i in range(4):
        load_id = random.choice(load_ids)
        if load_id not in booked_loads:
            carrier = random.choice(carriers)
            scenario = {"outcome": "booked", "sentiment": "positive", "rounds": random.randint(1, 3), 
                       "duration": random.randint(180, 300), "note": "Successfully booked"}
            log_call(load_id, carrier, scenario)
            booked_loads.add(load_id)
    
    print(f"\n✓ Booked loads: {booked_loads}")
    
    # Now simulate various other calls
    print("\n📞 Simulating various carrier calls...")
    
    # Try to book already booked loads
    print("\n🔄 Attempting to book already booked loads...")
    for load_id in list(booked_loads)[:2]:
        carrier = random.choice(carriers)
        scenario = random.choice([s for s in scenarios if s["outcome"] == "booked"])
        log_call(load_id, carrier, scenario)
    
    # Failed negotiations
    print("\n❌ Simulating failed negotiations...")
    for _ in range(3):
        load_id = random.choice([l for l in load_ids if l not in booked_loads])
        carrier = random.choice(carriers)
        scenario = random.choice([s for s in scenarios if s["outcome"] == "no_agreement"])
        log_call(load_id, carrier, scenario)
    
    # Not interested carriers
    print("\n🚫 Simulating not interested carriers...")
    for _ in range(3):
        load_id = random.choice(load_ids)
        carrier = random.choice(carriers)
        scenario = random.choice([s for s in scenarios if s["outcome"] == "not_interested"])
        log_call(load_id, carrier, scenario)
    
    # Ineligible carriers
    print("\n⛔ Simulating ineligible carriers...")
    ineligible_carriers = [
        {"mc": "9999991", "name": "Suspended Transport LLC"},
        {"mc": "9999992", "name": "No Insurance Freight Co"},
    ]
    for carrier in ineligible_carriers:
        load_id = random.choice(load_ids)
        scenario = random.choice([s for s in scenarios if s["outcome"] == "carrier_not_eligible"])
        log_call(load_id, carrier, scenario)
    
    # More successful bookings
    print("\n✅ Adding more successful bookings...")
    available_loads = [l for l in load_ids if l not in booked_loads]
    for load_id in available_loads[:3]:
        carrier = random.choice(carriers)
        scenario = random.choice([s for s in scenarios if s["outcome"] == "booked"])
        log_call(load_id, carrier, scenario)
        booked_loads.add(load_id)
    
    # Mixed realistic traffic
    print("\n🎲 Simulating mixed realistic traffic...")
    for _ in range(10):
        load_id = random.choice(load_ids)
        carrier = random.choice(carriers)
        scenario = random.choice(scenarios)
        log_call(load_id, carrier, scenario)
    
    # Check final metrics
    print("\n📊 Fetching final metrics...")
    try:
        response = requests.get(f"{API_URL}/metrics", headers=headers)
        if response.status_code == 200:
            metrics = response.json()
            print(f"\n✓ Total calls logged: {metrics['total_calls']}")
            print(f"✓ Loads booked: {metrics['loads_booked']}")
            print(f"✓ Success rate: {metrics['booking_rate']:.1%}")
            print("\nOutcome breakdown:")
            for outcome, count in metrics['outcomes'].items():
                print(f"  - {outcome}: {count}")
        else:
            print(f"✗ Error fetching metrics: {response.status_code}")
    except Exception as e:
        print(f"✗ Error: {e}")

if __name__ == "__main__":
    main()