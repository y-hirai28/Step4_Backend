from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import datetime, timezone
import math
from app.database import get_db
from app import models, schemas
# 本番環境では以下のコメントを外して認証を有効化
# from app.routers.auth import get_current_user

router = APIRouter(
    prefix="/api/screentime",
    tags=["screentime"]
)

@router.post("/start", response_model=schemas.ScreenTimeStatus)
def start_screentime(
    request: schemas.ScreenTimeCreate,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # Check if there is already an active session for this child
    # If active session exists (end_time is Null), resume it
    active_session = db.query(models.ScreenTime)\
        .filter(models.ScreenTime.child_id == request.child_id)\
        .filter(models.ScreenTime.end_time == None)\
        .first()
    
    if active_session:
        # Calculate elapsed
        elapsed = (datetime.now() - active_session.start_time).total_seconds()
        return create_status_response(active_session, elapsed)

    # Start new session
    new_session = models.ScreenTime(
        child_id=request.child_id,
        start_time=datetime.now()
    )
    db.add(new_session)
    db.commit()
    db.refresh(new_session)
    
    return create_status_response(new_session, 0)

@router.get("/status", response_model=schemas.ScreenTimeStatus)
def get_status(
    child_id: int,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    active_session = db.query(models.ScreenTime)\
        .filter(models.ScreenTime.child_id == child_id)\
        .filter(models.ScreenTime.end_time == None)\
        .first()
    
    if not active_session:
        return schemas.ScreenTimeStatus(
            screentime_id=0,
            is_active=False,
            message="計測していないよ",
            alert_level=0,
            elapsed_seconds=0
        )
    
    elapsed = (datetime.now() - active_session.start_time).total_seconds()
    return create_status_response(active_session, elapsed)

@router.post("/end", response_model=schemas.ScreenTimeResponse)
def end_screentime(
    request: schemas.ScreenTimeBase,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    active_session = db.query(models.ScreenTime)\
        .filter(models.ScreenTime.child_id == request.child_id)\
        .filter(models.ScreenTime.end_time == None)\
        .first()
    
    if not active_session:
        raise HTTPException(status_code=404, detail="Active session not found")
    
    now = datetime.now()
    active_session.end_time = now
    
    # Calculate minutes rounded up? or standard?
    delta = now - active_session.start_time
    total_minutes = math.ceil(delta.total_seconds() / 60)
    active_session.total_minutes = total_minutes
    
    # Check alert flag if > 30 min (dummy logic for now, could be passed from frontend or calculated)
    if total_minutes >= 30:
        active_session.alert_flag = True
        
    db.commit()
    db.refresh(active_session)
    return active_session

def create_status_response(session: models.ScreenTime, elapsed_seconds: float) -> schemas.ScreenTimeStatus:
    minutes = elapsed_seconds / 60
    
    # Message Logic
    if minutes < 10:
        message = "あと すこし つかう？"
        alert_level = 0
    elif minutes < 20:
        message = "そろそろ めを やすめようか"
        alert_level = 1
    elif minutes < 30:
        message = "ながく みてると つかれちゃうよ"
        alert_level = 1
    else:
        message = "おわったら めを やすめようね"
        alert_level = 2
        
    return schemas.ScreenTimeStatus(
        screentime_id=session.screentime_id,
        is_active=True,
        start_time=session.start_time,
        elapsed_seconds=int(elapsed_seconds),
        message=message,
        alert_level=alert_level
    )
