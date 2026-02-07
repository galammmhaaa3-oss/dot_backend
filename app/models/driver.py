import uuid
from sqlalchemy import Column, String, Integer, Enum as SQLEnum, ForeignKey, DateTime
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class DriverType(str, enum.Enum):
    TAXI = "taxi"
    DELIVERY = "delivery"


class DriverStatus(str, enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class VehicleType(str, enum.Enum):
    # For Taxi
    SEDAN = "sedan"
    SUV = "suv"
    VAN = "van"
    
    # For Delivery
    MOTORCYCLE = "motorcycle"
    BICYCLE = "bicycle"
    CAR = "car"


class Driver(Base):
    __tablename__ = "drivers"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Driver Type
    driver_type = Column(SQLEnum(DriverType), nullable=False)
    
    # Personal Information
    name = Column(String, nullable=False)
    national_id = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    phone_secondary = Column(String, nullable=True)
    age = Column(Integer, nullable=False)
    
    # Documents (URLs to uploaded files)
    national_id_photo = Column(String, nullable=False)
    license_photo = Column(String, nullable=False)
    selfie_with_id_photo = Column(String, nullable=False)
    
    # Vehicle Information
    vehicle_type = Column(SQLEnum(VehicleType), nullable=False)
    vehicle_brand = Column(String, nullable=True)
    vehicle_model = Column(String, nullable=True)
    vehicle_number = Column(String, nullable=False)
    vehicle_photo = Column(String, nullable=False)
    
    # Status
    status = Column(SQLEnum(DriverStatus), default=DriverStatus.PENDING, nullable=False, index=True)
    rejection_reason = Column(String, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", backref="driver_profile")
