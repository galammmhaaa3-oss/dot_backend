from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.config import settings
from app.api.v1 import api_router
from app.database import engine, Base

# Create database tables
Base.metadata.create_all(bind=engine)

# Create upload directory
Path("uploads/drivers").mkdir(parents=True, exist_ok=True)

# Create FastAPI app
app = FastAPI(
    title="DOT API",
    description="Backend API for DOT - خدمات التوصيل والنقل",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configure CORS
origins = settings.CORS_ORIGINS.split(",") if settings.CORS_ORIGINS != "*" else ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API router
app.include_router(api_router, prefix="/api/v1")

# Mount static files for uploads
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")


# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint for monitoring."""
    return {"status": "healthy", "service": "DOT API"}


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "Welcome to DOT API",
        "docs": "/docs",
        "health": "/health"
    }
