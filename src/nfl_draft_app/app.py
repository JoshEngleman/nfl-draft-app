import streamlit as st
import pandas as pd
from sqlalchemy import create_engine
from utils.database import get_database_engine
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode, JsCode
import sys
import os

# Add the src directory to the path so we can import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__)))
from utils.logo_utils import get_team_logo_html

# --- Page Configuration ---
st.set_page_config(
    page_title="Wife Pleaser 5000",
    page_icon="🏈",
    layout="wide"
)

# --- Custom CSS for professional typography and styling ---
st.markdown("""
<style>
/* Import modern font */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

/* Global typography */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
}

/* Main title styling */
h1 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 700 !important;
    font-size: 2.5rem !important;
    color: #1a1a1a !important;
    margin-bottom: 0.5rem !important;
}

/* Section headers */
h2, h3 {
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    color: #2c3e50 !important;
}

/* Reduce top padding of the main app container */
div[data-testid="stAppViewContainer"] {
    padding-top: 1.5rem;
}

/* Center the group headers with better typography */
.ag-header-group-cell-label {
    justify-content: center;
    font-family: 'Inter', sans-serif !important;
    font-weight: 600 !important;
    font-size: 0.875rem !important;
    letter-spacing: 0.05em !important;
    color: #374151 !important;
}

/* Style the main headers */
.ag-header-cell-label {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
    font-size: 0.8rem !important;
    color: #4b5563 !important;
}

/* Table cell typography */
.ag-cell {
    font-family: 'Inter', sans-serif !important;
    font-size: 0.875rem !important;
    color: #1f2937 !important;
}

/* Zebra-striping for rows */
.ag-row-even { background-color: #f8f9fa !important; }
.ag-row-odd { background-color: #ffffff !important; }

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    font-family: 'Inter', sans-serif !important;
}

.stTabs [data-baseweb="tab"] {
    font-family: 'Inter', sans-serif !important;
    font-weight: 500 !important;
}
</style>
""", unsafe_allow_html=True)

# --- Database Connection ---
# Automatically detects PostgreSQL (Railway) or SQLite (local)
engine = get_database_engine()  # Use shared engine

@st.cache_data
def load_data(table_name):
    """Loads and prepares data from a single table."""
    try:
        df = pd.read_sql_table(table_name, engine)
        for col in df.columns:
            if df[col].dtype == 'object' and col not in ['player', 'team', 'team_name']:
                df[col] = pd.to_numeric(df[col], errors='coerce')
        return df
    except Exception as e:
        st.error(f"Could not load data from table '{table_name}'. Error: {e}")
        return pd.DataFrame()

def add_team_logos_to_data(df):
    """Add team logo HTML to dataframe for AgGrid display."""
    if 'team' in df.columns:
        df = df.copy()
        df['team_with_logo'] = df['team'].apply(
            lambda team: get_team_logo_html(str(team).lower(), size="24px") + f" {team}" 
            if pd.notna(team) and team != '' and str(team) != '0' else str(team)
        )
    return df

@st.cache_data
def load_and_prepare_all_data():
    """Loads and combines data for all positions into a single DataFrame."""
    positions_to_load = ['qb_projections', 'rb_projections', 'wr_projections', 'te_projections', 'k_projections', 'dst_projections']
    all_dfs = []
    
    for pos_table in positions_to_load:
        pos_df = load_data(pos_table)
        if not pos_df.empty:
            if 'team_name' in pos_df.columns:
                pos_df.rename(columns={'team_name': 'player'}, inplace=True)
            pos_df['position'] = pos_table.split('_')[0].upper()
            all_dfs.append(pos_df)
            
    if not all_dfs:
        return pd.DataFrame()

    combined_df = pd.concat(all_dfs, ignore_index=True, sort=False).fillna(0)
    
    all_cols = [
        'player', 'team', 'position',
        'pass_att', 'pass_cmp', 'pass_yds', 'pass_tds', 'pass_ints',
        'rush_att', 'rush_yds', 'rush_tds',
        'receptions', 'rec_yds', 'rec_tds',
        'fumbles_lost', 'fantasy_points'
    ]
    
    combined_df = combined_df.reindex(columns=all_cols, fill_value=0)
    return combined_df

