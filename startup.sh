#!/bin/bash

# Create data directory if it doesn't exist
mkdir -p /app/data

# If database doesn't exist, run setup scripts
if [ ! -f "/app/data/fantasy_pros.db" ]; then
    echo "Database not found. Initializing..."
    
    # Download data if raw files don't exist
    if [ ! -d "/app/data/raw_projections" ] || [ -z "$(ls -A /app/data/raw_projections)" ]; then
        echo "Downloading initial data..."
        cd /app
        python src/nfl_draft_app/scripts/01_download_projections.py
    fi
    
    # Process data
    echo "Processing data..."
    cd /app
    python src/nfl_draft_app/scripts/02_process_projections.py
    
    # Setup draft tables
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

# Start the app
echo "Starting Streamlit app..."
streamlit run src/nfl_draft_app/app.py --server.port $PORT --server.headless true --server.address 0.0.0.0
