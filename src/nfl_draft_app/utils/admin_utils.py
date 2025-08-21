#!/usr/bin/env python3
"""
Admin utilities for managing data pipeline and system monitoring
"""

import os
import pandas as pd
import subprocess
import sys
from datetime import datetime
from typing import Dict, Optional
from .database import create_database_engine

# PostgreSQL-only configuration
RAW_DATA_DIR = "data/raw_projections/"
SCRIPTS_DIR = "src/nfl_draft_app/scripts/"

def get_data_status() -> Dict:
    """Get comprehensive data status for admin dashboard."""
    status = {
        'database': get_database_status(),
        'raw_files': get_raw_files_status(),
        'tables': get_table_status(),
        'last_update': get_last_update_time(),
        'validation': validate_data_integrity(),
        'system': get_system_status()
    }
    return status

def get_database_status() -> Dict:
    """Get PostgreSQL database connection information."""
    try:
        engine = create_database_engine()
        with engine.connect() as conn:
            from sqlalchemy import text
            # Test connection with a simple query
            result = conn.execute(text('SELECT 1'))
            result.fetchone()
        return {
            'exists': True,
            'type': 'PostgreSQL',
            'size_human': 'N/A (Cloud DB)',
            'last_modified': 'N/A (Cloud DB)',
            'status': 'connected'
        }
    except Exception as e:
        return {
            'exists': False,
            'type': 'PostgreSQL',
            'size_human': 'N/A',
            'last_modified': 'N/A',
            'status': 'error',
            'error': str(e)
        }


