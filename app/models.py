# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, UniqueConstraint, Boolean, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database import Base

class Exercise(Base):
    __tablename__ = "Exercise"
    
    exercise_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    exercise_type = Column(String(50), nullable=False)
    exercise_name = Column(String(100), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())

class ExerciseLog(Base):
    __tablename__ = "ExerciseLog"
    
    log_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(Integer, index=True, nullable=False) # Simplified for now, assuming external Child table or just ID
    exercise_id = Column(Integer, ForeignKey("Exercise.exercise_id"), nullable=False)
    exercise_date = Column(Date, nullable=False)
    created_at = Column(DateTime, server_default=func.now())
    
    __table_args__ = (
        UniqueConstraint('child_id', 'exercise_id', 'exercise_date', 
                        name='unique_child_exercise_date'),
    )

# --- New Models for Distance Check ---

class Child(Base):
    __tablename__ = "Child"

    child_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, index=True) 
    name = Column(String(50), index=True)
    age = Column(Integer, nullable=True)
    grade = Column(String(20), nullable=True)
    
    distance_checks = relationship("DistanceCheck", back_populates="child")

class DistanceCheck(Base):
    __tablename__ = "DistanceCheck"

    distance_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(Integer, ForeignKey("Child.child_id"), nullable=False)
    check_date = Column(Date, nullable=False)
    avg_distance_cm = Column(Integer, nullable=False)
    posture_score = Column(Integer, default=0)
    alert_flag = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

    child = relationship("Child", back_populates="distance_checks")

class Parent(Base):
    __tablename__ = "Parent"

    parent_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    email = Column(String(100), unique=True, index=True, nullable=False)
    password_hash = Column(String(255), nullable=True) # Check if fits bcrypt hash
    line_id = Column(String(255), unique=True, index=True, nullable=True)
    is_email_verified = Column(Boolean, default=False)
    last_login_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    refresh_tokens = relationship("RefreshToken", back_populates="parent", cascade="all, delete-orphan")

class RefreshToken(Base):
    __tablename__ = "refresh_tokens"

    token_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("Parent.parent_id"), nullable=False)
    token_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    parent = relationship("Parent", back_populates="refresh_tokens")

class VerificationCode(Base):
    __tablename__ = "verification_codes"

    verification_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    session_id = Column(String(36), unique=True, index=True, nullable=False)
    email = Column(String(255), index=True, nullable=False)
    code_hash = Column(String(255), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    verified = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())

class Settings(Base):
    __tablename__ = "Settings"

    settings_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    parent_id = Column(Integer, ForeignKey("Parent.parent_id"), unique=True, nullable=False)
    child_id = Column(Integer, ForeignKey("Child.child_id"), nullable=True) # Selected child
    voice_enabled = Column(Boolean, default=True)
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class EyeTest(Base):
    __tablename__ = "EyeTest"

    test_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(Integer, ForeignKey("Child.child_id"), index=True, nullable=False)
    check_date = Column(Date, nullable=False)
    left_eye = Column(String(10)) # e.g. "1.0", "A"
    right_eye = Column(String(10)) 
    created_at = Column(DateTime, server_default=func.now())
    test_distance_cm = Column(Integer, nullable=True) # Added for measurement distance

class MeasurementResult(Base):
    __tablename__ = "measurement_results"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime, server_default=func.now())
    eye = Column(String(10)) # "left" or "right"
    distance = Column(String(10)) # "30cm" or "3m"
    visual_acuity = Column(Float)

class RfpEyeTest(Base):
    __tablename__ = "rfp_eye_tests"

    id = Column(Integer, primary_key=True, index=True)
    child_id = Column(Integer, default=1) 
    check_date = Column(DateTime, server_default=func.now())
    left_eye = Column(Float, nullable=True)
    right_eye = Column(Float, nullable=True)
    recovery_level = Column(Float, nullable=True)
    test_type = Column(String(10), default="3m") # "3m" or "30cm"

class ScreenTime(Base):
    __tablename__ = "ScreenTime"

    screentime_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(Integer, ForeignKey("Child.child_id"), index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    total_minutes = Column(Integer, nullable=True)
    alert_flag = Column(Boolean, default=False)