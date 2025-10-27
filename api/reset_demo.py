#!/usr/bin/env python3
"""
Reset demo data for clean demo environment
"""

import json
import os
import shutil
from datetime import datetime

def reset_demo():
    """Reset all demo data to clean state"""
    
    # 1. Clear metrics data
    metrics_file = "data/metrics.json"
    if os.path.exists(metrics_file):
        # Backup existing data
        backup_name = f"data/metrics_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        shutil.copy2(metrics_file, backup_name)
        print(f"✅ Backed up existing metrics to {backup_name}")
    
    # Write empty metrics
    with open(metrics_file, 'w') as f:
        json.dump([], f, indent=2)
    print("✅ Reset metrics.json")
    
    # 2. Ensure all loads are available (no booking status in JSON)
    # Note: Booking status is tracked in memory, so it resets automatically on restart
    
    print("\n🎯 Demo environment reset complete!")
    print("   - All metrics cleared")
    print("   - Booking status will reset on server restart (in-memory)")
    print("\n💡 To start fresh demo:")
    print("   1. Run this script: python reset_demo.py")
    print("   2. Start the API: python main.py")
    print("   3. All loads will be available for booking")

if __name__ == "__main__":
    reset_demo()