# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import date, datetime, timedelta
from typing import List, Tuple
from app import models

def get_exercise_stats(db: Session, child_id: int) -> dict:
    """統計情報を計算"""
    
    # 連続実施日数を計算
    consecutive_days = calculate_consecutive_days(db, child_id)
    
    # 今週の実施日数を計算
    this_week_count = calculate_this_week_count(db, child_id)
    
    # 今日の達成状況
    today_completed, today_pending = get_today_status(db, child_id)
    
    return {
        "consecutive_days": consecutive_days,
        "this_week_count": this_week_count,
        "today_completed": today_completed,
        "today_pending": today_pending
    }

def calculate_consecutive_days(db: Session, child_id: int) -> int:
    """連続実施日数を計算"""
    # 実施日一覧を取得（降順）
    logs = db.query(distinct(models.ExerciseLog.exercise_date))\
        .filter(models.ExerciseLog.child_id == child_id)\
        .order_by(models.ExerciseLog.exercise_date.desc())\
        .all()
    
    if not logs:
        return 0
    
    dates = [log[0] for log in logs]
    today = date.today()
    
    # 今日から連続しているか確認
    if not dates:
        return 0
        
    current_idx = 0
    # If the latest log is not today or yesterday, streak is broken, unless we just want to count contiguous block from latest
    # Usually apps allow "today" to be missing if checked in the morning, but let's stick to strict continuity from "today" or "yesterday"
    
    if dates[0] == today:
        consecutive = 1
        current_idx = 0
    elif dates[0] == today - timedelta(days=1):
        consecutive = 1 # Streak continues from yesterday? Or streak is 0 if not done today yet? 
        # Requirement: "Continuous execution days". If I did it yesterday, streak is alive.
        # Let's count backwards from dates[0]
        consecutive = 1
        current_idx = 0
    else:
        return 0 # Last log was before yesterday
        
    # Check previous dates
    for i in range(1, len(dates)):
        diff = dates[i-1] - dates[i]
        if diff.days == 1:
            consecutive += 1
        else:
            break
            
    return consecutive

def calculate_this_week_count(db: Session, child_id: int) -> int:
    """今週の実施日数を計算"""
    today = date.today()
    start_of_week = today - timedelta(days=today.weekday())  # 月曜日
    end_of_week = start_of_week + timedelta(days=6)  # 日曜日
    
    count = db.query(func.count(distinct(models.ExerciseLog.exercise_date)))\
        .filter(models.ExerciseLog.child_id == child_id)\
        .filter(models.ExerciseLog.exercise_date >= start_of_week)\
        .filter(models.ExerciseLog.exercise_date <= end_of_week)\
        .scalar()
    
    return count or 0

def get_today_status(db: Session, child_id: int) -> Tuple[List[str], List[str]]:
    """今日の達成状況を取得"""
    today = date.today()
    
    # 今日実施済みのエクササイズ
    completed_logs = db.query(models.Exercise.exercise_type)\
        .join(models.ExerciseLog, models.ExerciseLog.exercise_id == models.Exercise.exercise_id)\
        .filter(models.ExerciseLog.child_id == child_id)\
        .filter(models.ExerciseLog.exercise_date == today)\
        .all()
    
    completed = [log[0] for log in completed_logs]
    
    # すべてのエクササイズタイプ
    all_types = ["distance_view", "blink", "eye_tracking"]
    pending = [t for t in all_types if t not in completed]
    
    return completed, pending

def log_exercise(db: Session, child_id: int, exercise_id: int, exercise_date: date) -> dict:
    """エクササイズ実施を記録"""
    # 既存レコードをチェック
    existing = db.query(models.ExerciseLog)\
        .filter(models.ExerciseLog.child_id == child_id)\
        .filter(models.ExerciseLog.exercise_id == exercise_id)\
        .filter(models.ExerciseLog.exercise_date == exercise_date)\
        .first()
    
    if existing:
        return {
            "success": False,
            "message": "今日はもうやったよ！"
        }
    
    # 新規記録
    new_log = models.ExerciseLog(
        child_id=child_id,
        exercise_id=exercise_id,
        exercise_date=exercise_date
    )
    db.add(new_log)
    db.commit()
    
    return {
        "success": True,
        "message": "よくできたね！"
    }

def init_db(db: Session):
    """初期データの投入"""
    # エクササイズデータが存在しない場合のみ投入
    if db.query(models.Exercise).count() == 0:
        exercises = [
            models.Exercise(
                exercise_type="distance_view",
                exercise_name="遠くを見よう",
                description="窓の外の雲を見てみよう"
            ),
            models.Exercise(
                exercise_type="blink",
                exercise_name="まばたき",
                description="パチパチしよう"
            ),
            models.Exercise(
                exercise_type="eye_tracking",
                exercise_name="目の体操",
                description="ぐるぐる動かそう"
            )
        ]
        db.add_all(exercises)
        db.commit()