def build_grid_options(position_key, df):
    """Builds AgGrid options with advanced filters and custom styling."""
    gb = GridOptionsBuilder.from_dataframe(df)
    gb.configure_default_column(resizable=True, filterable=True, sortable=True, editable=False, minWidth=50)
    gb.configure_selection(selection_mode="single", use_checkbox=False)
    
    jscode = JsCode("function(params) { if (params.node.selected) { return {'backgroundColor': '#ffebee'} } return {}; };")
    gb.configure_grid_options(getRowStyle=jscode)
    grid_options = gb.build()
    
    stat_width, num_filter = 85, 'agNumberColumnFilter'
    
    column_defs = {
        "OVERALL": [
            {"field": "player", "pinned": "left", "width": 200},
            {"field": "team", "pinned": "left", "width": 80},
            {"field": "position", "pinned": "left", "width": 90},
            {"headerName": "PASSING", "children": [
                {"field": "pass_att", "headerName": "ATT", "width": stat_width, "filter": num_filter},
                {"field": "pass_cmp", "headerName": "CMP", "width": stat_width, "filter": num_filter},
                {"field": "pass_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "pass_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter},
                {"field": "pass_ints", "headerName": "INTS", "width": stat_width, "filter": num_filter}
            ]},
            {"headerName": "RUSHING", "children": [
                {"field": "rush_att", "headerName": "ATT", "width": stat_width, "filter": num_filter},
                {"field": "rush_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rush_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"headerName": "RECEIVING", "children": [
                {"field": "receptions", "headerName": "REC", "width": stat_width, "filter": num_filter},
                {"field": "rec_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rec_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"field": "fumbles_lost", "headerName": "FL", "width": stat_width, "filter": num_filter},
            {"field": "fantasy_points", "headerName": "FPTS", "width": stat_width + 10, "filter": num_filter}
        ],
        "QB": [
            {"field": "player", "pinned": "left", "width": 200},
            {"field": "team", "pinned": "left", "width": 80},
            {"headerName": "PASSING", "children": [
                {"field": "pass_att", "headerName": "ATT", "width": stat_width, "filter": num_filter},
                {"field": "pass_cmp", "headerName": "CMP", "width": stat_width, "filter": num_filter},
                {"field": "pass_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "pass_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter},
                {"field": "pass_ints", "headerName": "INTS", "width": stat_width, "filter": num_filter}
            ]},
            {"headerName": "RUSHING", "children": [
                {"field": "rush_att", "headerName": "ATT", "width": stat_width, "filter": num_filter},
                {"field": "rush_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rush_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"field": "fumbles_lost", "headerName": "FL", "width": stat_width, "filter": num_filter},
            {"field": "fantasy_points", "headerName": "FPTS", "width": stat_width + 10, "filter": num_filter}
        ],
        "RB": [
            {"field": "player", "pinned": "left", "width": 200},
            {"field": "team", "pinned": "left", "width": 80},
            {"headerName": "RUSHING", "children": [
                {"field": "rush_att", "headerName": "ATT", "width": stat_width, "filter": num_filter},
                {"field": "rush_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rush_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"headerName": "RECEIVING", "children": [
                {"field": "receptions", "headerName": "REC", "width": stat_width, "filter": num_filter},
                {"field": "rec_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rec_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"field": "fumbles_lost", "headerName": "FL", "width": stat_width, "filter": num_filter},
            {"field": "fantasy_points", "headerName": "FPTS", "width": stat_width + 10, "filter": num_filter}
        ],
        "WR": [
            {"field": "player", "pinned": "left", "width": 200},
            {"field": "team", "pinned": "left", "width": 80},
            {"headerName": "RECEIVING", "children": [
                {"field": "receptions", "headerName": "REC", "width": stat_width, "filter": num_filter},
                {"field": "rec_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rec_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"headerName": "RUSHING", "children": [
                {"field": "rush_att", "headerName": "ATT", "width": stat_width, "filter": num_filter},
                {"field": "rush_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rush_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"field": "fumbles_lost", "headerName": "FL", "width": stat_width, "filter": num_filter},
            {"field": "fantasy_points", "headerName": "FPTS", "width": stat_width + 10, "filter": num_filter}
        ],
        "TE": [
            {"field": "player", "pinned": "left", "width": 200},
            {"field": "team", "pinned": "left", "width": 80},
            {"headerName": "RECEIVING", "children": [
                {"field": "receptions", "headerName": "REC", "width": stat_width, "filter": num_filter},
                {"field": "rec_yds", "headerName": "YDS", "width": stat_width, "filter": num_filter},
                {"field": "rec_tds", "headerName": "TDS", "width": stat_width, "filter": num_filter}
            ]},
            {"field": "fumbles_lost", "headerName": "FL", "width": stat_width, "filter": num_filter},
            {"field": "fantasy_points", "headerName": "FPTS", "width": stat_width + 10, "filter": num_filter}
        ],
    }

    if position_key in column_defs:
        grid_options['columnDefs'] = column_defs[position_key]
    
    return grid_options

# --- Main Application ---
st.title("🏈 NFL Fantasy Football Draft Dashboard")

# Navigation
nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
with nav_col1:
    if st.button("🏈 Live Draft Tool", use_container_width=True):
        st.switch_page("pages/draft_tool.py")

with nav_col2:
    if st.button("⚙️ Admin Dashboard", use_container_width=True):
        st.switch_page("pages/admin.py")

st.write("This dashboard displays player projections to help with your fantasy draft. Select a position tab to view the data.")

positions = {"Overall": "all", "QB": "qb_projections", "RB": "rb_projections", "WR": "wr_projections", "TE": "te_projections", "K": "k_projections", "DST": "dst_projections"}
tabs = st.tabs(list(positions.keys()))

for i, (pos_abbr, table_name) in enumerate(positions.items()):
    with tabs[i]:
        st.header(f"{pos_abbr} Projections")
        
        if pos_abbr == "Overall":
            data = load_and_prepare_all_data()
        else:
            data = load_data(table_name)
        
        if not data.empty:
            grid_options = build_grid_options(pos_abbr.upper(), data)
            AgGrid(data, gridOptions=grid_options, theme='alpine', height=800, width='100%', allow_unsafe_jscode=True, reload_data=True)
        else:
            st.warning(f"No data found for {pos_abbr}.")
