from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas import RideCreate, RideResponse, RideStatusUpdate
from app.models import User, Ride, RideStatus
from app.api.deps import get_current_active_user
from app.utils.location import calculate_distance
from app.core.pricing import calculate_ride_price

router = APIRouter()


@router.post("", response_model=RideResponse, status_code=status.HTTP_201_CREATED)
def create_ride(
    ride_data: RideCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new ride request."""
    # Calculate distance
    distance_km = calculate_distance(
        ride_data.pickup_lat,
        ride_data.pickup_lng,
        ride_data.destination_lat,
        ride_data.destination_lng
    )
    
    # Calculate price
    estimated_price = calculate_ride_price(distance_km)
    
    # Create ride
    new_ride = Ride(
        user_id=current_user.id,
        pickup_lat=ride_data.pickup_lat,
        pickup_lng=ride_data.pickup_lng,
        pickup_address=ride_data.pickup_address,
        destination_lat=ride_data.destination_lat,
        destination_lng=ride_data.destination_lng,
        destination_address=ride_data.destination_address,
        distance_km=distance_km,
        estimated_price=estimated_price
    )
    
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    return new_ride


@router.get("/{ride_id}", response_model=RideResponse)
def get_ride(
    ride_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get ride details."""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if user owns this ride
    if ride.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this ride"
        )
    
    return ride


@router.get("", response_model=List[RideResponse])
def get_user_rides(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Get user's ride history."""
    rides = db.query(Ride).filter(
        Ride.user_id == current_user.id
    ).order_by(Ride.created_at.desc()).offset(skip).limit(limit).all()
    
    return rides


@router.patch("/{ride_id}/status", response_model=RideResponse)
def update_ride_status(
    ride_id: UUID,
    status_update: RideStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update ride status."""
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Check if user owns this ride
    if ride.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this ride"
        )
    
    # Update status
    ride.status = RideStatus(status_update.status)
    
    db.commit()
    db.refresh(ride)
    
    return ride