def get_raw_files_status() -> Dict:
    """Get status of raw CSV files."""
    files_status = {}
    expected_files = [
        'qb_projections.csv', 'rb_projections.csv', 'wr_projections.csv',
        'te_projections.csv', 'k_projections.csv', 'dst_projections.csv',
        'overall_adp.csv'
    ]
    
    if not os.path.exists(RAW_DATA_DIR):
        return {'status': 'missing', 'files': {}, 'total_files': 0}
    
    for filename in expected_files:
        filepath = os.path.join(RAW_DATA_DIR, filename)
        if os.path.exists(filepath):
            stat = os.stat(filepath)
            files_status[filename] = {
                'exists': True,
                'size': stat.st_size,
                'size_human': format_file_size(stat.st_size),
                'last_modified': datetime.fromtimestamp(stat.st_mtime),
                'age_hours': (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600,
                'status': get_file_freshness_status(stat.st_mtime)
            }
        else:
            files_status[filename] = {
                'exists': False,
                'size': 0,
                'size_human': '0 B',
                'last_modified': None,
                'age_hours': float('inf'),
                'status': 'missing'
            }
    
    return {
        'files': files_status,
        'total_files': len([f for f in files_status.values() if f['exists']]),
        'status': 'healthy' if all(f['exists'] for f in files_status.values()) else 'warning'
    }

def get_table_status() -> Dict:
    """Get database table information."""
    try:
        engine = create_database_engine()
    except Exception as e:
        return {'status': 'missing', 'error': str(e), 'tables': {}}
    
    tables_status = {}
    expected_tables = [
        'qb_projections', 'rb_projections', 'wr_projections',
        'te_projections', 'k_projections', 'dst_projections',
        'overall_adp'
    ]
    
    for table in expected_tables:
        try:
            # Get row count
            count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", engine)
            row_count = count_df.iloc[0]['count']
            
            # Get approximate column count (could enhance this later)
            try:
                sample_df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 1", engine)
                column_count = len(sample_df.columns)
            except:
                column_count = 0
            
            # PostgreSQL doesn't have rowid, use current timestamp
            last_update = datetime.now()
            
            tables_status[table] = {
                'exists': True,
                'row_count': row_count,
                'column_count': column_count,
                'columns': list(sample_df.columns) if column_count > 0 else [],
                'last_update': last_update,
                'status': get_table_health_status(table, row_count)
            }
            
        except Exception as e:
            tables_status[table] = {
                'exists': False,
                'row_count': 0,
                'column_count': 0,
                'columns': [],
                'last_update': None,
                'status': 'error',
                'error': str(e)
            }
    

    
    return {
        'tables': tables_status,
        'total_tables': len([t for t in tables_status.values() if t['exists']]),
        'total_records': sum(t['row_count'] for t in tables_status.values() if t['exists']),
        'status': 'healthy' if all(t['exists'] and t['row_count'] > 0 for t in tables_status.values()) else 'warning'
    }

def get_last_update_time() -> Optional[datetime]:
    """Get the most recent update time across all data sources."""
    times = []
    
    # PostgreSQL database doesn't have a file timestamp, skip this check
    
    # Check raw files
    if os.path.exists(RAW_DATA_DIR):
        for filename in os.listdir(RAW_DATA_DIR):
            if filename.endswith('.csv'):
                filepath = os.path.join(RAW_DATA_DIR, filename)
                times.append(datetime.fromtimestamp(os.path.getmtime(filepath)))
    
    return max(times) if times else None

def validate_data_integrity() -> Dict:
    """Perform data validation checks."""
    validation_results = {
        'checks': [],
        'status': 'healthy',
        'warnings': [],
        'errors': []
    }
    
    try:
        engine = create_database_engine()
    except Exception as e:
        validation_results['errors'].append(f"PostgreSQL connection failed: {str(e)}")
        validation_results['status'] = 'error'
        return validation_results
    
    try:
        # Check expected record counts for each position
        expected_minimums = {
            'qb_projections': 25,    # Should have at least 25 QBs
            'rb_projections': 50,    # Should have at least 50 RBs
            'wr_projections': 80,    # Should have at least 80 WRs
            'te_projections': 30,    # Should have at least 30 TEs
            'k_projections': 20,     # Should have at least 20 Ks
            'dst_projections': 30,   # Should have at least 30 DSTs
            'overall_adp': 200       # Should have at least 200 ADP entries
        }
        
        for table, min_count in expected_minimums.items():
            try:
                df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table}", conn)
                actual_count = df.iloc[0]['count']
                
                check_result = {
                    'table': table,
                    'check': 'record_count',
                    'expected_min': min_count,
                    'actual': actual_count,
                    'status': 'pass' if actual_count >= min_count else 'fail'
                }
                validation_results['checks'].append(check_result)
                
                if actual_count < min_count:
                    validation_results['warnings'].append(
                        f"{table}: Only {actual_count} records (expected ≥{min_count})"
                    )
                    if validation_results['status'] == 'healthy':
                        validation_results['status'] = 'warning'
                
            except (Exception, pd.errors.DatabaseError) as e:
                validation_results['errors'].append(f"{table}: {str(e)}")
                validation_results['status'] = 'error'
        
        # Check for missing critical columns
        critical_columns = {
            'qb_projections': ['player', 'team', 'fantasy_points'],
            'rb_projections': ['player', 'team', 'fantasy_points'],
            'wr_projections': ['player', 'team', 'fantasy_points'],
            'te_projections': ['player', 'team', 'fantasy_points'],
            'k_projections': ['player', 'team', 'fantasy_points'],
            'dst_projections': ['team_name', 'fantasy_points'],
            'overall_adp': ['player', 'position', 'avg_adp']
        }
        
        for table, required_cols in critical_columns.items():
            try:
                # Get column names from PostgreSQL
                sample_df = pd.read_sql_query(f"SELECT * FROM {table} LIMIT 1", engine)
                columns = list(sample_df.columns)
                
                missing_cols = [col for col in required_cols if col not in columns]
                if missing_cols:
                    validation_results['errors'].append(
                        f"{table}: Missing columns {missing_cols}"
                    )
                    validation_results['status'] = 'error'
                else:
                    validation_results['checks'].append({
                        'table': table,
                        'check': 'required_columns',
                        'status': 'pass'
                    })
                    
            except Exception as e:
                validation_results['errors'].append(f"{table} column check: {str(e)}")
                validation_results['status'] = 'error'
    
    return validation_results

def get_system_status() -> Dict:
    """Get system-level status information."""
    return {
        'python_version': sys.version.split()[0],
        'working_directory': os.getcwd(),
        'scripts_available': check_scripts_availability(),
        'dependencies': check_dependencies()
    }

def check_scripts_availability() -> Dict:
    """Check if required scripts are available."""
    required_scripts = [
        '01_download_projections.py',
        '02_process_projections.py',
        '03_setup_draft_tables.py'
    ]
    
    scripts_status = {}
    for script in required_scripts:
        script_path = os.path.join(SCRIPTS_DIR, script)
        scripts_status[script] = {
            'exists': os.path.exists(script_path),
            'path': script_path,
            'executable': os.access(script_path, os.X_OK) if os.path.exists(script_path) else False
        }
    
    return scripts_status

