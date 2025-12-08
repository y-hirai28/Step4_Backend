from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date
from app.database import get_db
from app import models, schemas

router = APIRouter(
    prefix="/api",
    tags=["home"]
)

@router.get("/home/{child_id}", response_model=schemas.HomeResponse)
def get_home_data(child_id: int, db: Session = Depends(get_db)):
    # 1. Verify Child Exists
    child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    if not child:
        # For development, if child doesn't exist, we might want to return dummy data or create one?
        # But correctly we should 404. 
        # For this prototype, let's just return 404.
        raise HTTPException(status_code=404, detail="Child not found")

    today = date.today()

    # 2. Daily Missions Logic
    missions = []
    
    # Check simple missions based on logs (Dummy logic for now as logs might be empty)
    # Eye Test Status
    last_eye_test = db.query(models.EyeTest)\
        .filter(models.EyeTest.child_id == child_id)\
        .order_by(models.EyeTest.check_date.desc())\
        .first()
        
    eye_test_done = last_eye_test and last_eye_test.check_date == today
    missions.append(schemas.DailyMission(
        mission_id="eye_test",
        title="視力チェック",
        status="completed" if eye_test_done else "pending",
        link="/eyetest"
    ))

    # Distance Check Status
    last_distance_check = db.query(models.DistanceCheck)\
        .filter(models.DistanceCheck.child_id == child_id)\
        .order_by(models.DistanceCheck.check_date.desc())\
        .first()
        
    distance_done = last_distance_check and last_distance_check.check_date == today
    missions.append(schemas.DailyMission(
        mission_id="distance_check",
        title="距離チェック",
        status="completed" if distance_done else "pending",
        link="/distancecheck"
    ))

    # Blink Challenge (Dummy Status)
    missions.append(schemas.DailyMission(
        mission_id="blink_challenge",
        title="まばたきチャレンジ",
        status="pending", # To be implemented
        link="/blinkchallenge" # Assumed link
    ))

    # MeRelax Exercise (Dummy Status)
    missions.append(schemas.DailyMission(
        mission_id="merelax_exercise",
        title="めラックス体操",
        status="pending", # To be implemented
        link="/exercise"
    ))

    # 3. Last Results Logic
    last_results = schemas.LastResults()
    if last_eye_test:
        last_results.eye_test_date = last_eye_test.check_date
        last_results.left_eye = last_eye_test.left_eye
        last_results.right_eye = last_eye_test.right_eye
    
    if last_distance_check:
        last_results.distance_check_date = last_distance_check.check_date
        last_results.avg_distance_cm = last_distance_check.avg_distance_cm
        last_results.posture_score = last_distance_check.posture_score

    # 4. Character Message Logic
    # Simple logic based on completion
    completed_count = sum(1 for m in missions if m.status == "completed")
    if completed_count == 4:
        message = "ぜんぶクリア！すごいね！あしたもがんばろう！"
    elif completed_count >= 1:
        message = "そのちょうし！あとのミッションもやってみよう！"
    else:
        message = "今日は距離チェックまだだよ！めをまもろう！"

    return schemas.HomeResponse(
        missions=missions,
        last_results=last_results,
        character_message=message
    )

@router.get("/character/message/{child_id}")
def get_character_message(child_id: int):
    # This could be a separate lighter endpoint for just updating the message
    return {"message": "きょうもがんばろう！"}
