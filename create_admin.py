"""
Script to create an admin user in the database.
Run this once to create your admin account.
"""
from app.database import SessionLocal
from app.models import User
from app.core.security import get_password_hash

def create_admin():
    db = SessionLocal()
    
    try:
        # Check if admin already exists
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print(f"⚠️ Admin already exists: {existing_admin.phone}")
            return
        
        # Create admin user
        admin_phone = input("Enter admin phone number (10 digits): ")
        admin_password = input("Enter admin password: ")
        admin_name = input("Enter admin name: ")
        
        admin_user = User(
            phone=admin_phone,
            name=admin_name,
            password_hash=get_password_hash(admin_password),
            role="admin"  # Set role as admin
        )
        
        db.add(admin_user)
        db.commit()
        db.refresh(admin_user)
        
        print(f"✅ Admin user created successfully!")
        print(f"   Phone: {admin_user.phone}")
        print(f"   Name: {admin_user.name}")
        print(f"   Role: {admin_user.role}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_admin()
