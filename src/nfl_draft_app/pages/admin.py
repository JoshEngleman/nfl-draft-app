"""
Admin Dashboard - Data management and system monitoring
"""
import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import sys
import os

# Add the parent directory to the path so we can import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.admin_utils import (
    get_data_status, run_data_scraping, run_data_processing, 
    run_full_refresh, format_file_size
)

# Page configuration
st.set_page_config(
    page_title="Admin Dashboard",
    page_icon="⚙️",
    layout="wide"
)

# Enhanced CSS for admin dashboard
st.markdown("""
<style>
/* Import modern fonts */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* Design system variables */
:root {
    --primary-navy: #1e293b;
    --primary-blue: #3b82f6;
    --primary-light: #dbeafe;
    --accent-green: #10b981;
    --accent-orange: #f59e0b;
    --accent-red: #ef4444;
    --neutral-50: #f8fafc;
    --neutral-100: #f1f5f9;
    --neutral-200: #e2e8f0;
    --neutral-600: #475569;
    --neutral-700: #334155;
    --neutral-800: #1e293b;
    --success-green: #059669;
    --warning-orange: #d97706;
    --error-red: #dc2626;
}

/* Global typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    color: var(--neutral-800);
}

/* Enhanced status badges */
.status-badge {
    display: inline-flex;
    align-items: center;
    padding: 0.375rem 0.75rem;
    border-radius: 0.5rem;
    font-size: 0.875rem;
    font-weight: 600;
    text-transform: uppercase;
    letter-spacing: 0.05em;
    margin: 0.25rem;
}

.status-healthy {
    background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%);
    color: var(--success-green);
    border: 1px solid #86efac;
}

.status-warning {
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
    color: var(--warning-orange);
    border: 1px solid #fbbf24;
}

.status-error {
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%);
    color: var(--error-red);
    border: 1px solid #f87171;
}

.status-missing {
    background: linear-gradient(135deg, #f1f5f9 0%, #e2e8f0 100%);
    color: var(--neutral-600);
    border: 1px solid #cbd5e1;
}

.status-fresh {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    color: var(--success-green);
    border: 1px solid #86efac;
}

.status-stale {
    background: linear-gradient(135deg, #fffbeb 0%, #fef3c7 100%);
    color: var(--warning-orange);
    border: 1px solid #fbbf24;
}

.status-old {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    color: var(--error-red);
    border: 1px solid #f87171;
}

/* Admin cards */
.admin-card {
    background: white;
    border-radius: 0.75rem;
    padding: 1.5rem;
    margin: 1rem 0;
    border: 1px solid var(--neutral-200);
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    transition: all 0.2s ease;
}

.admin-card:hover {
    transform: translateY(-2px);
    box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
}

.admin-card h3 {
    color: var(--primary-navy);
    font-weight: 700;
    margin-bottom: 1rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

/* Metric displays */
.metric-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.75rem 0;
    border-bottom: 1px solid var(--neutral-100);
}

.metric-row:last-child {
    border-bottom: none;
}

.metric-label {
    font-weight: 500;
    color: var(--neutral-700);
}

.metric-value {
    font-weight: 600;
    color: var(--primary-navy);
}

/* Progress bars */
.progress-container {
    width: 100%;
    height: 0.5rem;
    background-color: var(--neutral-200);
    border-radius: 0.25rem;
    overflow: hidden;
    margin: 0.5rem 0;
}

.progress-bar {
    height: 100%;
    background: linear-gradient(90deg, var(--accent-green) 0%, var(--primary-blue) 100%);
    border-radius: 0.25rem;
    transition: width 0.3s ease;
}

/* Action buttons */
.admin-button {
    background: linear-gradient(135deg, var(--primary-blue) 0%, #2563eb 100%);
    color: white;
    border: none;
    border-radius: 0.5rem;
    padding: 0.75rem 1.5rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
    margin: 0.25rem;
}

.admin-button:hover {
    background: linear-gradient(135deg, #2563eb 0%, #1d4ed8 100%);
    transform: translateY(-1px);
    box-shadow: 0 4px 12px rgba(59, 130, 246, 0.3);
}

.admin-button-danger {
    background: linear-gradient(135deg, var(--error-red) 0%, #b91c1c 100%);
}

.admin-button-danger:hover {
    background: linear-gradient(135deg, #b91c1c 0%, #991b1b 100%);
    box-shadow: 0 4px 12px rgba(220, 38, 38, 0.3);
}

.admin-button-success {
    background: linear-gradient(135deg, var(--accent-green) 0%, #059669 100%);
}

.admin-button-success:hover {
    background: linear-gradient(135deg, #059669 0%, #047857 100%);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.3);
}

/* Log output styling */
.log-output {
    background: #1e293b;
    color: #e2e8f0;
    padding: 1rem;
    border-radius: 0.5rem;
    font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', monospace;
    font-size: 0.875rem;
    line-height: 1.5;
    overflow-x: auto;
    white-space: pre-wrap;
    max-height: 400px;
    overflow-y: auto;
}

/* Validation results */
.validation-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem;
    margin: 0.25rem 0;
    border-radius: 0.375rem;
    background: var(--neutral-50);
}

.validation-pass {
    background: linear-gradient(135deg, #ecfdf5 0%, #d1fae5 100%);
    border-left: 4px solid var(--success-green);
}

.validation-fail {
    background: linear-gradient(135deg, #fef2f2 0%, #fee2e2 100%);
    border-left: 4px solid var(--error-red);
}

/* Header styling */
.admin-header {
    background: linear-gradient(135deg, var(--primary-navy) 0%, var(--primary-blue) 100%);
    color: white;
    padding: 2rem;
    border-radius: 0.75rem;
    margin-bottom: 2rem;
    text-align: center;
}

.admin-header h1 {
    color: white;
    margin: 0;
    font-size: 2rem;
    font-weight: 800;
}

.admin-header p {
    color: rgba(255, 255, 255, 0.9);
    margin: 0.5rem 0 0 0;
    font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

def display_status_badge(status: str, text: str = None) -> str:
    """Generate HTML for status badge."""
    display_text = text or status.title()
    return f'<span class="status-badge status-{status}">{display_text}</span>'

def display_data_overview(data_status: dict):
    """Display high-level data overview."""
    st.markdown("""
    <div class="admin-card">
        <h3>📊 Data Overview</h3>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        db_status = data_status['database']['status']
        db_size = data_status['database']['size_human']
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h4>Database</h4>
            {display_status_badge(db_status)}
            <p><strong>{db_size}</strong></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        raw_files = data_status['raw_files']
        files_count = raw_files['total_files']
        files_status = raw_files['status']
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h4>Raw Files</h4>
            {display_status_badge(files_status)}
            <p><strong>{files_count}/7</strong> files</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col3:
        tables = data_status['tables']
        tables_count = tables['total_tables']
        total_records = tables['total_records']
        tables_status = tables['status']
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h4>Database Tables</h4>
            {display_status_badge(tables_status)}
            <p><strong>{tables_count}/7</strong> tables<br>{total_records:,} records</p>
        </div>
        """, unsafe_allow_html=True)
    
    with col4:
        validation = data_status['validation']
        validation_status = validation['status']
        checks_passed = len([c for c in validation['checks'] if c['status'] == 'pass'])
        total_checks = len(validation['checks'])
        st.markdown(f"""
        <div style="text-align: center; padding: 1rem;">
            <h4>Data Validation</h4>
            {display_status_badge(validation_status)}
            <p><strong>{checks_passed}/{total_checks}</strong> checks passed</p>
        </div>
        """, unsafe_allow_html=True)

def display_detailed_status(data_status: dict):
    """Display detailed status information."""
    
    # Database Status
    st.markdown("""
    <div class="admin-card">
        <h3>🗄️ Database Status</h3>
    </div>
    """, unsafe_allow_html=True)
    
    db_info = data_status['database']
    if db_info['exists']:
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
            <div class="metric-row">
                <span class="metric-label">Status:</span>
                <span class="metric-value">{display_status_badge(db_info['status'])}</span>
            </div>
            <div class="metric-row">
                <span class="metric-label">File Size:</span>
                <span class="metric-value">{db_info['size_human']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if db_info['last_modified'] and isinstance(db_info['last_modified'], datetime):
                age = datetime.now() - db_info['last_modified']
                st.markdown(f"""
                <div class="metric-row">
                    <span class="metric-label">Last Modified:</span>
                    <span class="metric-value">{db_info['last_modified'].strftime('%Y-%m-%d %H:%M:%S')}</span>
                </div>
                <div class="metric-row">
                    <span class="metric-label">Age:</span>
                    <span class="metric-value">{age.days} days, {age.seconds//3600} hours</span>
                </div>
                """, unsafe_allow_html=True)
            elif db_info['last_modified']:
                st.markdown(f"""
                <div class="metric-row">
                    <span class="metric-label">Last Modified:</span>
                    <span class="metric-value">{db_info['last_modified']}</span>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.error("❌ Database file not found!")
    
    # Tables Status
    st.markdown("""
    <div class="admin-card">
        <h3>📋 Tables Status</h3>
    </div>
    """, unsafe_allow_html=True)
    
    tables_info = data_status['tables']['tables']
    
    for table_name, table_info in tables_info.items():
        if table_info['exists']:
            col1, col2, col3 = st.columns([2, 1, 1])
            with col1:
                st.markdown(f"**{table_name}**")
            with col2:
                st.markdown(f"{display_status_badge(table_info['status'])}", unsafe_allow_html=True)
            with col3:
                st.markdown(f"**{table_info['row_count']:,}** records")
        else:
            st.markdown(f"❌ **{table_name}**: Missing or error")
    
    # Raw Files Status
    st.markdown("""
    <div class="admin-card">
        <h3>📁 Raw Files Status</h3>
    </div>
    """, unsafe_allow_html=True)
    
    files_info = data_status['raw_files']['files']
    
    for filename, file_info in files_info.items():
        if file_info['exists']:
            col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
            with col1:
                st.markdown(f"**{filename}**")
            with col2:
                st.markdown(f"{display_status_badge(file_info['status'])}", unsafe_allow_html=True)
            with col3:
                st.markdown(f"{file_info['size_human']}")
            with col4:
                st.markdown(f"{file_info['age_hours']:.1f}h ago")
        else:
            st.markdown(f"❌ **{filename}**: Missing")

def display_validation_results(validation_data: dict):
    """Display data validation results."""
    st.markdown("""
    <div class="admin-card">
        <h3>✅ Data Validation Results</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Overall status
    overall_status = validation_data['status']
    st.markdown(f"**Overall Status**: {display_status_badge(overall_status)}", unsafe_allow_html=True)
    
    # Individual checks
    if validation_data['checks']:
        st.markdown("### Validation Checks")
        for check in validation_data['checks']:
            status_class = "validation-pass" if check['status'] == 'pass' else "validation-fail"
            status_icon = "✅" if check['status'] == 'pass' else "❌"
            
            check_details = f"{check['table']} - {check['check']}"
            if 'expected_min' in check and 'actual' in check:
                check_details += f" (Expected ≥{check['expected_min']}, Got {check['actual']})"
            
            st.markdown(f"""
            <div class="validation-item {status_class}">
                <span>{status_icon} {check_details}</span>
                <span class="status-badge status-{check['status']}">{check['status']}</span>
            </div>
            """, unsafe_allow_html=True)
    
    # Warnings and errors
    if validation_data['warnings']:
        st.markdown("### ⚠️ Warnings")
        for warning in validation_data['warnings']:
            st.warning(warning)
    
    if validation_data['errors']:
        st.markdown("### ❌ Errors")
        for error in validation_data['errors']:
            st.error(error)

def display_data_controls():
    """Display data management controls."""
    st.markdown("""
    <div class="admin-card">
        <h3>🔧 Data Management Controls</h3>
        <p>Use these controls to update your fantasy data. <strong>Scraping</strong> downloads fresh data from FantasyPros, <strong>Processing</strong> cleans and loads it into the database.</p>
    </div>
    """, unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("📥 Scrape Data", help="Download fresh projections and ADP data from FantasyPros", use_container_width=True):
            st.session_state.run_scraping = True
    
    with col2:
        if st.button("⚙️ Process Data", help="Process raw CSV files into database", use_container_width=True):
            st.session_state.run_processing = True
    
    with col3:
        if st.button("🔄 Full Refresh", help="Complete data refresh: scrape + process", use_container_width=True, type="primary"):
            st.session_state.run_full_refresh = True
    
    # Handle script execution
    if st.session_state.get('run_scraping', False):
        st.session_state.run_scraping = False  # Clear flag immediately
        execute_scraping()
    
    if st.session_state.get('run_processing', False):
        st.session_state.run_processing = False  # Clear flag immediately
        execute_processing()
    
    if st.session_state.get('run_full_refresh', False):
        st.session_state.run_full_refresh = False  # Clear flag immediately
        execute_full_refresh()

def execute_scraping():
    """Execute data scraping with progress display."""
    st.markdown("### 📥 Running Data Scraping...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Starting data scraping...")
    progress_bar.progress(10)
    
    with st.spinner("Scraping data from FantasyPros..."):
        result = run_data_scraping()
    
    progress_bar.progress(100)
    
    if result['success']:
        st.success(f"✅ Data scraping completed successfully in {result['duration']:.1f} seconds!")
        if result['output']:
            with st.expander("📋 Scraping Output"):
                st.markdown(f'<div class="log-output">{result["output"]}</div>', unsafe_allow_html=True)
    else:
        st.error(f"❌ Data scraping failed: {result['error']}")
        if result['output']:
            with st.expander("📋 Output"):
                st.markdown(f'<div class="log-output">{result["output"]}</div>', unsafe_allow_html=True)
    
    # Data will be refreshed on next page load

def execute_processing():
    """Execute data processing with progress display."""
    st.markdown("### ⚙️ Running Data Processing...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Starting data processing...")
    progress_bar.progress(10)
    
    with st.spinner("Processing CSV files into database..."):
        result = run_data_processing()
    
    progress_bar.progress(100)
    
    if result['success']:
        st.success(f"✅ Data processing completed successfully in {result['duration']:.1f} seconds!")
        if result['output']:
            with st.expander("📋 Processing Output"):
                st.markdown(f'<div class="log-output">{result["output"]}</div>', unsafe_allow_html=True)
    else:
        st.error(f"❌ Data processing failed: {result['error']}")
        if result['output']:
            with st.expander("📋 Output"):
                st.markdown(f'<div class="log-output">{result["output"]}</div>', unsafe_allow_html=True)
    
    # Data will be refreshed on next page load

def execute_full_refresh():
    """Execute full data refresh with progress display."""
    st.markdown("### 🔄 Running Full Data Refresh...")
    
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    # Step 1: Scraping
    status_text.text("Step 1/2: Scraping data from FantasyPros...")
    progress_bar.progress(10)
    
    with st.spinner("Scraping data..."):
        result = run_full_refresh()
    
    progress_bar.progress(50)
    
    # Display results
    if result['overall_success']:
        st.success(f"✅ Full data refresh completed successfully in {result['total_duration']:.1f} seconds!")
        
        # Show individual step results
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("#### 📥 Scraping Results")
            scraping = result['scraping']
            if scraping['success']:
                st.success(f"✅ Completed in {scraping['duration']:.1f}s")
            else:
                st.error(f"❌ Failed: {scraping['error']}")
        
        with col2:
            st.markdown("#### ⚙️ Processing Results")
            processing = result['processing']
            if processing and processing['success']:
                st.success(f"✅ Completed in {processing['duration']:.1f}s")
            elif processing:
                st.error(f"❌ Failed: {processing['error']}")
            else:
                st.warning("⏭️ Skipped due to scraping failure")
        
        # Show output logs
        if result['scraping']['output'] or (result['processing'] and result['processing']['output']):
            with st.expander("📋 Detailed Output"):
                if result['scraping']['output']:
                    st.markdown("**Scraping Output:**")
                    st.markdown(f'<div class="log-output">{result["scraping"]["output"]}</div>', unsafe_allow_html=True)
                
                if result['processing'] and result['processing']['output']:
                    st.markdown("**Processing Output:**")
                    st.markdown(f'<div class="log-output">{result["processing"]["output"]}</div>', unsafe_allow_html=True)
    else:
        st.error("❌ Full data refresh failed!")
        
        # Show failure details
        if not result['scraping']['success']:
            st.error(f"Scraping failed: {result['scraping']['error']}")
        elif result['processing'] and not result['processing']['success']:
            st.error(f"Processing failed: {result['processing']['error']}")
    
    progress_bar.progress(100)
    
    # Data will be refreshed on next page load

def display_debug_diagnostics():
    """Display debug information for Value/VONA calculation issues."""
    st.markdown("### 🔍 Replacement Levels Diagnostics")
    
    try:
        from utils.draft_logic import get_replacement_levels, calculate_replacement_values, calculate_value_score
        from utils.database import get_database_engine
        import pandas as pd
        
        # Test 1: Check replacement_levels table
        st.markdown("#### 1. Replacement Levels Table")
        engine = get_database_engine()
        
        try:
            replacement_df = pd.read_sql_query("SELECT * FROM replacement_levels ORDER BY position", engine)
            st.dataframe(replacement_df, use_container_width=True)
            
            if replacement_df.empty:
                st.error("❌ replacement_levels table is empty!")
            else:
                st.success(f"✅ Found {len(replacement_df)} positions in replacement_levels table")
                
                # Check if values are all 0
                zero_values = replacement_df[replacement_df['replacement_value'] == 0.0]
                if len(zero_values) == len(replacement_df):
                    st.warning("⚠️ All replacement values are 0.0 - need to calculate!")
                elif len(zero_values) > 0:
                    st.warning(f"⚠️ {len(zero_values)} positions have 0.0 replacement values")
                else:
                    st.success("✅ All positions have calculated replacement values")
                    
        except Exception as e:
            st.error(f"❌ Error reading replacement_levels table: {e}")
        
        # Test 2: Check projection tables data
        st.markdown("#### 2. Projection Tables Sample Data")
        projection_tables = ['qb_projections', 'rb_projections', 'wr_projections', 'te_projections']
        
        for table in projection_tables:
            try:
                # Get count and sample
                count_df = pd.read_sql_query(f"SELECT COUNT(*) as count FROM {table} WHERE fantasy_points IS NOT NULL", engine)
                count = count_df.iloc[0]['count']
                
                if count > 0:
                    sample_df = pd.read_sql_query(f"SELECT player, fantasy_points FROM {table} WHERE fantasy_points IS NOT NULL ORDER BY fantasy_points DESC LIMIT 3", engine)
                    st.markdown(f"**{table}**: {count} players with fantasy_points")
                    st.dataframe(sample_df, use_container_width=True)
                else:
                    st.error(f"❌ {table}: No players with fantasy_points!")
                    
            except Exception as e:
                st.error(f"❌ Error checking {table}: {e}")
        
        # Test 2.5: Direct SQL Query Test
        st.markdown("#### 2.5. Direct SQL Query Test")
        if st.button("🧪 Test Direct SQL Queries", key="test_sql"):
            st.markdown("**Testing the exact SQL queries used in replacement calculation:**")
            
            # Test QB query directly
            try:
                # Test the exact query for QB rank 22
                qb_query = '''
                    SELECT fantasy_points 
                    FROM qb_projections 
                    WHERE fantasy_points IS NOT NULL
                    ORDER BY fantasy_points DESC 
                    LIMIT 1 OFFSET 21
                '''
                qb_result = pd.read_sql_query(qb_query, engine)
                
                if not qb_result.empty:
                    qb_value = qb_result.iloc[0]['fantasy_points']
                    st.success(f"✅ QB Query Success: 22nd best QB = {qb_value:.2f} points")
                else:
                    st.error("❌ QB Query returned empty result")
                    
                # Also test the count
                count_query = "SELECT COUNT(*) as count FROM qb_projections WHERE fantasy_points IS NOT NULL"
                count_result = pd.read_sql_query(count_query, engine)
                qb_count = count_result.iloc[0]['count']
                st.info(f"QB Count: {qb_count} players with fantasy_points")
                
                # Show top 5 QBs for reference
                top_qb_query = "SELECT player, fantasy_points FROM qb_projections WHERE fantasy_points IS NOT NULL ORDER BY fantasy_points DESC LIMIT 5"
                top_qbs = pd.read_sql_query(top_qb_query, engine)
                st.markdown("**Top 5 QBs:**")
                st.dataframe(top_qbs, use_container_width=True)
                
                # Show 20th-25th QBs
                mid_qb_query = "SELECT player, fantasy_points FROM qb_projections WHERE fantasy_points IS NOT NULL ORDER BY fantasy_points DESC LIMIT 5 OFFSET 19"
                mid_qbs = pd.read_sql_query(mid_qb_query, engine)
                st.markdown("**QBs ranked 20-24 (including our 22nd):**")
                st.dataframe(mid_qbs, use_container_width=True)
                
            except Exception as e:
                st.error(f"❌ SQL Query Error: {e}")
                import traceback
                st.code(traceback.format_exc())

        # Test 3: Manual replacement calculation test
        st.markdown("#### 3. Manual Replacement Calculation Test")
        if st.button("🧪 Test Replacement Calculation", key="test_replacement"):
            with st.spinner("Testing replacement calculation..."):
                try:
                    # Capture the calculation result
                    replacement_values = calculate_replacement_values()
                    
                    st.markdown("**Calculation Results:**")
                    for position, value in replacement_values.items():
                        if value > 0:
                            st.success(f"✅ {position}: {value:.2f} points")
                        else:
                            st.error(f"❌ {position}: {value} points (failed)")
                            
                    # Test get_replacement_levels function
                    levels = get_replacement_levels()
                    st.markdown("**Retrieved Levels:**")
                    st.json(levels)
                    
                except Exception as e:
                    st.error(f"❌ Error in replacement calculation: {e}")
                    import traceback
                    st.code(traceback.format_exc())
        
        # Test 4: Value calculation test
        st.markdown("#### 4. Value Calculation Test")
        if st.button("🧪 Test Value Calculation", key="test_value"):
            try:
                levels = get_replacement_levels()
                
                # Test with sample data
                test_cases = [
                    ("QB", 25.5),
                    ("RB", 18.3),
                    ("WR", 15.7)
                ]
                
                st.markdown("**Value Calculation Tests:**")
                for position, projection in test_cases:
                    value = calculate_value_score(projection, position, levels)
                    
                    if position in levels:
                        replacement_val = levels[position].get('value', 0)
                        expected = projection - replacement_val if replacement_val > 0 else 0.0
                        st.markdown(f"**{position}**: projection={projection}, replacement={replacement_val}, value={value} (expected={expected})")
                    else:
                        st.error(f"❌ {position} not found in replacement levels")
                        
            except Exception as e:
                st.error(f"❌ Error in value calculation test: {e}")
                import traceback
                st.code(traceback.format_exc())
        
    except ImportError as e:
        st.error(f"❌ Could not import required modules: {e}")
    except Exception as e:
        st.error(f"❌ Unexpected error in diagnostics: {e}")
        import traceback
        st.code(traceback.format_exc())

def main():
    """Main admin dashboard."""
    # Header
    st.markdown("""
    <div class="admin-header">
        <h1>⚙️ Admin Dashboard</h1>
        <p>Data management and system monitoring for NFL Fantasy Football Draft Tool</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Load data status
    with st.spinner("Loading system status..."):
        data_status = get_data_status()
    
    # Last update info
    last_update = data_status['last_update']
    if last_update:
        age = datetime.now() - last_update
        st.info(f"📅 **Last Data Update**: {last_update.strftime('%Y-%m-%d %H:%M:%S')} ({age.days} days, {age.seconds//3600} hours ago)")
    else:
        st.warning("📅 **No data found** - Please run data scraping to get started")
    
    # Main dashboard sections
    display_data_overview(data_status)
    
    # Data controls
    display_data_controls()
    
    # Detailed status (collapsible)
    with st.expander("📊 Detailed Status Information", expanded=False):
        display_detailed_status(data_status)
    
    # Validation results
    with st.expander("✅ Data Validation Results", expanded=False):
        display_validation_results(data_status['validation'])
    
    # Debug Section - Value/VONA Calculation Diagnostics
    with st.expander("🔧 Debug: Value/VONA Calculation Diagnostics", expanded=False):
        display_debug_diagnostics()
    
    # System information
    with st.expander("🖥️ System Information", expanded=False):
        system_info = data_status['system']
        
        st.markdown("### System Details")
        st.markdown(f"**Python Version**: {system_info['python_version']}")
        st.markdown(f"**Working Directory**: `{system_info['working_directory']}`")
        
        st.markdown("### Available Scripts")
        scripts = system_info['scripts_available']
        for script, info in scripts.items():
            status = "✅" if info['exists'] else "❌"
            st.markdown(f"{status} **{script}**: {'Available' if info['exists'] else 'Missing'}")
        
        st.markdown("### Dependencies")
        deps = system_info['dependencies']
        for dep, info in deps.items():
            status = "✅" if info['available'] else "❌"
            st.markdown(f"{status} **{dep}**: {info['status']}")

if __name__ == "__main__":
    main()
