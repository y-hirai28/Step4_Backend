
import requests
import json
from datetime import date
import sys

# API Base URL
BASE_URL = "http://localhost:8000/api/v1"
LEGACY_BASE_URL = "http://localhost:8000/api"

def debug_dashboard():
    print("--- Debugging Dashboard API ---")
    
    # 1. Simulate saving a distance check (as Frontend does)
    print("\n1. Saving Distance Check Data via POST /api/distance-check...")
    distance_payload = {
        "child_id": 1,
        "distance_cm": 25,
        "alert_flag": True
    }
    try:
        # Note: Frontend uses http://localhost:8000/api/distance-check (no v1)
        res = requests.post(f"{LEGACY_BASE_URL}/distance-check", json=distance_payload)
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            print("Save Response:", res.json())
        else:
            print("Save Failed:", res.text)
            return
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # 2. Fetch Parent Dashboard (to get children)
    print("\n2. Fetching Parent Dashboard (GET /api/v1/dashboard/parent/1)...")
    try:
        res = requests.get(f"{BASE_URL}/dashboard/parent/1")
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            # print(json.dumps(data, indent=2, ensure_ascii=False))
            children = data.get("children_data", [])
            print(f"Found {len(children)} children.")
            if len(children) > 0:
                print("First Child ID:", children[0]["child"]["child_id"])
        else:
            print("Fetch Parent Failed:", res.text)
            return
    except Exception as e:
        print(f"Connection Failed: {e}")
        return

    # 3. Fetch Child Dashboard (specific child)
    print("\n3. Fetching Child Dashboard (GET /api/v1/dashboard/child/1)...")
    try:
        res = requests.get(f"{BASE_URL}/dashboard/child/1")
        print(f"Status: {res.status_code}")
        if res.status_code == 200:
            data = res.json()
            print("Child Dashboard Data Keys:", data.keys())
            
            # Check recent_distance_checks
            checks = data.get("recent_distance_checks", [])
            print(f"Recent Distance Checks Count: {len(checks)}")
            if len(checks) > 0:
                print("Latest Check:", checks[0])
                if "avg_distance_cm" in checks[0]:
                    print("SUCCESS: 'avg_distance_cm' found in response.")
                else:
                    print("FAILURE: 'avg_distance_cm' MISSING in response.")
            else:
                print("WARNING: No distance checks found (despite just saving one).")
        else:
            print("Fetch Child Failed:", res.text)
    except Exception as e:
        print(f"Connection Failed: {e}")

if __name__ == "__main__":
    debug_dashboard()
