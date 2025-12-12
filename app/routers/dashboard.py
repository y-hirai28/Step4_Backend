from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/dashboard",
    tags=["dashboard"]
)

@router.get("/child/{child_id}")
def get_child_dashboard(child_id: int, db: Session = Depends(get_db)):
    import traceback
    try:
        child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
        if not child:
            raise HTTPException(status_code=404, detail="Child not found")

        # Fetch recent data (limit 5 for summary)
        recent_exercises = db.query(models.ExerciseLog)\
            .filter(models.ExerciseLog.child_id == child_id)\
            .order_by(models.ExerciseLog.exercise_date.desc())\
            .limit(5).all()

        recent_distance_checks = db.query(models.DistanceCheck)\
            .filter(models.DistanceCheck.child_id == child_id)\
            .order_by(models.DistanceCheck.check_date.desc())\
            .limit(5).all()

        recent_eye_tests = db.query(models.EyeTest)\
            .filter(models.EyeTest.child_id == child_id)\
            .order_by(models.EyeTest.check_date.desc())\
            .limit(5).all()
            
        recent_screentime = db.query(models.ScreenTime)\
            .filter(models.ScreenTime.child_id == child_id)\
            .order_by(models.ScreenTime.start_time.desc())\
            .limit(5).all()

        # Manually validate and return valid model
        try:
             # Convert ORM Child and lists to Pydantic models
             response_model = schemas.DashboardChildResponse(
                 child=schemas.Child.model_validate(child),
                 recent_exercises=[schemas.ExerciseLogResponse.model_validate(x) for x in recent_exercises],
                 recent_distance_checks=[schemas.DistanceCheck.model_validate(x) for x in recent_distance_checks],
                 recent_eye_tests=[schemas.EyeTest.model_validate(x) for x in recent_eye_tests],
                 recent_screentime=[schemas.ScreenTimeResponse.model_validate(x) for x in recent_screentime]
             )
             
             from fastapi.encoders import jsonable_encoder
             return jsonable_encoder(response_model)
        except Exception as e:
             with open("dashboard_debug.log", "w", encoding="utf-8") as f:
                f.write(f"Validation Error: {e}\n")
                f.write(traceback.format_exc())
             raise e
    except Exception as e:
        with open("dashboard_debug.log", "w", encoding="utf-8") as f:
            f.write(traceback.format_exc())
        raise e

@router.get("/parent/{parent_id}", response_model=schemas.DashboardParentResponse)
def get_parent_dashboard(parent_id: int, db: Session = Depends(get_db)):
    parent = db.query(models.Parent).filter(models.Parent.parent_id == parent_id).first()
    if not parent:
        raise HTTPException(status_code=404, detail="Parent not found")

    children = db.query(models.Child).filter(models.Child.parent_id == parent_id).all()
    
    children_data = []
    for child in children:
        # Re-use logic or call internal function (simplifying here by repeating for clarity/speed)
        recent_exercises = db.query(models.ExerciseLog)\
            .filter(models.ExerciseLog.child_id == child.child_id)\
            .order_by(models.ExerciseLog.exercise_date.desc())\
            .limit(5).all()

        recent_distance_checks = db.query(models.DistanceCheck)\
            .filter(models.DistanceCheck.child_id == child.child_id)\
            .order_by(models.DistanceCheck.check_date.desc())\
            .limit(5).all()

        recent_eye_tests = db.query(models.EyeTest)\
            .filter(models.EyeTest.child_id == child.child_id)\
            .order_by(models.EyeTest.check_date.desc())\
            .limit(5).all()
            
        recent_screentime = db.query(models.ScreenTime)\
            .filter(models.ScreenTime.child_id == child.child_id)\
            .order_by(models.ScreenTime.start_time.desc())\
            .limit(5).all()
            
        children_data.append({
            "child": child,
            "recent_exercises": recent_exercises,
            "recent_distance_checks": recent_distance_checks,
            "recent_eye_tests": recent_eye_tests,
            "recent_screentime": recent_screentime
        })

    # Manually validate and return valid model
    try:
         # Convert ORM Parent to Pydantic Parent
         parent_data = schemas.Parent.model_validate(parent)
         
         formatted_children_data = []
         for child_item in children_data:
             # Convert ORM Child and lists to Pydantic models
             formatted_children_data.append({
                 "child": schemas.Child.model_validate(child_item["child"]),
                 "recent_exercises": [schemas.ExerciseLogResponse.model_validate(x) for x in child_item["recent_exercises"]],
                 "recent_distance_checks": [schemas.DistanceCheck.model_validate(x) for x in child_item["recent_distance_checks"]],
                 "recent_eye_tests": [schemas.EyeTest.model_validate(x) for x in child_item["recent_eye_tests"]],
                 "recent_screentime": [schemas.ScreenTimeResponse.model_validate(x) for x in child_item["recent_screentime"]]
             })

         response_model = schemas.DashboardParentResponse(
             parent=parent_data,
             children_data=formatted_children_data
         )
         
         from fastapi.encoders import jsonable_encoder
         return jsonable_encoder(response_model)
    except Exception as e:
         import traceback
         with open("dashboard_parent_debug.log", "w", encoding="utf-8") as f:
            f.write(f"Validation Error: {e}\n")
            f.write(traceback.format_exc())
         raise e
