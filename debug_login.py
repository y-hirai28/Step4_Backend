from app.database import SessionLocal
from app import crud, schemas, models
import app.utils as utils
import traceback

db = SessionLocal()
try:
    print("--- Starting Debug ---")
    # Try to find the demo user
    email = "demo@example.com"
    user = crud.get_parent_by_email(db, email)
    print(f"Found user: {user}")
    
    if user:
        # Try to create verification code (logic from auth.login)
        code = utils.generate_verification_code()
        session_id = utils.generate_session_id()
        print(f"Generated code: {code}, session: {session_id}")
        
        crud.store_verification_code(db, email, code, session_id)
        print("Stored verification code successfully")
    else:
        print("Demo user not found!")

except Exception as e:
    print("\n!!! ERROR OCCURRED !!!\n")
    traceback.print_exc()
finally:
    db.close()
