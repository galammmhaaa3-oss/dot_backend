from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas import UserResponse, UserUpdate
from app.models import User
from app.api.deps import get_current_active_user

router = APIRouter()


@router.get("/me", response_model=UserResponse)
def get_current_user_profile(current_user: User = Depends(get_current_active_user)):
    """Get current user profile."""
    return current_user


@router.put("/me", response_model=UserResponse)
def update_current_user_profile(
    user_update: UserUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update current user profile."""
    if user_update.name is not None:
        current_user.name = user_update.name
    
    if user_update.national_id is not None:
        current_user.national_id = user_update.national_id
    
    db.commit()
    db.refresh(current_user)
    
    return current_user
