"""
Live Draft Tool - Main interface for conducting fantasy football drafts
"""
import streamlit as st
import pandas as pd
from datetime import datetime
import sys
import os

# Add the parent directory to the path so we can import our utilities
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
from utils.draft_logic import (DraftManager, get_replacement_levels, calculate_value_score, 
                               update_replacement_levels, calculate_replacement_values, 
                               get_draft_settings, update_draft_settings, calculate_vona_scores,
                               generate_fantasypros_url)
from utils.logo_utils import get_team_logo_with_text_html, get_team_logo_html, get_team_abbr_from_defense_name

# Page configuration
st.set_page_config(
    page_title="Live Draft Tool",
    page_icon="🏈",
    layout="wide"
)

# Enhanced Design System with Cohesive Theme
st.markdown("""
<style>
/* Import modern fonts with extended weights */
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

/* === DESIGN SYSTEM VARIABLES === */
:root {
    /* Primary Color Palette (Navy, Blue, Accent, Neutral) */
    --primary-navy: #1e293b;
    --primary-blue: #3b82f6;
    --primary-light: #dbeafe;
    --accent-green: #10b981;
    --accent-orange: #f59e0b;
    --accent-red: #ef4444;
    
    /* Neutral Grays */
    --neutral-50: #f8fafc;
    --neutral-100: #f1f5f9;
    --neutral-200: #e2e8f0;
    --neutral-300: #cbd5e1;
    --neutral-600: #475569;
    --neutral-700: #334155;
    --neutral-800: #1e293b;
    --neutral-900: #0f172a;
    
    /* Typography Scale */
    --text-xs: 0.75rem;
    --text-sm: 0.875rem;
    --text-base: 1rem;
    --text-lg: 1.125rem;
    --text-xl: 1.25rem;
    --text-2xl: 1.5rem;
    
    /* Spacing Scale */
    --space-xs: 0.25rem;
    --space-sm: 0.5rem;
    --space-md: 0.75rem;
    --space-lg: 1rem;
    --space-xl: 1.5rem;
    --space-2xl: 2rem;
    
    /* Shadows */
    --shadow-sm: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    --shadow-md: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    --shadow-lg: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    
    /* Border Radius */
    --radius-sm: 0.375rem;
    --radius-md: 0.5rem;
    --radius-lg: 0.75rem;
}

/* === GLOBAL TYPOGRAPHY HIERARCHY === */
html, body, [class*="css"] {
    font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
    color: var(--neutral-800);
    line-height: 1.6;
}

/* Enhanced text hierarchy */
h1, h2, h3, h4, h5, h6 {
    font-weight: 700;
    color: var(--primary-navy);
    letter-spacing: -0.025em;
}

h1 { font-size: var(--text-2xl); font-weight: 800; }
h2 { font-size: var(--text-xl); font-weight: 700; }
h3 { font-size: var(--text-lg); font-weight: 600; }

/* Body text improvements */
.stMarkdown p {
    color: var(--neutral-700);
    font-size: var(--text-base);
    font-weight: 400;
}

/* Strong text enhancement */
strong, .stMarkdown strong {
    color: var(--primary-navy);
    font-weight: 600;
}

/* === STREAMLIT COMPONENT OVERRIDES === */

/* Main container background */
.stApp {
    background: linear-gradient(135deg, var(--neutral-50) 0%, #ffffff 100%);
}

/* Sidebar enhanced styling */
.stSidebar > div {
    background: linear-gradient(180deg, var(--neutral-50) 0%, #ffffff 100%);
    border-right: 1px solid var(--neutral-200);
}

/* Tab styling */
.stTabs [data-baseweb="tab-list"] {
    background: var(--neutral-100);
    border-radius: var(--radius-lg);
    padding: var(--space-xs);
    border: 1px solid var(--neutral-200);
}

.stTabs [data-baseweb="tab"] {
    font-weight: 500;
    color: var(--neutral-600);
    border-radius: var(--radius-md);
    padding: var(--space-md) var(--space-lg);
    transition: all 0.2s ease;
}

.stTabs [aria-selected="true"] {
    background: linear-gradient(135deg, var(--primary-blue) 0%, #2563eb 100%);
    color: white;
    font-weight: 600;
    box-shadow: var(--shadow-sm);
}

/* === DRAFT BOARD STYLING === */
.draft-pick {
    padding: var(--space-md);
    margin: var(--space-xs);
    border-radius: var(--radius-md);
    text-align: center;
    font-size: var(--text-sm);
    font-weight: 500;
    border: 1px solid var(--neutral-200);
    transition: all 0.2s ease;
    box-shadow: var(--shadow-sm);
}

.draft-pick.empty {
    background: var(--neutral-50);
    border: 1px dashed var(--neutral-300);
    color: var(--neutral-600);
}

/* Enhanced position colors with better contrast */
.draft-pick.qb { 
    background: linear-gradient(135deg, #dbeafe 0%, #bfdbfe 100%); 
    border-color: var(--primary-blue);
    color: var(--primary-navy);
}
.draft-pick.rb { 
    background: linear-gradient(135deg, #dcfce7 0%, #bbf7d0 100%); 
    border-color: var(--accent-green);
    color: var(--neutral-800);
}
.draft-pick.wr { 
    background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%); 
    border-color: var(--accent-orange);
    color: var(--neutral-800);
}
.draft-pick.te { 
    background: linear-gradient(135deg, #f3e8ff 0%, #e9d5ff 100%); 
    border-color: #a855f7;
    color: var(--neutral-800);
}
.draft-pick.k { 
    background: linear-gradient(135deg, #fce7f3 0%, #fbcfe8 100%); 
    border-color: #ec4899;
    color: var(--neutral-800);
}
.draft-pick.dst { 
    background: linear-gradient(135deg, #fee2e2 0%, #fecaca 100%); 
    border-color: var(--accent-red);
    color: var(--neutral-800);
}

/* Current pick highlight with pulse animation */
.current-pick {
    border: 3px solid var(--accent-red) !important;
    box-shadow: 0 0 0 4px rgba(239, 68, 68, 0.2);
    animation: pulse 2s infinite;
}

@keyframes pulse {
    0%, 100% { transform: scale(1); }
    50% { transform: scale(1.02); }
}

/* === ENHANCED HEADERS WITH GRADIENTS === */
.header-gradient {
    background: linear-gradient(135deg, var(--primary-navy) 0%, var(--primary-blue) 100%);
    color: white;
    padding: var(--space-lg) var(--space-xl);
    border-radius: var(--radius-lg);
    margin: var(--space-lg) 0;
    text-align: center;
    box-shadow: var(--shadow-md);
    border: 1px solid rgba(255, 255, 255, 0.1);
}

.header-gradient h3 {
    color: white;
    margin: 0;
    font-weight: 700;
    text-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
}

/* Section background improvements */
.section-bg {
    background: rgba(248, 250, 252, 0.5);
    border-radius: var(--radius-lg);
    padding: var(--space-xl);
    border: 1px solid var(--neutral-200);
    box-shadow: var(--shadow-sm);
}

/* === PLAYER SEARCH ENHANCEMENTS === */
.player-row {
    padding: var(--space-md) var(--space-lg);
    border-bottom: 1px solid var(--neutral-200);
    cursor: pointer;
    transition: all 0.3s ease;
    border-radius: var(--radius-sm);
    margin: var(--space-xs) 0;
}

.player-row:hover {
    background: linear-gradient(135deg, var(--neutral-50) 0%, var(--primary-light) 100%);
    transform: translateY(-1px);
    box-shadow: var(--shadow-sm);
}

/* Smooth pick animations */
.player-row-picked {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    color: white;
    transform: scale(1.02);
    box-shadow: 0 4px 12px rgba(16, 185, 129, 0.4);
    animation: pickSuccess 0.6s ease-out;
}

@keyframes pickSuccess {
    0% { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        transform: scale(1.02);
    }
    50% { 
        background: linear-gradient(135deg, #34d399 0%, #10b981 100%);
        transform: scale(1.05);
    }
    100% { 
        background: linear-gradient(135deg, #10b981 0%, #059669 100%);
        transform: scale(1.02);
        opacity: 0.7;
    }
}

.player-row-fade-out {
    opacity: 0.3;
    transform: translateX(-20px);
    transition: all 0.5s ease-out;
}

/* Smooth table transitions */
.player-table-container {
    transition: all 0.3s ease;
}

/* Keep expected picks collapsed by default */
.expected-picks-section {
    transition: max-height 0.3s ease-out;
    overflow: hidden;
}

.expected-picks-section.collapsed {
    max-height: 60px;
}

.expected-picks-section.expanded {
    max-height: 1000px;
}

/* === IMPROVED CONTRAST FOR DATA === */
.data-value {
    color: var(--primary-navy);
    font-weight: 600;
    font-size: var(--text-sm);
}

.data-label {
    color: var(--neutral-600);
    font-weight: 500;
    font-size: var(--text-sm);
    text-transform: uppercase;
    letter-spacing: 0.05em;
}

/* High contrast text for readability */
.high-contrast {
    color: var(--primary-navy);
    font-weight: 600;
}

.medium-contrast {
    color: var(--neutral-700);
    font-weight: 500;
}

.low-contrast {
    color: var(--neutral-600);
    font-weight: 400;
}
</style>
""", unsafe_allow_html=True)

# Initialize session state
if 'draft_manager' not in st.session_state:
    st.session_state.draft_manager = None
if 'current_session_id' not in st.session_state:
    st.session_state.current_session_id = None
if 'replacement_levels' not in st.session_state:
    st.session_state.replacement_levels = get_replacement_levels()

# Try to restore last active draft session on page refresh
# This helps maintain draft continuity across browser refreshes
if ('last_session_id' in st.session_state and 
    st.session_state.current_session_id is None and 
    st.session_state.draft_manager is None):
    
    try:
        last_session_id = st.session_state.last_session_id
        dm = DraftManager()
        
        # Check if the last session still exists
        session = dm.get_draft_session(last_session_id)
        if session:
            # Restore the session
            st.session_state.draft_manager = DraftManager(last_session_id)
            st.session_state.current_session_id = last_session_id
            st.success(f"🔄 **Restored draft session**: {session['name']}")
        else:
            # Last session was deleted, clear the reference
            del st.session_state.last_session_id
            
    except Exception as e:
        # Clear invalid last session reference
        if 'last_session_id' in st.session_state:
            del st.session_state.last_session_id

