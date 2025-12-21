#!/usr/bin/env python3
"""
Manual script to fix userrole enum data mismatch in production.
Run this script in the production environment to fix the enum issue.
"""

import os
import sys
import psycopg2
from psycopg2 import sql
from urllib.parse import urlparse

def fix_userrole_enum():
    """Fix the userrole enum data mismatch."""

    # Get database URL from environment
    database_url = os.getenv('DATABASE_URL')
    if not database_url:
        print("❌ DATABASE_URL environment variable not set")
        sys.exit(1)

    # Parse the database URL properly
    try:
        parsed = urlparse(database_url)
        
        user = parsed.username
        password = parsed.password
        host = parsed.hostname
        port = parsed.port or 5432
        database = parsed.path.lstrip('/')  # Remove leading slash
        
        # Handle query parameters (like sslmode)
        sslmode = None
        if parsed.query:
            params = dict(param.split('=') for param in parsed.query.split('&'))
            sslmode = params.get('sslmode')

        # Connect to database
        conn_params = {
            'host': host,
            'port': port,
            'database': database,
            'user': user,
            'password': password
        }
        
        if sslmode:
            conn_params['sslmode'] = sslmode

        conn = psycopg2.connect(**conn_params)
        conn.autocommit = True
        cursor = conn.cursor()

        print(f"🔧 Connected to database: {database}")
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