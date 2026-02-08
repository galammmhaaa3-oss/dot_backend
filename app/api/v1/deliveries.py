from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from uuid import UUID

from app.database import get_db
from app.schemas import DeliveryCreate, DeliveryResponse, DeliveryStatusUpdate
from app.models import User, Delivery, DeliveryStatus
from app.api.deps import get_current_active_user
from app.utils.location import calculate_distance
from app.core.pricing import calculate_delivery_price

router = APIRouter()


@router.post("", response_model=DeliveryResponse, status_code=status.HTTP_201_CREATED)
def create_delivery(
    delivery_data: DeliveryCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new delivery request."""
    # Calculate distance
    distance_km = calculate_distance(
        delivery_data.pickup_lat,
        delivery_data.pickup_lng,
        delivery_data.delivery_lat,
        delivery_data.delivery_lng
    )
    
    # Calculate pricing
    pricing = calculate_delivery_price(
        distance_km,
        delivery_data.driver_pays,
        delivery_data.product_amount
    )
    
    # Create delivery
    new_delivery = Delivery(
        user_id=current_user.id,
        order_type=delivery_data.order_type,
        pickup_lat=delivery_data.pickup_lat,
        pickup_lng=delivery_data.pickup_lng,
        pickup_address=delivery_data.pickup_address,
        pickup_details=delivery_data.pickup_details,
        sender_name=delivery_data.sender_name,
        delivery_lat=delivery_data.delivery_lat,
        delivery_lng=delivery_data.delivery_lng,
        delivery_address=delivery_data.delivery_address,
        delivery_details=delivery_data.delivery_details,
        receiver_name=delivery_data.receiver_name,
        receiver_phone=delivery_data.receiver_phone,
        receiver_national_id=delivery_data.receiver_national_id,
        driver_pays=delivery_data.driver_pays,
        product_amount=delivery_data.product_amount,
        distance_km=distance_km,
        delivery_fee=pricing["delivery_fee"],
        total_cost=pricing["total_cost"]
    )
    
    db.add(new_delivery)
    db.commit()
    db.refresh(new_delivery)
    
    return new_delivery


@router.get("/{delivery_id}", response_model=DeliveryResponse)
def get_delivery(
    delivery_id: UUID,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get delivery details."""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    # Check if user owns this delivery
    if delivery.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to access this delivery"
        )
    
    return delivery


@router.get("", response_model=List[DeliveryResponse])
def get_user_deliveries(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db),
    skip: int = 0,
    limit: int = 20
):
    """Get user's delivery history."""
    deliveries = db.query(Delivery).filter(
        Delivery.user_id == current_user.id
    ).order_by(Delivery.created_at.desc()).offset(skip).limit(limit).all()
    
    return deliveries


@router.patch("/{delivery_id}/status", response_model=DeliveryResponse)
def update_delivery_status(
    delivery_id: UUID,
    status_update: DeliveryStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update delivery status."""
    delivery = db.query(Delivery).filter(Delivery.id == delivery_id).first()
    
    if not delivery:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Delivery not found"
        )
    
    # Check if user owns this delivery
    if delivery.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to update this delivery"
        )
    
    # Update status
    delivery.status = DeliveryStatus(status_update.status)
    
    db.commit()
    db.refresh(delivery)
    
    return delivery
