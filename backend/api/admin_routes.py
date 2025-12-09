"""
Admin API routes: user management, token tracking, and system stats.
"""
from datetime import datetime
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from database import get_db
from models import User, UserPreferences, EquationTab, EquationSet, RegistrationToken
from auth import get_admin_user

router = APIRouter(prefix="/admin", tags=["admin"])


# ============== Response Models ==============

class UserListItem(BaseModel):
    id: int
    username: str
    is_admin: bool
    created_at: datetime
    last_active: datetime
    equation_tab_count: int
    equation_set_count: int


class TokenStatus(BaseModel):
    token: str
    is_available: bool
    used_by_username: str | None
    used_at: datetime | None


class AdminStatsResponse(BaseModel):
    total_users: int
    regular_users: int
    max_users: int
    available_tokens: int
    total_equation_tabs: int
    total_equation_sets: int


# ============== Routes ==============

@router.get("/users", response_model=List[UserListItem])
async def list_users(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    List all registered users with their stats.
    Admin only.
    """
    users = db.query(User).order_by(User.created_at.desc()).all()
    
    result = []
    for user in users:
        tab_count = db.query(EquationTab).filter(EquationTab.user_id == user.id).count()
        set_count = db.query(EquationSet).join(EquationTab).filter(
            EquationTab.user_id == user.id
        ).count()
        
        result.append({
            "id": user.id,
            "username": user.username,
            "is_admin": user.is_admin,
            "created_at": user.created_at,
            "last_active": user.last_active,
            "equation_tab_count": tab_count,
            "equation_set_count": set_count
        })
    
    return result


@router.delete("/users/{user_id}")
async def delete_user(
    user_id: int,
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Delete a user account.
    This frees up their registration token for reuse.
    Admin only. Cannot delete admin accounts.
    """
    user = db.query(User).filter(User.id == user_id).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )
    
    if user.is_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Cannot delete admin accounts"
        )
    
    # Free up the registration token
    token = db.query(RegistrationToken).filter(
        RegistrationToken.used_by_user_id == user_id
    ).first()
    if token:
        token.used_by_user_id = None
        token.used_at = None
    
    # Delete user (cascades to preferences, tabs, and sets)
    db.delete(user)
    db.commit()
    
    return {"message": f"User '{user.username}' deleted successfully"}


@router.get("/tokens", response_model=List[TokenStatus])
async def get_token_status(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get the status of all registration tokens.
    Admin only.
    """
    tokens = db.query(RegistrationToken).all()
    
    result = []
    for token in tokens:
        username = None
        if token.used_by_user_id:
            user = db.query(User).filter(User.id == token.used_by_user_id).first()
            if user:
                username = user.username
        
        result.append({
            "token": token.token,
            "is_available": token.used_by_user_id is None,
            "used_by_username": username,
            "used_at": token.used_at
        })
    
    return result


@router.get("/stats", response_model=AdminStatsResponse)
async def get_admin_stats(
    admin: User = Depends(get_admin_user),
    db: Session = Depends(get_db)
):
    """
    Get system statistics.
    Admin only.
    """
    total_users = db.query(User).count()
    regular_users = db.query(User).filter(User.is_admin == False).count()
    available_tokens = db.query(RegistrationToken).filter(
        RegistrationToken.used_by_user_id.is_(None)
    ).count()
    total_tabs = db.query(EquationTab).count()
    total_sets = db.query(EquationSet).count()
    
    return {
        "total_users": total_users,
        "regular_users": regular_users,
        "max_users": 10,
        "available_tokens": available_tokens,
        "total_equation_tabs": total_tabs,
        "total_equation_sets": total_sets
    }
