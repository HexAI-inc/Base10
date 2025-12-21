#!/usr/bin/env python3
"""
Manual script to fix userrole enum data mismatch in production.
Run this script in the production environment to fix the enum issue.
"""

import os
import sys
import psycopg2
from psycopg2 import sql

def fix_userrole_enum():
    """Fix the userrole enum data mismatch."""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)

    # Parse the database URL
    # Expected format: postgresql://user:password@host:port/database
    try:
        # Simple parsing - you might need to adjust based on your URL format
        parts = database_url.replace('postgresql://', '').split('@')
        user_pass = parts[0].split(':')
        host_db = parts[1].split('/')

        user = user_pass[0]
        password = user_pass[1]
        host_port = host_db[0].split(':')
        host = host_port[0]
        port = host_port[1] if len(host_port) > 1 else '5432'
        database = host_db[1]

        conn = psycopg2.connect(
            host=host,
            port=port,
            database=database,
            user=user,
            password=password
        )
        conn.autocommit = True
        cursor = conn.cursor()

        print("🔧 Fixing userrole enum data mismatch...")

        # 1. Convert role column to VARCHAR temporarily
        print("1. Converting role column to VARCHAR...")
        cursor.execute("ALTER TABLE users ALTER COLUMN role TYPE VARCHAR(20) USING role::text")

        # 2. Drop the existing enum
        print("2. Dropping existing userrole enum...")
        cursor.execute("DROP TYPE IF EXISTS userrole CASCADE")

        # 3. Create the enum with correct lowercase values
        print("3. Creating new userrole enum...")
        cursor.execute("CREATE TYPE userrole AS ENUM ('student', 'teacher', 'admin', 'moderator')")

        # 4. Normalize existing data
        print("4. Normalizing existing user role data...")
        cursor.execute("""
            UPDATE users SET role = CASE
                WHEN LOWER(COALESCE(role, '')) = 'student' THEN 'student'
                WHEN LOWER(COALESCE(role, '')) = 'teacher' THEN 'teacher'
                WHEN LOWER(COALESCE(role, '')) = 'admin' THEN 'admin'
                WHEN LOWER(COALESCE(role, '')) = 'administrator' THEN 'admin'
                WHEN LOWER(COALESCE(role, '')) = 'moderator' THEN 'moderator'
                WHEN COALESCE(role, '') = 'STUDENT' THEN 'student'
                WHEN COALESCE(role, '') = 'TEACHER' THEN 'teacher'
                WHEN COALESCE(role, '') = 'ADMIN' THEN 'admin'
                WHEN COALESCE(role, '') = 'MODERATOR' THEN 'moderator'
                ELSE 'student'
            END WHERE role IS NOT NULL OR role = ''
        """)

        # 5. Convert back to enum
        print("5. Converting role column back to enum...")
        cursor.execute("ALTER TABLE users ALTER COLUMN role TYPE userrole USING role::userrole")

        cursor.close()
        conn.close()

        print("✅ Userrole enum data mismatch fixed successfully!")
        print("🔄 Please restart your application to apply the changes.")

    except Exception as e:
        print(f"❌ Error fixing userrole enum: {e}")
        sys.exit(1)

if __name__ == "__main__":
    fix_userrole_enum()