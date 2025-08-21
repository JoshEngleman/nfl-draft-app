"""
Database configuration and connection management.
Supports both SQLite (local development) and PostgreSQL (Railway production).
"""

import os
from sqlalchemy import create_engine
from typing import Tuple

def get_database_config() -> Tuple[str, str]:
    """
    Get database configuration based on environment.
    Returns (database_url, database_type)
    """
    # Check for Railway PostgreSQL environment variables
    postgres_url = os.getenv('DATABASE_URL')
    
    if postgres_url:
        # Railway PostgreSQL - production
        print("Using PostgreSQL database (Railway)")
        return postgres_url, "postgresql"
    else:
        # SQLite - local development
        db_file = "data/fantasy_pros.db"
        sqlite_url = f"sqlite:///{db_file}"
        print(f"Using SQLite database: {db_file}")
        return sqlite_url, "sqlite"

def create_database_engine():
    """Create and return a database engine based on environment."""
    database_url, db_type = get_database_config()
    
    if db_type == "postgresql":
        # PostgreSQL configuration
        engine = create_engine(
            database_url,
            pool_pre_ping=True,  # Verify connections before use
            pool_recycle=300,    # Recycle connections every 5 minutes
        )
    else:
        # SQLite configuration
        engine = create_engine(
            database_url,
            connect_args={"check_same_thread": False}  # Allow multiple threads
        )
    
    return engine

def get_db_file_path() -> str:
    """Get the database file path (only relevant for SQLite)."""
    return "data/fantasy_pros.db"
