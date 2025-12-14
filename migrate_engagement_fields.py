"""
Database migration to add engagement tracking fields.

Run with:
    alembic revision --autogenerate -m "Add engagement fields"
    alembic upgrade head

Or manually run this script for quick testing:
    python migrate_engagement_fields.py
"""
from sqlalchemy import text
from app.db.session import engine

def migrate():
    """Add new fields to User and Attempt tables."""
    
    with engine.connect() as conn:
        print("🔄 Adding engagement fields to User table...")
        
        try:
            # Add has_app_installed field
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS has_app_installed BOOLEAN DEFAULT FALSE;
            """))
            print("  ✅ Added has_app_installed")
            
            # Add study_streak field
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS study_streak INTEGER DEFAULT 0;
            """))
            print("  ✅ Added study_streak")
            
            # Add last_activity_date field
            conn.execute(text("""
                ALTER TABLE users 
                ADD COLUMN IF NOT EXISTS last_activity_date TIMESTAMP WITH TIME ZONE;
            """))
            print("  ✅ Added last_activity_date")
            
            print("\n🔄 Adding skipped field to Attempt table...")
            
            # Add skipped field
            conn.execute(text("""
                ALTER TABLE attempts 
                ADD COLUMN IF NOT EXISTS skipped BOOLEAN DEFAULT FALSE;
            """))
            print("  ✅ Added skipped")
            
            conn.commit()
            print("\n✅ Migration completed successfully!")
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            raise


def rollback():
    """Remove added fields (for development only)."""
    
    with engine.connect() as conn:
        print("🔄 Rolling back engagement fields...")
        
        try:
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS has_app_installed;"))
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS study_streak;"))
            conn.execute(text("ALTER TABLE users DROP COLUMN IF EXISTS last_activity_date;"))
            conn.execute(text("ALTER TABLE attempts DROP COLUMN IF EXISTS skipped;"))
            
            conn.commit()
            print("✅ Rollback completed!")
            
        except Exception as e:
            print(f"❌ Rollback failed: {e}")
            conn.rollback()
            raise


if __name__ == "__main__":
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        rollback()
    else:
        migrate()
