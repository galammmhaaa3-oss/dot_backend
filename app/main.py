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

# Startup event - Run migrations automatically
@app.on_event("startup")
async def startup_event():
    """Run database migrations on startup."""
    from sqlalchemy import text
    from app.database import SessionLocal
    
    db = SessionLocal()
    try:
        print("🔄 Running database migrations...")
        
        migrations = [
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS online_status VARCHAR(20) DEFAULT 'offline'",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS current_location_lat FLOAT",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS current_location_lng FLOAT",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS last_location_update TIMESTAMP",
            "ALTER TABLE rides ADD COLUMN IF NOT EXISTS assigned_driver_id UUID REFERENCES drivers(id)",
            "ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_response_deadline TIMESTAMP",
            "CREATE INDEX IF NOT EXISTS idx_drivers_online_status ON drivers(online_status)",
        ]
        
        for migration in migrations:
            try:
                db.execute(text(migration))
            except Exception:
                pass
        
        db.commit()
        print("✅ Migrations completed!")
    except Exception as e:
        print(f"❌ Migration error: {str(e)}")
        db.rollback()
    finally:
        db.close()

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
