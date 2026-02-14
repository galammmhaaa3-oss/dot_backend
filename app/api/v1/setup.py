from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.database import get_db
from app.models import User
from app.core.security import get_password_hash

router = APIRouter()


class AdminSetup(BaseModel):
    phone: str
    password: str
    name: str
    setup_key: str  # Secret key to prevent unauthorized access


class AdminReset(BaseModel):
    national_id: str
    phone: str
    password: str
    name: str
    setup_key: str


@router.post("/setup-admin")
def setup_admin(
    admin_data: AdminSetup,
    db: Session = Depends(get_db)
):
    """
    One-time endpoint to create admin user.
    Use setup_key='DOT_ADMIN_SETUP_2026' to authenticate.
    This endpoint should be disabled after first use.
    """
    
    # Simple security check
    if admin_data.setup_key != "DOT_ADMIN_SETUP_2026":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid setup key"
        )
    
    # Check if admin already exists
    existing_admin = db.query(User).filter(User.role == "admin").first()
    if existing_admin:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Admin already exists: {existing_admin.phone}"
        )
    
    # Validate phone
    if len(admin_data.phone) < 8 or len(admin_data.phone) > 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone must be 8-15 digits"
        )
    
    # Create admin user
    admin_user = User(
        phone=admin_data.phone,
        name=admin_data.name,
        password_hash=get_password_hash(admin_data.password),
        role="admin"
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return {
        "message": "✅ Admin user created successfully!",
        "phone": admin_user.phone,
        "name": admin_user.name,
        "role": admin_user.role,
        "note": "You can now login with these credentials. This endpoint is now disabled."
    }


@router.post("/reset-admin")
def reset_admin(
    admin_data: AdminReset,
    db: Session = Depends(get_db)
):
    """
    Reset endpoint to delete existing admin and create new one with national_id.
    Use setup_key='DOT_ADMIN_SETUP_2026' to authenticate.
    """
    
    # Security check
    if admin_data.setup_key != "DOT_ADMIN_SETUP_2026":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid setup key"
        )
    
    # Validate national_id (must be 11 digits)
    if len(admin_data.national_id) != 11 or not admin_data.national_id.isdigit():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="National ID must be exactly 11 digits"
        )
    
    # Validate phone
    if len(admin_data.phone) < 8 or len(admin_data.phone) > 15:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Phone must be 8-15 digits"
        )
    
    # Delete all existing admin users
    deleted_count = db.query(User).filter(User.role == "admin").delete()
    db.commit()
    
    # Create new admin user with national_id
    admin_user = User(
        national_id=admin_data.national_id,
        phone=admin_data.phone,
        name=admin_data.name,
        password_hash=get_password_hash(admin_data.password),
        role="admin"
    )
    
    db.add(admin_user)
    db.commit()
    db.refresh(admin_user)
    
    return {
        "message": "✅ Admin user reset successfully!",
        "deleted_admins": deleted_count,
        "national_id": admin_user.national_id,
        "phone": admin_user.phone,
        "name": admin_user.name,
        "role": admin_user.role,
        "note": "You can now login with national_id and password"
    }
