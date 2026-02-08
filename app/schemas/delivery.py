from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# Delivery schemas
class DeliveryCreate(BaseModel):
    order_type: str
    
    # Pickup
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lng: float = Field(..., ge=-180, le=180)
    pickup_address: str
    pickup_details: Optional[str] = None
    sender_name: str = Field(..., min_length=3)
    
    # Delivery
    delivery_lat: float = Field(..., ge=-90, le=90)
    delivery_lng: float = Field(..., ge=-180, le=180)
    delivery_address: str
    delivery_details: Optional[str] = None
    receiver_name: str = Field(..., min_length=3)
    receiver_phone: str = Field(..., min_length=10, max_length=10)
    receiver_national_id: str = Field(..., min_length=11, max_length=11)
    
    # Payment
    driver_pays: bool = False
    product_amount: float = Field(default=0, ge=0)


class DeliveryResponse(BaseModel):
    id: UUID
    user_id: UUID
    driver_id: Optional[UUID]
    order_type: str
    
    # Pickup
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    pickup_details: Optional[str]
    sender_name: str
    
    # Delivery
    delivery_lat: float
    delivery_lng: float
    delivery_address: str
    delivery_details: Optional[str]
    receiver_name: str
    receiver_phone: str
    receiver_national_id: str
    
    # Payment
    driver_pays: bool
    product_amount: float
    
    # Pricing
    distance_km: float
    delivery_fee: float
    total_cost: float
    
    # Status
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DeliveryStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|matched|picked_up|in_transit|delivered|cancelled)$")
