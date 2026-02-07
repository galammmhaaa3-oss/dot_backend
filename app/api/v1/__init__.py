from fastapi import APIRouter
from app.api.v1 import auth, users, rides, deliveries, drivers

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(rides.router, prefix="/rides", tags=["Rides"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
