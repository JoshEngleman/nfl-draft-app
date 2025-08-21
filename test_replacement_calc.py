#!/usr/bin/env python3
"""
Local test script for replacement value calculation
Tests against Railway PostgreSQL database
"""

import os
import sys
import pandas as pd
from sqlalchemy import text

# Load .env file if it exists
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("python-dotenv not installed, trying without .env loading")

# Add src to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from nfl_draft_app.utils.database import get_database_engine
from nfl_draft_app.utils.draft_logic import calculate_replacement_values, get_replacement_levels

def test_direct_queries():
    """Test the direct SQL queries that should work."""
    print("=== Testing Direct SQL Queries ===")
    engine = get_database_engine()
    
    # Test QB query with CAST
    qb_query_cast = '''
        SELECT fantasy_points 
        FROM qb_projections 
        WHERE fantasy_points IS NOT NULL
        ORDER BY CAST(fantasy_points AS NUMERIC) DESC 
        LIMIT 1 OFFSET 21
    '''
    
    # Test QB query without CAST
    qb_query_no_cast = '''
        SELECT fantasy_points 
        FROM qb_projections 
        WHERE fantasy_points IS NOT NULL
        ORDER BY fantasy_points DESC 
        LIMIT 1 OFFSET 21
    '''
    
    try:
        # Test with CAST
        result_cast = pd.read_sql_query(qb_query_cast, engine)
        if not result_cast.empty:
            value_cast = result_cast.iloc[0]['fantasy_points']
            print(f"✅ QB Query WITH CAST: 22nd best QB = {value_cast} points")
        else:
            print("❌ QB Query WITH CAST: No results")
            
        # Test without CAST
        result_no_cast = pd.read_sql_query(qb_query_no_cast, engine)
        if not result_no_cast.empty:
            value_no_cast = result_no_cast.iloc[0]['fantasy_points']
            print(f"✅ QB Query WITHOUT CAST: 22nd best QB = {value_no_cast} points")
        else:
            print("❌ QB Query WITHOUT CAST: No results")
            
        # Compare results
        if not result_cast.empty and not result_no_cast.empty:
            if value_cast != value_no_cast:
                print(f"⚠️  DIFFERENCE DETECTED: CAST={value_cast} vs NO_CAST={value_no_cast}")
                print("   This confirms the data type issue!")
            else:
                print("✅ Both queries return same result - data types are consistent")
                
    except Exception as e:
        print(f"❌ Error testing queries: {e}")
        import traceback
        traceback.print_exc()

def test_replacement_calculation():
    """Test the actual replacement calculation function."""
    print("\n=== Testing Replacement Calculation Function ===")
    
    try:
        # Show current state
        print("Current replacement levels:")
        current_levels = get_replacement_levels()
        for pos, data in current_levels.items():
            print(f"  {pos}: rank={data.get('rank', 'N/A')}, value={data.get('value', 'N/A')}")
        
        # Run the calculation
        print("\nRunning calculate_replacement_values()...")
        calculated_values = calculate_replacement_values()
        
        print("\nCalculated values:")
        for pos, value in calculated_values.items():
            print(f"  {pos}: {value}")
            
        # Check if values were saved to database
        print("\nChecking if values were saved to database...")
        updated_levels = get_replacement_levels()
        for pos, data in updated_levels.items():
            print(f"  {pos}: rank={data.get('rank', 'N/A')}, value={data.get('value', 'N/A')}")
            
    except Exception as e:
        print(f"❌ Error in replacement calculation: {e}")
        import traceback
        traceback.print_exc()

def test_data_types():
    """Check the actual data types in the fantasy_points columns."""
    print("\n=== Testing Data Types ===")
    engine = get_database_engine()
    
    # Check column data types
    type_query = """
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'qb_projections' 
        AND column_name = 'fantasy_points'
    """
    
    try:
        result = pd.read_sql_query(type_query, engine)
        if not result.empty:
            data_type = result.iloc[0]['data_type']
            print(f"fantasy_points column type: {data_type}")
            
            if data_type in ['text', 'character varying', 'varchar']:
                print("⚠️  Column is TEXT type - this explains the sorting issue!")
            elif data_type in ['numeric', 'decimal', 'float', 'double precision']:
                print("✅ Column is numeric type - should sort correctly")
            else:
                print(f"❓ Unknown column type: {data_type}")
        else:
            print("❌ Could not determine column type")
            
    except Exception as e:
        print(f"❌ Error checking data types: {e}")

if __name__ == "__main__":
    print("🧪 Testing Replacement Value Calculation")
    print("=" * 50)
    
    # Check if we have DATABASE_URL
    if not os.getenv('DATABASE_URL'):
        print("❌ DATABASE_URL environment variable not set")
        print("   Please set your Railway PostgreSQL connection string")
        sys.exit(1)
    
    print(f"Database URL: {os.getenv('DATABASE_URL', '').split('@')[1] if '@' in os.getenv('DATABASE_URL', '') else 'Not set'}")
    
    test_data_types()
    test_direct_queries() 
    test_replacement_calculation()
    
    print("\n" + "=" * 50)
    print("🧪 Test completed!")