# HANDLE NO ACTIVE DRAFT - Show management interface instead of auto-creating
# This prevents accidentally creating new drafts on page refresh
if (st.session_state.current_session_id is None and 
    st.session_state.draft_manager is None and 
    not st.session_state.get('show_draft_loader', False) and
    not st.session_state.get('show_draft_creator', False) and
    not st.session_state.get('show_draft_manager', False)):
    
    # Check if there are existing drafts first
    try:
        dm = DraftManager()
        existing_sessions = dm.get_all_draft_sessions()
        
        if existing_sessions:
            # Show draft manager to load existing drafts
            st.session_state.show_draft_manager = True
            st.info("💡 **Page refreshed** - Please select your draft to continue.")
        else:
            # No existing drafts, show creation interface
            st.session_state.show_draft_creator = True
            st.info("🏈 **Welcome!** Create your first draft to get started.")
            
    except Exception as e:
        # Fall back to showing creation interface
        st.error(f"Failed to check existing drafts: {e}")
        st.session_state.show_draft_creator = True

def create_new_draft():
    """Interface for creating a new draft configuration and session."""
    st.subheader("Create New Draft")
    
    with st.form("new_draft_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            draft_name = st.text_input("Draft Name", value=f"Draft {datetime.now().strftime('%m/%d/%Y')}")
            num_teams = st.selectbox("Number of Teams", [8, 10, 12, 14, 16], index=2)
            num_rounds = st.selectbox("Number of Rounds", list(range(10, 20)), index=5)  # Default to 15
        
        with col2:
            draft_type = st.selectbox("Draft Type", ["snake", "straight"])
            session_name = st.text_input("Session Name", value=f"Session {datetime.now().strftime('%H:%M')}")
        
        # Team names section
        st.subheader("Team Names")
        st.write("Enter names for each team (optional - will default to 'Team 1', 'Team 2', etc.)")
        
        team_names = []
        cols = st.columns(2)
        for i in range(num_teams):
            col_idx = i % 2
            with cols[col_idx]:
                team_name = st.text_input(f"Team {i+1}", value=f"Team {i+1}", key=f"team_{i}")
                team_names.append(team_name)
        
        submitted = st.form_submit_button("Create Draft")
    
    # Handle form submission
        
    if submitted and draft_name:
        try:
            # Create draft configuration
            dm = DraftManager()
            config_id = dm.create_draft_config(draft_name, num_teams, num_rounds, draft_type)
            session_id = dm.create_draft_session(config_id, session_name, team_names)
            
            # Create a new DraftManager instance with the correct session_id
            st.session_state.draft_manager = DraftManager(session_id)
            st.session_state.current_session_id = session_id
            st.session_state.last_session_id = session_id  # Track for session persistence
            
            # Clear any creation/loading flags
            st.session_state.show_draft_creator = False
            st.session_state.show_draft_loader = False
            
            st.success(f"✅ Draft created successfully: {draft_name}")
            st.rerun()
            
        except Exception as e:
            st.error(f"❌ Failed to create draft: {str(e)}")
    elif submitted:
        st.error("Please enter a draft name")

def display_draft_manager():
    """Comprehensive draft management interface - load, delete, and manage drafts."""
    st.markdown("### 📊 Draft Management")
    
    # Get draft manager
    if st.session_state.draft_manager:
        dm = st.session_state.draft_manager
    else:
        dm = DraftManager()
    
    # Get all draft sessions
    sessions = dm.get_all_draft_sessions()
    
    if not sessions:
        st.info("📭 No existing drafts found.")
        if st.button("❌ Close Manager"):
            st.session_state.show_draft_manager = False
            st.rerun()
        return
    
    st.markdown(f"**Found {len(sessions)} draft session(s)**")
    
    # Add bulk actions
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("🔄 Refresh List", use_container_width=True):
            st.rerun()
    with col2:
        selected_for_bulk = st.session_state.get('bulk_selected', [])
        if selected_for_bulk and st.button(f"🗑️ Delete Selected ({len(selected_for_bulk)})", use_container_width=True, type="secondary"):
            st.session_state.show_bulk_confirm = True
    with col3:
        if st.button("❌ Close Manager", use_container_width=True):
            st.session_state.show_draft_manager = False
            st.session_state.bulk_selected = []
            st.rerun()
    
    # Handle bulk delete confirmation
    if st.session_state.get('show_bulk_confirm', False):
        st.error("⚠️ **Bulk Delete Confirmation**")
        st.write(f"You are about to delete {len(selected_for_bulk)} draft session(s). This action cannot be undone.")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✅ Confirm Bulk Delete", type="primary"):
                deleted_count = 0
                failed_count = 0
                current_session_deleted = False
                
                for session_id in selected_for_bulk:
                    if dm.delete_draft_session(session_id):
                        deleted_count += 1
                        # Check if we deleted the current session
                        if st.session_state.get('current_session_id') == session_id:
                            current_session_deleted = True
                    else:
                        failed_count += 1
                
                # Clear current session if it was deleted
                if current_session_deleted:
                    st.session_state.current_session_id = None
                    st.session_state.draft_manager = None
                    if 'last_session_id' in st.session_state:
                        del st.session_state.last_session_id
                
                if deleted_count > 0:
                    st.success(f"✅ Successfully deleted {deleted_count} draft session(s)")
                if failed_count > 0:
                    st.error(f"❌ Failed to delete {failed_count} draft session(s)")
                
                st.session_state.show_bulk_confirm = False
                st.session_state.bulk_selected = []
                st.rerun()
        
        with col2:
            if st.button("❌ Cancel Bulk Delete"):
                st.session_state.show_bulk_confirm = False
                st.rerun()
        
        st.divider()
    
    # Initialize bulk selection if not exists
    if 'bulk_selected' not in st.session_state:
        st.session_state.bulk_selected = []
    
    # Display each draft session
    for i, session in enumerate(sessions):
        # Create a container for each session
        with st.container():
            col1, col2, col3, col4, col5, col6 = st.columns([0.5, 3, 1.5, 1, 1, 1])
            
            with col1:
                # Bulk selection checkbox
                is_selected = session['id'] in st.session_state.bulk_selected
                if st.checkbox("", key=f"bulk_{session['id']}", value=is_selected, label_visibility="collapsed"):
                    if session['id'] not in st.session_state.bulk_selected:
                        st.session_state.bulk_selected.append(session['id'])
                else:
                    if session['id'] in st.session_state.bulk_selected:
                        st.session_state.bulk_selected.remove(session['id'])
            
            with col2:
                # Draft info
                draft_name = session.get('name', 'Unnamed Draft')
                config_name = session.get('config_name', 'Unknown Config')
                st.markdown(f"**{draft_name}**")
                st.caption(f"Config: {config_name}")
                
                # Additional details
                created = session.get('created_at', 'Unknown')
                picks_made = session.get('picks_made', 0)
                total_picks = session.get('num_teams', 0) * session.get('num_rounds', 0)
                completion = f"{picks_made}/{total_picks}" if total_picks > 0 else f"{picks_made} picks"
                
                st.caption(f"📅 {created} | 🎯 {completion}")
            
            with col3:
                # Status indicator
                picks_made = session.get('picks_made', 0)
                total_picks = session.get('num_teams', 0) * session.get('num_rounds', 0)
                
                if picks_made == 0:
                    st.markdown("🆕 **New Draft**")
                elif total_picks > 0 and picks_made >= total_picks:
                    st.markdown("✅ **Complete**")
                elif picks_made > 0:
                    st.markdown(f"⏳ **In Progress**")
                else:
                    st.markdown("📋 **Ready**")
            
            with col4:
                # Load button
                if st.button("📂 Load", key=f"load_{session['id']}", use_container_width=True):
                    st.session_state.current_session_id = session['id']
                    st.session_state.draft_manager = DraftManager(session['id'])
                    st.session_state.last_session_id = session['id']  # Track for session persistence
                    st.session_state.show_draft_manager = False
                    st.session_state.bulk_selected = []
                    st.success(f"✅ Loaded: {draft_name}")
                    st.rerun()
            
            with col5:
                # Individual delete button
                if st.button("🗑️", key=f"delete_{session['id']}", use_container_width=True, help="Delete this draft"):
                    st.session_state[f"confirm_delete_{session['id']}"] = True
                    st.rerun()
            
            with col6:
                # Info button
                if st.button("ℹ️", key=f"info_{session['id']}", use_container_width=True, help="View details"):
                    st.session_state[f"show_info_{session['id']}"] = True
                    st.rerun()
        
        # Handle individual delete confirmation
        if st.session_state.get(f"confirm_delete_{session['id']}", False):
            st.error(f"⚠️ **Delete '{draft_name}'?**")
            st.write("This action cannot be undone.")
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Confirm Delete", key=f"confirm_yes_{session['id']}", type="primary"):
                    if dm.delete_draft_session(session['id']):
                        st.success(f"✅ Deleted: {draft_name}")
                        # Clear current session if we deleted it
                        if st.session_state.get('current_session_id') == session['id']:
                            st.session_state.current_session_id = None
                            st.session_state.draft_manager = None
                            if 'last_session_id' in st.session_state:
                                del st.session_state.last_session_id
                    else:
                        st.error("❌ Failed to delete draft session")
                    
                    del st.session_state[f"confirm_delete_{session['id']}"]
                    st.rerun()
            
            with col2:
                if st.button("❌ Cancel", key=f"confirm_no_{session['id']}"):
                    del st.session_state[f"confirm_delete_{session['id']}"]
                    st.rerun()
        
        # Handle info display
        if st.session_state.get(f"show_info_{session['id']}", False):
            with st.expander(f"📋 Details: {draft_name}", expanded=True):
                info_col1, info_col2 = st.columns(2)
                with info_col1:
                    st.write("**Draft Configuration:**")
                    st.write(f"• Teams: {session.get('num_teams', 'Unknown')}")
                    st.write(f"• Rounds: {session.get('num_rounds', 'Unknown')}")
                    st.write(f"• Type: {session.get('draft_type', 'Unknown')}")
                
                with info_col2:
                    st.write("**Progress:**")
                    st.write(f"• Current Pick: {session.get('current_pick', 'Unknown')}")
                    st.write(f"• Current Round: {session.get('current_round', 'Unknown')}")
                    st.write(f"• Status: {session.get('status', 'Unknown')}")
                
                if st.button("❌ Close Details", key=f"close_info_{session['id']}"):
                    del st.session_state[f"show_info_{session['id']}"]
                    st.rerun()
        
        st.divider()

def load_existing_draft():
    """Legacy function - replaced by display_draft_manager()."""
    st.subheader("Load Existing Draft")
    
    dm = DraftManager()
    existing_sessions = dm.get_all_draft_sessions()
    
    if not existing_sessions:
        st.info("No existing draft sessions found.")
        return
    
    st.write("Select a draft session to resume:")
    
    for session in existing_sessions:
        with st.container():
            col1, col2, col3, col4, col5 = st.columns([3, 1, 1, 1, 1])
            
            with col1:
                st.write(f"**{session['config_name']}** - {session['name'] or 'Unnamed Session'}")
                st.write(f"Created: {session['created_at']}")
                
            with col2:
                st.write(f"{session['num_teams']} teams")
                st.write(f"{session['draft_type'].title()} draft")
                
            with col3:
                st.write(f"Round {session['current_round']}")
                st.write(f"Pick {session['current_pick']}")
                
            with col4:
                progress = session['picks_made'] / (session['num_teams'] * session['num_rounds'])
                st.write(f"{session['picks_made']} picks")
                st.write(f"{progress:.1%} complete")
                
                if st.button(f"Load Draft", key=f"load_{session['id']}"):
                    # Create a new DraftManager instance with the correct session_id
                    session_dm = DraftManager(session['id'])
                    if session_dm.load_draft_session(session['id']):
                        st.session_state.draft_manager = session_dm
                        st.session_state.current_session_id = session['id']
                        st.session_state.last_session_id = session['id']  # Track for session persistence
                        
                        # Clear any creation/loading flags
                        st.session_state.show_draft_creator = False
                        st.session_state.show_draft_loader = False
                        
                        st.success(f"✅ Loaded draft session: {session['name']}")
                        st.rerun()
                    else:
                        st.error("Failed to load draft session")
            
            with col5:
                st.write("")  # Empty space to align with other columns
                if st.button("🗑️ Delete", key=f"delete_{session['id']}", type="secondary", help="Delete this draft session"):
                    # Show confirmation dialog
                    if f"confirm_delete_{session['id']}" not in st.session_state:
                        st.session_state[f"confirm_delete_{session['id']}"] = True
                        st.warning(f"⚠️ Are you sure you want to delete '{session['config_name']}'? This action cannot be undone.")
                        st.rerun()
                
                # Handle confirmation
                if st.session_state.get(f"confirm_delete_{session['id']}", False):
                    col_confirm, col_cancel = st.columns(2)
                    with col_confirm:
                        if st.button("✅ Confirm Delete", key=f"confirm_yes_{session['id']}", type="primary"):
                            if dm.delete_draft_session(session['id']):
                                st.success(f"Deleted draft session: {session['config_name']}")
                                # Clear the confirmation flag
                                del st.session_state[f"confirm_delete_{session['id']}"]
                                st.rerun()
                            else:
                                st.error("Failed to delete draft session")
                    
                    with col_cancel:
                        if st.button("❌ Cancel", key=f"confirm_no_{session['id']}"):
                            # Clear the confirmation flag
                            del st.session_state[f"confirm_delete_{session['id']}"]
                            st.rerun()
            
            st.divider()

def display_draft_board():
    """Display the visual draft board grid."""
    if not st.session_state.draft_manager or not st.session_state.current_session_id:
        return
    
    dm = st.session_state.draft_manager
    session = dm.get_draft_session(st.session_state.current_session_id)
    
    # Check if session exists (might have been deleted)
    if not session:
        st.error("❌ Draft session no longer exists. It may have been deleted.")
        st.info("Please create a new draft or load an existing one from Settings.")
        # Clear the invalid session
        st.session_state.current_session_id = None
        st.session_state.draft_manager = None
        if 'last_session_id' in st.session_state:
            del st.session_state.last_session_id
        return
    
    picks_df = dm.get_draft_picks(st.session_state.current_session_id)
    current_pick_info = dm.get_current_pick_info(st.session_state.current_session_id)
    
    st.subheader(f"Draft Board - {session['name']} ({session['draft_type'].title()} Draft)")
    
    # Create draft order
    draft_order = dm.calculate_draft_order(session['num_teams'], session['num_rounds'], session['draft_type'])
    
    # Convert picks to dictionary for easy lookup
    picks_dict = {}
    if not picks_df.empty:
        for _, pick in picks_df.iterrows():
            picks_dict[pick['pick_number']] = pick
    
    # Display draft board
    cols = st.columns(session['num_teams'])
    
    # Get team names and settings
    team_names = dm.get_team_names(st.session_state.current_session_id)
    draft_settings = get_draft_settings(st.session_state.current_session_id)
    my_team_number = draft_settings.get('my_team_number')
    
    # Header row with team names
    for i, col in enumerate(cols):
        team_name = team_names.get(i+1, f"Team {i+1}")
        if my_team_number and i+1 == my_team_number:
            # Highlight my team
            col.markdown(f"""
            <div style="background: linear-gradient(90deg, #28a745 0%, #20c997 100%); 
                        padding: 8px; border-radius: 6px; text-align: center;">
                <strong style="color: white;">🏆 {team_name}</strong>
            </div>
            """, unsafe_allow_html=True)
        else:
            col.markdown(f"**{team_name}**")
    
    # Draft board rows
    for round_num in range(1, session['num_rounds'] + 1):
        cols = st.columns(session['num_teams'])
        
        # Get picks for this round
        round_picks = [p for p in draft_order if p[1] == round_num]
        
        for pick_info in round_picks:
            pick_number, round_number, team_number = pick_info
            col_index = team_number - 1
            
            with cols[col_index]:
                if pick_number in picks_dict:
                    # Player has been picked
                    pick = picks_dict[pick_number]
                    position_class = pick['position'].lower() if pick['position'] else 'unknown'
                    
                    # Get team logo for the player
                    team_logo_html = ""
                    team_for_logo = pick['player_team']
                    
                    # Special handling for DST positions - extract team from player name
                    if (not pick['player_team'] or pick['player_team'] == '-') and pick['position'] == 'DST':
                        team_abbr = get_team_abbr_from_defense_name(pick['player_name'])
                        if team_abbr:
                            team_for_logo = team_abbr
                    
                    if team_for_logo and team_for_logo != '-':
                        team_logo_html = get_team_logo_html(team_for_logo.lower(), size="28px")
                    
                    # Format bye week display
                    bye_week_display = f"Bye {int(pick['bye_week'])}" if pick['bye_week'] else ""
                    
                    st.markdown(f"""
                    <div class="draft-pick {position_class}">
                        <strong style="font-size: 1rem;">{pick['player_name']}</strong><br>
                        <div style="display: flex; align-items: center; justify-content: center; gap: 6px; margin: 4px 0;">
                            {team_logo_html}
                            <span>{pick['position']}</span>
                        </div>
                        {f'<div style="font-size: 0.75rem; color: var(--neutral-600); margin: 2px 0;">{bye_week_display}</div>' if bye_week_display else ''}
                        <small>Pick {pick_number}</small>
                    </div>
                    """, unsafe_allow_html=True)
                else:
                    # Empty pick slot
                    is_current = current_pick_info and pick_number == current_pick_info['pick_number']
                    current_class = "current-pick" if is_current else ""
                    
                    st.markdown(f"""
                    <div class="draft-pick empty {current_class}">
                        Pick {pick_number}<br>
                        <small>Round {round_number}</small>
                    </div>
                    """, unsafe_allow_html=True)

def display_player_search():
    """Display player search and selection interface."""
    if not st.session_state.draft_manager or not st.session_state.current_session_id:
        return
    
    dm = st.session_state.draft_manager
    
    # Check if session still exists (might have been deleted)
    session = dm.get_draft_session(st.session_state.current_session_id)
    if not session:
        st.error("❌ Draft session no longer exists. It may have been deleted.")
        st.info("Please create a new draft or load an existing one from Settings.")
        # Clear the invalid session
        st.session_state.current_session_id = None
        st.session_state.draft_manager = None
        if 'last_session_id' in st.session_state:
            del st.session_state.last_session_id
        return
    
    current_pick_info = dm.get_current_pick_info(st.session_state.current_session_id)
    
    if not current_pick_info:
        st.info("Draft is complete!")
        return
    
    # Get team names and current team name
    team_names = dm.get_team_names(st.session_state.current_session_id)
    current_team_name = team_names.get(current_pick_info['team_number'], f"Team {current_pick_info['team_number']}")
    
    # Enhanced current pick header with increased prominence
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, var(--primary-navy) 0%, var(--primary-blue) 100%);
        color: white;
        padding: var(--space-xl) var(--space-2xl);
        border-radius: var(--radius-lg);
        margin: var(--space-xl) 0;
        text-align: center;
        box-shadow: var(--shadow-lg), 0 0 20px rgba(59, 130, 246, 0.3);
        border: 2px solid rgba(255, 255, 255, 0.2);
        position: relative;
        overflow: hidden;
    ">
        <div style="
            position: absolute;
            top: -50%;
            left: -50%;
            width: 200%;
            height: 200%;
            background: radial-gradient(circle, rgba(255,255,255,0.1) 0%, transparent 70%);
            animation: pulse-glow 3s infinite;
        "></div>
        <div style="position: relative; z-index: 1;">
            <h2 style="
                color: white;
                margin: 0;
                font-weight: 800;
                font-size: var(--text-2xl);
                text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
                letter-spacing: -0.025em;
            ">
                🕑 Current Pick: #{current_pick_info['pick_number']}
            </h2>
            <p style="
                color: rgba(255, 255, 255, 0.9);
                margin: var(--space-sm) 0 0 0;
                font-size: var(--text-lg);
                font-weight: 500;
            ">
                Round {current_pick_info['round_number']} • {current_team_name}
            </p>
    </div>
    </div>
    
    <style>
    @keyframes pulse-glow {{
        0%, 100% {{ opacity: 0.3; }}
        50% {{ opacity: 0.1; }}
    }}
    </style>
    """, unsafe_allow_html=True)
    
    # Get available players
    available_players = dm.get_available_players(st.session_state.current_session_id)
    
    if available_players.empty:
        st.warning("No players available!")
        return
    
    # Get current replacement levels and recalculate if needed
    if 'replacement_levels' not in st.session_state or not st.session_state.replacement_levels:
        calculate_replacement_values()
        st.session_state.replacement_levels = get_replacement_levels()
    
    replacement_levels = st.session_state.replacement_levels
    
    # Check if replacement values are still 0 and force recalculation
    if replacement_levels and all(level.get('value', 0) == 0.0 for level in replacement_levels.values()):
        st.info("🔄 Calculating replacement values for the first time...")
        calculate_replacement_values()
        st.session_state.replacement_levels = get_replacement_levels()
        replacement_levels = st.session_state.replacement_levels
    
    # Calculate value scores
    available_players['value_score'] = available_players.apply(
        lambda row: calculate_value_score(row['projection'], row['position'], replacement_levels), 
        axis=1
    )
    
    # Calculate VONA scores using the sophisticated scarcity-based system
    available_players = calculate_vona_scores(st.session_state.current_session_id, available_players)
    
    # Clean, Minimal Search & Filter Interface
    st.markdown("""
    <div style="
        background: white;
        border-radius: 12px;
        padding: 20px;
        margin: 20px 0;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
    ">
    """, unsafe_allow_html=True)
    
    # Single clean row: Search + Core Filters
    search_col, pos_col, team_col, advanced_col = st.columns([3, 1.2, 1.2, 1])
    
    with search_col:
        search_term = st.text_input(
            "Search players by name, team, or position...", 
            key="player_search",
            placeholder="🔍 Search players...",
            label_visibility="collapsed"
        )
    
    with pos_col:
        all_positions = ['All'] + sorted(available_players['position'].unique().tolist())
        selected_position = st.selectbox("Position", all_positions, index=0, key="pos_filter")
    
    with team_col:
        all_teams = ['All'] + sorted([team for team in available_players['team'].unique() if pd.notna(team) and team != ''])
        selected_team = st.selectbox("Team", all_teams, index=0, key="team_filter")
    
    with advanced_col:
        # Advanced filters toggle
        if 'advanced_filters_open' not in st.session_state:
            st.session_state.advanced_filters_open = False
        
        st.markdown("<div style='margin-top: 26px;'></div>", unsafe_allow_html=True)
        if st.button("⚙️ More", help="Show advanced filters", use_container_width=True):
            st.session_state.advanced_filters_open = not st.session_state.advanced_filters_open
            st.rerun()
    
    # Advanced filters (expandable)
    if st.session_state.advanced_filters_open:
        st.markdown("<div style='margin-top: 15px; padding-top: 15px; border-top: 1px solid #e5e7eb;'>", unsafe_allow_html=True)
        
        adv_col1, adv_col2, adv_col3, adv_col4 = st.columns(4)
        
        with adv_col1:
            num_players = st.selectbox("Show Players", [25, 50, 100, 200], index=1, key="num_players")
        
        with adv_col2:
            # VONA debug toggle (moved here)
            show_vona_debug = st.checkbox("Show VONA Debug", key="show_vona_debug")
        
        with adv_col3:
            # Clear filters
            if st.button("🗑️ Clear All Filters", type="secondary"):
                # Clear the search term only - position and team will reset on rerun
                if 'player_search' in st.session_state:
                    del st.session_state.player_search
                st.rerun()
        
        with adv_col4:
            # Close advanced filters
            if st.button("✕ Close", type="secondary"):
                st.session_state.advanced_filters_open = False
                st.rerun()
        
        st.markdown("</div>", unsafe_allow_html=True)
    else:
        # Default values when advanced filters are closed
        num_players = 50
        show_vona_debug = False
    
    st.markdown("</div>", unsafe_allow_html=True)
    
    # Clean interface CSS
    st.markdown("""
    <style>
    /* Clean search and filter styling */
    .stTextInput > div > div > input {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        padding: 10px 12px !important;
        font-size: 14px !important;
        transition: all 0.2s ease !important;
    }
    
    .stTextInput > div > div > input:focus {
        border-color: #3b82f6 !important;
        box-shadow: 0 0 0 3px rgba(59, 130, 246, 0.1) !important;
        outline: none !important;
    }
    
    .stSelectbox > div > div > div {
        border: 1px solid #d1d5db !important;
        border-radius: 8px !important;
        font-size: 14px !important;
    }
    
    /* Clean button styling */
    .stButton > button {
        border-radius: 8px !important;
        font-size: 14px !important;
        font-weight: 500 !important;
        transition: all 0.2s ease !important;
    }
    
    /* Remove excessive spacing */
    .block-container {
        padding-top: 2rem !important;
    }
    </style>
    """, unsafe_allow_html=True)
    

    
    # Apply filters
    filtered_players = available_players.copy()
    
    # Position filter
    if selected_position != 'All':
        filtered_players = filtered_players[filtered_players['position'] == selected_position]
    
    # Team filter
    if selected_team != 'All':
        filtered_players = filtered_players[filtered_players['team'] == selected_team]
    
    # Search filter
    if search_term:
        mask = (
            filtered_players['player'].str.contains(search_term, case=False, na=False) |
            filtered_players['team'].str.contains(search_term, case=False, na=False) |
            filtered_players['position'].str.contains(search_term, case=False, na=False)
        )
        filtered_players = filtered_players[mask]
    
    # Limit number of players (sorting happens after headers)
    filtered_players = filtered_players.head(num_players)
    
    # Results summary and VONA debug info
    # Clean player count display
    st.markdown(f"""
    <div style="
        background: #f8fafc;
        border-radius: 8px;
        padding: 12px 16px;
        margin: 16px 0;
        border-left: 4px solid #3b82f6;
    ">
        <span style="color: #64748b; font-size: 14px;">📊 Showing <strong>{len(filtered_players)}</strong> available players</span>
    </div>
    """, unsafe_allow_html=True)

    
    # VONA Debug Section
    if show_vona_debug:
        with st.expander("🔧 VONA Calculation Debug", expanded=True):
            # Get debug info
            from utils.draft_logic import (calculate_picks_until_next_turn, get_predicted_next_picks, 
                                         count_positions_in_predicted_picks)
            
            current_pick = current_pick_info['pick_number']
            session = dm.get_draft_session(st.session_state.current_session_id)
            
            picks_until_next = calculate_picks_until_next_turn(
                current_pick, session['num_teams'], session['draft_type']
            )
            
            predicted_picks = get_predicted_next_picks(available_players, picks_until_next)
            position_counts = count_positions_in_predicted_picks(predicted_picks)
            
            st.markdown(f"**Current Pick:** {current_pick}")
            st.markdown(f"**Picks Until Next Turn:** {picks_until_next}")
            st.markdown(f"**Draft Type:** {session['draft_type'].title()}")
            
            st.markdown("**Expected Position Counts (before +1 adjustment):**")
            for pos, count in position_counts.items():
                scarcity_rank = count + 1 if count > 0 else 0
                st.write(f"- {pos}: {count} expected → Scarcity rank: {scarcity_rank}")
            
            if predicted_picks:
                st.markdown("**Predicted Next Picks (by ADP):**")
                for i, pick in enumerate(predicted_picks[:10], 1):  # Show first 10
                    st.write(f"{i}. {pick['player']} ({pick['position']}) - ADP: {pick['adp']:.1f}")
    
    # Expected Picks Table (Collapsible)
    if current_pick_info:
        st.markdown("---")
        
        # Get the predicted picks data
        from utils.draft_logic import (calculate_picks_until_next_turn, get_predicted_next_picks)
        
        current_pick = current_pick_info['pick_number']
        session = dm.get_draft_session(st.session_state.current_session_id)
        
        picks_until_next = calculate_picks_until_next_turn(
            current_pick, session['num_teams'], session['draft_type']
        )
        
        predicted_picks = get_predicted_next_picks(available_players, picks_until_next, exclude_current_pick_best_vona=True)
        
        # Create collapsible expander - collapsed by default for cleaner interface
        is_expanded = st.session_state.get('expected_picks_expanded', False)
        if predicted_picks:
            with st.expander(f"🎯 Expected picks before your turn ({len(predicted_picks)})", expanded=is_expanded):
                # Convert to DataFrame for easier display
                picks_df = pd.DataFrame(predicted_picks)
                
                # Add pick numbers (starting from current pick + 1)
                picks_df['pick_number'] = range(current_pick + 1, current_pick + 1 + len(picks_df))
                
                # Reorder columns to include team and VONA
                picks_df = picks_df[['pick_number', 'player', 'team', 'position', 'adp', 'vona_score']]
                
                # Display info
                st.markdown(f"**{len(predicted_picks)} picks expected before your next turn (Pick #{current_pick + picks_until_next + 1})**")
                
                # Create header row with new columns
                st.markdown(f"""
                <div style="display: grid; grid-template-columns: 0.6fr 2.5fr 1fr 0.8fr 0.8fr 0.8fr; gap: 0.5rem; margin-bottom: 0.5rem;">
                    <div class="expected-picks-header">Pick</div>
                    <div class="expected-picks-header">Player</div>
                    <div class="expected-picks-header">Team</div>
                    <div class="expected-picks-header">Pos</div>
                    <div class="expected-picks-header">ADP</div>
                    <div class="expected-picks-header">VONA</div>
                </div>
                """, unsafe_allow_html=True)
                
                # Display each predicted pick with team and VONA
                for _, pick in picks_df.iterrows():
                    pos_class = f"pos-{pick['position'].lower()}" if pick['position'] else "pos-unknown"
                    
                    # Get VONA color class
                    vona_class = "high-vona" if pick['vona_score'] > 10 else "medium-vona" if pick['vona_score'] > 0 else "low-vona"
                    
                    # Handle team display for DST positions
                    team_display = pick['team']
                    if (not pick['team'] or pick['team'] == '-') and pick['position'] == 'DST':
                        team_abbr = get_team_abbr_from_defense_name(pick['player'])
                        if team_abbr:
                            team_display = team_abbr.upper()
                    
                    # Generate FantasyPros URL for expected pick
                    expected_pick_url = generate_fantasypros_url(
                        pick['player'], 
                        pick['position'], 
                        team_display if team_display != '-' else None
                    )
                    
                    st.markdown(f"""
                    <div style="display: grid; grid-template-columns: 0.6fr 2.5fr 1fr 0.8fr 0.8fr 0.8fr; gap: 0.5rem; align-items: center;" class="expected-picks-row">
                        <div style="text-align: center; font-weight: 700;">{pick['pick_number']}</div>
                        <div style="font-weight: 600;">
                            <a href="{expected_pick_url}" target="_blank" style="
                                color: #1f2937;
                                text-decoration: none;
                                font-weight: 600;
                                transition: color 0.2s ease;
                            " onmouseover="this.style.color='#3b82f6'" onmouseout="this.style.color='#1f2937'">
                                {pick['player']}
                            </a>
                        </div>
                        <div style="text-align: center; font-weight: 600;">{team_display}</div>
                        <div style="display: flex; justify-content: center;">
                            <span class="position-circle {pos_class}" style="width: 2rem; height: 2rem; font-size: 0.8rem;">{pick["position"]}</span>
                        </div>
                        <div style="text-align: center;">{pick['adp']:.1f}</div>
                        <div style="text-align: center;" class="{vona_class}">{pick['vona_score']:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)
        else:
            with st.expander("🎯 Expected picks before your turn", expanded=is_expanded):
                st.info("No picks expected - you're up next!")
    
    if filtered_players.empty:
        st.info("No players match your filters. Try adjusting your search criteria.")
        return
    
    # Clean, minimal player table styling
    st.markdown("""
    <style>
    /* Clean expected picks styling */
    .expected-picks-header {
        background: #f1f5f9;
        color: #374151;
        padding: 12px 16px;
        border-radius: 6px;
        font-weight: 600;
        text-align: center;
        margin: 4px 0;
        font-size: 14px;
        border: 1px solid #e5e7eb;
    }
    
    .expected-picks-row {
        padding: 8px 16px;
        margin: 2px 0;
        border: 1px solid #f3f4f6;
        border-radius: 6px;
        background: #ffffff;
        display: flex;
        align-items: center;
        min-height: 40px;
        font-size: 14px;
    }
    
    .expected-picks-row:nth-child(even) {
        background: #f9fafb;
    }
    
    .expected-picks-row:hover {
        background: #f3f4f6;
        border-color: #d1d5db;
    }
    
    /* Clean button styling */
    .stButton > button {
        border-radius: 6px;
        font-weight: 500;
        font-size: 14px;
        padding: 8px 16px;
        transition: all 0.2s ease;
        border: 1px solid #d1d5db;
        height: 36px;
    }
    
    .stButton > button[kind="primary"] {
        background: #3b82f6;
        border-color: #3b82f6;
        color: white;
    }
    
    .stButton > button[kind="secondary"] {
        background: #6b7280;
        color: white;
        border-color: #6b7280;
    }
    
    /* Clean player table styling */
    .player-row {
        padding: 12px !important;
        font-size: 14px !important;
        color: #374151 !important;
        text-align: center !important;
        border-radius: 6px !important;
        margin: 2px 0 !important;
        background: #ffffff !important;
        border: 1px solid #f3f4f6 !important;
        min-height: 44px !important;
        display: flex !important;
        align-items: center !important;
        justify-content: center !important;
    }
    
    .player-row:hover {
        background: #f9fafb !important;
        border-color: #d1d5db !important;
    }
    
    /* Simple position badges */
    .position-circle {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        width: 32px;
        height: 32px;
        border-radius: 50%;
        font-size: 12px;
        font-weight: 600;
        text-align: center;
        color: white;
        border: 1px solid rgba(255,255,255,0.3);
    }
    
    /* Simple position colors */
    .position-circle.pos-qb { background: #3b82f6; }
    .position-circle.pos-rb { background: #22c55e; }
    .position-circle.pos-wr { background: #f59e0b; }
    .position-circle.pos-te { background: #a855f7; }
    .position-circle.pos-k { background: #ec4899; }
    .position-circle.pos-dst { background: #ef4444; }
    
    /* Simple value indicators */
    .value-high { background: #22c55e; color: white; font-weight: 600; }
    .value-medium { background: #f59e0b; color: white; font-weight: 600; }
    .value-low { background: #ef4444; color: white; font-weight: 600; }
    
    .high-vona { color: #22c55e; font-weight: 600; }
    .medium-vona { color: #f59e0b; font-weight: 600; }
    .low-vona { color: #6b7280; }
    
    /* Clean draft button styling */
    div[data-testid="column"]:first-child .stButton > button {
        font-size: 14px !important;
        padding: 8px 12px !important;
        border-radius: 6px !important;
        min-height: 44px !important;
        height: 44px !important;
        margin: 2px 0 !important;
        font-weight: 600 !important;
        text-align: left !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Initialize multi-column sorting state
    if 'sort_columns' not in st.session_state:
        st.session_state.sort_columns = [('adp', True)]  # List of (column, ascending) tuples - default to ADP low to high
    if 'sort_column' not in st.session_state:  # Legacy support
        st.session_state.sort_column = 'adp'
    if 'sort_ascending' not in st.session_state:  # Legacy support
        st.session_state.sort_ascending = True
    
    # Multi-sort toggle
    if 'multi_sort_enabled' not in st.session_state:
        st.session_state.multi_sort_enabled = False
    
    col_toggle, col_info = st.columns([1, 3])
    with col_toggle:
        st.session_state.multi_sort_enabled = st.checkbox("Multi-Sort", value=st.session_state.multi_sort_enabled, help="Enable to add multiple sort columns")
    
    with col_info:
        if st.session_state.multi_sort_enabled and len(st.session_state.sort_columns) > 1:
            sort_desc = " → ".join([f"{col} {'↑' if asc else '↓'}" for col, asc in st.session_state.sort_columns])
            st.caption(f"🔄 **Active Sorts**: {sort_desc}")
        elif not st.session_state.multi_sort_enabled:
            st.caption("💡 **Single Sort Mode**: Click any header to sort by that column")
    
    # Table headers with sorting
    header_cols = st.columns([3, 1.2, 1, 0.8, 0.8, 1, 1, 1])
    headers = [
        ("Player", "player"),
        ("Team", "team"), 
        ("Pos", "position"), 
        ("Bye", "bye_week"), 
        ("ADP", "adp"), 
        ("Proj", "projection"), 
        ("Value", "value_score"), 
        ("VONA", "vona_score")
    ]
    

    
    for i, (col, (header_text, column_key)) in enumerate(zip(header_cols, headers)):
        with col:
            # Create sort indicators for multi-column sorting
            sort_indicators = []
            sort_priority = None
            
            for idx, (sort_col, ascending) in enumerate(st.session_state.sort_columns):
                if sort_col == column_key:
                    sort_priority = idx + 1
                    arrow = "↑" if ascending else "↓"
                    if len(st.session_state.sort_columns) > 1:
                        sort_indicators.append(f"{arrow}{sort_priority}")
                    else:
                        sort_indicators.append(arrow)
                    break
            
            indicator_text = "".join(sort_indicators)
            button_text = f"{header_text} {indicator_text}".strip()
            
            # Enhanced tooltips with detailed information
            tooltip_info = {
                "Player": "Sort alphabetically by player name (A-Z or Z-A)",
                "Team": "Sort by NFL team abbreviation",
                "Pos": "Sort by position (QB, RB, WR, TE, K, DST)",
                "Bye": "Sort by bye week number (earliest to latest)",
                "ADP": "Sort by Average Draft Position (lower = higher draft value)",
                "Proj": "Sort by projected fantasy points",
                "Value": "Sort by Value over Replacement calculation",
                "VONA": "Sort by Value Over Next Available (scarcity-based ranking)"
            }
            help_text = tooltip_info.get(header_text, f"Sort by {header_text}") + " • Multi-sort enabled"
            
            if sort_priority == 1:
                # Primary sort button
                if st.button(button_text, key=f"sort_{column_key}", 
                            help=help_text, type="primary"):
                    handle_sort_click = True
                else:
                    handle_sort_click = False
            elif sort_priority:
                # Secondary sort button
                if st.button(button_text, key=f"sort_{column_key}", 
                            help=help_text, type="secondary"):
                    handle_sort_click = True
                else:
                    handle_sort_click = False
            else:
                # No sort priority - default button
                if st.button(button_text, key=f"sort_{column_key}", 
                            help=help_text):
                    handle_sort_click = True
                else:
                    handle_sort_click = False
            
            if handle_sort_click:
                
                # Check if multi-sort is enabled
                if st.session_state.multi_sort_enabled:
                    # Multi-sort mode: add/toggle columns
                    existing_columns = [col for col, _ in st.session_state.sort_columns]
                    
                    if column_key in existing_columns:
                        # Toggle direction for existing column
                        new_sort_columns = []
                        for sort_col, ascending in st.session_state.sort_columns:
                            if sort_col == column_key:
                                new_sort_columns.append((sort_col, not ascending))
                            else:
                                new_sort_columns.append((sort_col, ascending))
                        st.session_state.sort_columns = new_sort_columns
                    else:
                        # Add new column (up to 3 total)
                        default_ascending = column_key not in ['projection', 'value_score', 'vona_score']
                        if len(st.session_state.sort_columns) < 3:
                            st.session_state.sort_columns.append((column_key, default_ascending))
                        else:
                            # Replace the last sort column
                            st.session_state.sort_columns[-1] = (column_key, default_ascending)
                else:
                    # Single sort mode: replace current sort
                    if len(st.session_state.sort_columns) > 0 and st.session_state.sort_columns[0][0] == column_key:
                        # If clicking the current sort column, just toggle direction
                        current_ascending = st.session_state.sort_columns[0][1]
                        st.session_state.sort_columns = [(column_key, not current_ascending)]
                    else:
                        # Replace with new sort
                        default_ascending = column_key not in ['projection', 'value_score', 'vona_score']
                        st.session_state.sort_columns = [(column_key, default_ascending)]
                
                # Update legacy state for compatibility
                st.session_state.sort_column = st.session_state.sort_columns[0][0]
                st.session_state.sort_ascending = st.session_state.sort_columns[0][1]
                st.rerun()
    
    # Apply multi-column sorting
    if st.session_state.sort_columns:
        sort_cols = []
        sort_ascending = []
        
        for sort_col, ascending in st.session_state.sort_columns:
            if sort_col in filtered_players.columns:
                sort_cols.append(sort_col)
                sort_ascending.append(ascending)
        
        if sort_cols:
            # Handle NaN values specially for ADP
            if 'adp' in sort_cols:
                filtered_players = filtered_players.sort_values(
                    sort_cols, ascending=sort_ascending, na_position='last'
                )
            else:
                filtered_players = filtered_players.sort_values(
                    sort_cols, ascending=sort_ascending
                )
    

    
    # Player rows
    for idx, player in filtered_players.iterrows():
        row_cols = st.columns([3, 1.2, 1, 0.8, 0.8, 1, 1, 1])
        
        with row_cols[0]:  # Player name and draft button
            # Create two sub-columns: one for draft button, one for player name
            name_cols = st.columns([0.3, 0.7])
            
            with name_cols[0]:  # Small draft button
                if st.button("📝", key=f"draft_{idx}", help=f"Draft {player['player']}", 
                            type="primary", use_container_width=True):
                    # Store the pick in session state for smooth feedback
                    st.session_state[f"picking_{idx}"] = True
                    
                    # Record the pick
                    success = dm.record_pick(
                        player_name=player['player'],
                        player_team=player['team'],
                        position=player['position'],
                        bye_week=int(player['bye_week']) if pd.notna(player['bye_week']) else None,
                        adp=player['adp'],
                        projection=player['projection'],
                        value_score=player['value_score'],
                        vona_score=player['vona_score']
                    )
                    
                    if success:
                        # Show success message and set state for smooth transition
                        st.success(f"✅ Drafted {player['player']}!")
                        # Force expected picks to stay collapsed
                        st.session_state['expected_picks_expanded'] = False
                        # Mark this player as picked for visual feedback
                        st.session_state[f"player_picked_{player['player']}"] = True
                        
                        # Clear all search filters for easier next pick selection
                        filter_keys_to_clear = ['player_search', 'pos_filter', 'team_filter', 'advanced_filters_open']
                        for key in filter_keys_to_clear:
                            if key in st.session_state:
                                del st.session_state[key]
                        
                        st.rerun()
                    else:
                        st.error("❌ Failed to record pick")
                        st.session_state.pop(f"picking_{idx}", None)
            
            with name_cols[1]:  # Player name in all caps with FantasyPros link
                player_name_caps = player["player"].upper()
                
                # Generate FantasyPros URL
                fantasypros_url = generate_fantasypros_url(
                    player["player"], 
                    player["position"], 
                    player.get("team", None)
                )
                
                st.markdown(f"""
                <div style="
                    padding: 0.75rem 1rem;
                    font-weight: 700;
                    font-size: 0.875rem;
                    color: #1f2937;
                    font-family: 'Inter', sans-serif;
                    display: flex;
                    align-items: center;
                    justify-content: flex-start;
                    min-height: 3.5rem;
                    height: 3.5rem;
                    background: #ffffff;
                    border: 1px solid #e5e7eb;
                    border-radius: 0.375rem;
                    margin: 0.125rem 0;
                    box-sizing: border-box;
                ">
                    <a href="{fantasypros_url}" target="_blank" style="
                        color: #1f2937;
                        text-decoration: none;
                        font-weight: 700;
                        transition: color 0.2s ease;
                    " onmouseover="this.style.color='#3b82f6'" onmouseout="this.style.color='#1f2937'">
                        {player_name_caps}
                    </a>
                </div>
                """, unsafe_allow_html=True)
            


        
        with row_cols[1]:  # Team with NFL logos
            team_display = player['team'] if pd.notna(player['team']) and player['team'] != '' else '-'
            
            # Special handling for DST positions - extract team from player name
            if team_display == '-' and player['position'] == 'DST':
                team_abbr = get_team_abbr_from_defense_name(player['player'])
                if team_abbr:
                    team_display = team_abbr.upper()
                    # Use larger team logo with text
                    team_logo_html = get_team_logo_with_text_html(team_abbr.lower(), logo_size="36px")
                    st.markdown(f'<div class="player-row" style="display: flex; align-items: center; justify-content: center; padding: 0.75rem 1rem; font-size: 1.1rem; font-weight: 600;">{team_logo_html}</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="player-row">{team_display}</div>', unsafe_allow_html=True)
            elif team_display != '-':
                # Use larger team logo with text
                team_logo_html = get_team_logo_with_text_html(team_display.lower(), logo_size="36px")
                st.markdown(f'<div class="player-row" style="display: flex; align-items: center; justify-content: center; padding: 0.75rem 1rem; font-size: 1.1rem; font-weight: 600;">{team_logo_html}</div>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="player-row">{team_display}</div>', unsafe_allow_html=True)
        
        with row_cols[2]:  # Position with large colored circle
            pos_class = f"pos-{player['position'].lower()}" if player['position'] else "pos-unknown"
            st.markdown(f'<div style="display: flex; align-items: center; justify-content: center; height: 3.5rem; margin: 0.125rem 0;"><span class="position-circle {pos_class}">{player["position"]}</span></div>', unsafe_allow_html=True)
        
        with row_cols[3]:  # Bye week
            bye_display = f"{player['bye_week']:.0f}" if pd.notna(player['bye_week']) else "-"
            st.markdown(f'<div class="player-row">{bye_display}</div>', unsafe_allow_html=True)
        
        with row_cols[4]:  # ADP
            adp_display = f"{player['adp']:.1f}" if pd.notna(player['adp']) else "-"
            st.markdown(f'<div class="player-row">{adp_display}</div>', unsafe_allow_html=True)
        
        with row_cols[5]:  # Projection
            proj_display = f"{player['projection']:.1f}" if pd.notna(player['projection']) else "-"
            st.markdown(f'<div class="player-row">{proj_display}</div>', unsafe_allow_html=True)
        
        with row_cols[6]:  # Value with stoplight gradient
            value_score = player['value_score']
            if value_score >= 75:
                value_class = "value-high"
            elif value_score >= 25:
                value_class = "value-medium"
            else:
                value_class = "value-low"
            
            st.markdown(f'<div class="player-row {value_class}">{value_score:.1f}</div>', unsafe_allow_html=True)
        
        with row_cols[7]:  # VONA with enhanced styling
            vona_score = player['vona_score']
            if vona_score > 50:
                vona_class = "high-vona"
                vona_icon = "🔥"
            elif vona_score > 20:
                vona_class = "medium-vona"
                vona_icon = "⚡"
            else:
                vona_class = "low-vona"
                vona_icon = ""
            
            st.markdown(f'<div class="player-row"><span class="{vona_class}">{vona_icon} {vona_score:.1f}</span></div>', unsafe_allow_html=True)
    


def display_settings():
    """Display draft settings interface."""
    st.markdown("""
    <div class="header-gradient">
        <h3>⚙️ Draft Settings</h3>
    </div>
    """, unsafe_allow_html=True)
    
    # Draft Management Section (always visible)
    st.markdown("### 📋 Draft Management")
    
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        if st.button("🆕 Create New Draft", use_container_width=True):
            # Create a fresh draft immediately
            from datetime import datetime
            try:
                dm = DraftManager()
                
                # Create default draft config
                draft_name = f"Draft {datetime.now().strftime('%m/%d/%Y %H:%M')}"
                config_id = dm.create_draft_config(draft_name, 10, 15, "snake")
                
                # Create session with default team names
                session_name = f"Session {datetime.now().strftime('%H:%M')}"
                team_names = [f"Team {i}" for i in range(1, 11)]
                session_id = dm.create_draft_session(config_id, session_name, team_names)
                
                # Set up the new draft
                st.session_state.draft_manager = DraftManager(session_id)
                st.session_state.current_session_id = session_id
                st.session_state.last_session_id = session_id  # Track for session persistence
                
                # Calculate replacement values for this new draft
                calculate_replacement_values()
                st.session_state.replacement_levels = get_replacement_levels()
                
                st.success(f"✅ Created new draft: {draft_name}")
                st.rerun()
                
            except Exception as e:
                st.error(f"❌ Failed to create draft: {e}")
    
    with col2:
        if st.button("📊 Manage Drafts", use_container_width=True):
            st.session_state.show_draft_manager = True
            st.rerun()
    
    with col3:
        if st.session_state.current_session_id:
            if st.button("🔄 Refresh Current Draft", use_container_width=True):
                st.rerun()
    
    # Show draft manager if requested
    if st.session_state.get('show_draft_manager', False):
        display_draft_manager()
        st.markdown("---")
    
    # Rest of settings (only show if we have an active draft)
    if not st.session_state.draft_manager or not st.session_state.current_session_id:
        st.info("Create or load a draft to access additional settings.")
        return
    
    dm = st.session_state.draft_manager
    session = dm.get_draft_session(st.session_state.current_session_id)
    
    # Handle case where session data is None or corrupted
    if not session or 'num_teams' not in session:
        st.error("⚠️ Session data is corrupted or missing. Please create a new draft or load a different one.")
        return
    
    team_names = dm.get_team_names(st.session_state.current_session_id)
    current_settings = get_draft_settings(st.session_state.current_session_id)
    current_replacement_levels = get_replacement_levels()
    
    # My Team Selection (outside form for auto-save)
    st.markdown("### 🏆 My Team")
    st.write("Select which team is yours to highlight it throughout the app:")
    
    team_options = ["None"] + [f"{i}: {team_names.get(i, f'Team {i}')}" for i in range(1, session['num_teams'] + 1)]
    current_my_team = current_settings.get('my_team_number', 0)
    current_index = current_my_team if current_my_team and current_my_team <= len(team_options) - 1 else 0
    
    selected_team = st.selectbox(
        "My Team",
        team_options,
        index=current_index,
        help="This team will be highlighted in the draft board and picks",
        key="my_team_selector"
    )
    
    # Extract team number from selection
    my_team_number = None
    if selected_team != "None":
        my_team_number = int(selected_team.split(":")[0])
    
    # Auto-save team selection when changed
    previous_team = current_settings.get('my_team_number')
    if my_team_number != previous_team:
        update_draft_settings(st.session_state.current_session_id, my_team_number)
        st.success(f"✅ My Team updated to: {selected_team.split(': ')[1] if my_team_number else 'None'}")
        st.rerun()
    
    st.markdown("---")
    
    # Team Names Editor
    st.markdown("### ✏️ Edit Team Names")
    st.write("Customize the names of teams in your draft:")
    
    with st.form("team_names_form"):
        st.markdown("#### Team Names")
        
        # Create input fields for each team
        updated_team_names = {}
        
        # Get current team names
        current_team_names = dm.get_team_names(st.session_state.current_session_id)
        
        # Create columns for better layout
        num_teams = session['num_teams']
        cols_per_row = 3
        rows_needed = (num_teams + cols_per_row - 1) // cols_per_row
        
        for row in range(rows_needed):
            cols = st.columns(cols_per_row)
            for col_idx in range(cols_per_row):
                team_num = row * cols_per_row + col_idx + 1
                if team_num <= num_teams:
                    with cols[col_idx]:
                        current_name = current_team_names.get(team_num, f"Team {team_num}")
                        updated_team_names[team_num] = st.text_input(
                            f"Team {team_num}",
                            value=current_name,
                            key=f"team_name_{team_num}",
                            help=f"Enter custom name for Team {team_num}"
                        )
        
        # Form submission buttons
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Update Team Names", type="primary"):
                try:
                    # Convert dictionary to list format expected by update_team_names
                    team_names_list = [updated_team_names[i] for i in range(1, num_teams + 1)]
                    # Update team names in database
                    dm.update_team_names(team_names_list, st.session_state.current_session_id)
                    st.success("✅ Team names updated successfully!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error updating team names: {e}")
        
        with col2:
            if st.form_submit_button("🔄 Reset to Defaults"):
                try:
                    # Reset to default team names
                    default_names_list = [f"Team {i}" for i in range(1, num_teams + 1)]
                    dm.update_team_names(default_names_list, st.session_state.current_session_id)
                    st.success("✅ Team names reset to defaults!")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Error resetting team names: {e}")
    
    st.markdown("---")
    
    # Replacement Levels Configuration
    st.markdown("### 📊 Replacement Levels")
    st.write("Set the rank for replacement level calculations. For example, QB=22 means the 22nd highest projected QB is the replacement level.")
    
    # Calculate current replacement values
    if st.button("🔄 Recalculate Replacement Values", help="Update replacement values based on current projections"):
        with st.spinner("Calculating replacement values..."):
            replacement_values = calculate_replacement_values()
            st.success("Replacement values updated!")
            st.session_state.replacement_levels = get_replacement_levels()
            st.rerun()
    
    # Display current replacement levels with editing
    st.markdown("#### Current Replacement Levels:")
    
    with st.form("replacement_levels_form"):
        new_levels = {}
        
        col1, col2, col3 = st.columns(3)
        
        positions = ['QB', 'RB', 'WR', 'TE', 'K', 'DST']
        for i, position in enumerate(positions):
            current_rank = current_replacement_levels.get(position, {}).get('rank', 22)
            current_value = current_replacement_levels.get(position, {}).get('value', 0)
            
            col_idx = i % 3
            with [col1, col2, col3][col_idx]:
                st.markdown(f"**{position}**")
                new_rank = st.number_input(
                    f"Rank",
                    min_value=1,
                    max_value=200,
                    value=current_rank,
                    key=f"rank_{position}",
                    help=f"Current replacement value: {current_value:.1f} points"
                )
                new_levels[position] = new_rank
                
                # Show current replacement value
                if current_value:
                    st.caption(f"Replacement: {current_value:.1f} pts")
        
        # Form submission
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("💾 Update Settings", type="primary"):
                # Update replacement levels
                update_replacement_levels(new_levels)
                
                # Team settings are now auto-saved above
                
                # Recalculate replacement values
                calculate_replacement_values()
                
                # Update session state
                st.session_state.replacement_levels = get_replacement_levels()
                
                st.success("Settings updated successfully!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("🔄 Reset to Defaults"):
                default_levels = {'QB': 22, 'RB': 36, 'WR': 48, 'TE': 18, 'K': 12, 'DST': 12}
                update_replacement_levels(default_levels)
                calculate_replacement_values()
                st.session_state.replacement_levels = get_replacement_levels()
                st.success("Reset to default values!")
                st.rerun()
    
    # Current Settings Summary
    st.markdown("### 📋 Current Settings Summary")
    
    summary_col1, summary_col2 = st.columns(2)
    
    with summary_col1:
        st.markdown("**My Team:**")
        if my_team_number:
            my_team_name = team_names.get(my_team_number, f"Team {my_team_number}")
            st.write(f"🏆 {my_team_name}")
        else:
            st.write("Not selected")
    
    with summary_col2:
        st.markdown("**Replacement Level Ranks:**")
        for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
            rank = current_replacement_levels.get(position, {}).get('rank', 'N/A')
            value = current_replacement_levels.get(position, {}).get('value', 0)
            st.write(f"{position}: Rank {rank} ({value:.1f} pts)")

def edit_team_names():
    """Interface for editing team names."""
    if not st.session_state.draft_manager or not st.session_state.current_session_id:
        return
    
    dm = st.session_state.draft_manager
    session = dm.get_draft_session(st.session_state.current_session_id)
    current_team_names = dm.get_team_names(st.session_state.current_session_id)
    
    st.subheader("Edit Team Names")
    
    with st.form("edit_team_names_form"):
        st.write("Update team names:")
        
        new_team_names = []
        cols = st.columns(2)
        
        for i in range(1, session['num_teams'] + 1):
            col_idx = (i - 1) % 2
            with cols[col_idx]:
                current_name = current_team_names.get(i, f"Team {i}")
                new_name = st.text_input(f"Team {i}", value=current_name, key=f"edit_team_{i}")
                new_team_names.append(new_name)
        
        col1, col2 = st.columns(2)
        with col1:
            if st.form_submit_button("Update Team Names"):
                dm.update_team_names(new_team_names, st.session_state.current_session_id)
                st.session_state.show_team_editor = False
                st.success("Team names updated!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_team_editor = False
                st.rerun()

def display_draft_summary():
    """Display enhanced draft picks summary in sidebar."""
    if not st.session_state.draft_manager or not st.session_state.current_session_id:
        return
    
    dm = st.session_state.draft_manager
    picks_df = dm.get_draft_picks(st.session_state.current_session_id)
    team_names = dm.get_team_names(st.session_state.current_session_id)
    
    st.markdown("## 📋 Draft Tracker")
    
    if picks_df.empty:
        st.info("No picks recorded yet.")
        return
    
    # Display total picks with current round info
    if not picks_df.empty:
        current_round = picks_df['round_number'].max()
        picks_in_current_round = len(picks_df[picks_df['round_number'] == current_round])
        st.markdown(f"**Total Picks**: {len(picks_df)} | **Round {current_round}**: {picks_in_current_round} picks")
    
    # Enhanced Undo button with warning styling and hover effect
    st.markdown("""
    <style>
    /* Undo button styling */
    div[data-testid="stButton"] button[kind="secondary"] {
        background: linear-gradient(135deg, #dc2626, #b91c1c) !important;
        color: white !important;
        border: 2px solid #991b1b !important;
        font-weight: 700 !important;
        transition: all 0.2s ease !important;
        box-shadow: 0 3px 6px rgba(220, 38, 38, 0.3) !important;
        border-radius: 8px !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:hover {
        background: linear-gradient(135deg, #b91c1c, #991b1b) !important;
        transform: translateY(-2px) !important;
        box-shadow: 0 5px 12px rgba(220, 38, 38, 0.4) !important;
    }
    div[data-testid="stButton"] button[kind="secondary"]:active {
        transform: translateY(0px) !important;
        box-shadow: 0 2px 4px rgba(220, 38, 38, 0.5) !important;
    }
    </style>
    """, unsafe_allow_html=True)
    
    if st.button("🔙 Undo Last Pick", use_container_width=True, type="secondary"):
        if dm.undo_last_pick(st.session_state.current_session_id):
            st.success("Last pick undone!")
            st.rerun()
        else:
            st.error("No picks to undo")
    
    st.markdown("---")
    st.markdown("### 📜 Recent Picks")
    
    # Display recent picks grouped by round with enhanced styling
    recent_picks = picks_df.tail(20).sort_values('pick_number', ascending=False)
    
    # Group picks by round for better organization
    current_round_display = None
    pick_count = 0
    
    for _, pick in recent_picks.iterrows():
        team_name = team_names.get(pick['team_number'], f"Team {pick['team_number']}")
        
        # Show round header when round changes
        if current_round_display != pick['round_number']:
            if current_round_display is not None:
                st.markdown("---")
            # Enhanced round header with design system
            st.markdown(f"""
            <div class="header-gradient" style="padding: var(--space-md) var(--space-lg); margin: var(--space-md) 0;">
                <h4 style="color: white; margin: 0; font-size: var(--text-base);">🏆 Round {pick['round_number']}</h4>
            </div>
            """, unsafe_allow_html=True)
            current_round_display = pick['round_number']
        

        
        # Safely handle projection and VONA score formatting
        proj_display = f"{pick['projection']:.1f}" if pd.notna(pick['projection']) else "N/A"
        vona_display = f"{pick['vona_score']:.1f}" if pd.notna(pick['vona_score']) else "N/A"
        
        # Simple, clean pick display with subtle alternating backgrounds
        if pick_count % 2 == 0:
            st.markdown('<div style="background-color: #f8fafc; padding: 10px; border-radius: 4px; margin: 2px 0;">', unsafe_allow_html=True)
        else:
            st.markdown('<div style="background-color: #ffffff; padding: 10px; border-radius: 4px; margin: 2px 0;">', unsafe_allow_html=True)
        
        # Pick header
        st.write(f"**Pick #{pick['pick_number']} - {team_name}**")
        
        # Player info with logo in a clean row
        col1, col2 = st.columns([1, 6])
        with col1:
            # Team logo (smaller and cleaner)
            team_for_logo = pick['player_team']
            
            # Special handling for DST positions - extract team from player name
            if (not pick['player_team'] or pick['player_team'] == '' or pick['player_team'] == '-') and pick['position'] == 'DST':
                team_abbr = get_team_abbr_from_defense_name(pick['player_name'])
                if team_abbr:
                    team_for_logo = team_abbr
            
            if team_for_logo and team_for_logo != '' and team_for_logo != '-':
                try:
                    team_logo_html = get_team_logo_html(team_for_logo.lower(), size="20px")
                    st.markdown(team_logo_html, unsafe_allow_html=True)
                except (AttributeError, KeyError, FileNotFoundError):
                    st.write(team_for_logo[:3].upper())
            else:
                st.write("—")
        
        with col2:
            st.write(f"**{pick['player_name']}** ({pick['position']})")
            st.markdown(f'<span class="data-label">Proj:</span> <span class="data-value">{proj_display}</span> | <span class="data-label">VONA:</span> <span class="data-value">{vona_display}</span>', unsafe_allow_html=True)
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        pick_count += 1

def display_my_team():
    """Display my drafted players with comprehensive stats and analysis."""
    if not st.session_state.draft_manager or not st.session_state.current_session_id:
        return
    
    dm = st.session_state.draft_manager
    session = dm.get_draft_session(st.session_state.current_session_id)
    picks_df = dm.get_draft_picks(st.session_state.current_session_id)
    draft_settings = get_draft_settings(st.session_state.current_session_id)
    my_team_number = draft_settings.get('my_team_number')
    team_names = dm.get_team_names(st.session_state.current_session_id)
    
    # Header with team name
    my_team_name = team_names.get(my_team_number, f"Team {my_team_number}") if my_team_number else "My Team"
    st.markdown(f"""
    <div style="
        background: linear-gradient(135deg, #1e40af 0%, #3730a3 100%);
        color: white;
        padding: 20px;
        border-radius: 12px;
        margin-bottom: 20px;
        text-align: center;
    ">
        <h2 style="margin: 0; color: white; font-weight: 700; text-shadow: 0 2px 4px rgba(0,0,0,0.3);">🏆 {my_team_name}</h2>
    </div>
    """, unsafe_allow_html=True)
    
    if not my_team_number:
        st.warning("⚠️ Please set 'My Team' in the Settings tab to see your drafted players here.")
        return
    
    # Get my picks
    if picks_df.empty:
        st.info("No players drafted yet. Start drafting to see your team!")
        return
    
    my_picks = picks_df[picks_df['team_number'] == my_team_number].copy()
    
    if my_picks.empty:
        st.info("You haven't drafted any players yet.")
        return
    
    # Sort by pick number
    my_picks = my_picks.sort_values('pick_number')
    
    # Enhanced team summary stats
    total_players = len(my_picks)
    total_projection = my_picks['projection'].sum() if 'projection' in my_picks.columns else 0
    avg_adp = my_picks['adp'].mean() if 'adp' in my_picks.columns else 0
    avg_vona = my_picks['vona_score'].mean() if 'vona_score' in my_picks.columns and not my_picks['vona_score'].isna().all() else 0
    total_value = my_picks['value_score'].sum() if 'value_score' in my_picks.columns else 0
    
    # Position counts
    pos_counts = my_picks['position'].value_counts()
    
    # Advanced metrics
    early_picks = my_picks[my_picks['round_number'] <= 3]
    late_picks = my_picks[my_picks['round_number'] > 10]
    value_picks = my_picks[my_picks['vona_score'] > 20] if 'vona_score' in my_picks.columns else pd.DataFrame()
    
    # Compact summary dashboard
    col1, col2, col3, col4, col5, col6 = st.columns(6)
    
    with col1:
        st.metric("Players", total_players, help="Total drafted players")
    
    with col2:
        st.metric("Proj Points", f"{total_projection:.0f}" if total_projection > 0 else "N/A", help="Total projected fantasy points")
    
    with col3:
        st.metric("Avg ADP", f"{avg_adp:.1f}" if avg_adp > 0 else "N/A", help="Average draft position")
    
    with col4:
        vona_delta = "Great" if avg_vona > 15 else "Good" if avg_vona > 5 else None
        st.metric("Avg VONA", f"{avg_vona:.1f}" if avg_vona else "N/A", delta=vona_delta, help="Average value over next available")
    
    with col5:
        st.metric("Value Picks", len(value_picks), help="Players with VONA > 20")
    
    with col6:
        st.metric("Rounds", len(my_picks['round_number'].unique()), help="Rounds participated")
    
    # Roster composition table
    st.markdown("### 📋 Roster Breakdown")
    
    # Create comprehensive player table
    display_df = my_picks[['pick_number', 'round_number', 'player_name', 'position', 'player_team', 'bye_week',
                          'projection', 'adp', 'value_score', 'vona_score']].copy()
    
    # Format the data for display
    display_df['Round'] = display_df['round_number'].astype(int)
    display_df['Pick'] = display_df['pick_number'].astype(int)
    display_df['Player'] = display_df['player_name']
    display_df['Pos'] = display_df['position']
    display_df['Team'] = display_df['player_team'].fillna('-')
    display_df['Bye'] = display_df['bye_week'].fillna('').astype(str).replace('nan', '').replace('', '-')
    display_df['Proj'] = display_df['projection'].round(1)
    display_df['ADP'] = display_df['adp'].round(1)
    display_df['Value'] = display_df['value_score'].round(1)
    display_df['VONA'] = display_df['vona_score'].round(1)
    
    # Select final columns (Round first, then Pick)
    final_df = display_df[['Round', 'Pick', 'Player', 'Pos', 'Team', 'Bye', 'Proj', 'ADP', 'Value', 'VONA']]
    
    # Display with custom styling
    st.dataframe(
        final_df,
        use_container_width=True,
        hide_index=True,
        column_config={
            'Round': st.column_config.NumberColumn('Round', width='small'),
            'Pick': st.column_config.NumberColumn('Pick', width='small'),
            'Player': st.column_config.TextColumn('Player', width='medium'),
            'Pos': st.column_config.TextColumn('Pos', width='small'),
            'Team': st.column_config.TextColumn('Team', width='small'),
            'Bye': st.column_config.TextColumn('Bye', width='small'),
            'Proj': st.column_config.NumberColumn('Proj', width='small', format='%.1f'),
            'ADP': st.column_config.NumberColumn('ADP', width='small', format='%.1f'),
            'Value': st.column_config.NumberColumn('Value', width='small', format='%.1f'),
            'VONA': st.column_config.NumberColumn('VONA', width='small', format='%.1f')
        }
    )
    
    # Position analysis (simplified)
    st.markdown("### 📊 Position Analysis")
    pos_data = []
    for pos in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
        count = pos_counts.get(pos, 0)
        if count > 0:
            pos_players = my_picks[my_picks['position'] == pos]
            avg_proj = pos_players['projection'].mean()
            pos_data.append({
                'Position': pos,
                'Count': count,
                'Avg Proj': f"{avg_proj:.1f}" if pd.notna(avg_proj) else "N/A"
            })
    
    if pos_data:
        pos_df = pd.DataFrame(pos_data)
        st.dataframe(
            pos_df, 
            use_container_width=True, 
            hide_index=True,
            column_config={
                'Position': st.column_config.TextColumn('Position', width='medium'),
                'Count': st.column_config.NumberColumn('Count', width='small'),
                'Avg Proj': st.column_config.TextColumn('Avg Proj', width='small')
            }
        )
    


def display_player_card(player):
    """Display a single player card with stats."""
    from utils.logo_utils import get_team_logo_html
    
    # Get team logo
    team_logo_html = ""
    if player['player_team'] and player['player_team'] != '-':
        team_logo_html = get_team_logo_html(player['player_team'].lower(), size="20px")
    
    # Format stats safely
    projection = f"{player['projection']:.1f}" if pd.notna(player['projection']) else "N/A"
    adp = f"{player['adp']:.1f}" if pd.notna(player['adp']) else "N/A"
    vona = f"{player['vona_score']:.1f}" if pd.notna(player['vona_score']) else "N/A"
    value = f"{player['value_score']:.1f}" if pd.notna(player['value_score']) else "N/A"
    
    # Use Streamlit components instead of raw HTML
    with st.container():
        st.markdown(f"""
        <div style="
            background: white;
            border: 1px solid #e5e7eb;
            border-radius: 8px;
            padding: 16px;
            margin: 8px 0;
            box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
        ">
            <div style="margin-bottom: 12px;">
                <strong style="font-size: 18px; color: #1f2937;">{player['player_name']}</strong>
                <span style="color: #6b7280; margin-left: 8px;">({player['position']})</span>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        # Stats in a clean format
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Pick", f"#{int(player['pick_number'])} (R{int(player['round_number'])})")
            st.metric("Projection", projection)
        with col2:
            st.metric("ADP", adp)
            vona_delta = "Good Value" if pd.notna(player['vona_score']) and player['vona_score'] > 20 else None
            st.metric("VONA", vona, delta=vona_delta)

# Main app
def main():
    st.title("🏈 Live Draft Tool")
    
    # Navigation
    nav_col1, nav_col2, nav_col3 = st.columns([1, 1, 2])
    with nav_col1:
        if st.button("📊 Main Dashboard", use_container_width=True):
            st.switch_page("app.py")
    
    with nav_col2:
        if st.button("⚙️ Admin Dashboard", use_container_width=True):
            st.switch_page("pages/admin.py")
    
    # Sidebar for draft tracking (only show if we have an active draft)
    if st.session_state.current_session_id is not None:
        with st.sidebar:
            display_draft_summary()
    
    # Show draft interface (we always have a draft now)
    # Only show creation interface if explicitly loading a draft
    if st.session_state.get('show_draft_loader', False):
        st.subheader("Load Existing Draft")
        load_existing_draft()
    else:
        # Main draft interface
        tab1, tab2, tab3, tab4 = st.tabs(["Draft Board", "Player Search", "My Team", "Settings"])
        
        with tab1:
            display_draft_board()
            
            # Draft controls
            st.markdown("---")
            col1, col2, col3 = st.columns([1, 1, 1])
            
            with col1:
                if st.button("New Draft"):
                    st.session_state.current_session_id = None
                    st.session_state.draft_manager = None
                    st.rerun()
            
            with col2:
                if st.button("Refresh Board"):
                    st.rerun()
            
            with col3:
                if st.button("Edit Team Names"):
                    st.session_state.show_team_editor = True
                    st.rerun()
            

            
            # Team name editor
            if st.session_state.get('show_team_editor', False):
                edit_team_names()
        
        with tab2:
            display_player_search()
        
        with tab3:
            display_my_team()
        
        with tab4:
            display_settings()

if __name__ == "__main__":
    main()