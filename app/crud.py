# app/crud.py
from sqlalchemy.orm import Session
from sqlalchemy import func, distinct
from datetime import date, datetime, timedelta
from typing import List, Tuple, Optional
from app import models, schemas, utils

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

    # Seed Demo Users
    demo_users = [
        {"email": "demo@example.com", "password": "demo123", "child_name": "デモ太郎"},
        {"email": "test@example.com", "password": "test123", "child_name": "テスト花子"}
    ]

    for user_data in demo_users:
        if not get_parent_by_email(db, user_data["email"]):
            # Create Parent
            hashed_pwd = utils.get_password_hash(user_data["password"])
            new_parent = models.Parent(
                email=user_data["email"], 
                password_hash=hashed_pwd,
                is_email_verified=True
            )
            db.add(new_parent)
            db.commit()
            db.refresh(new_parent)
            
            # Create Default Child
            new_child = models.Child(
                name=user_data["child_name"],
                parent_id=new_parent.parent_id
            )
            db.add(new_child)
            db.commit()
            print(f"Created demo user: {user_data['email']}")


# --- Auth CRUD ---

def get_parent_by_email(db: Session, email: str):
    return db.query(models.Parent).filter(models.Parent.email == email).first()

def create_parent(db: Session, user: schemas.UserRegister):
    hashed_password = utils.get_password_hash(user.password)
    db_user = models.Parent(email=user.email, password_hash=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def create_parent_via_line(db: Session, email: str, line_id: str):
    # LINEログインで新規登録の場合（パスワードなし）
    db_user = models.Parent(email=email, line_id=line_id, is_email_verified=True)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_parent_line_id(db: Session, parent_id: int, line_id: str):
    parent = db.query(models.Parent).filter(models.Parent.parent_id == parent_id).first()
    if parent:
        parent.line_id = line_id
        parent.updated_at = datetime.utcnow() # Update timestamp
        db.commit()
        db.refresh(parent)
    return parent

def store_verification_code(db: Session, email: str, code: str, session_id: str):
    # Store hashed code? Spec says hashed.
    code_hash = utils.get_password_hash(code) 
    expires_at = datetime.utcnow() + timedelta(minutes=5)
    
    db_code = models.VerificationCode(
        session_id=session_id,
        email=email,
        code_hash=code_hash,
        expires_at=expires_at
    )
    db.add(db_code)
    db.commit()
    return db_code

def verify_code(db: Session, session_id: str, plain_code: str):
    record = db.query(models.VerificationCode).filter(models.VerificationCode.session_id == session_id).first()
    if not record:
        return None
    
    if record.expires_at < datetime.utcnow():
        return None # Expired
        
    if not utils.verify_password(plain_code, record.code_hash):
        return None # Invalid code
        
    # Mark as verified (or delete)
    record.verified = True
    db.commit()
    return record

def store_refresh_token(db: Session, parent_id: int, token: str):
    token_hash = utils.get_token_hash(token)
    expires_at = datetime.utcnow() + timedelta(days=7)
    
    db_token = models.RefreshToken(
        parent_id=parent_id,
        token_hash=token_hash,
        expires_at=expires_at
    )
    db.add(db_token)
    db.commit()
    return db_token

def get_refresh_token_record(db: Session, token: str):
    # This is tricky since we store hash. We can't query by token.
    # Usually refresh token rotation involves sending the token, finding the user/session associated (if we stored it unhashed or with an ID), 
    # but spec says store hash.
    # If we store ONLY hash, we can't find the record efficiently without an ID.
    # But usually the client sends the refresh token. 
    # Let's assume for now we verify it against all tokens for the user? No, that's inefficient.
    # Re-reading spec: "データベースに保存(ハッシュ化)"
    # A standard way is to return a transparent token ID or just handle it like a password.
    # However, for refresh tokens, usually we store them so we can REVOKE them.
    # Unlike passwords, we can store the token itself or a hash. If hash, we need a way to look it up.
    # Maybe the refresh token contains the ID? 
    # For now, let's implement lookup by verifying it against user's tokens if we had logical association, 
    # but to be practical: we might need to store the raw token or use the JWT ID (jti) in the DB.
    # Given the spec, let's assume we decode the JWT to get the user ID, then iterate/check? 
    # Or simply: The RefreshToken model has `token_hash`. 
    # If we receive a JWT refresh token, we can get `sub` (parent_id). 
    # Then we check valid refresh tokens for that parent.
    return None 
    
def revoke_refresh_token(db: Session, token: str):
    # Need to find it first.
    pass
