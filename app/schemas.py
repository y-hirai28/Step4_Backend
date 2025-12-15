from pydantic import BaseModel
from datetime import date, datetime
from typing import List, Optional

class LogExerciseRequest(BaseModel):
    exercise_id: int
    exercise_date: date

class ExerciseStats(BaseModel):
    consecutive_days: int
    this_week_count: int
    today_completed: List[str]
    today_pending: List[str]

class LogExerciseResponse(BaseModel):
    success: bool
    message: str
    stats: ExerciseStats

class ExerciseBase(BaseModel):
    exercise_type: str
    exercise_name: str
    description: str | None = None

class Exercise(ExerciseBase):
    exercise_id: int

    class Config:
        from_attributes = True

# --- New Schemas for Distance Check ---

class DistanceCheckBase(BaseModel):
    distance_cm: int
    alert_flag: bool

class DistanceCheckCreate(DistanceCheckBase):
    child_id: int
    # check_date (handled by server)

class DistanceCheck(BaseModel):
    distance_id: int
    child_id: int
    check_date: date
    avg_distance_cm: int
    posture_score: int
    alert_flag: bool

    class Config:
        from_attributes = True

class ChildBase(BaseModel):
    name: str
    age: Optional[int] = None
    grade: Optional[str] = None

class ChildCreate(ChildBase):
    parent_id: int

class ChildUpdate(BaseModel):
    name: Optional[str] = None
    age: Optional[int] = None
    grade: Optional[str] = None

class Child(ChildBase):
    child_id: int
    parent_id: int

    class Config:
        from_attributes = True

class DailyMission(BaseModel):
    mission_id: str 
    title: str
    status: str 
    link: str

class LastResults(BaseModel):
    eye_test_date: Optional[date] = None
    left_eye: Optional[str] = None
    right_eye: Optional[str] = None
    distance_check_date: Optional[date] = None
    avg_distance_cm: Optional[float] = None
    posture_score: Optional[int] = None

class HomeResponse(BaseModel):
    missions: List[DailyMission]
    last_results: LastResults
    character_message: str

# --- Settings Related Schemas ---

class ParentBase(BaseModel):
    email: Optional[str] = None

class Parent(ParentBase):
    parent_id: int
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True

class SettingsBase(BaseModel):
    parent_id: int
    child_id: Optional[int] = None
    voice_enabled: bool = True

class SettingsUpdate(BaseModel):
    child_id: Optional[int] = None
    voice_enabled: Optional[bool] = None

class Settings(SettingsBase):
    settings_id: int
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- Eye Test Schemas ---

class EyeTestBase(BaseModel):
    left_eye: Optional[float] = None
    right_eye: Optional[float] = None
    test_distance_cm: Optional[int] = None

class EyeTestCreate(EyeTestBase):
    child_id: int
    # check_date handled by server

class EyeTest(EyeTestBase):
    test_id: int
    child_id: int
    check_date: date
    created_at: datetime

    class Config:
        from_attributes = True



class ScreenTimeBase(BaseModel):
    child_id: int

class ScreenTimeCreate(ScreenTimeBase):
    start_time: Optional[datetime] = None # Optional, defaulted to now in backend

class ScreenTimeStatus(BaseModel):
    screentime_id: int
    is_active: bool
    start_time: Optional[datetime] = None
    elapsed_seconds: int = 0
    message: str
    alert_level: int = 0 # 0: Safe, 1: Warning, 2: Alert

class ScreenTimeResponse(BaseModel):
    screentime_id: int
    child_id: int
    start_time: datetime
    end_time: Optional[datetime] = None
    total_minutes: Optional[int] = None

    class Config:
        from_attributes = True

# --- Dashboard Schemas ---

class ExerciseLogResponse(BaseModel):
    log_id: int
    child_id: int
    exercise_id: int
    exercise_date: date
    created_at: datetime

    class Config:
        from_attributes = True

class DashboardChildResponse(BaseModel):
    child: Child
    recent_exercises: List[ExerciseLogResponse] = [] # Need to ensure LogResponse is available or use a generic one
    recent_distance_checks: List[DistanceCheck] = []
    recent_eye_tests: List[EyeTest] = []
    recent_screentime: List[ScreenTimeResponse] = []

class DashboardParentResponse(BaseModel):
    parent: Parent
    children_data: List[DashboardChildResponse]

# --- Auth Schemas ---

class UserRegister(BaseModel):
    email: str
    password: str

class UserLogin(BaseModel):
    email: str
    password: str

class VerifyCode(BaseModel):
    session_id: str
    verification_code: str

class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str
    expires_in: int
    user: dict # or a specifically typed user object

class TokenData(BaseModel):
    parent_id: Optional[str] = None

class RefreshRequest(BaseModel):
    refresh_token: str

class RefreshResponse(BaseModel):
    access_token: str
    token_type: str
    expires_in: int

class LineLoginCallback(BaseModel):
    code: str
    state: str

class UserResponse(BaseModel):
    parent_id: int
    email: str
    line_id: Optional[str] = None
    created_at: datetime

    class Config:
        from_attributes = True

class MeasurementResultCreate(BaseModel):
    eye: str
    distance: str
    visual_acuity: float

class RfpEyeTestCreate(BaseModel):
    child_id: int = 1
    left_eye: Optional[float] = None
    right_eye: Optional[float] = None
    test_type: str = "3m"

class RfpEyeTest(BaseModel):
    id: int
    child_id: int
    check_date: datetime
    left_eye: Optional[float] = None
    right_eye: Optional[float] = None
    recovery_level: Optional[float] = None
    test_type: str

    class Config:
        from_attributes = True

