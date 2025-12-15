from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from datetime import date, datetime
import random
from app.database import get_db
from app import models, schemas
# 本番環境では以下のコメントを外して認証を有効化
# from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/home",
    tags=["home"]
)

@router.get("/{child_id}", response_model=schemas.HomeResponse)
def get_home_data(
    child_id: int,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # 1. Verify Child Exists
    # 本番環境では認証を有効化した場合、以下のクエリに parent_id チェックを追加
    # child = db.query(models.Child).filter(
    #     models.Child.child_id == child_id,
    #     models.Child.parent_id == current_user.parent_id  # 所有者チェック
    # ).first()
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
        .order_by(models.EyeTest.check_date.desc(), models.EyeTest.created_at.desc())\
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

    # Get latest completed screentime session
    last_screentime = db.query(models.ScreenTime)\
        .filter(models.ScreenTime.child_id == child_id)\
        .filter(models.ScreenTime.end_time != None)\
        .order_by(models.ScreenTime.end_time.desc())\
        .first()

    if last_screentime:
        last_results.total_screentime_minutes = last_screentime.total_minutes

    # 4. Character Message Logic
    # Time-based or general messages (randomly selected)
    now = datetime.now()
    hour = now.hour

    # 時間帯別メッセージ
    morning_messages = [
        "おはよう！きょうも にこにこだね！",
        "おきた？めも おきたよ！",
        "きょうは どんな いちにちに なるかな？"
    ]

    afternoon_messages = [
        "こんにちは！げんきに あそんでる？"
    ]

    evening_messages = [
        "きょうも いっぱい がんばったね",
        "そろそろ めを やすめよう",
        "おやすみ！また あした あそぼうね！"
    ]

    # ふだん用メッセージ
    general_messages = [
        "きょうも あいにきてくれて うれしい！",
        "めが きらきらしてるね！",
        "こんにちは！きょうも いっしょに みよう！",
        "めを たいせつに してるね！えらいね！",
        "きょうも たのしく すごそうね！",
        "めめめが みまもってるよ！"
    ]

    # 時間帯別メッセージもしくは普段用メッセージのどちらかを選択
    use_time_based = random.choice([True, False])

    if use_time_based:
        # 時間帯別メッセージを表示
        if 5 <= hour < 11:
            # 朝（5:00〜10:59）
            message = random.choice(morning_messages)
        elif 11 <= hour < 18:
            # 昼（11:00〜17:59）
            message = random.choice(afternoon_messages)
        elif 18 <= hour < 24:
            # 夜（18:00〜23:59）
            message = random.choice(evening_messages)
        else:
            # 深夜（0:00〜4:59）はふだん用メッセージにフォールバック
            message = random.choice(general_messages)
    else:
        # ふだん用メッセージを表示
        message = random.choice(general_messages)

    return schemas.HomeResponse(
        missions=missions,
        last_results=last_results,
        character_message=message
    )

@router.get("/character/message/{child_id}")
def get_character_message(
    child_id: int,
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # This could be a separate lighter endpoint for just updating the message
    return {"message": "きょうもがんばろう！"}
