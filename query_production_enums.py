#!/usr/bin/env python3
"""
Query production database to check userrole enum values and user data.
Run this on your production server.
"""
import os
import psycopg2
from urllib.parse import urlparse

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("🔍 Checking production database enums and data...")
    print("=" * 50)
    
    # Check enum values
    print("\n1. Current userrole enum values:")
    cursor.execute("""
        SELECT enumtypid, enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid FROM pg_type WHERE typname = 'userrole'
        )
        ORDER BY enumsortorder
    """)
    
    results = cursor.fetchall()
    if results:
        for typid, label in results:
            print(f"   ✅ {label}")
    else:
        print("   ❌ No userrole enum found!")
    
    # Check user roles in database
    print("\n2. User roles in database:")
    cursor.execute("""
        SELECT role, COUNT(*) as count 
        FROM users 
        GROUP BY role 
        ORDER BY count DESC
    """)
    
    user_roles = cursor.fetchall()
    if user_roles:
        for role, count in user_roles:
            print(f"   📊 {role}: {count} users")
    else:
        print("   ❌ No users found!")
    
    # Check recent users
    print("\n3. Recent user records (last 5):")
    cursor.execute("""
        SELECT id, email, phone_number, role, is_active, created_at
        FROM users 
        ORDER BY created_at DESC 
        LIMIT 5
    """)
    
    recent_users = cursor.fetchall()
    if recent_users:
        for user in recent_users:
            user_id, email, phone, role, active, created = user
            print(f"   👤 ID:{user_id} | {email or phone or 'No contact'} | Role:{role} | Active:{active}")
    else:
        print("   ❌ No recent users!")
    
    # Check if there are any invalid enum values
    print("\n4. Checking for invalid role values:")
    cursor.execute("""
        SELECT role, COUNT(*) as count
        FROM users 
        WHERE role NOT IN ('student', 'teacher', 'admin', 'moderator')
        GROUP BY role
    """)
    
    invalid_roles = cursor.fetchall()
    if invalid_roles:
        print("   ⚠️  Found invalid role values:")
        for role, count in invalid_roles:
            print(f"      ❌ '{role}': {count} users")
    else:
        print("   ✅ All user roles are valid!")
    
    # Check alembic version
    print("\n5. Database migration status:")
    try:
        cursor.execute("""
            SELECT version_num 
            FROM alembic_version 
            LIMIT 1
        """)
        version = cursor.fetchone()
        if version:
            print(f"   📋 Alembic version: {version[0]}")
        else:
            print("   ❌ No alembic version found!")
    except:
        print("   ❌ Could not check alembic version")
    
    cursor.close()
    conn.close()
    
    print("\n" + "=" * 50)
    print("✅ Database check complete!")
    
except Exception as e:
    print(f"❌ Error connecting to database: {e}")
    print("Make sure DATABASE_URL is set correctly")
