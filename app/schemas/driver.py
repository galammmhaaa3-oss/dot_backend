from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# Driver schemas
class DriverRegister(BaseModel):
    driver_type: str = Field(..., pattern="^(taxi|delivery)$")
    
    # Personal Info
    name: str = Field(..., min_length=3)
    national_id: str = Field(..., min_length=11, max_length=11)
    phone: str = Field(..., min_length=10, max_length=10)
    phone_secondary: Optional[str] = Field(None, min_length=10, max_length=10)
    age: int = Field(..., ge=18, le=70)
    
    # Documents
    national_id_photo: str
    license_photo: str
    selfie_with_id_photo: str
    
    # Vehicle
    vehicle_type: str
    vehicle_brand: Optional[str] = None
    vehicle_model: Optional[str] = None
    vehicle_number: str = Field(..., min_length=3)
    vehicle_photo: str


class DriverResponse(BaseModel):
    id: UUID
    user_id: UUID
    driver_type: str
    
    # Personal Info
    name: str
    national_id: str
    phone: str
    phone_secondary: Optional[str]
    age: int
    
    # Documents
    national_id_photo: str
    license_photo: str
    selfie_with_id_photo: str
    
    # Vehicle
    vehicle_type: str
    vehicle_brand: Optional[str]
    vehicle_model: Optional[str]
    vehicle_number: str
    vehicle_photo: str
    
    # Status
    status: str
    rejection_reason: Optional[str]
    
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True


class DriverStatusResponse(BaseModel):
    status: str
    rejection_reason: Optional[str] = None
    created_at: datetime
