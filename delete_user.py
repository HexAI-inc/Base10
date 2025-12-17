"""Script to delete a specific user from the database."""
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models.user import User
from app.core.config import settings

def delete_user_by_email(email: str):
    """Delete user by email address."""
    # Create database connection
    engine = create_engine(settings.DATABASE_URL)
    SessionLocal = sessionmaker(bind=engine)
    db = SessionLocal()
    
    try:
        # Find user
        user = db.query(User).filter(User.email == email).first()
        
        if not user:
            print(f"❌ User with email '{email}' not found")
            return False
        
        # Display user info
        print(f"\n🔍 Found user:")
        print(f"   ID: {user.id}")
        print(f"   Email: {user.email}")
        print(f"   Username: {user.username}")
        print(f"   Full Name: {user.full_name}")
        print(f"   Role: {user.role}")
        print(f"   Created: {user.created_at}")
        
        # Confirm deletion
        confirm = input(f"\n⚠️  Are you sure you want to DELETE this user? (yes/no): ")
        
        if confirm.lower() != 'yes':
            print("❌ Deletion cancelled")
            return False
        
        # Delete user
        db.delete(user)
        db.commit()
        
        print(f"✅ Successfully deleted user: {email}")
        return True
        
    except Exception as e:
        print(f"❌ Error deleting user: {e}")
        db.rollback()
        return False
    finally:
        db.close()


if __name__ == "__main__":
    email = "cjalloh25@gmail.com"
    
    if len(sys.argv) > 1:
        email = sys.argv[1]
    
    print(f"🗑️  Attempting to delete user: {email}")
    delete_user_by_email(email)
