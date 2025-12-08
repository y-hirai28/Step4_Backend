# app/main.py
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from datetime import date
from typing import List

from app.routers import exercise
from app.database import engine, get_db, SessionLocal
from app import models, crud, schemas

models.Base.metadata.create_all(bind=engine)

# Initialize data
db = SessionLocal()
crud.init_db(db)
db.close()

app = FastAPI(title="Merelax API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(exercise.router, prefix="/api", tags=["exercise"])

@app.get("/")
def read_root():
    return {"message": "Merelax API"}

# --- Distance Check Endpoints ---

@app.post("/api/distance-check", response_model=schemas.DistanceCheck)
def create_distance_check(check: schemas.DistanceCheckCreate, db: Session = Depends(get_db)):
    db_check = models.DistanceCheck(
        child_id=check.child_id,
        check_date=date.today(),
        avg_distance_cm=check.distance_cm,
        posture_score=0,
        alert_flag=check.alert_flag
    )
    db.add(db_check)
    db.commit()
    db.refresh(db_check)
    return db_check

@app.get("/api/dashboard", response_model=List[schemas.DistanceCheck])
def read_dashboard(child_id: int, db: Session = Depends(get_db)):
    checks = db.query(models.DistanceCheck).filter(models.DistanceCheck.child_id == child_id).all()
    return checks

@app.post("/api/seed-child", response_model=schemas.Child)
def create_child(child: schemas.ChildCreate, db: Session = Depends(get_db)):
    db_child = models.Child(name=child.name, parent_id=1) # Default parent
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    return db_child
