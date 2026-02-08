"""
Database Migration Script for Real-Time Driver-User Sync

This script adds the necessary columns to support:
- Driver online status (online, in_ride, paused, offline)
- Driver location tracking (lat, lng, last_update)
- Ride assignment (assigned_driver_id, driver_response_deadline)

Run this script ONCE after deploying the updated backend code.
"""

from app.database import SessionLocal, engine
from app.models import Base
from sqlalchemy import text

def run_migration():
    """Run database migration."""
    db = SessionLocal()
    
    try:
        print("🔄 Starting database migration...")
        
        # Add columns to drivers table
        print("📝 Adding columns to drivers table...")
        
        migrations = [
            # Driver online status and location
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS online_status VARCHAR(20) DEFAULT 'offline'",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS current_location_lat FLOAT",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS current_location_lng FLOAT",
            "ALTER TABLE drivers ADD COLUMN IF NOT EXISTS last_location_update TIMESTAMP",
            
            # Ride assignment
            "ALTER TABLE rides ADD COLUMN IF NOT EXISTS assigned_driver_id UUID REFERENCES drivers(id)",
            "ALTER TABLE rides ADD COLUMN IF NOT EXISTS driver_response_deadline TIMESTAMP",
            
            # Create indexes for performance
            "CREATE INDEX IF NOT EXISTS idx_drivers_online_status ON drivers(online_status)",
            "CREATE INDEX IF NOT EXISTS idx_drivers_location ON drivers(current_location_lat, current_location_lng)",
            "CREATE INDEX IF NOT EXISTS idx_rides_assigned_driver ON rides(assigned_driver_id)",
        ]
        
        for migration in migrations:
            try:
                db.execute(text(migration))
                print(f"✅ {migration[:50]}...")
            except Exception as e:
                print(f"⚠️  Migration already applied or error: {str(e)[:100]}")
        
        db.commit()
        print("✅ Migration completed successfully!")
        
    except Exception as e:
        print(f"❌ Migration failed: {str(e)}")
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("=" * 60)
    print("DOT Backend - Database Migration")
    print("=" * 60)
    run_migration()
    print("=" * 60)
    print("Migration complete! You can now use the new features.")
    print("=" * 60)
