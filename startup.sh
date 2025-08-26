#!/bin/bash

# Railway deployment script - PostgreSQL only
set -e  # Exit on any error

# Create data directory if it doesn't exist
mkdir -p /app/data

# Activate virtual environment for Railway
export PATH="/opt/venv/bin:$PATH"

# Check PostgreSQL database and tables
DB_EXISTS=false
if [ -n "$DATABASE_URL" ]; then
    echo "PostgreSQL database detected (Railway). Checking for draft tables..."
    # Check if draft tables exist in PostgreSQL
    if python -c "
import os
import sys
sys.path.insert(0, '/app/src')
try:
    from nfl_draft_app.utils.database import create_database_engine
    from sqlalchemy import text
    engine = create_database_engine()
    with engine.connect() as conn:
        result = conn.execute(text('SELECT COUNT(*) FROM draft_sessions LIMIT 1'))
        count = result.scalar()
        print(f'Found {count} draft sessions in PostgreSQL')
    print('PostgreSQL draft tables exist and are accessible')
    sys.exit(0)
except Exception as e:
    print(f'PostgreSQL draft table check failed: {e}')
    sys.exit(1)
"; then
        echo "PostgreSQL database and draft tables found. Skipping initialization."
        DB_EXISTS=true
    else
        echo "PostgreSQL database exists but draft tables missing. Will initialize draft tables only."
    fi
else
    echo "ERROR: DATABASE_URL not found. PostgreSQL database is required."
    echo "Please add a PostgreSQL database to your Railway project."
    exit 1
fi

# Always process CSV files if they exist (fresh data from git)
if [ -d "/app/data/raw_projections" ] && [ "$(ls -A /app/data/raw_projections)" ]; then
    echo "Found CSV files in /app/data/raw_projections - processing fresh data..."
    
    # Process projection data into PostgreSQL
    echo "Processing projection data into PostgreSQL..."
    cd /app
    python src/nfl_draft_app/scripts/02_process_projections.py
    
    echo "Fresh data processing completed."
else
    echo "No CSV files found - will download fresh data..."
    # Download projection data if needed
    echo "Downloading initial projection data..."
    cd /app
    python src/nfl_draft_app/scripts/01_download_projections.py
    
    # Process the downloaded data
    echo "Processing downloaded projection data into PostgreSQL..."
    python src/nfl_draft_app/scripts/02_process_projections.py
fi

# Always ensure draft tables exist (idempotent operation)
echo "Setting up draft tables in PostgreSQL..."
cd /app
python src/nfl_draft_app/scripts/03_setup_draft_tables.py

# Calculate replacement values
echo "Calculating replacement values..."
python -c "
import sys
sys.path.insert(0, '/app/src')
from nfl_draft_app.utils.draft_logic import calculate_replacement_values
print('Calculating replacement values...')
replacement_values = calculate_replacement_values()
print(f'Replacement values calculated: {replacement_values}')
print('PostgreSQL initialization complete!')
"

# Debug: Show PostgreSQL database info
echo "=== DEBUG INFO ==="
echo "PostgreSQL DATABASE_URL: $(echo $DATABASE_URL | sed 's/:[^@]*@/:***@/')"  # Hide password
echo "Data directory exists: $(test -d /app/data && echo 'YES' || echo 'NO')"
echo "Data directory contents: $(ls -la /app/data 2>/dev/null || echo 'Directory not accessible')"
echo "=================="

# Start the app
echo "Starting Streamlit app..."
streamlit run src/nfl_draft_app/app.py --server.port $PORT --server.headless true --server.address 0.0.0.0
