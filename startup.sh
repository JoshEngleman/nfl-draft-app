#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p /app/data

# Check if database exists and has draft tables
DB_EXISTS=false
if [ -f "/app/data/fantasy_pros.db" ]; then
    echo "Database file found. Checking for draft tables..."
    # Check if draft tables exist by trying to query one
    if python -c "
import sqlite3
import sys
try:
    conn = sqlite3.connect('/app/data/fantasy_pros.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM draft_sessions LIMIT 1')
    conn.close()
    sys.exit(0)
except:
    sys.exit(1)
" 2>/dev/null; then
        echo "Database and draft tables found. Skipping initialization."
        DB_EXISTS=true
    else
        echo "Database exists but draft tables missing. Will initialize draft tables only."
    fi
else
    echo "Database not found. Full initialization needed."
fi

# Only run full initialization if database doesn't exist
if [ "$DB_EXISTS" = false ]; then
    # Download data if raw files don't exist or database doesn't exist
    if [ ! -f "/app/data/fantasy_pros.db" ] && ([ ! -d "/app/data/raw_projections" ] || [ -z "$(ls -A /app/data/raw_projections)" ]); then
        echo "Downloading initial data..."
        cd /app
        python src/nfl_draft_app/scripts/01_download_projections.py
    fi
    
    # Process data only if database doesn't exist
    if [ ! -f "/app/data/fantasy_pros.db" ]; then
        echo "Processing data..."
        cd /app
        python src/nfl_draft_app/scripts/02_process_projections.py
    fi
    
    # Setup draft tables (this won't affect existing draft data)
    echo "Setting up draft tables..."
    python src/nfl_draft_app/scripts/03_setup_draft_tables.py
    
    # Calculate replacement values
    echo "Calculating replacement values..."
    python -c "
import sys
sys.path.append('/app/src')
from nfl_draft_app.utils.draft_logic import calculate_replacement_values
print('Calculating replacement values...')
replacement_values = calculate_replacement_values()
print(f'Replacement values calculated: {replacement_values}')
print('Database initialization complete!')
"
fi

# Debug: Show volume and database info before starting
echo "=== DEBUG INFO ==="
echo "Data directory exists: $(test -d /app/data && echo 'YES' || echo 'NO')"
echo "Data directory contents: $(ls -la /app/data 2>/dev/null || echo 'Directory not accessible')"
echo "Database file exists: $(test -f /app/data/fantasy_pros.db && echo 'YES' || echo 'NO')"
if [ -f "/app/data/fantasy_pros.db" ]; then
    echo "Database size: $(ls -lh /app/data/fantasy_pros.db | awk '{print $5}')"
    echo "Draft sessions count: $(python -c "
import sqlite3
try:
    conn = sqlite3.connect('/app/data/fantasy_pros.db')
    cursor = conn.cursor()
    cursor.execute('SELECT COUNT(*) FROM draft_sessions')
    print(cursor.fetchone()[0])
    conn.close()
except Exception as e:
    print('Error:', e)
" 2>/dev/null || echo 'Query failed')"
fi
echo "Volume mount info: $(df -h /app/data 2>/dev/null || echo 'No volume info available')"
echo "=================="

# Start the app
echo "Starting Streamlit app..."
streamlit run src/nfl_draft_app/app.py --server.port $PORT --server.headless true --server.address 0.0.0.0
