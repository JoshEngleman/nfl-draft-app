import sys
import os
from datetime import datetime

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from nfl_draft_app.utils.database import create_database_engine
from sqlalchemy import text

def create_draft_tables():
    """Creates the database tables needed for draft functionality in PostgreSQL."""
    
    engine = create_database_engine()
    
    print("Creating draft tables in PostgreSQL...")
    
    with engine.connect() as conn:
        # Draft configurations table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS draft_configs (
                id SERIAL PRIMARY KEY,
                name TEXT NOT NULL,
                num_teams INTEGER NOT NULL,
                num_rounds INTEGER NOT NULL,
                draft_type TEXT NOT NULL CHECK (draft_type IN ('snake', 'straight')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        
        # Draft sessions table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS draft_sessions (
                id SERIAL PRIMARY KEY,
                config_id INTEGER NOT NULL,
                name TEXT,
                current_pick INTEGER DEFAULT 1,
                current_round INTEGER DEFAULT 1,
                current_team INTEGER DEFAULT 1,
                status TEXT DEFAULT 'active' CHECK (status IN ('active', 'completed', 'paused')),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (config_id) REFERENCES draft_configs(id)
            )
        '''))
        
        # Team names table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS draft_teams (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                team_number INTEGER NOT NULL,
                team_name TEXT NOT NULL,
                FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
                UNIQUE(session_id, team_number)
            )
        '''))
        
        # Draft picks table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS draft_picks (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                pick_number INTEGER NOT NULL,
                round_number INTEGER NOT NULL,
                team_number INTEGER NOT NULL,
                player_name TEXT NOT NULL,
                player_team TEXT,
                position TEXT,
                bye_week INTEGER,
                adp REAL,
                projection REAL,
                value_score REAL,
                vona_score REAL,
                picked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
                UNIQUE(session_id, pick_number)
            )
        '''))
        
        # Draft settings table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS draft_settings (
                id SERIAL PRIMARY KEY,
                session_id INTEGER NOT NULL,
                my_team_number INTEGER,
                notes TEXT,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
                UNIQUE(session_id)
            )
        '''))
        
        # Replacement levels table
        conn.execute(text('''
            CREATE TABLE IF NOT EXISTS replacement_levels (
                id SERIAL PRIMARY KEY,
                position TEXT NOT NULL UNIQUE,
                replacement_rank INTEGER NOT NULL,
                replacement_value REAL DEFAULT 0.0,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        '''))
        
        conn.commit()
    
    print("Draft tables created successfully!")
    
    # Insert default replacement levels
    insert_default_replacement_levels()

def insert_default_replacement_levels():
    """Insert default replacement level values for each position."""
    engine = create_database_engine()
    
    default_levels = {
        'QB': {'rank': 15, 'value': 0.0},
        'RB': {'rank': 30, 'value': 0.0},
        'WR': {'rank': 36, 'value': 0.0},
        'TE': {'rank': 15, 'value': 0.0},
        'K': {'rank': 15, 'value': 0.0},
        'DST': {'rank': 15, 'value': 0.0}
    }
    
    with engine.connect() as conn:
        for position, data in default_levels.items():
            # Use ON CONFLICT DO NOTHING to avoid duplicates
            conn.execute(text('''
                INSERT INTO replacement_levels (position, replacement_rank, replacement_value)
                VALUES (:position, :rank, :value)
                ON CONFLICT (position) DO NOTHING
            '''), {
                'position': position,
                'rank': data['rank'],
                'value': data['value']
            })
        
        conn.commit()
    
    print("Default replacement levels inserted!")

if __name__ == "__main__":
    create_draft_tables()