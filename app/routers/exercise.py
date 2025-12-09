from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app import crud, schemas, models
from app.database import get_db
# 本番環境では以下のコメントを外して認証を有効化
# from app.routers.auth import get_current_user

router = APIRouter()

@router.get("/child/{child_id}/exercise/stats", response_model=schemas.ExerciseStats)
def get_stats(
    child_id: int,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
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
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
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
