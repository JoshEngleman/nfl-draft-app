"""
PostgreSQL-compatible version of draft tables setup.
Uses SQLAlchemy for cross-database compatibility.
"""

import os
import sys
from datetime import datetime
from sqlalchemy import create_engine, text, MetaData, inspect

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from nfl_draft_app.utils.database import create_database_engine, get_database_config

def create_draft_tables():
    """Creates the database tables needed for draft functionality using SQLAlchemy."""
    
    database_url, db_type = get_database_config()
    print(f"Creating draft tables using {db_type} database...")
    
    engine = create_database_engine()
    
    # SQL statements that work with both SQLite and PostgreSQL
    table_definitions = [
        # Draft configurations table
        '''
        CREATE TABLE IF NOT EXISTS draft_configs (
            id SERIAL PRIMARY KEY,
            name TEXT NOT NULL,
            num_teams INTEGER NOT NULL,
            num_rounds INTEGER NOT NULL,
            draft_type TEXT NOT NULL CHECK (draft_type IN ('snake', 'straight')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        ''',
        
        # Draft sessions table
        '''
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
        ''',
        
        # Team names table
        '''
        CREATE TABLE IF NOT EXISTS draft_teams (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL,
            team_number INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
            UNIQUE(session_id, team_number)
        )
        ''',
        
        # Draft picks table
        '''
        CREATE TABLE IF NOT EXISTS draft_picks (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL,
            pick_number INTEGER NOT NULL,
            round_number INTEGER NOT NULL,
            team_number INTEGER NOT NULL,
            player_name TEXT NOT NULL,
            position TEXT,
            player_team TEXT,
            bye_week INTEGER,
            projection REAL,
            adp REAL,
            value_score REAL,
            vona_score REAL,
            picked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
            UNIQUE(session_id, pick_number)
        )
        ''',
        
        # Draft settings table
        '''
        CREATE TABLE IF NOT EXISTS draft_settings (
            id SERIAL PRIMARY KEY,
            session_id INTEGER NOT NULL,
            my_team_number INTEGER,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
            UNIQUE(session_id)
        )
        ''',
        
        # Replacement levels table
        '''
        CREATE TABLE IF NOT EXISTS replacement_levels (
            id SERIAL PRIMARY KEY,
            position TEXT NOT NULL UNIQUE,
            replacement_rank INTEGER,
            replacement_value REAL,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
    ]
    
    # Adjust for SQLite vs PostgreSQL differences
    if db_type == "sqlite":
        # Replace SERIAL with INTEGER PRIMARY KEY AUTOINCREMENT for SQLite
        table_definitions = [sql.replace('SERIAL PRIMARY KEY', 'INTEGER PRIMARY KEY AUTOINCREMENT') 
                           for sql in table_definitions]
    
    try:
        with engine.connect() as conn:
            # Create tables
            for sql in table_definitions:
                conn.execute(text(sql))
            
            # Insert default replacement levels if table is empty
            result = conn.execute(text('SELECT COUNT(*) FROM replacement_levels'))
            if result.scalar() == 0:
                print("Inserting default replacement levels...")
                default_replacements = [
                    ('QB', 22, None, 'QB replacement level - 22nd ranked QB'),
                    ('RB', 36, None, 'RB replacement level - 36th ranked RB'), 
                    ('WR', 48, None, 'WR replacement level - 48th ranked WR'),
                    ('TE', 18, None, 'TE replacement level - 18th ranked TE'),
                    ('K', 12, None, 'K replacement level - 12th ranked K'),
                    ('DST', 12, None, 'DST replacement level - 12th ranked DST')
                ]
                
                for pos, rank, value, notes in default_replacements:
                    conn.execute(text('''
                        INSERT INTO replacement_levels (position, replacement_rank, replacement_value, notes)
                        VALUES (:position, :rank, :value, :notes)
                        ON CONFLICT (position) DO NOTHING
                    '''), {"position": pos, "rank": rank, "value": value, "notes": notes})
            
            conn.commit()
            print("Draft tables created successfully!")
            
            # Show table info
            inspector = inspect(engine)
            draft_tables = [t for t in inspector.get_table_names() 
                          if 'draft' in t or 'replacement' in t]
            print(f"Draft-related tables: {draft_tables}")
            
    except Exception as e:
        print(f"Error creating tables: {e}")
        raise

def main():
    create_draft_tables()

if __name__ == "__main__":
    main()
