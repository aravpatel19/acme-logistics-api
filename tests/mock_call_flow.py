#!/usr/bin/env python3
"""
Mock Carrier Call Flow - Simulates a complete carrier call through the API
This demonstrates how HappyRobot would interact with our API
"""

import requests
import json
import time
from datetime import datetime

# API Configuration
API_BASE_URL = "http://localhost:8000"
API_KEY = "acme_dev_test_key_123"
headers = {"Authorization": f"Bearer {API_KEY}"}

def print_step(step, description):
    print(f"\n{'='*60}")
    print(f"STEP {step}: {description}")
    print(f"{'='*60}")

def print_response(response):
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    else:
        print(f"Error: {response.text}")

def main():
    print("\n🚚 ACME LOGISTICS - MOCK CARRIER CALL SIMULATION 🚚")
    print("Simulating a carrier calling in to book a load...")
    
    # Step 1: Carrier calls in with MC number
    print_step(1, "Carrier provides MC number - Verify carrier eligibility")
    mc_number = "1234567"  # Mock MC number
    
    verify_url = f"{API_BASE_URL}/api/v1/carriers/find?mc={mc_number}"
    print(f"Calling: GET {verify_url}")
    
    response = requests.get(verify_url, headers=headers)
    print_response(response)
    
    if response.status_code != 200:
        print("❌ Carrier not eligible - ending call")
        return
    
    carrier_data = response.json()
    print(f"✅ Carrier verified: {carrier_data.get('carrier_name', 'Unknown Carrier')}")
    
    # Step 2: Get carrier's location and equipment
    print_step(2, "Carrier provides location and equipment type")
    origin_city = "Los Angeles"
    equipment_type = "Dry Van"
    
    print(f"Carrier location: {origin_city}")
    print(f"Equipment type: {equipment_type}")
    
    # Step 3: Search for available loads
    print_step(3, "Search for available loads matching carrier criteria")
    
    search_url = f"{API_BASE_URL}/api/v1/loads?origin_city={origin_city}&equipment_type={equipment_type}"
    print(f"Calling: GET {search_url}")
    
    response = requests.get(search_url, headers=headers)
    
    if response.status_code != 200:
        print("❌ Error searching loads")
        return
    
    loads_data = response.json()
    loads = loads_data.get('body', {}).get('loads', [])
    
    print(f"\n✅ Found {len(loads)} matching loads")
    
    if loads:
        # Present the first load to carrier
        load = loads[0]
        print(f"\n📦 Presenting load to carrier:")
        print(f"  Load ID: {load['load_id']}")
        print(f"  Route: {load['origin']} → {load['destination']}")
        print(f"  Miles: {load['miles']}")
        print(f"  Posted Rate: ${load['posted_carrier_rate']:,}")
        print(f"  Max Buy: ${load['max_buy']:,}")
        print(f"  Equipment: {load['equipment_type']}")
        print(f"  Notes: {load['notes']}")
    else:
        print("No matching loads found")
        return
    
    # Step 4: Carrier negotiation
    print_step(4, "Carrier negotiates rate")
    
    print(f"AI: The posted rate is ${load['posted_carrier_rate']:,}")
    print(f"Carrier: I need $3,600 to run this load")
    print(f"AI: I can offer you $3,500 (within max_buy of ${load['max_buy']:,})")
    print(f"Carrier: Agreed!")
    
    agreed_rate = 3500
    
    # Step 5: Log the successful booking
    print_step(5, "Log the booking and transfer to sales rep")
    
    log_url = f"{API_BASE_URL}/api/v1/offers/log"
    log_data = {
        "load_id": load['load_id'],
        "mc_number": mc_number,
        "carrier_name": carrier_data.get('carrier_name', 'Test Carrier LLC'),
        "carrier_offer": agreed_rate,  # The final agreed rate
        "outcome": "booked",
        "sentiment": "positive",
        "negotiation_rounds": 2,
        "call_duration": 180,  # 3 minutes
        "notes": "Carrier agreed to $3,500 after initial ask of $3,600"
    }
    
    print(f"\nCalling: POST {log_url}")
    print(f"Payload: {json.dumps(log_data, indent=2)}")
    
    response = requests.post(log_url, json=log_data, headers=headers)
    print_response(response)
    
    if response.status_code == 200:
        print("\n✅ Booking logged successfully!")
        print("🔄 Transferring to sales rep to finalize...")
        print(f"\n💰 Load {load['load_id']} is now BOOKED at ${agreed_rate:,}")
    
    # Step 6: Check dashboard metrics
    print_step(6, "Verify booking appears in dashboard metrics")
    
    time.sleep(1)  # Small delay
    
    metrics_url = f"{API_BASE_URL}/metrics"
    print(f"Calling: GET {metrics_url}")
    
    response = requests.get(metrics_url, headers=headers)
    
    if response.status_code == 200:
        metrics = response.json()
        print(f"\n📊 Dashboard Metrics Updated:")
        print(f"  Total Calls: {metrics.get('total_calls', 0)}")
        print(f"  Success Rate: {metrics.get('success_rate', 0)}%")
        print(f"  Recent Calls: {len(metrics.get('recent_calls', []))}")
        
        # Check if our call appears
        recent_calls = metrics.get('recent_calls', [])
        our_call = next((c for c in recent_calls if c.get('load_id') == load['load_id']), None)
        
        if our_call:
            print(f"\n✅ Our booking appears in recent calls!")
            print(f"  Load: {our_call.get('load_id')}")
            print(f"  Outcome: {our_call.get('outcome')}")
            print(f"  Agreed Rate: ${our_call.get('agreed_rate', 0):,}")
            print(f"\n🎯 The dashboard will now show Load {load['load_id']} as BOOKED!")

if __name__ == "__main__":
    main()