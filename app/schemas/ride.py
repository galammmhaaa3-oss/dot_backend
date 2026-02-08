from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# Ride schemas
class RideCreate(BaseModel):
    pickup_lat: float = Field(..., ge=-90, le=90)
    pickup_lng: float = Field(..., ge=-180, le=180)
    pickup_address: str
    destination_lat: float = Field(..., ge=-90, le=90)
    destination_lng: float = Field(..., ge=-180, le=180)
    destination_address: str


class RideResponse(BaseModel):
    id: UUID
    user_id: UUID
    driver_id: Optional[UUID]
    pickup_lat: float
    pickup_lng: float
    pickup_address: str
    destination_lat: float
    destination_lng: float
    destination_address: str
    distance_km: float
    estimated_price: float
    final_price: Optional[float]
    status: str
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class RideStatusUpdate(BaseModel):
    status: str = Field(..., pattern="^(pending|matched|in_progress|completed|cancelled)$")
