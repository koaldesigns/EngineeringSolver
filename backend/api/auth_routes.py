"""
Authentication API routes: register, login, logout, and session management.
"""
import os
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserPreferences, RegistrationToken, VALID_TOKENS
from auth import (
    hash_password, 
    verify_password, 
    create_access_token, 
    get_current_user,
    get_current_user_optional,
    ACCESS_TOKEN_EXPIRE_HOURS
)

router = APIRouter(prefix="/auth", tags=["auth"])

# Maximum regular users (not counting admin)
MAX_USERS = 10


# ============== Request/Response Models ==============

class RegisterRequest(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    password: str = Field(..., min_length=4, max_length=100)
    token: str = Field(..., description="Registration token")


class LoginRequest(BaseModel):
    username: str
    password: str


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int  # seconds
    user: dict


class UserResponse(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime
    last_active: datetime


# ============== Helper Functions ==============

def init_tokens_if_needed(db: Session):
    """Initialize registration tokens in database if not present."""
    existing = db.query(RegistrationToken).count()
    if existing == 0:
        for token in VALID_TOKENS:
            db.add(RegistrationToken(token=token))
        db.commit()


def create_admin_if_needed(db: Session):
    """Create admin account from environment variables if not exists."""
    admin_username = os.environ.get("ADMIN_USERNAME")
    admin_password = os.environ.get("ADMIN_PASSWORD")
    
    if not admin_username or not admin_password:
        return
    
    existing_admin = db.query(User).filter(User.username == admin_username).first()
    if existing_admin:
        return
    
    admin_user = User(
        username=admin_username,
        password_hash=hash_password(admin_password),
        is_admin=True
    )
    db.add(admin_user)
    
    # Create default preferences for admin
    db.flush()  # Get the user ID
    prefs = UserPreferences(user_id=admin_user.id)
    db.add(prefs)
    
    db.commit()
    print(f"Admin account '{admin_username}' created.")


# ============== Routes ==============

@router.post("/register", response_model=TokenResponse)
async def register(request: RegisterRequest, db: Session = Depends(get_db)):
    """
    Register a new user account.
    Requires a valid registration token.
    """
    # Initialize tokens if needed
    init_tokens_if_needed(db)
    
    # Check if token is valid and available
    token_record = db.query(RegistrationToken).filter(
        RegistrationToken.token == request.token,
        RegistrationToken.used_by_user_id.is_(None)
    ).first()
    
    if not token_record:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or already used registration token"
        )
    
    # Check user count limit (excluding admin users)
    regular_user_count = db.query(User).filter(User.is_admin == False).count()
    if regular_user_count >= MAX_USERS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Maximum user limit reached"
        )
    
    # Check if username already exists
    existing_user = db.query(User).filter(User.username == request.username).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already taken"
        )
    
    # Create the user
    new_user = User(
        username=request.username,
        password_hash=hash_password(request.password),
        is_admin=False
    )
    db.add(new_user)
    db.flush()  # Get user ID
    
    # Mark token as used
    token_record.used_by_user_id = new_user.id
    token_record.used_at = datetime.utcnow()
    
    # Create default preferences
    prefs = UserPreferences(user_id=new_user.id)
    db.add(prefs)
    
    db.commit()
    db.refresh(new_user)
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(new_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        "user": {
            "id": new_user.id,
            "username": new_user.username,
            "is_admin": new_user.is_admin
        }
    }


@router.post("/login", response_model=TokenResponse)
async def login(request: LoginRequest, db: Session = Depends(get_db)):
    """
    Login with username and password.
    Returns a JWT access token.
    """
    # Create admin if needed (on first login attempt)
    create_admin_if_needed(db)
    
    # Find user
    user = db.query(User).filter(User.username == request.username).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Verify password
    if not verify_password(request.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid username or password"
        )
    
    # Update last active
    user.last_active = datetime.utcnow()
    db.commit()
    
    # Generate access token
    access_token = create_access_token(data={"sub": str(user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        "user": {
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin
        }
    }


@router.get("/me", response_model=UserResponse)
async def get_current_user_info(current_user: User = Depends(get_current_user)):
    """
    Get the current authenticated user's information.
    Also refreshes the session.
    """
    return {
        "id": current_user.id,
        "username": current_user.username,
        "is_admin": current_user.is_admin,
        "created_at": current_user.created_at,
        "last_active": current_user.last_active
    }


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(current_user: User = Depends(get_current_user)):
    """
    Refresh the access token (extends session).
    Call this periodically while the user is active.
    """
    access_token = create_access_token(data={"sub": str(current_user.id)})
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "expires_in": ACCESS_TOKEN_EXPIRE_HOURS * 3600,
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "is_admin": current_user.is_admin
        }
    }


@router.post("/logout")
async def logout():
    """
    Logout the current user.
    Note: JWT tokens are stateless, so this is mainly for client-side cleanup.
    The client should discard the token.
    """
    return {"message": "Logged out successfully"}
