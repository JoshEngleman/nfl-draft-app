import sqlite3
import os
from datetime import datetime

# Configuration
DB_FILE = "data/fantasy_pros.db"

def create_draft_tables():
    """Creates the database tables needed for draft functionality."""
    
    if not os.path.exists(DB_FILE):
        print(f"Error: Database file not found at {DB_FILE}")
        print("Please run the data processing scripts first.")
        return
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    print("Creating draft tables...")
    
    # Draft configurations table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_configs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            num_teams INTEGER NOT NULL,
            num_rounds INTEGER NOT NULL,
            draft_type TEXT NOT NULL CHECK (draft_type IN ('snake', 'straight')),
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Draft sessions table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    ''')
    
    # Team names table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_teams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            team_number INTEGER NOT NULL,
            team_name TEXT NOT NULL,
            FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
            UNIQUE(session_id, team_number)
        )
    ''')
    
    # Draft picks table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_picks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    ''')
    
    # Replacement levels table for value calculations
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS replacement_levels (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            position TEXT NOT NULL UNIQUE,
            replacement_rank INTEGER NOT NULL,
            replacement_value REAL,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Draft settings table for user preferences
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS draft_settings (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER NOT NULL,
            my_team_number INTEGER,
            notes TEXT,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (session_id) REFERENCES draft_sessions(id),
            UNIQUE(session_id)
        )
    ''')
    
    conn.commit()
    
    # Insert default replacement levels (rank-based system)
    default_replacements = [
        ('QB', 22, None, 'QB replacement level - 22nd ranked QB'),
        ('RB', 36, None, 'RB replacement level - 36th ranked RB'), 
        ('WR', 48, None, 'WR replacement level - 48th ranked WR'),
        ('TE', 18, None, 'TE replacement level - 18th ranked TE'),
        ('K', 12, None, 'K replacement level - 12th ranked K'),
        ('DST', 12, None, 'DST replacement level - 12th ranked DST')
    ]
    
    cursor.execute('SELECT COUNT(*) FROM replacement_levels')
    if cursor.fetchone()[0] == 0:
        print("Inserting default replacement levels...")
        cursor.executemany('''
            INSERT OR IGNORE INTO replacement_levels (position, replacement_rank, replacement_value, notes)
            VALUES (?, ?, ?, ?)
        ''', default_replacements)
        conn.commit()
    
    print("Draft tables created successfully!")
    
    # Show table info
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name LIKE '%draft%' OR name LIKE '%replacement%'")
    tables = cursor.fetchall()
    print(f"Draft-related tables: {[table[0] for table in tables]}")
    
    conn.close()

def show_draft_schema():
    """Display the schema of draft tables for verification."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    tables = ['draft_configs', 'draft_sessions', 'draft_picks', 'replacement_levels']
    
    for table in tables:
        print(f"\n=== {table.upper()} ===")
        cursor.execute(f"PRAGMA table_info({table})")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
    
    conn.close()

if __name__ == "__main__":
    create_draft_tables()
    show_draft_schema()