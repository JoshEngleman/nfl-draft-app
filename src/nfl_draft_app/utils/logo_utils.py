#!/usr/bin/env python3
"""
Utility functions for handling NFL team logos
"""

import os
import json
import base64
from typing import Dict, Optional

def get_logo_mapping() -> Dict:
    """Load the logo mapping from JSON file."""
    mapping_file = 'data/nfl_logos/logo_mapping.json'
    
    if os.path.exists(mapping_file):
        with open(mapping_file, 'r') as f:
            return json.load(f)
    return {}

def get_logo_base64(team_abbr: str) -> Optional[str]:
    """Get base64 encoded logo for a team abbreviation."""
    logo_mapping = get_logo_mapping()
    
    if team_abbr.lower() in logo_mapping:
        logo_path = logo_mapping[team_abbr.lower()]['local_path']
        
        if os.path.exists(logo_path):
            with open(logo_path, 'rb') as f:
                logo_data = f.read()
                return base64.b64encode(logo_data).decode('utf-8')
    
    return None

def get_team_logo_html(team_abbr: str, size: str = "30px", alt_text: Optional[str] = None) -> str:
    """
    Generate HTML for displaying a team logo.
    
    Args:
        team_abbr: Team abbreviation (e.g., 'buf', 'dal')
        size: CSS size for the logo (default: "30px")
        alt_text: Alt text for the image (defaults to team abbreviation)
    
    Returns:
        HTML string for the logo image or team abbreviation if logo not found
    """
    logo_base64 = get_logo_base64(team_abbr)
    
    if logo_base64:
        if alt_text is None:
            alt_text = team_abbr.upper()
        
        return f'<img src="data:image/png;base64,{logo_base64}" alt="{alt_text}" style="width: {size}; height: {size}; object-fit: contain; vertical-align: middle;" />'
    else:
        # Fallback to text if logo not found
        return f'<span style="font-weight: bold; font-size: 0.9rem;">{team_abbr.upper()}</span>'

def get_team_logo_with_text_html(team_abbr: str, logo_size: str = "24px") -> str:
    """
    Generate HTML for displaying a team logo with the team abbreviation next to it.
    
    Args:
        team_abbr: Team abbreviation (e.g., 'buf', 'dal')
        logo_size: CSS size for the logo (default: "24px")
    
    Returns:
        HTML string with logo and text
    """
    logo_base64 = get_logo_base64(team_abbr)
    
    if logo_base64:
        return f'<div style="display: flex; align-items: center; gap: 10px;"><img src="data:image/png;base64,{logo_base64}" alt="{team_abbr.upper()}" style="width: {logo_size}; height: {logo_size}; object-fit: contain;" /><span style="font-weight: 700; font-size: 1.1rem;">{team_abbr.upper()}</span></div>'
    else:
        # Fallback to text only if logo not found
        return f'<span style="font-weight: bold; font-size: 1.1rem;">{team_abbr.upper()}</span>'

def list_available_logos() -> Dict[str, str]:
    """List all available team logos."""
    logo_mapping = get_logo_mapping()
    return {abbr: info['team_name'] for abbr, info in logo_mapping.items()}

def is_logo_available(team_abbr: str) -> bool:
    """Check if a logo is available for the given team abbreviation."""
    return get_logo_base64(team_abbr) is not None

def get_defense_team_mapping() -> Dict[str, str]:
    """
    Create a mapping from defense team names to team abbreviations.
    
    Returns:
        Dictionary mapping full team names to abbreviations
    """
    return {
        "ARIZONA CARDINALS": "ari",
        "ATLANTA FALCONS": "atl", 
        "BALTIMORE RAVENS": "bal",
        "BUFFALO BILLS": "buf",
        "CAROLINA PANTHERS": "car",
        "CHICAGO BEARS": "chi",
        "CINCINNATI BENGALS": "cin",
        "CLEVELAND BROWNS": "cle",
        "DALLAS COWBOYS": "dal",
        "DENVER BRONCOS": "den",
        "DETROIT LIONS": "det",
        "GREEN BAY PACKERS": "gb",
        "HOUSTON TEXANS": "hou",
        "INDIANAPOLIS COLTS": "ind",
        "JACKSONVILLE JAGUARS": "jac",
        "KANSAS CITY CHIEFS": "kc",
        "LAS VEGAS RAIDERS": "lv",
        "LOS ANGELES CHARGERS": "lac",
        "LOS ANGELES RAMS": "lar",
        "MIAMI DOLPHINS": "mia",
        "MINNESOTA VIKINGS": "min",
        "NEW ENGLAND PATRIOTS": "ne",
        "NEW ORLEANS SAINTS": "no",
        "NEW YORK GIANTS": "nyg",
        "NEW YORK JETS": "nyj",
        "PHILADELPHIA EAGLES": "phi",
        "PITTSBURGH STEELERS": "pit",
        "SAN FRANCISCO 49ERS": "sf",
        "SEATTLE SEAHAWKS": "sea",
        "TAMPA BAY BUCCANEERS": "tb",
        "TENNESSEE TITANS": "ten",
        "WASHINGTON COMMANDERS": "was"
    }

def get_team_abbr_from_defense_name(defense_name: str) -> Optional[str]:
    """
    Extract team abbreviation from defense team name.
    
    Args:
        defense_name: Full team name (e.g., "PHILADELPHIA EAGLES")
    
    Returns:
        Team abbreviation (e.g., "phi") or None if not found
    """
    defense_mapping = get_defense_team_mapping()
    return defense_mapping.get(defense_name.upper())