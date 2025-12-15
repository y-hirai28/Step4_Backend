from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import models, schemas
from app.database import get_db

router = APIRouter()

@router.post("/results", response_model=None)
def create_result(result: schemas.MeasurementResultCreate, db: Session = Depends(get_db)):
    db_result = models.MeasurementResult(
        eye=result.eye,
        distance=result.distance,
        visual_acuity=result.visual_acuity
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@router.get("/results", response_model=None)
def read_results(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    results = db.query(models.MeasurementResult).offset(skip).limit(limit).all()
    return results

@router.post("/eyetests", response_model=None)
def create_eyetest(eyetest: schemas.RfpEyeTestCreate, db: Session = Depends(get_db)):
    from datetime import date

    # Map test_type to test_distance_cm
    # "30cm" -> 30, "3m" -> 300
    distance_cm = 30
    if eyetest.test_type == "3m":
        distance_cm = 300
    
    # Create new EyeTest record (Always Insert)
    # Note: RfpEyeTestCreate receives floats for eyes, and EyeTest model now expects floats.
    db_eyetest = models.EyeTest(
        child_id=eyetest.child_id,
        check_date=date.today(),
        left_eye=eyetest.left_eye,
        right_eye=eyetest.right_eye,
        test_distance_cm=distance_cm
    )
    
    db.add(db_eyetest)
    db.commit()
    db.refresh(db_eyetest)
    
    return db_eyetest

@router.get("/eyetests", response_model=None)
def read_eyetests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Query EyeTest model instead of RfpEyeTest
    eyetests = db.query(models.EyeTest).order_by(models.EyeTest.check_date.desc()).offset(skip).limit(limit).all()
    return eyetests
