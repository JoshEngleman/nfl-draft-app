"""
PostgreSQL database configuration for Railway.
Simple, focused, PostgreSQL-only.
"""

import os
from sqlalchemy import create_engine

def create_database_engine():
    """Create and return a PostgreSQL database engine."""
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not found. Make sure PostgreSQL is configured on Railway.")
    
    print("Using PostgreSQL database (Railway)")
    
    # PostgreSQL configuration optimized for Railway
    engine = create_engine(
        database_url,
        pool_pre_ping=True,  # Verify connections before use
        pool_recycle=300,    # Recycle connections every 5 minutes
        echo=False           # Set to True for SQL debugging
    )
    
    return engine