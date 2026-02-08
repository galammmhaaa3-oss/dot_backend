from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from datetime import datetime
from typing import Optional

from app.database import get_db
from app.models import Driver, DriverOnlineStatus
from app.api.deps import get_current_active_user
from app.models.user import User

router = APIRouter()


class DriverStatusUpdate(BaseModel):
    status: str  # online, in_ride, paused, offline
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class LocationUpdate(BaseModel):
    latitude: float
    longitude: float


@router.post("/status")
def update_driver_status(
    status_data: DriverStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update driver online status and optionally location."""
    # Get driver profile
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Validate status
    try:
        new_status = DriverOnlineStatus(status_data.status)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {[s.value for s in DriverOnlineStatus]}"
        )
    
    # Update status
    driver.online_status = new_status
    
    # Update location if provided
    if status_data.latitude is not None and status_data.longitude is not None:
        driver.current_location_lat = status_data.latitude
        driver.current_location_lng = status_data.longitude
        driver.last_location_update = datetime.utcnow()
    
    db.commit()
    db.refresh(driver)
    
    return {
        "message": "Status updated successfully",
        "status": driver.online_status.value,
        "location": {
            "lat": driver.current_location_lat,
            "lng": driver.current_location_lng
        } if driver.current_location_lat else None
    }


@router.post("/location")
def update_driver_location(
    location: LocationUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update driver location (called periodically when online)."""
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    driver.current_location_lat = location.latitude
    driver.current_location_lng = location.longitude
    driver.last_location_update = datetime.utcnow()
    
    db.commit()
    
    return {
        "message": "Location updated",
        "location": {
            "lat": driver.current_location_lat,
            "lng": driver.current_location_lng
        }
    }


@router.get("/me/status")
def get_driver_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current driver status and pending ride requests."""
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    return {
        "status": driver.online_status.value,
        "location": {
            "lat": driver.current_location_lat,
            "lng": driver.current_location_lng,
            "last_update": driver.last_location_update.isoformat() if driver.last_location_update else None
        },
        "pending_rides": []  # Will implement ride matching next
    }
