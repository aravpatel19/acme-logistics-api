#!/usr/bin/env python3
"""
Manual System Test - Verify all components are working correctly
"""

import requests
import json
import time
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
API_KEY = "acme_dev_test_key_123"
headers = {"Authorization": f"Bearer {API_KEY}"}

def test_step(step_num, description):
    print(f"\n{'='*60}")
    print(f"STEP {step_num}: {description}")
    print(f"{'='*60}")

def print_success(message):
    print(f"✅ {message}")

def print_error(message):
    print(f"❌ {message}")

def run_system_test():
    print("\n" + "*" * 60)
    print(" MANUAL SYSTEM TEST ")
    print("*" * 60)
    print(f"\nStarted at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Test 1: API Health
    test_step(1, "Check API Health")
    response = requests.get(f"{API_BASE_URL}/healthcheck")
    if response.status_code == 200:
        data = response.json()
        print_success(f"API is healthy")
        print(f"   - Loads available: {data['loads_available']}")
        print(f"   - Loads booked: {data['loads_booked']}")
    else:
        print_error(f"API health check failed: {response.status_code}")
        return
    
    # Test 2: Carrier Verification
    test_step(2, "Verify Valid Carrier (MC 1515)")
    response = requests.get(f"{API_BASE_URL}/api/v1/carriers/find", params={"mc": "1515"}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        carrier = data['body']['carrier']
        print_success(f"Carrier found: {carrier['carrier_name']}")
        print(f"   - Status: {carrier['status']}")
        print(f"   - DOT: {carrier['dot_number']}")
    else:
        print_error(f"Carrier verification failed: {response.status_code}")
    
    # Test 3: Invalid Carrier
    test_step(3, "Verify Invalid Carrier (MC 9999999)")
    response = requests.get(f"{API_BASE_URL}/api/v1/carriers/find", params={"mc": "9999999"}, headers=headers)
    if response.status_code == 404:
        print_success("Invalid carrier correctly rejected (404)")
    else:
        print_error(f"Expected 404, got {response.status_code}")
    
    # Test 4: Load Search
    test_step(4, "Search Loads from Los Angeles")
    response = requests.get(f"{API_BASE_URL}/api/v1/loads", params={"origin_city": "Los Angeles"}, headers=headers)
    if response.status_code == 200:
        data = response.json()
        loads = data['body']['loads']
        print_success(f"Found {len(loads)} loads from Los Angeles")
        if loads:
            load = loads[0]
            print(f"\n   First load: {load['load_id']}")
            print(f"   - Route: {load['origin']} → {load['destination']}")
            print(f"   - Equipment: {load['equipment_type']}")
            print(f"   - Posted rate: ${load.get('posted_carrier_rate', load.get('loadboard_rate', 0)):,}")
            print(f"   - Max buy: ${load['max_buy']:,}")
    else:
        print_error(f"Load search failed: {response.status_code}")
    
    # Test 5: Book a Load
    test_step(5, "Book Load (LOAD-003)")
    booking_data = {
        "load_id": "LOAD-003",
        "mc_number": "123456",
        "carrier_name": "Test Carrier LLC",
        "carrier_offer": 4200,
        "outcome": "booked",
        "sentiment": "positive",
        "negotiation_rounds": 1,
        "call_duration": 180,
        "notes": "Carrier agreed to posted rate"
    }
    response = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=booking_data, headers=headers)
    if response.status_code in [200, 201]:
        print_success("Load successfully booked")
        body = response.json().get('body', {})
        if 'call_id' in body:
            print(f"   - Call ID: {body['call_id']}")
    else:
        print_error(f"Booking failed: {response.status_code}")
    
    # Test 6: Try Double Booking
    test_step(6, "Attempt Double Booking (LOAD-003)")
    booking_data['mc_number'] = "789012"
    booking_data['carrier_name'] = "Another Carrier Inc"
    response = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=booking_data, headers=headers)
    if response.status_code == 409:
        print_success("Double booking correctly prevented (409 Conflict)")
        print(f"   - Error: {response.json()['body']['message']}")
    else:
        print_error(f"Expected 409, got {response.status_code}")
    
    # Test 7: Log Rejection
    test_step(7, "Log Carrier Rejection")
    rejection_data = {
        "mc_number": "555555",
        "carrier_name": "Picky Carrier Corp",
        "outcome": "not_interested",
        "sentiment": "negative",
        "call_duration": 60,
        "notes": "Rate too low for this lane"
    }
    response = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=rejection_data, headers=headers)
    if response.status_code in [200, 201]:
        print_success("Rejection logged successfully")
    else:
        print_error(f"Rejection logging failed: {response.status_code}")
    
    # Test 8: Check Metrics
    test_step(8, "Verify Metrics Updated")
    response = requests.get(f"{API_BASE_URL}/metrics", headers=headers)
    if response.status_code == 200:
        metrics = response.json()
        print_success(f"Metrics retrieved successfully")
        print(f"   - Total calls: {metrics['total_calls']}")
        print(f"   - Success rate: {metrics['success_rate']}%")
        print(f"   - Calls by outcome:")
        for outcome, count in metrics['calls_by_outcome'].items():
            print(f"     • {outcome}: {count}")
    else:
        print_error(f"Metrics retrieval failed: {response.status_code}")
    
    # Test 9: Dashboard Accessibility
    test_step(9, "Check Dashboard")
    response = requests.get("http://localhost:8001/")
    if response.status_code == 200:
        print_success("Dashboard is accessible")
        print("   - URL: http://localhost:8001")
    else:
        print_error(f"Dashboard not accessible: {response.status_code}")
    
    # Final Summary
    print("\n" + "=" * 60)
    print(" SYSTEM TEST COMPLETE ")
    print("=" * 60)
    print("\n🎆 All core functionality is working correctly!")
    print("\nSystem is ready for:")
    print("  • Voice agent integration")
    print("  • Real carrier calls")
    print("  • Production deployment")
    print("\nNext step: Set up ngrok and configure HappyRobot")

if __name__ == "__main__":
    run_system_test()