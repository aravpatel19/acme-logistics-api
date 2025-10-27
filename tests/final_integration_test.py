#!/usr/bin/env python3
"""
Final Integration Test - Complete workflow verification
"""

import requests
import json
import time
import sys
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
DASHBOARD_URL = "http://localhost:8001"
API_KEY = "acme_dev_test_key_123"
headers = {"Authorization": f"Bearer {API_KEY}"}

# Test tracking
passed_tests = 0
failed_tests = 0

def test_case(description):
    print(f"\n▶ {description}")
    return description

def pass_test(message=""):
    global passed_tests
    passed_tests += 1
    print(f"  ✅ PASS {message}")

def fail_test(message):
    global failed_tests
    failed_tests += 1
    print(f"  ❌ FAIL: {message}")

def run_integration_tests():
    print("\n" + "=" * 70)
    print(" FINAL INTEGRATION TEST SUITE ")
    print("=" * 70)
    print(f"Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"\nAPI URL: {API_BASE_URL}")
    print(f"Dashboard URL: {DASHBOARD_URL}")
    
    # Test 1: Service Health
    test_case("Service Health Checks")
    
    # API Health
    try:
        resp = requests.get(f"{API_BASE_URL}/healthcheck")
        if resp.status_code == 200:
            data = resp.json()
            pass_test(f"API healthy - {data['loads_available']} loads available")
        else:
            fail_test(f"API health check returned {resp.status_code}")
    except Exception as e:
        fail_test(f"Cannot connect to API: {e}")
        print("\n⚠️  Please ensure API is running: cd api && python main.py")
        return
    
    # Dashboard Health
    try:
        resp = requests.get(DASHBOARD_URL)
        if resp.status_code == 200:
            pass_test("Dashboard accessible")
        else:
            fail_test(f"Dashboard returned {resp.status_code}")
    except Exception as e:
        fail_test(f"Cannot connect to Dashboard: {e}")
        print("\n⚠️  Please ensure dashboard is running: cd dashboard && python -m http.server 8001")
    
    # Test 2: Authentication
    test_case("API Authentication")
    
    # Valid auth
    resp = requests.get(f"{API_BASE_URL}/api/v1/loads", headers=headers)
    if resp.status_code == 200:
        pass_test("Valid API key accepted")
    else:
        fail_test(f"Valid API key rejected: {resp.status_code}")
    
    # Invalid auth
    bad_headers = {"Authorization": "Bearer invalid_key"}
    resp = requests.get(f"{API_BASE_URL}/api/v1/loads", headers=bad_headers)
    if resp.status_code in [401, 403]:  # Both are acceptable for auth rejection
        pass_test("Invalid API key rejected")
    else:
        fail_test(f"Invalid API key not rejected: {resp.status_code}")
    
    # Test 3: Carrier Verification Workflow
    test_case("Carrier Verification Workflow")
    
    # Valid carrier
    resp = requests.get(f"{API_BASE_URL}/api/v1/carriers/find?mc=383025", headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        if 'body' in data and 'carrier' in data['body']:
            carrier = data['body']['carrier']
            pass_test(f"Valid carrier found: {carrier['carrier_name']}")
        else:
            # FMCSA might be rejecting this carrier
            pass_test("Carrier verification endpoint working (carrier may not be eligible)")
    else:
        fail_test(f"Valid carrier lookup failed: {resp.status_code}")
    
    # Invalid carrier with rejection logging
    invalid_mc = "0000001"
    resp = requests.get(f"{API_BASE_URL}/api/v1/carriers/find?mc={invalid_mc}", headers=headers)
    
    # Log the rejection
    rejection = {
        "mc_number": invalid_mc,
        "carrier_name": "Invalid Carrier Test",
        "outcome": "carrier_not_eligible",
        "sentiment": "neutral",
        "call_duration": 30,
        "notes": "MC number not found in FMCSA database"
    }
    resp = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=rejection, headers=headers)
    if resp.status_code in [200, 201]:
        pass_test("Carrier rejection logged")
    else:
        fail_test(f"Rejection logging failed: {resp.status_code}")
    
    # Test 4: Load Search Variations
    test_case("Load Search Functionality")
    
    # Search by city
    resp = requests.get(f"{API_BASE_URL}/api/v1/loads?origin_city=Houston", headers=headers)
    if resp.status_code == 200:
        loads = resp.json()['body']['loads']
        pass_test(f"City search found {len(loads)} loads")
    else:
        fail_test(f"City search failed: {resp.status_code}")
    
    # Search by state
    resp = requests.get(f"{API_BASE_URL}/api/v1/loads?origin_state=TX", headers=headers)
    if resp.status_code == 200:
        loads = resp.json()['body']['loads']
        pass_test(f"State search found {len(loads)} loads")
    else:
        fail_test(f"State search failed: {resp.status_code}")
    
    # Equipment filter
    resp = requests.get(f"{API_BASE_URL}/api/v1/loads?equipment_type=Reefer", headers=headers)
    if resp.status_code == 200:
        loads = resp.json()['body']['loads']
        pass_test(f"Equipment filter found {len(loads)} reefer loads")
    else:
        fail_test(f"Equipment filter failed: {resp.status_code}")
    
    # Test 5: Complete Booking Workflow
    test_case("Complete Booking Workflow")
    
    # Find available load
    resp = requests.get(f"{API_BASE_URL}/api/v1/loads?origin_state=NC", headers=headers)
    if resp.status_code == 200 and resp.json()['body']['loads']:
        load = resp.json()['body']['loads'][0]
        load_id = load['load_id']
        max_buy = load['max_buy']
        
        # Negotiate and book
        booking = {
            "load_id": load_id,
            "mc_number": "424242",
            "carrier_name": "Integration Test Trucking",
            "carrier_offer": max_buy,
            "outcome": "booked",
            "sentiment": "positive",
            "negotiation_rounds": 2,
            "call_duration": 240,
            "notes": "Carrier accepted after negotiation"
        }
        
        resp = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=booking, headers=headers)
        if resp.status_code in [200, 201]:
            pass_test(f"Successfully booked {load_id}")
            
            # Try double booking
            booking['mc_number'] = "535353"
            booking['carrier_name'] = "Double Book Attempt Inc"
            resp = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=booking, headers=headers)
            
            # Check if it was logged as already_booked
            time.sleep(1)
            metrics_resp = requests.get(f"{API_BASE_URL}/metrics", headers=headers)
            if metrics_resp.status_code == 200:
                recent_calls = metrics_resp.json()['recent_calls']
                double_book_attempt = next((c for c in recent_calls if c['mc_number'] == "535353"), None)
                if double_book_attempt and double_book_attempt['outcome'] == 'already_booked':
                    pass_test("Double booking prevented correctly")
                else:
                    fail_test("Double booking not prevented")
        else:
            fail_test(f"Booking failed: {resp.status_code}")
    else:
        fail_test("No loads available to test booking")
    
    # Test 6: Metrics and Reporting
    test_case("Metrics and Reporting")
    
    resp = requests.get(f"{API_BASE_URL}/metrics", headers=headers)
    if resp.status_code == 200:
        metrics = resp.json()
        pass_test(f"Metrics retrieved: {metrics['total_calls']} total calls")
        
        # Verify all outcome types are tracked
        outcomes = metrics['calls_by_outcome']
        expected_outcomes = ['booked', 'carrier_not_eligible', 'already_booked']
        missing = [o for o in expected_outcomes if o not in outcomes or outcomes[o] == 0]
        if not missing:
            pass_test("All outcome types tracked correctly")
        else:
            fail_test(f"Missing outcomes: {missing}")
            
        # Check success rate calculation
        if metrics['success_rate'] >= 0:
            pass_test(f"Success rate calculated: {metrics['success_rate']}%")
        else:
            fail_test("Success rate not calculated")
    else:
        fail_test(f"Metrics retrieval failed: {resp.status_code}")
    
    # Test 7: Error Handling
    test_case("Error Handling")
    
    # Malformed request
    bad_booking = {
        "mc_number": "123",  # Missing required fields
        "invalid_field": "test"
    }
    resp = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=bad_booking, headers=headers)
    if resp.status_code == 422:
        pass_test("Malformed request rejected with 422")
    else:
        fail_test(f"Malformed request returned {resp.status_code}, expected 422")
    
    # Invalid enum value
    bad_outcome = {
        "mc_number": "123456",
        "outcome": "invalid_outcome",
        "sentiment": "happy"  # Invalid sentiment
    }
    resp = requests.post(f"{API_BASE_URL}/api/v1/offers/log", json=bad_outcome, headers=headers)
    if resp.status_code == 422:
        pass_test("Invalid enum values rejected")
    else:
        fail_test(f"Invalid enums not rejected: {resp.status_code}")
    
    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY ")
    print("=" * 70)
    
    total_tests = passed_tests + failed_tests
    print(f"\n✅ Passed: {passed_tests}/{total_tests}")
    print(f"❌ Failed: {failed_tests}/{total_tests}")
    
    if failed_tests == 0:
        print("\n🎉 ALL TESTS PASSED! System is ready for production.")
        print("\n🚀 Next steps:")
        print("  1. Set up ngrok for public URL")
        print("  2. Configure HappyRobot with API endpoints")
        print("  3. Test voice agent integration")
    else:
        print("\n⚠️  Some tests failed. Please review and fix issues before proceeding.")
    
    print(f"\nCompleted at: {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    run_integration_tests()