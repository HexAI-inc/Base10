#!/usr/bin/env python3
"""
Fix userrole enum mismatch in production database.
This script ensures the database enum has lowercase values matching the Python enum.
"""
import os
import psycopg2
from urllib.parse import urlparse

# Get database URL from environment
DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    exit(1)

# Parse the database URL
parsed = urlparse(DATABASE_URL)
if parsed.scheme != 'postgresql':
    print("❌ Only PostgreSQL databases are supported")
    exit(1)

def fix_userrole_enum():
    """Fix the userrole enum to have lowercase values."""
    try:
        # Connect to database
        conn = psycopg2.connect(DATABASE_URL)
        conn.autocommit = True
        cursor = conn.cursor()

        print("🔧 Fixing userrole enum...")

        # 1. Convert role column to VARCHAR temporarily
        print("1. Converting role column to VARCHAR...")
        cursor.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20) USING role::text")

        # 2. Drop existing enum if it exists
        print("2. Dropping existing userrole enum...")
        cursor.execute("DROP TYPE IF EXISTS userrole CASCADE")

        # 3. Create enum with correct lowercase values
        print("3. Creating new userrole enum with lowercase values...")
        cursor.execute("CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin', 'moderator')")

        # 4. Normalize existing data to match enum values
        print("4. Normalizing existing user role data...")
        cursor.execute("""
            UPDATE users SET role = CASE
                WHEN LOWER(COALESCE(role, '')) = 'student' THEN 'student'
                WHEN LOWER(COALESCE(role, '')) = 'teacher' THEN 'teacher'
                WHEN LOWER(COALESCE(role, '')) = 'admin' THEN 'admin'
                WHEN LOWER(COALESCE(role, '')) = 'administrator' THEN 'admin'
                WHEN LOWER(COALESCE(role, '')) = 'moderator' THEN 'moderator'
                WHEN UPPER(COALESCE(role, '')) = 'STUDENT' THEN 'student'
                WHEN UPPER(COALESCE(role, '')) = 'TEACHER' THEN 'teacher'
                WHEN UPPER(COALESCE(role, '')) = 'ADMIN' THEN 'admin'
                WHEN UPPER(COALESCE(role, '')) = 'MODERATOR' THEN 'moderator'
                ELSE 'student'  -- Default to student for any invalid values
            END WHERE role IS NOT NULL OR role = ''
        """)

        # 5. Convert back to enum
        print("5. Converting role column back to enum...")
        cursor.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")

        print("✅ UserRole enum fixed successfully!")

        # Verify the fix
        print("6. Verifying the fix...")
        cursor.execute("SELECT role, COUNT(*) FROM users GROUP BY role ORDER BY role")
        results = cursor.fetchall()
        print("Role distribution:")
        for role, count in results:
            print(f"  {role}: {count} users")

        cursor.close()
        conn.close()

    except Exception as e:
        print(f"❌ Error fixing userrole enum: {e}")
        exit(1)

if __name__ == "__main__":
    fix_userrole_enum()