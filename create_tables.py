#!/usr/bin/env python3
"""
Create all database tables for local development.
"""
from app.db.session import engine
from app.db.base import Base

print("Creating database tables...")
Base.metadata.create_all(bind=engine)
print("✅ Database tables created successfully!")
