import uuid
from sqlalchemy import Column, String, Float, Boolean, DateTime, Enum as SQLEnum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class DeliveryStatus(str, enum.Enum):
    PENDING = "pending"
    MATCHED = "matched"
    PICKED_UP = "picked_up"
    IN_TRANSIT = "in_transit"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class Delivery(Base):
    __tablename__ = "deliveries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True)
    driver_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    
    # Order details
    order_type = Column(String, nullable=False)
    
    # Pickup location
    pickup_lat = Column(Float, nullable=False)
    pickup_lng = Column(Float, nullable=False)
    pickup_address = Column(String, nullable=False)
    pickup_details = Column(String, nullable=True)
    sender_name = Column(String, nullable=False)
    
    # Delivery location
    delivery_lat = Column(Float, nullable=False)
    delivery_lng = Column(Float, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_details = Column(String, nullable=True)
    receiver_name = Column(String, nullable=False)
    receiver_phone = Column(String, nullable=False)
    receiver_national_id = Column(String, nullable=False)
    
    # Payment
    driver_pays = Column(Boolean, default=False, nullable=False)
    product_amount = Column(Float, default=0, nullable=False)
    
    # Pricing
    distance_km = Column(Float, nullable=False)
    delivery_fee = Column(Float, nullable=False)
    total_cost = Column(Float, nullable=False)
    
    # Status
    status = Column(SQLEnum(DeliveryStatus), default=DeliveryStatus.PENDING, nullable=False, index=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="deliveries", foreign_keys=[user_id])
