#!/usr/bin/env python3
"""
Initialize KeyGuard database schema
Run this script once before starting the application
"""
import sys
from pathlib import Path

# Add backend to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from database.db import engine, Base
from utils.config import DATABASE_URL, IS_SQLITE

def init_db():
    """Create all database tables"""
    print(f"Initializing database: {DATABASE_URL}")
    
    try:
        # Create all tables
        Base.metadata.create_all(bind=engine)
        print("✅ Database initialized successfully!")
        print("✅ All tables created")
        
        if IS_SQLITE:
            print("📊 Using SQLite database (development)")
        else:
            print("📊 Using PostgreSQL database (production)")
            
    except Exception as e:
        print(f"❌ Error initializing database: {e}")
        sys.exit(1)

if __name__ == "__main__":
    init_db()
