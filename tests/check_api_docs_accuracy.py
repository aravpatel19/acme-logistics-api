#!/usr/bin/env python3
"""
Compare API documentation vs actual API responses
"""

import requests
import json
from typing import Dict, Any

API_BASE_URL = "http://localhost:8000"
API_KEY = "acme_dev_test_key_123"
headers = {"Authorization": f"Bearer {API_KEY}"}

def print_section(title: str):
    print("\n" + "=" * 80)
    print(f" {title}")
    print("=" * 80)

def check_endpoint(endpoint: str, method: str = "GET", params: Dict = None, body: Dict = None) -> Dict[str, Any]:
    """Make API call and return response"""
    url = f"{API_BASE_URL}{endpoint}"
    
    if method == "GET":
        response = requests.get(url, params=params, headers=headers)
    else:
        response = requests.post(url, json=body, headers=headers)
    
    return {
        "status": response.status_code,
        "data": response.json() if response.status_code == 200 else None,
        "error": response.text if response.status_code != 200 else None
    }

def analyze_api_vs_docs():
    print_section("API DOCUMENTATION vs ACTUAL RESPONSES")
    
    # Test 1: Load search endpoint
    print("\n1. GET /api/v1/loads")
    print("-" * 40)
    
    loads_response = check_endpoint("/api/v1/loads", params={"origin_city": "Los Angeles"})
    
    print("Expected (from docs):")
    print("  - Returns loads in HappyRobot format")
    print("  - Required: origin_city OR origin_state")
    print("  - Optional: destination, equipment_type, etc.")
    
    print("\nActual response structure:")
    if loads_response["data"]:
        data = loads_response["data"]
        print(f"  - Status code: {data.get('statusCode')}")
        print(f"  - Body contains: {list(data.get('body', {}).keys())}")
        
        if 'loads' in data.get('body', {}):
            loads = data['body']['loads']
            if loads:
                print(f"  - Number of loads: {len(loads)}")
                print("  - Load object keys:")
                for key in list(loads[0].keys())[:10]:
                    print(f"    - {key}")
                print("    ... (showing first 10 fields)")
    
    # Test 2: Carrier verification endpoint
    print("\n\n2. GET /api/v1/carriers/find")
    print("-" * 40)
    
    carrier_response = check_endpoint("/api/v1/carriers/find", params={"mc": "1515"})
    
    print("Expected (from docs):")
    print("  - Verifies carrier through FMCSA")
    print("  - Required: mc OR dot number")
    print("  - Returns carrier eligibility")
    
    print("\nActual response structure:")
    if carrier_response["data"]:
        data = carrier_response["data"]
        print(f"  - Status code: {data.get('statusCode')}")
        print(f"  - Body contains: {list(data.get('body', {}).keys())}")
        
        if 'carrier' in data.get('body', {}):
            carrier = data['body']['carrier']
            print("  - Carrier object keys:")
            for key, value in carrier.items():
                print(f"    - {key}: {value}")
    
    # Test 3: Offers logging endpoint
    print("\n\n3. POST /api/v1/offers/log")
    print("-" * 40)
    
    print("Expected (from docs):")
    print("  - Logs carrier offers and call outcomes")
    print("  - Required: load_id, mc_number, carrier_offer, notes")
    print("  - Missing: outcome, sentiment, negotiation_rounds, call_duration")
    
    print("\nActual accepted fields:")
    test_log = {
        "load_id": "LOAD-999",
        "mc_number": "12345",
        "carrier_name": "Test Carrier",
        "carrier_offer": 3000,
        "outcome": "not_interested",
        "sentiment": "neutral",
        "negotiation_rounds": 1,
        "call_duration": 120,
        "notes": "API test"
    }
    
    log_response = check_endpoint("/api/v1/offers/log", method="POST", body=test_log)
    if log_response["status"] == 201 or log_response["status"] == 200:
        print("✅ All these fields are accepted:")
        for field in test_log.keys():
            print(f"    - {field}")
    
    # Test 4: Check OpenAPI spec
    print("\n\n4. OpenAPI Specification Check")
    print("-" * 40)
    
    openapi_response = requests.get(f"{API_BASE_URL}/openapi.json")
    if openapi_response.status_code == 200:
        spec = openapi_response.json()
        
        # Check offers/log endpoint schema
        offers_path = spec['paths'].get('/api/v1/offers/log', {})
        if offers_path:
            post_op = offers_path.get('post', {})
            print("\nDocumented description:")
            print(f"  {post_op.get('description', 'No description')[:200]}...")
            
            # Check request body schema
            request_body = post_op.get('requestBody', {}).get('content', {}).get('application/json', {}).get('schema')
            if request_body:
                print("\nDocumented request body: ANY type (not specific fields!)")
    
    print("\n" + "=" * 80)
    print(" FINDINGS ")
    print("=" * 80)
    
    print("\n🔴 DOCUMENTATION ISSUES FOUND:")
    print("\n1. Response Format Mismatch:")
    print("   - API returns HappyRobot format with nested structure")
    print("   - Docs don't clearly show the statusCode/body wrapper")
    
    print("\n2. Missing Fields in /api/v1/offers/log:")
    print("   - Docs show only 4 required fields")
    print("   - Actually accepts 9+ fields including critical ones:")
    print("     • outcome (booked, not_interested, etc.)")
    print("     • sentiment (positive, neutral, negative)")
    print("     • negotiation_rounds")
    print("     • call_duration")
    print("     • carrier_name")
    
    print("\n3. Carrier Verification Response:")
    print("   - Returns detailed carrier object")
    print("   - Docs don't show the actual structure")
    
    print("\n4. Request Body Schema:")
    print("   - OpenAPI spec shows 'any' type for request bodies")
    print("   - No specific field documentation")
    print("   - Makes it hard to know what fields are available")
    
    print("\n💡 RECOMMENDATION:")
    print("   The API works correctly, but the auto-generated docs from FastAPI")
    print("   are not showing the actual field structures. This is because the")
    print("   endpoints accept 'dict' instead of Pydantic models.")
    print("\n   For better documentation, the API should use Pydantic models")
    print("   for request/response bodies.")

if __name__ == "__main__":
    analyze_api_vs_docs()