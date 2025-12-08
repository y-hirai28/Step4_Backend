from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session
from datetime import timedelta
import os
import requests
from typing import Optional

from app import schemas, models, crud, utils
from app.database import get_db

router = APIRouter(
    prefix="/auth",
    tags=["auth"],
)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/auth/token") # Not strictly used in this flow but good for Swagger UI

# --- Dependency ---
def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = utils.verify_token(token, credentials_exception)
    parent_id: int = payload.get("sub")
    if parent_id is None:
        raise credentials_exception
    user = db.query(models.Parent).filter(models.Parent.parent_id == parent_id).first()
    if user is None:
        raise credentials_exception
    return user

# --- Email Auth Endpoints ---

@router.post("/register", response_model=schemas.UserResponse)
def register(user: schemas.UserRegister, db: Session = Depends(get_db)):
    db_user = crud.get_parent_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_parent(db=db, user=user)

@router.post("/login")
def login(user: schemas.UserLogin, db: Session = Depends(get_db)):
    db_user = crud.get_parent_by_email(db, email=user.email)
    if not db_user or not utils.verify_password(user.password, db_user.password_hash):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    # Generate verification code
    code = utils.generate_verification_code()
    session_id = utils.generate_session_id()
    
    # Store code
    crud.store_verification_code(db, user.email, code, session_id)
    
    # In a real app, send email here. For now, return in response as requested.
    return {
        "message": "Verification code generated",
        "session_id": session_id,
        "verification_code": code, # For display purposes
        "expires_in": 300
    }

@router.post("/verify-code", response_model=schemas.Token)
def verify_code(data: schemas.VerifyCode, db: Session = Depends(get_db)):
    record = crud.verify_code(db, data.session_id, data.verification_code)
    if not record:
        raise HTTPException(status_code=400, detail="Invalid or expired verification code")
    
    user = crud.get_parent_by_email(db, record.email)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": user.parent_id}, expires_delta=access_token_expires
    )
    
    refresh_token = utils.create_refresh_token(
        data={"sub": user.parent_id}
    )
    
    # Store refresh token hash
    crud.store_refresh_token(db, user.parent_id, refresh_token)
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer",
        "expires_in": utils.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        "user": {
            "parent_id": user.parent_id,
            "email": user.email
        }
    }

# --- LINE Auth Endpoints ---

LINE_CHANNEL_ID = os.getenv("LINE_CHANNEL_ID")
LINE_CHANNEL_SECRET = os.getenv("LINE_CHANNEL_SECRET")
LINE_REDIRECT_URI = os.getenv("LINE_REDIRECT_URI") # e.g. http://localhost:3000/auth/callback

@router.get("/line/login")
def line_login():
    if not LINE_CHANNEL_ID or not LINE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="LINE configuration missing")
        
    state = utils.generate_session_id() # Simple state generation
    # Redirect URL
    url = f"https://access.line.me/oauth2/v2.1/authorize?response_type=code&client_id={LINE_CHANNEL_ID}&redirect_uri={LINE_REDIRECT_URI}&state={state}&scope=profile%20openid%20email"
    return {"url": url}

@router.post("/line/callback")
def line_callback(data: schemas.LineLoginCallback, db: Session = Depends(get_db)):
    # Verify implementation on frontend calls this with code
    
    if not LINE_CHANNEL_ID or not LINE_CHANNEL_SECRET or not LINE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="LINE configuration missing")

    # Exchange code for token
    token_url = "https://api.line.me/oauth2/v2.1/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    payload = {
        "grant_type": "authorization_code",
        "code": data.code,
        "redirect_uri": LINE_REDIRECT_URI,
        "client_id": LINE_CHANNEL_ID,
        "client_secret": LINE_CHANNEL_SECRET
    }
    
    res = requests.post(token_url, headers=headers, data=payload)
    if res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get LINE token")
        
    token_data = res.json()
    id_token = token_data.get("id_token") # contains user info
    
    # Verify ID token (simplified, ideally verify signature)
    # Get user profile
    profile_url = "https://api.line.me/v2/profile"
    profile_headers = {"Authorization": f"Bearer {token_data['access_token']}"}
    profile_res = requests.get(profile_url, headers=profile_headers)
    
    if profile_res.status_code != 200:
        raise HTTPException(status_code=400, detail="Failed to get LINE profile")
    
    profile = profile_res.json()
    line_user_id = profile["userId"]
    # Email is available in id_token payload if scope includes email and user permitted
    # For simplicity, we might generate a dummy email or extract from id_token if critical
    # Here assuming we just use line_id to login or create
    
    # Check if user exists by LINE ID
    user = db.query(models.Parent).filter(models.Parent.line_id == line_user_id).first()
    
    if not user:
        # Create new user
        # We need an email. If LINE doesn't provide one easily without complex verification, 
        # we might use a placeholder or ask user to input email.
        # Spec 2.2.7 says "Existing user login, New user register".
        # Let's generate a placeholder email if not available, or just fail?
        # unique constraint on email.
        dummy_email = f"{line_user_id}@line.user"
        user = crud.create_parent_via_line(db, dummy_email, line_user_id)
    
    # Issue JWT
    access_token = utils.create_access_token(data={"sub": user.parent_id})
    refresh_token = utils.create_refresh_token(data={"sub": user.parent_id})
    crud.store_refresh_token(db, user.parent_id, refresh_token)
    
    return {
        "access_token": access_token, 
        "refresh_token": refresh_token, 
        "token_type": "bearer",
        "user": {
            "parent_id": user.parent_id,
            "email": user.email
        }
    }

@router.get("/me", response_model=schemas.UserResponse)
def read_users_me(current_user: models.Parent = Depends(get_current_user)):
    return current_user

@router.post("/refresh", response_model=schemas.RefreshResponse)
def refresh_token(request: schemas.RefreshRequest, db: Session = Depends(get_db)):
    # Verify refresh token
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        payload = utils.verify_token(request.refresh_token, credentials_exception)
        parent_id: int = payload.get("sub")
        if parent_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception
        
    # Check if refresh token is in DB (optional/TODO: implement proper revocation check)
    # For now simply issue new access token
    
    access_token_expires = timedelta(minutes=utils.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = utils.create_access_token(
        data={"sub": parent_id}, expires_delta=access_token_expires
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": utils.ACCESS_TOKEN_EXPIRE_MINUTES * 60
    }
