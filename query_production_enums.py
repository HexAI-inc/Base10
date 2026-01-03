#!/usr/bin/env python3
import os
import psycopg2
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv('DATABASE_URL')
if not DATABASE_URL:
    print("❌ DATABASE_URL environment variable not set")
    exit(1)

try:
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()
    
    print("🔍 Listing all custom types in production database...")
    print("=" * 50)
    
    cursor.execute("""
        SELECT n.nspname as schema, t.typname as type 
        FROM pg_type t 
        LEFT JOIN pg_catalog.pg_namespace n ON n.oid = t.typnamespace 
        WHERE (t.typrelid = 0 OR (SELECT c.relkind = 'c' FROM pg_catalog.pg_class c WHERE c.oid = t.typrelid)) 
        AND NOT EXISTS(SELECT 1 FROM pg_catalog.pg_type el WHERE el.oid = t.typelem AND el.typarray = t.oid)
        AND n.nspname NOT IN ('pg_catalog', 'information_schema')
        ORDER BY 1, 2;
    """)
    
    for schema, typname in cursor.fetchall():
        print(f"   Type: {typname} (Schema: {schema})")

    print("\n" + "=" * 50)
    print("✅ Database check complete!")

except Exception as e:
    print(f"❌ Error: {e}")
finally:
    if 'conn' in locals():
        conn.close()
