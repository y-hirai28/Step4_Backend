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

    # Check if there's already a test for this child today
    today = date.today()
    existing_test = db.query(models.RfpEyeTest)\
        .filter(models.RfpEyeTest.child_id == eyetest.child_id)\
        .filter(db.func.date(models.RfpEyeTest.check_date) == today)\
        .first()

    if existing_test:
        # Update existing test
        existing_test.left_eye = eyetest.left_eye
        existing_test.right_eye = eyetest.right_eye
        existing_test.test_type = eyetest.test_type
        db.commit()
        db.refresh(existing_test)
        return existing_test

    # Create new test
    db_eyetest = models.RfpEyeTest(
        child_id=eyetest.child_id,
        left_eye=eyetest.left_eye,
        right_eye=eyetest.right_eye,
        test_type=eyetest.test_type
    )
    db.add(db_eyetest)
    db.commit()
    db.refresh(db_eyetest)
    return db_eyetest

@router.get("/eyetests", response_model=None)
def read_eyetests(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    # Query RfpEyeTest model
    eyetests = db.query(models.RfpEyeTest).order_by(models.RfpEyeTest.check_date.desc()).offset(skip).limit(limit).all()
    return eyetests
