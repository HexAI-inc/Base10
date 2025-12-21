#!/usr/bin/env python3
"""
Check the current userrole enum in the database.
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
    
    # Check enum values
    cursor.execute("""
        SELECT enumtypid, enumlabel 
        FROM pg_enum 
        WHERE enumtypid = (
            SELECT oid FROM pg_type WHERE typname = 'userrole'
        )
        ORDER BY enumsortorder
    """)
    
    results = cursor.fetchall()
    print("Current userrole enum values in database:")
    for typid, label in results:
        print(f"  - {label}")
    
    # Check some user roles
    cursor.execute("SELECT id, role FROM users LIMIT 5")
    users = cursor.fetchall()
    print("\nSample user roles:")
    for user_id, role in users:
        print(f"  User {user_id}: {role}")
    
    cursor.close()
    conn.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
