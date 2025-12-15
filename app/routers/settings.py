from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database import get_db
from app import models, schemas
# 本番環境では以下のコメントを外して認証を有効化
# from app.routers.auth import get_current_user


router = APIRouter(
    prefix="/api/v1",
    tags=["settings"]
)

# --- Settings API ---

@router.get("/settings/{parent_id}", response_model=schemas.Settings)
def get_settings(
    parent_id: int,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # 本番環境では認証を有効化した場合、parent_id チェックを追加
    # if parent_id != current_user.parent_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    settings = db.query(models.Settings).filter(models.Settings.parent_id == parent_id).first()
    if not settings:
        # Create default settings if not exists
        # Ensure parent exists first (Mock logic: create parent if not exists for prototype)
        parent = db.query(models.Parent).filter(models.Parent.parent_id == parent_id).first()
        if not parent:
            parent = models.Parent(parent_id=parent_id, email=f"parent{parent_id}@example.com")
            db.add(parent)
            db.commit()
            
        settings = models.Settings(parent_id=parent_id, voice_enabled=True)
        # Try to set default child
        child = db.query(models.Child).filter(models.Child.parent_id == parent_id).first()
        if child:
            settings.child_id = child.child_id
            
        db.add(settings)
        db.commit()
        db.refresh(settings)
        
    return settings

@router.put("/settings/{parent_id}", response_model=schemas.Settings)
def update_settings(
    parent_id: int,
    settings_update: schemas.SettingsUpdate,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # 本番環境では認証を有効化した場合、parent_id チェックを追加
    # if parent_id != current_user.parent_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    settings = db.query(models.Settings).filter(models.Settings.parent_id == parent_id).first()
    if not settings:
        raise HTTPException(status_code=404, detail="Settings not found")

    if settings_update.child_id is not None:
        settings.child_id = settings_update.child_id
    if settings_update.voice_enabled is not None:
        settings.voice_enabled = settings_update.voice_enabled
        
    db.commit()
    db.refresh(settings)
    return settings

# --- Child Management API ---

@router.get("/child/all/{parent_id}", response_model=List[schemas.Child])
def get_children(
    parent_id: int,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # 本番環境では認証を有効化した場合、parent_id チェックを追加
    # if parent_id != current_user.parent_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    children = db.query(models.Child).filter(models.Child.parent_id == parent_id).all()
    return children

@router.post("/child/add", response_model=schemas.Child)
def add_child(
    child: schemas.ChildCreate,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    # 本番環境では認証を有効化した場合、parent_id チェックを追加
    # if child.parent_id != current_user.parent_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    db_child = models.Child(
        parent_id=child.parent_id,
        name=child.name,
        age=child.age,
        grade=child.grade
    )
    db.add(db_child)
    db.commit()
    db.refresh(db_child)
    
    # If this is the first child, update settings to select this child
    settings = db.query(models.Settings).filter(models.Settings.parent_id == child.parent_id).first()
    if settings and not settings.child_id:
        settings.child_id = db_child.child_id
        db.commit()
        
    return db_child

@router.put("/child/{child_id}", response_model=schemas.Child)
def update_child(
    child_id: int,
    child_update: schemas.ChildUpdate,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    db_child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    if not db_child:
        raise HTTPException(status_code=404, detail="Child not found")

    # 本番環境では認証を有効化した場合、parent_id チェックを追加
    # if db_child.parent_id != current_user.parent_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    if child_update.name is not None:
        db_child.name = child_update.name
    if child_update.age is not None:
        db_child.age = child_update.age
    if child_update.grade is not None:
        db_child.grade = child_update.grade
        
    db.commit()
    db.refresh(db_child)
    return db_child

@router.delete("/child/{child_id}")
def delete_child(
    child_id: int,
    db: Session = Depends(get_db),
    # 本番環境では以下のコメントを外して認証を有効化
    # current_user: models.Parent = Depends(get_current_user)
):
    db_child = db.query(models.Child).filter(models.Child.child_id == child_id).first()
    if not db_child:
        raise HTTPException(status_code=404, detail="Child not found")

    # 本番環境では認証を有効化した場合、parent_id チェックを追加
    # if db_child.parent_id != current_user.parent_id:
    #     raise HTTPException(status_code=403, detail="Access denied")

    # Also update settings if this child was selected
    settings = db.query(models.Settings).filter(models.Settings.child_id == child_id).first()
    if settings:
        settings.child_id = None
        db.add(settings)

    db.delete(db_child)
    db.commit()
    return {"status": "deleted"}
