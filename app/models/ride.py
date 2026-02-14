import uuid
from sqlalchemy import Column, String, Float, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class RideStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class Ride(Base):
    __tablename__ = "rides"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    assigned_driver_id = Column(UUID(as_uuid=True), ForeignKey("drivers.id"), nullable=True, index=True)
    driver_response_deadline = Column(DateTime, nullable=True)
    
    # Pickup location
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    pickup_address = Column(String, nullable=False)
    
    # Destination location
    destination_lat = Column(Float, nullable=False)
    destination_lng = Column(Float, nullable=False)
    destination_address = Column(String, nullable=False)
    
    # Pricing
    distance_km = Column(Float, nullable=False)
    estimated_price = Column(Float, nullable=False)
    final_price = Column(Float, nullable=True)
    
    # Status
    status = Column(SQLEnum(RideStatus), default=RideStatus.PENDING, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="rides", foreign_keys=[user_id])
