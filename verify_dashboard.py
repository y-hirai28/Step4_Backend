
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base
from app.models import Child, EyeTest, DistanceCheck, ExerciseLog
from fastapi.testclient import TestClient
from app.main import app
from dotenv import load_dotenv

load_dotenv()

def verify_db_connection():
    # Check if DATABASE_URL is set, otherwise warning
    db_url = os.getenv("DATABASE_URL")
    print(f"Checking connection to: {db_url if db_url else 'SQLite (Default)'}")
    
    try:
        from app.database import engine
        connection = engine.connect()
        print("Successfully connected to the database!")
        connection.close()
        return True
    except Exception as e:
        print(f"Failed to connect: {e}")
        return False

def verify_api():
    # client = TestClient(app)
    
    try:
        # 1. Create a Child if not exists (using direct DB session for setup)
        # Using the same engine as app
        from app.database import SessionLocal
        db = SessionLocal()
        
        # Create Dummy Child
        child = Child(name="Test Child", parent_id=999)
        db.add(child)
        db.commit()
        db.refresh(child)
        print(f"Created Test Child: ID {child.child_id}")

        # 2. Add some dummy data linked to this child
        from datetime import date
        # Distance Check
        d_check = DistanceCheck(child_id=child.child_id, check_date=date(2025, 12, 1), avg_distance_cm=30)
        db.add(d_check)
        
        # Eye Test
        e_test = EyeTest(child_id=child.child_id, check_date=date(2025, 12, 1), left_eye="1.0", right_eye="1.0", test_distance_cm=500)
        db.add(e_test)
        
        db.commit()
        
        # 3. Call Dashboard API (Direct Function Call to bypass TestClient)
        print(f"Testing Dashboard API Logic for child {child.child_id}...")
        from app.routers.dashboard import get_child_dashboard
        
        data_response = get_child_dashboard(child_id=child.child_id, db=db)
        # Result is a Pydantic model or dict?
        # If response_model is used in decorator, the function returns the raw data (dict or ORM object), not the Pydantic model, validation happens at FastAPI layer.
        # But for DashboardChildResponse, we return a dict in the function.
        
        print("Dashboard API Logic Success!")
        print("Child Name:", data_response['child'].name)
        print("Recent Distance Checks:", len(data_response['recent_distance_checks']))
        print("Recent Eye Tests:", len(data_response['recent_eye_tests']))

        # Cleanup (Optional, but good for local SQLite)
        # db.delete(d_check)
        # db.delete(e_test)
        # db.delete(child)
        # db.commit()
        db.close()
        
    except Exception as e:
        print(f"Verify Failed: {e}")
        import traceback
        with open("verify_error.log", "w") as f:
            traceback.print_exc(file=f)

if __name__ == "__main__":
    if verify_db_connection():
        verify_api()
