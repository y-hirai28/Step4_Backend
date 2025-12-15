from app.database import SessionLocal
from app import models
from sqlalchemy import text, cast, Date
from datetime import date

def check_data():
    db = SessionLocal()
    try:
        today = date(2025, 12, 15)
        print(f"Checking for date: {today}")
        results = db.query(models.EyeTest)\
            .filter(models.EyeTest.child_id == 1, models.EyeTest.check_date == today)\
            .order_by(models.EyeTest.created_at.desc())\
            .all()
        
        print(f"Total records for Child 1 on {today}: {len(results)}")
        for i, r in enumerate(results):
            print(f"Record {i}: ID={r.test_id}, Date={r.check_date}, CreatedAt={r.created_at}, L={r.left_eye}, R={r.right_eye}, Dist={r.test_distance_cm}")
            
    finally:
        db.close()

if __name__ == "__main__":
    check_data()
