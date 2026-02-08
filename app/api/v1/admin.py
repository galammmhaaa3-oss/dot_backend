from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime

from app.database import get_db
from app.schemas import DriverResponse
from app.models import User, Driver, DriverStatus
from app.api.deps import get_current_active_user

router = APIRouter()


def is_admin(current_user: User) -> bool:
    """Check if user is admin."""
    return current_user.role == "admin"


@router.get("/drivers/pending", response_model=List[DriverResponse])
def get_pending_drivers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all pending driver applications (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    pending_drivers = db.query(Driver).filter(
        Driver.status == DriverStatus.PENDING
    ).all()
    
    return pending_drivers


@router.get("/drivers/approved", response_model=List[DriverResponse])
def get_approved_drivers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all approved drivers (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    approved_drivers = db.query(Driver).filter(
        Driver.status == DriverStatus.APPROVED
    ).all()
    
    return approved_drivers


@router.get("/drivers/rejected", response_model=List[DriverResponse])
def get_rejected_drivers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all rejected drivers (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    rejected_drivers = db.query(Driver).filter(
        Driver.status == DriverStatus.REJECTED
    ).all()
    
    return rejected_drivers


@router.post("/drivers/{driver_id}/approve")
def approve_driver(
    driver_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Approve driver application (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.status = DriverStatus.APPROVED
    driver.rejection_reason = None
    db.commit()
    
    return {"message": "Driver approved successfully", "driver_id": driver_id}


@router.post("/drivers/{driver_id}/reject")
def reject_driver(
    driver_id: str,
    reason: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Reject driver application with reason (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    if not reason or len(reason.strip()) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Rejection reason is required (minimum 3 characters)"
        )
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    driver.status = DriverStatus.REJECTED
    driver.rejection_reason = reason
    db.commit()
    
    return {"message": "Driver rejected", "driver_id": driver_id, "reason": reason}


@router.delete("/drivers/{driver_id}")
def delete_driver(
    driver_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a driver permanently (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    db.delete(driver)
    db.commit()
    
    return {"message": "Driver deleted successfully", "driver_id": driver_id}


@router.get("/drivers/{driver_id}", response_model=DriverResponse)
def get_driver_details(
    driver_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get specific driver details (Admin only)."""
    if not is_admin(current_user):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Admin access required"
        )
    
    driver = db.query(Driver).filter(Driver.id == driver_id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver not found"
        )
    
    return driver
