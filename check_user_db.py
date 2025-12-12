
import requests

BASE_URL = "http://localhost:8000/api/v1"

def check_health():
    try:
        res = requests.get("http://localhost:8000/")
        print(f"Root Health Check: {res.status_code} ({res.json()})")
    except Exception as e:
        print(f"Root Health Check Failed: {e}")

def login_demo():
    print("Attempting login as demo@example.com...")
    payload = {
        "username": "demo@example.com", # OAuth2 usually uses form-data 'username', but let's check schema
        "password": "password" # Assuming a default password if seeded?
    }
    # Trying typical endpoint
    try:
        # Check standard auth endpoint. Often /token or /auth/login
        # Checking main.py: app.include_router(auth.router, prefix="/api/v1", tags=["auth"])
        # We need to see auth router paths. Assuming /auth/login based on common practices.
        # But for now, let's try to infer from previous files or errors.
        pass
    except:
        pass

# I will instead create a script that just connects to DB directly to check for users, 
# as I don't know the exact auth endpoint path simply from memory without reading auth.py.
# Actually, I can use the existing debug_dashboard_api.py logic to just query the API.
# But wait, dashboard API worked (200 OK for save).
# "Network Error" usually means CORS or Connection Refused.

# Let's write a script to check if the user exists via DB directly.
from app.database import SessionLocal
from app import models

def check_user():
    db = SessionLocal()
    try:
        user = db.query(models.Parent).filter(models.Parent.email == "demo@example.com").first()
        if user:
            print(f"User found: {user.email}, ID: {user.parent_id}")
        else:
            print("User 'demo@example.com' NOT FOUND in database.")
            
        # Also check Child
        child = db.query(models.Child).filter(models.Child.child_id == 1).first()
        if child:
             print(f"Child 1 found: {child.name}")
        else:
             print("Child 1 NOT FOUND. (This explains why dashboard might be weird but Save worked if validation skipped?)")
             
    except Exception as e:
        print(f"DB Error: {e}")
    finally:
        db.close()

if __name__ == "__main__":
    check_user()
