# app/models.py
from sqlalchemy import Column, Integer, String, Text, DateTime, Date, ForeignKey, UniqueConstraint, Boolean
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
    email = Column(String(100), unique=True, index=True)
    line_id = Column(String(100))
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

class DistanceCheck(Base):
    __tablename__ = "DistanceCheck"

    check_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(Integer, ForeignKey("Child.child_id"), index=True, nullable=False)
    check_date = Column(Date, nullable=False)
    avg_distance_cm = Column(Float)
    posture_score = Column(Integer) # e.g. 0-100
    alert_flag = Column(Integer, default=0) # 0: No Alert, 1: Alerted
    created_at = Column(DateTime, server_default=func.now())

class ScreenTime(Base):
    __tablename__ = "ScreenTime"

    screentime_id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    child_id = Column(Integer, ForeignKey("Child.child_id"), index=True, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=True)
    total_minutes = Column(Integer, nullable=True)
    alert_flag = Column(Boolean, default=False)