import os
import sys
import pandas as pd
from sqlalchemy import create_engine, text

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))
from nfl_draft_app.utils.database import create_database_engine

# Configuration
RAW_FILES_DIR = "data/raw_projections/"

def process_projection_file(file_path, table_name, engine):
    """
    Reads a raw projection CSV, applies a specific column schema based on the position,
    cleans the data, and loads it into the database.
    """
    print(f"Processing {file_path}...")
    
    # Read the CSV - ADP files don't have the blank second row that projections have
    try:
        if 'adp' in table_name:
            # ADP files don't need to skip row 1, but may have parsing issues
            try:
                df = pd.read_csv(file_path, header=0)
            except pd.errors.ParserError:
                # Try with error_bad_lines=False for problematic files
                print(f"  [!] WARNING: Parsing errors in {file_path}, attempting to fix...")
                df = pd.read_csv(file_path, header=0, on_bad_lines='skip')
        else:
            df = pd.read_csv(file_path, header=0, skiprows=[1])  # Projection files skip blank row
        df.dropna(how='all', inplace=True)  # Drop any other fully empty rows
    except (pd.errors.ParserError, FileNotFoundError, OSError) as e:
        print(f"  [!] ERROR: Could not read {file_path}. Reason: {e}")
        return

    # Define the correct column names for each position type. This is crucial for consistency.
    column_map = {
        'qb_projections': ['player', 'team', 'pass_att', 'pass_cmp', 'pass_yds', 'pass_tds', 'pass_ints', 'rush_att', 'rush_yds', 'rush_tds', 'fumbles_lost', 'fantasy_points'],
        'rb_projections': ['player', 'team', 'rush_att', 'rush_yds', 'rush_tds', 'receptions', 'rec_yds', 'rec_tds', 'fumbles_lost', 'fantasy_points'],
        'wr_projections': ['player', 'team', 'receptions', 'rec_yds', 'rec_tds', 'rush_att', 'rush_yds', 'rush_tds', 'fumbles_lost', 'fantasy_points'],
        'te_projections': ['player', 'team', 'receptions', 'rec_yds', 'rec_tds', 'fumbles_lost', 'fantasy_points'],
        'k_projections': ['player', 'team', 'fg_made', 'fg_att', 'xp_made', 'fantasy_points'],
        'dst_projections': ['team_name', 'team_abbr', 'sacks', 'def_int', 'fumble_rec', 'forced_fumbles', 'def_tds', 'safeties', 'pts_allowed', 'yds_allowed', 'fantasy_points'],
        'overall_adp': ['rank', 'player', 'team', 'bye_week', 'position', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp'],
        # Position-specific ADP files - some have 8 columns, others have 12
        'qb_adp': ['rank', 'player', 'team', 'bye_week', 'position', 'sleeper_adp', 'rtsports_adp', 'avg_adp'],
        'rb_adp': ['pos_rank', 'overall_rank', 'player', 'team', 'bye_week', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp'],
        'wr_adp': ['pos_rank', 'overall_rank', 'player', 'team', 'bye_week', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp'],
        'te_adp': ['pos_rank', 'overall_rank', 'player', 'team', 'bye_week', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp'],
        'k_adp': ['rank', 'player', 'team', 'bye_week', 'position', 'sleeper_adp', 'rtsports_adp', 'avg_adp'],
        'dst_adp': ['rank', 'player', 'team', 'bye_week', 'position', 'sleeper_adp', 'rtsports_adp', 'avg_adp']
    }

    if table_name in column_map:
        expected_cols = column_map[table_name]
        if len(df.columns) == len(expected_cols):
            df.columns = expected_cols
        else:
            print(f"  [!] WARNING: Column count mismatch for {table_name}. Expected {len(expected_cols)}, but found {len(df.columns)}. Skipping.")
            return
    else:
        print(f"  [!] WARNING: No column map found for {table_name}. Skipping.")
        return

    # Clean numeric columns - different approach for ADP vs projections
    if table_name.endswith('_adp'):
        # For ADP data, clean numeric columns and handle empty values
        # Different columns based on file type
        if table_name == 'overall_adp':
            numeric_cols = ['rank', 'bye_week', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp']
        elif table_name in ['rb_adp', 'wr_adp', 'te_adp']:
            # These files have full ADP data
            numeric_cols = ['pos_rank', 'overall_rank', 'bye_week', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp']
        else:
            # Simplified files (qb_adp, k_adp, dst_adp)
            numeric_cols = ['rank', 'bye_week', 'sleeper_adp', 'rtsports_adp', 'avg_adp']
        
        for col in numeric_cols:
            if col in df.columns:
                # Replace empty strings with NaN, then handle commas
                df[col] = df[col].replace('', pd.NA)
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '', regex=False)
                # Convert to numeric, errors='coerce' will turn invalid values to NaN
                df[col] = pd.to_numeric(df[col], errors='coerce')
        
        # Drop rows with missing player names
        df.dropna(subset=['player'], inplace=True)
        
        # For position-specific ADP files, we need to standardize the structure
        if table_name != 'overall_adp':
            # Handle different ADP file structures
            if table_name in ['rb_adp', 'wr_adp', 'te_adp']:
                # These files have full ADP data with pos_rank and overall_rank
                # Use overall_rank as the main rank and add position info
                df['rank'] = df['overall_rank']
                df['position'] = table_name.split('_')[0].upper() + '1'  # Add basic position info
                
                # Ensure all required columns exist
                required_cols = ['rank', 'player', 'team', 'bye_week', 'position', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp']
                df = df[required_cols]
            else:
                # Files with simplified structure (qb_adp, k_adp, dst_adp)
                # Add missing ADP columns with NaN values
                missing_cols = ['espn_adp', 'cbs_adp', 'nfl_adp', 'fantrax_adp']
                for col in missing_cols:
                    if col not in df.columns:
                        df[col] = pd.NA
                
                # Ensure position column exists
                if 'position' not in df.columns:
                    df['position'] = table_name.split('_')[0].upper() + '1'
                
                # Reorder columns to match overall_adp structure
                df = df[['rank', 'player', 'team', 'bye_week', 'position', 'espn_adp', 'sleeper_adp', 'cbs_adp', 'nfl_adp', 'rtsports_adp', 'fantrax_adp', 'avg_adp']]
            
            target_table = 'overall_adp'  # All ADP data goes into one table
        else:
            target_table = table_name
        
    elif table_name == 'dst_projections':
        # Special handling for DST file where team name is the primary identifier
        for col in df.columns:
            if col not in ['team_name']:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '', regex=False)
        df.drop(columns=['team_abbr'], inplace=True, errors='ignore')
        df.dropna(subset=['team_name'], inplace=True)
        target_table = table_name
        
    else:
        # For projection data, replace commas in numeric columns
        for col in df.columns:
            if col not in ['player', 'team']:
                if df[col].dtype == 'object':
                    df[col] = df[col].str.replace(',', '', regex=False)
        df.dropna(subset=['player'], inplace=True)
        target_table = table_name

    # Save the cleaned data to the database
    # For ADP files, append to overall_adp table (duplicates will be cleaned up later)
    if target_table == 'overall_adp' and table_name != 'overall_adp':
        df.to_sql(target_table, engine, if_exists="append", index=False)
        print(f"Successfully processed and appended {table_name} data to table: {target_table}")
    else:
        df.to_sql(target_table, engine, if_exists="replace", index=False)
        print(f"Successfully processed and saved data to table: {target_table}")
    
    print(f"  Columns: {df.columns.tolist()}")
    print("  Sample Data:")
    print(df.head(2).to_string())
    print("-" * 50)


def main():
    """Main function to process all raw projection files."""
    if not os.path.exists(RAW_FILES_DIR):
        print(f"Error: Raw data directory not found at {RAW_FILES_DIR}")
        print("Please run the '01_download_projections.py' script first.")
        return

    print("Starting data processing...")
    
    # Clear all data tables at the start to ensure fresh data
    engine = create_database_engine()
    tables_to_clear = ['overall_adp', 'qb_projections', 'rb_projections', 'wr_projections', 
                      'te_projections', 'k_projections', 'dst_projections']
    
    try:
        with engine.connect() as conn:
            for table in tables_to_clear:
                try:
                    conn.execute(text(f"DELETE FROM {table}"))
                    print(f"Cleared existing data from {table}")
                except Exception as table_error:
                    print(f"Warning: Could not clear {table}: {table_error}")
            conn.commit()
            print("Data clearing completed")
    except Exception as e:
        print(f"Warning: Could not connect to database: {e}")
    
    # Get all CSV files
    all_files = [f for f in os.listdir(RAW_FILES_DIR) if f.endswith(".csv")]
    
    # Process projection files first, then ONLY the overall ADP file
    projection_files = [f for f in all_files if not f.endswith('_adp.csv')]
    
    # Only process overall_adp.csv - skip position-specific ADP files to avoid duplicates
    adp_files = []
    if 'overall_adp.csv' in all_files:
        adp_files = ['overall_adp.csv']
        print("Found overall_adp.csv - skipping position-specific ADP files to avoid duplicates")
    
    # Process all files in order
    all_files_ordered = sorted(projection_files) + adp_files

    for filename in all_files_ordered:
        file_path = os.path.join(RAW_FILES_DIR, filename)
        table_name = os.path.splitext(filename)[0]
        process_projection_file(file_path, table_name, engine)
    
    # No deduplication needed since we only process overall_adp.csv
            
    print("Data processing completed.")

if __name__ == "__main__":
    main()
