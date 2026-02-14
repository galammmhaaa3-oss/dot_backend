from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from typing import Optional
import os
import uuid
import shutil
from pathlib import Path

from app.database import get_db
from app.schemas import DriverRegister, DriverResponse, DriverStatusResponse
from app.models import User, Driver, DriverType, DriverStatus, VehicleType
from app.api.deps import get_current_active_user

router = APIRouter()

# Upload directory
UPLOAD_DIR = Path("uploads/drivers")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


@router.post("/upload-document", status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload a driver document (photo) - requires auth."""
    return await _upload_file(file, str(current_user.id))


@router.post("/upload-public", status_code=status.HTTP_201_CREATED)
async def upload_document_public(
    file: UploadFile = File(...),
):
    """Upload a driver document (photo) - public for registration."""
    # Use a temp folder for unregistered users
    return await _upload_file(file, "temp")


async def _upload_file(file: UploadFile, user_folder: str):
    """Internal function to handle file upload."""
    # Validate file type
    allowed_types = ["image/jpeg", "image/jpg", "image/png"]
    if file.content_type not in allowed_types:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only JPEG and PNG images are allowed"
        )
    
    # Validate file size (5MB max)
    file.file.seek(0, 2)  # Seek to end
    file_size = file.file.tell()
    file.file.seek(0)  # Reset to beginning
    
    if file_size > 5 * 1024 * 1024:  # 5MB
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File size must be less than 5MB"
        )
    
    # Generate unique filename
    file_extension = file.filename.split(".")[-1]
    unique_filename = f"{uuid.uuid4()}.{file_extension}"
    
    # Create user directory
    user_dir = UPLOAD_DIR / user_folder
    user_dir.mkdir(parents=True, exist_ok=True)
    
    # Save file
    file_path = user_dir / unique_filename
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    
    # Return relative URL
    file_url = f"/uploads/drivers/{user_folder}/{unique_filename}"
    
    return {"url": file_url, "filename": unique_filename}


@router.post("/register", response_model=DriverResponse, status_code=status.HTTP_201_CREATED)
def register_driver(
    driver_data: DriverRegister,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Register as a driver."""
    # Check if user already has a driver profile
    existing_driver = db.query(Driver).filter(
        (Driver.user_id == current_user.id) |
        (Driver.national_id == driver_data.national_id) |
        (Driver.phone == driver_data.phone)
    ).first()
    
    if existing_driver:
        if existing_driver.status == DriverStatus.APPROVED:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="لديك طلب مقبول بالفعل"
            )
        elif existing_driver.status == DriverStatus.PENDING:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="لديك طلب قيد المراجعة"
            )
        elif existing_driver.status == DriverStatus.REJECTED:
            # Allow re-registration by deleting old rejected application
            db.delete(existing_driver)
            db.commit()
    
    # Create driver profile
    new_driver = Driver(
        user_id=current_user.id,
        driver_type=DriverType(driver_data.driver_type),
        name=driver_data.name,
        national_id=driver_data.national_id,
        phone=driver_data.phone,
        phone_secondary=driver_data.phone_secondary,
        age=driver_data.age,
        national_id_photo=driver_data.national_id_photo,
        license_photo=driver_data.license_photo,
        selfie_with_id_photo=driver_data.selfie_with_id_photo,
        vehicle_type=VehicleType(driver_data.vehicle_type),
        vehicle_brand=driver_data.vehicle_brand,
        vehicle_model=driver_data.vehicle_model,
        vehicle_number=driver_data.vehicle_number,
        vehicle_photo=driver_data.vehicle_photo,
    )
    
    db.add(new_driver)
    db.commit()
    db.refresh(new_driver)
    
    return new_driver


@router.get("/me", response_model=DriverResponse)
def get_driver_profile(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get current driver profile."""
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Driver profile not found"
        )
    
    return driver


@router.get("/status", response_model=DriverStatusResponse)
def get_driver_status(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get driver application status."""
    driver = db.query(Driver).filter(Driver.user_id == current_user.id).first()
    
    if not driver:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No driver application found"
        )
    
    return {
        "status": driver.status,
        "rejection_reason": driver.rejection_reason,
        "created_at": driver.created_at
    }
