#!/usr/bin/env python3
"""
Demo: Carrier Rejection Flow
Shows how the system handles carriers that fail verification
"""

import requests
import json
from datetime import datetime

API_BASE_URL = "http://localhost:8000"
API_KEY = "acme_dev_test_key_123"
headers = {"Authorization": f"Bearer {API_KEY}"}

def print_conversation(speaker, message):
    """Print conversation in a nice format"""
    if speaker == "CARRIER":
        print(f"\n🚚 CARRIER: {message}")
    elif speaker == "AI":
        print(f"\n🤖 AI AGENT: {message}")
    elif speaker == "SYSTEM":
        print(f"\n💻 SYSTEM: {message}")
    else:
        print(f"\n{speaker}: {message}")

def demo_carrier_rejection():
    print("\n" + "=" * 80)
    print(" DEMO: Carrier Verification Failure Flow ")
    print("=" * 80)
    print(f"\nStarted at: {datetime.now().strftime('%H:%M:%S')}")
    
    # Scenario setup
    invalid_mc = "1234567"  # 7-digit MC (invalid)
    
    print_conversation("AI", "Thank you for calling Acme Logistics. This is our automated booking system. May I have your MC number please?")
    
    print_conversation("CARRIER", f"Yes, it's {invalid_mc}")
    
    print_conversation("AI", f"Thank you. Let me verify MC number {invalid_mc} in our system...")
    
    # Step 1: Try to verify carrier
    print_conversation("SYSTEM", "Calling /api/v1/carriers/find endpoint...")
    
    response = requests.get(
        f"{API_BASE_URL}/api/v1/carriers/find",
        params={"mc": invalid_mc},
        headers=headers
    )
    
    print(f"\n   API Response: {response.status_code}")
    
    if response.status_code == 404:
        print("   ❌ Carrier not found in FMCSA database")
        
        print_conversation("AI", "I'm sorry, but I cannot find your MC number in the FMCSA database. "
                                 "This could mean the number is incorrect or your authority may not be active. "
                                 "Could you please verify your MC number?")
        
        print_conversation("CARRIER", "Let me check... Actually, I think we're still waiting for our MC number to be issued.")
        
        print_conversation("AI", "I understand. Unfortunately, we can only work with carriers who have active FMCSA authority. "
                                 "Please call us back once your MC number is active. Thank you for calling Acme Logistics.")
        
        # Step 2: Log the failed attempt
        print_conversation("SYSTEM", "Logging carrier rejection...")
        
        log_data = {
            "mc_number": invalid_mc,
            "carrier_name": "Unknown Carrier",
            "outcome": "carrier_not_eligible",
            "sentiment": "neutral",
            "call_duration": 45,
            "notes": "Carrier MC not found in FMCSA database - no active authority"
        }
        
        log_response = requests.post(
            f"{API_BASE_URL}/api/v1/offers/log",
            json=log_data,
            headers=headers
        )
        
        if log_response.status_code == 200:
            print("   ✅ Rejection logged successfully")
        
        # Step 3: Show metrics update
        print("\n" + "-" * 40)
        print("\n📊 METRICS UPDATE:")
        
        metrics_response = requests.get(f"{API_BASE_URL}/metrics", headers=headers)
        if metrics_response.status_code == 200:
            metrics = metrics_response.json()
            
            # Find our recent call
            recent_rejection = None
            for call in metrics.get("recent_calls", []):
                if call.get("mc_number") == invalid_mc:
                    recent_rejection = call
                    break
            
            if recent_rejection:
                print(f"\n✅ Call logged in metrics:")
                print(f"   - MC Number: {recent_rejection['mc_number']}")
                print(f"   - Outcome: {recent_rejection['outcome']}")
                print(f"   - Sentiment: {recent_rejection['sentiment']}")
                print(f"   - Notes: {recent_rejection['notes']}")
                print(f"   - Timestamp: {recent_rejection['timestamp']}")
            
            # Show outcome stats
            outcomes = metrics.get("calls_by_outcome", {})
            not_eligible = outcomes.get("carrier_not_eligible", 0)
            print(f"\n📈 Total 'carrier_not_eligible' calls: {not_eligible}")
    
    print("\n" + "=" * 80)
    print(" END OF DEMO ")
    print("=" * 80)

def demo_other_rejection_scenarios():
    print("\n\n📝 OTHER REJECTION SCENARIOS WE HANDLE:\n")
    
    scenarios = [
        {
            "outcome": "not_interested",
            "scenario": "Carrier declines after hearing the route/rate",
            "example": "CARRIER: 'That rate is too low for us, we'll pass.'"
        },
        {
            "outcome": "no_agreement", 
            "scenario": "Cannot agree on price after negotiation",
            "example": "After 3 rounds of negotiation, carrier still wants $4000 but our max is $3675"
        },
        {
            "outcome": "already_booked",
            "scenario": "Load was booked by another carrier",
            "example": "Carrier tries to book LOAD-001 but it's already taken"
        },
        {
            "outcome": "carrier_not_eligible",
            "scenario": "Failed verification (our current demo)",
            "example": "Invalid MC, no insurance, inactive authority"
        }
    ]
    
    for s in scenarios:
        print(f"\n🔸 Outcome: '{s['outcome']}'")
        print(f"   Scenario: {s['scenario']}")
        print(f"   Example: {s['example']}")

if __name__ == "__main__":
    demo_carrier_rejection()
    demo_other_rejection_scenarios()
    
    print("\n💡 Check the dashboard at http://localhost:8001 to see:")
    print("   - The rejected call in 'Recent Calls' tab")
    print("   - Updated metrics in 'Analytics' tab")
    print("   - Outcome distribution chart includes 'carrier_not_eligible'")
