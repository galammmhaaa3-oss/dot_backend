import uuid
from sqlalchemy import Column, String, DateTime, Enum as SQLEnum
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.database import Base


class UserRole(str, enum.Enum):
    USER = "user"
    DRIVER = "driver"
    ADMIN = "admin"


class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    phone = Column(String, unique=True, nullable=False, index=True)
    name = Column(String, nullable=False)
    national_id = Column(String, nullable=True)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    password_hash = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    # Relationships
    rides = relationship("Ride", back_populates="user", foreign_keys="Ride.user_id")
    deliveries = relationship("Delivery", back_populates="user", foreign_keys="Delivery.user_id")
