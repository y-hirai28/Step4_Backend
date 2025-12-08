from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/child/{child_id}/exercise/stats", response_model=schemas.ExerciseStats)
def get_stats(child_id: int, db: Session = Depends(get_db)):
    """統計情報取得"""
    try:
        stats = crud.get_exercise_stats(db, child_id)
        return stats
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/child/{child_id}/exercise/log", response_model=schemas.LogExerciseResponse)
def log_exercise_endpoint(
    child_id: int,
    request: schemas.LogExerciseRequest,
    db: Session = Depends(get_db)
):
    """エクササイズ実施記録"""
    try:
        result = crud.log_exercise(
            db, 
            child_id, 
            request.exercise_id, 
            request.exercise_date
        )
        
        # 更新された統計情報を取得
        stats = crud.get_exercise_stats(db, child_id)
        
        return {
            "success": result["success"],
            "message": result["message"],
            "stats": stats
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
