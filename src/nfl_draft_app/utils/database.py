"""
PostgreSQL database configuration for Railway.
Simple, focused, PostgreSQL-only with connection pooling.
"""

import os
from sqlalchemy import create_engine

# Global engine instance for connection pooling
_engine = None

def create_database_engine():
    """Create and return a PostgreSQL database engine with connection pooling."""
    global _engine
    
    # Return existing engine if already created
    if _engine is not None:
        return _engine
    
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        raise ValueError("DATABASE_URL environment variable not found. Make sure PostgreSQL is configured on Railway.")
    
    print("Creating PostgreSQL database engine (Railway)")
    
    # PostgreSQL configuration optimized for Railway with connection pooling
    _engine = create_engine(
        database_url,
        pool_pre_ping=True,      # Verify connections before use
        pool_recycle=300,        # Recycle connections every 5 minutes
        pool_size=5,             # Number of connections to keep open
        max_overflow=10,         # Additional connections if pool is full
        pool_timeout=30,         # Timeout waiting for connection
        echo=False               # Set to True for SQL debugging
    )
    
    return _engine

def get_database_engine():
    """Get the shared database engine instance."""
    return create_database_engine()