def check_dependencies() -> Dict:
    """Check if required dependencies are available."""
    dependencies = ['pandas', 'psycopg2-binary', 'playwright']
    deps_status = {}
    
    for dep in dependencies:
        try:
            __import__(dep)
            deps_status[dep] = {'available': True, 'status': 'installed'}
        except ImportError:
            deps_status[dep] = {'available': False, 'status': 'missing'}
    
    return deps_status

def run_data_scraping() -> Dict:
    """Execute the data scraping script."""
    script_path = os.path.join(SCRIPTS_DIR, '01_download_projections.py')
    
    if not os.path.exists(script_path):
        return {
            'success': False,
            'error': f'Script not found: {script_path}',
            'output': '',
            'duration': 0
        }
    
    start_time = datetime.now()
    
    try:
        # Run the script and capture output
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=300,  # 5 minute timeout
            check=False
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None,
            'duration': duration
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Script execution timed out (5 minutes)',
            'output': '',
            'duration': 300
        }
    except (subprocess.SubprocessError, OSError) as e:
        return {
            'success': False,
            'error': f'Execution error: {str(e)}',
            'output': '',
            'duration': (datetime.now() - start_time).total_seconds()
        }

def run_data_processing() -> Dict:
    """Execute the data processing script."""
    script_path = os.path.join(SCRIPTS_DIR, '02_process_projections.py')
    
    if not os.path.exists(script_path):
        return {
            'success': False,
            'error': f'Script not found: {script_path}',
            'output': '',
            'duration': 0
        }
    
    start_time = datetime.now()
    
    try:
        result = subprocess.run(
            [sys.executable, script_path],
            cwd=os.getcwd(),
            capture_output=True,
            text=True,
            timeout=120,  # 2 minute timeout
            check=False
        )
        
        duration = (datetime.now() - start_time).total_seconds()
        
        return {
            'success': result.returncode == 0,
            'returncode': result.returncode,
            'output': result.stdout,
            'error': result.stderr if result.returncode != 0 else None,
            'duration': duration
        }
        
    except subprocess.TimeoutExpired:
        return {
            'success': False,
            'error': 'Script execution timed out (2 minutes)',
            'output': '',
            'duration': 120
        }
    except (subprocess.SubprocessError, OSError) as e:
        return {
            'success': False,
            'error': f'Execution error: {str(e)}',
            'output': '',
            'duration': (datetime.now() - start_time).total_seconds()
        }

def run_full_refresh() -> Dict:
    """Execute complete data refresh (scraping + processing)."""
    start_time = datetime.now()
    
    # Step 1: Scrape data
    scraping_result = run_data_scraping()
    
    # Step 2: Process data (only if scraping succeeded)
    processing_result = None
    if scraping_result['success']:
        processing_result = run_data_processing()
        overall_success = processing_result['success']
    else:
        overall_success = False
    
    results = {
        'scraping': scraping_result,
        'processing': processing_result,
        'overall_success': overall_success,
        'total_duration': (datetime.now() - start_time).total_seconds()
    }
    
    return results

# Helper functions

def format_file_size(size_bytes: int) -> str:
    """Convert bytes to human readable format."""
    if size_bytes == 0:
        return "0 B"
    
    size_names = ["B", "KB", "MB", "GB"]
    import math
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = round(size_bytes / p, 2)
    return f"{s} {size_names[i]}"

def get_file_freshness_status(mtime: float) -> str:
    """Determine file freshness status based on modification time."""
    age_hours = (datetime.now() - datetime.fromtimestamp(mtime)).total_seconds() / 3600
    
    if age_hours < 24:
        return 'fresh'
    elif age_hours < 168:  # 1 week
        return 'stale'
    else:
        return 'old'

def get_table_health_status(table_name: str, row_count: int) -> str:
    """Determine table health status based on row count."""
    minimums = {
        'qb_projections': 20,
        'rb_projections': 40,
        'wr_projections': 60,
        'te_projections': 25,
        'k_projections': 15,
        'dst_projections': 25,
        'overall_adp': 150
    }
    
    min_expected = minimums.get(table_name, 10)
    
    if row_count == 0:
        return 'empty'
    elif row_count < min_expected:
        return 'warning'
    else:
        return 'healthy'
