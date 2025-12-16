#!/usr/bin/env python3
"""
Apply migration directly to production PostgreSQL database
"""
import os
import sys

# Set the DATABASE_URL from .env
from dotenv import load_dotenv
load_dotenv()

# Force alembic to use production database
os.environ['DATABASE_URL'] = os.getenv('DATABASE_URL')

print(f"🔄 Applying migration to production database...")
print(f"   Database: {os.getenv('DATABASE_URL').split('@')[1].split('/')[0] if '@' in os.getenv('DATABASE_URL', '') else 'unknown'}")

# Run alembic upgrade
import subprocess
result = subprocess.run(['alembic', 'upgrade', 'head'], capture_output=True, text=True)

print(result.stdout)
if result.stderr:
    print(result.stderr)

if result.returncode == 0:
    print("✅ Migration applied successfully to production!")
else:
    print("❌ Migration failed!")
    sys.exit(1)
