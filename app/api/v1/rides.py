from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime, timedelta
import math

from app.database import get_db
from app.models import Ride, RideStatus, Driver, DriverOnlineStatus, DriverType
from app.models.user import User
from app.api.deps import get_current_active_user
from app.schemas import RideResponse

router = APIRouter()


class RideRequestCreate(BaseModel):
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    destination_lat: float
    destination_lng: float
    destination_address: str


class RideAcceptReject(BaseModel):
    ride_id: str
    action: str  # "accept" or "reject"


def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers using Haversine formula."""
    R = 6371  # Earth's radius in kilometers
    
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    a = math.sin(delta_lat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    return R * c


def calculate_price(distance_km: float) -> float:
    """Calculate ride price based on distance."""
    base_price = 5000  # 5000 SYP base fare
    price_per_km = 2000  # 2000 SYP per km
    return base_price + (distance_km * price_per_km)


@router.post("/request", response_model=RideResponse)
def request_ride(
    ride_request: RideRequestCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """User requests a new ride."""
    
    # Calculate distance and price
    distance_km = calculate_distance(
        ride_request.pickup_lat,
        ride_request.pickup_lng,
        ride_request.destination_lat,
        ride_request.destination_lng
    )
    estimated_price = calculate_price(distance_km)
    
    # Find nearest online driver
    online_drivers = db.query(Driver).filter(
        Driver.status == "approved",
        Driver.online_status == DriverOnlineStatus.ONLINE,
        Driver.driver_type == DriverType.TAXI,
        Driver.current_location_lat.isnot(None),
        Driver.current_location_lng.isnot(None)
    ).all()
    
    if not online_drivers:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No drivers available at the moment"
        )
    
    # Calculate distances and sort
    driver_distances = []
    for driver in online_drivers:
        dist = calculate_distance(
            ride_request.pickup_lat,
            ride_request.pickup_lng,
            driver.current_location_lat,
            driver.current_location_lng
        )
        driver_distances.append((driver, dist))
    
    # Sort by distance
    driver_distances.sort(key=lambda x: x[1])
    nearest_driver = driver_distances[0][0]
    
    # Create ride
    new_ride = Ride(
        user_id=current_user.id,
        driver_id=nearest_driver.user_id,
        assigned_driver_id=nearest_driver.id,
        pickup_lat=ride_request.pickup_lat,
        pickup_lng=ride_request.pickup_lng,
        pickup_address=ride_request.pickup_address,
        destination_lat=ride_request.destination_lat,
        destination_lng=ride_request.destination_lng,
        destination_address=ride_request.destination_address,
        distance_km=distance_km,
        estimated_price=estimated_price,
        status=RideStatus.PENDING,
        driver_response_deadline=datetime.utcnow() + timedelta(seconds=30)
    )
    
    db.add(new_ride)
    db.commit()
    db.refresh(new_ride)
    
    return new_ride


@router.get("/pending", response_model=List[RideResponse])
def get_pending_rides(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Driver gets pending ride requests assigned to them."""
    
    # Get driver profile
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Get pending rides assigned to this driver
    pending_rides = db.query(Ride).filter(
        Ride.assigned_driver_id == driver.id,
        Ride.status == RideStatus.PENDING,
        Ride.driver_response_deadline > datetime.utcnow()
    ).all()
    
    return pending_rides


@router.post("/{ride_id}/accept")
def accept_ride(
    ride_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Driver accepts a ride request."""
    
    # Get driver profile
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Get ride
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify ride is assigned to this driver
    if str(ride.assigned_driver_id) != str(driver.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This ride is not assigned to you"
        )
    
    # Check if still pending
    if ride.status != RideStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ride is no longer pending"
        )
    
    # Accept ride
    ride.status = RideStatus.MATCHED
    driver.online_status = DriverOnlineStatus.IN_RIDE
    
    db.commit()
    
    return {"message": "Ride accepted successfully", "ride_id": ride_id}


@router.post("/{ride_id}/reject")
def reject_ride(
    ride_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Driver rejects a ride request."""
    
    # Get driver profile
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    # Get ride
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify ride is assigned to this driver
    if str(ride.assigned_driver_id) != str(driver.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="This ride is not assigned to you"
        )
    
    # Find next nearest driver
    online_drivers = db.query(Driver).filter(
        Driver.id != driver.id,
        Driver.status == "approved",
        Driver.online_status == DriverOnlineStatus.ONLINE,
        Driver.driver_type == DriverType.TAXI,
        Driver.current_location_lat.isnot(None),
        Driver.current_location_lng.isnot(None)
    ).all()
    
    if online_drivers:
        # Calculate distances and find nearest
        driver_distances = []
        for next_driver in online_drivers:
            dist = calculate_distance(
                ride.pickup_lat,
                ride.pickup_lng,
                next_driver.current_location_lat,
                next_driver.current_location_lng
            )
            driver_distances.append((next_driver, dist))
        
        driver_distances.sort(key=lambda x: x[1])
        nearest_driver = driver_distances[0][0]
        
        # Reassign to next driver
        ride.assigned_driver_id = nearest_driver.id
        ride.driver_id = nearest_driver.user_id
        ride.driver_response_deadline = datetime.utcnow() + timedelta(seconds=30)
        db.commit()
        
        return {"message": "Ride reassigned to next driver"}
    else:
        # No drivers available, cancel ride
        ride.status = RideStatus.CANCELLED
        db.commit()
        
        return {"message": "No drivers available, ride cancelled"}


@router.get("/{ride_id}/status", response_model=RideResponse)
def get_ride_status(
    ride_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """User polls for ride status updates."""
    
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    # Verify user owns this ride
    if str(ride.user_id) != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied"
        )
    
    return ride


@router.post("/{ride_id}/start")
def start_ride(
    ride_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Driver starts the ride (picked up passenger)."""
    
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride or str(ride.assigned_driver_id) != str(driver.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    ride.status = RideStatus.IN_PROGRESS
    db.commit()
    
    return {"message": "Ride started"}


@router.post("/{ride_id}/complete")
def complete_ride(
    ride_id: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Driver completes the ride."""
    
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    ride = db.query(Ride).filter(Ride.id == ride_id).first()
    if not ride or str(ride.assigned_driver_id) != str(driver.id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ride not found"
        )
    
    ride.status = RideStatus.COMPLETED
    ride.final_price = ride.estimated_price
    driver.online_status = DriverOnlineStatus.ONLINE  # Back to online
    
    db.commit()
    
    return {"message": "Ride completed", "final_price": ride.final_price}
