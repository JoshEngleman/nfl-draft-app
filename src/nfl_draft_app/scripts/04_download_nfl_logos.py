#!/usr/bin/env python3
"""
Script to download NFL team logos from ESPN or other reliable sources
"""

import os
import requests
import json
from urllib.parse import urlparse
import time

# Team mapping with official NFL.com logo API (most reliable source)
# Based on pattern: https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/{TEAM_ABBR}
# Note: NFL.com uses different abbreviations for some teams
TEAM_LOGOS = {
    'ari': {'name': 'Arizona Cardinals', 'nfl_abbr': 'ARI'},
    'atl': {'name': 'Atlanta Falcons', 'nfl_abbr': 'ATL'},
    'bal': {'name': 'Baltimore Ravens', 'nfl_abbr': 'BAL'},
    'buf': {'name': 'Buffalo Bills', 'nfl_abbr': 'BUF'},
    'car': {'name': 'Carolina Panthers', 'nfl_abbr': 'CAR'},
    'chi': {'name': 'Chicago Bears', 'nfl_abbr': 'CHI'},
    'cin': {'name': 'Cincinnati Bengals', 'nfl_abbr': 'CIN'},
    'cle': {'name': 'Cleveland Browns', 'nfl_abbr': 'CLE'},
    'dal': {'name': 'Dallas Cowboys', 'nfl_abbr': 'DAL'},
    'den': {'name': 'Denver Broncos', 'nfl_abbr': 'DEN'},
    'det': {'name': 'Detroit Lions', 'nfl_abbr': 'DET'},
    'gb': {'name': 'Green Bay Packers', 'nfl_abbr': 'GB'},
    'hou': {'name': 'Houston Texans', 'nfl_abbr': 'HOU'},
    'ind': {'name': 'Indianapolis Colts', 'nfl_abbr': 'IND'},
    'jac': {'name': 'Jacksonville Jaguars', 'nfl_abbr': 'JAX'},  # NFL uses JAX
    'kc': {'name': 'Kansas City Chiefs', 'nfl_abbr': 'KC'},
    'lv': {'name': 'Las Vegas Raiders', 'nfl_abbr': 'LV'},
    'lac': {'name': 'Los Angeles Chargers', 'nfl_abbr': 'LAC'},
    'lar': {'name': 'Los Angeles Rams', 'nfl_abbr': 'LAR'},
    'mia': {'name': 'Miami Dolphins', 'nfl_abbr': 'MIA'},
    'min': {'name': 'Minnesota Vikings', 'nfl_abbr': 'MIN'},
    'ne': {'name': 'New England Patriots', 'nfl_abbr': 'NE'},
    'no': {'name': 'New Orleans Saints', 'nfl_abbr': 'NO'},
    'nyg': {'name': 'New York Giants', 'nfl_abbr': 'NYG'},
    'nyj': {'name': 'New York Jets', 'nfl_abbr': 'NYJ'},
    'phi': {'name': 'Philadelphia Eagles', 'nfl_abbr': 'PHI'},
    'pit': {'name': 'Pittsburgh Steelers', 'nfl_abbr': 'PIT'},
    'sf': {'name': 'San Francisco 49ers', 'nfl_abbr': 'SF'},
    'sea': {'name': 'Seattle Seahawks', 'nfl_abbr': 'SEA'},
    'tb': {'name': 'Tampa Bay Buccaneers', 'nfl_abbr': 'TB'},
    'ten': {'name': 'Tennessee Titans', 'nfl_abbr': 'TEN'},
    'was': {'name': 'Washington Commanders', 'nfl_abbr': 'WAS'}
}

def create_logos_directory():
    """Create directory for storing logos if it doesn't exist."""
    logos_dir = 'data/nfl_logos'
    os.makedirs(logos_dir, exist_ok=True)
    return logos_dir

def download_image(url, filepath):
    """Download an image from URL to filepath."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.nfl.com/'
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()
        
        with open(filepath, 'wb') as f:
            f.write(response.content)
        
        print(f"  ✓ Downloaded: {os.path.basename(filepath)}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to download {url}: {e}")
        return False

def download_nfl_logos():
    """Download NFL logos from official NFL.com API."""
    logos_dir = create_logos_directory()
    logo_urls = {}
    successful_downloads = 0
    
    print("🏈 Starting NFL Logo Download from NFL.com Official API...")
    print(f"📁 Logos will be saved to: {logos_dir}")
    
    for team_abbr, team_info in TEAM_LOGOS.items():
        team_name = team_info['name']
        nfl_abbr = team_info['nfl_abbr']
        
        print(f"\n🏈 Processing {team_name} ({team_abbr.upper()})...")
        
        # Construct the official NFL.com logo URL
        logo_url = f"https://static.www.nfl.com/t_headshot_desktop/f_auto/league/api/clubs/logos/{nfl_abbr}"
        
        logo_filename = f"{team_abbr}_logo.png"
        logo_filepath = os.path.join(logos_dir, logo_filename)
        
        print(f"   Downloading from: {logo_url}")
        
        if download_image(logo_url, logo_filepath):
            logo_urls[team_abbr] = {
                'team_name': team_name,
                'logo_url': logo_url,
                'local_path': logo_filepath,
                'nfl_abbr': nfl_abbr
            }
            successful_downloads += 1
        else:
            print(f"  ⚠️  Could not download logo for {team_name}")
        
        # Be respectful to NFL's servers
        time.sleep(0.5)
    
    # Save the logo mapping to JSON
    mapping_file = os.path.join(logos_dir, 'logo_mapping.json')
    with open(mapping_file, 'w') as f:
        json.dump(logo_urls, f, indent=2)
    
    print(f"\n✅ Logo download complete!")
    print(f"📊 Downloaded {successful_downloads}/{len(TEAM_LOGOS)} team logos")
    print(f"💾 Logo mapping saved to: {mapping_file}")
    
    return logo_urls

def main():
    """Main function to download NFL logos."""
    logos = download_nfl_logos()
    
    if logos:
        print("\n🎉 Successfully downloaded logos for:")
        for abbr, info in logos.items():
            print(f"   {abbr.upper()}: {info['team_name']}")
    else:
        print("\n❌ No logos were downloaded successfully")

if __name__ == "__main__":
    main()