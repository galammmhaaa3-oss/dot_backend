from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from uuid import UUID


# User schemas
class UserBase(BaseModel):
    phone: str = Field(..., min_length=8, max_length=15, description="Phone number")
    name: str = Field(..., min_length=3, max_length=100, description="User name")
    national_id: Optional[str] = Field(None, min_length=11, max_length=11, description="National ID (11 digits)")


class UserCreate(UserBase):
    password: str = Field(..., min_length=6, description="Password")


class UserLogin(BaseModel):
    national_id: str = Field(..., min_length=11, max_length=11, description="National ID")
    password: str = Field(..., min_length=6)


class UserUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=3)
    national_id: Optional[str] = Field(None, min_length=11, max_length=11)


class UserResponse(UserBase):
    id: UUID
    role: str
    created_at: datetime
    
    class Config:
        from_attributes = True
