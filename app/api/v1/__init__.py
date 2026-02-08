from fastapi import APIRouter
from app.api.v1 import auth, users, rides, deliveries, drivers, admin, setup, driver_status

api_router = APIRouter()

# Include sub-routers
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(rides.router, prefix="/rides", tags=["Rides"])
api_router.include_router(deliveries.router, prefix="/deliveries", tags=["Deliveries"])
api_router.include_router(drivers.router, prefix="/drivers", tags=["Drivers"])
api_router.include_router(driver_status.router, prefix="/driver-status", tags=["Driver Status"])
api_router.include_router(admin.router, prefix="/admin", tags=["Admin"])
api_router.include_router(setup.router, prefix="/setup", tags=["Setup"])
