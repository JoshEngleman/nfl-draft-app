"""
Draft logic utilities for managing draft order, pick calculations, and draft flow.
"""
import sqlite3
import pandas as pd
import re
from typing import List, Tuple, Dict, Optional
from datetime import datetime
from .database import create_database_engine, get_database_config, get_db_file_path

DB_FILE = get_db_file_path()  # Legacy compatibility - will use PostgreSQL when available

def generate_fantasypros_url(player_name: str, position: str, team: str = None) -> str:
    """Generate FantasyPros player profile URL.
    
    Args:
        player_name: Player's full name (e.g., "Josh Allen", "Bijan Robinson")
        position: Player position (QB, RB, WR, TE, K, DST)
        team: Team abbreviation (for DST)
    
    Returns:
        Full FantasyPros URL
    """
    if position == 'DST':
        # For defenses: https://www.fantasypros.com/nfl/teams/{team-name}-defense.php
        team_names = {
            'ARI': 'arizona', 'ATL': 'atlanta', 'BAL': 'baltimore', 'BUF': 'buffalo',
            'CAR': 'carolina', 'CHI': 'chicago', 'CIN': 'cincinnati', 'CLE': 'cleveland',
            'DAL': 'dallas', 'DEN': 'denver', 'DET': 'detroit', 'GB': 'green-bay',
            'HOU': 'houston', 'IND': 'indianapolis', 'JAC': 'jacksonville', 'KC': 'kansas-city',
            'LV': 'las-vegas', 'LAC': 'los-angeles-chargers', 'LAR': 'los-angeles-rams',
            'MIA': 'miami', 'MIN': 'minnesota', 'NE': 'new-england', 'NO': 'new-orleans',
            'NYG': 'new-york-giants', 'NYJ': 'new-york-jets', 'PHI': 'philadelphia',
            'PIT': 'pittsburgh', 'SF': 'san-francisco', 'SEA': 'seattle', 'TB': 'tampa-bay',
            'TEN': 'tennessee', 'WAS': 'washington'
        }
        team_slug = team_names.get(team, team.lower() if team else 'unknown')
        return f"https://www.fantasypros.com/nfl/teams/{team_slug}-defense.php"
    
    # For players: https://www.fantasypros.com/nfl/players/{player-name-slug}.php
    # Convert name to URL slug
    name_slug = player_name.lower()
    # Replace spaces with hyphens
    name_slug = re.sub(r'\s+', '-', name_slug)
    # Remove special characters except hyphens
    name_slug = re.sub(r'[^a-z0-9\-]', '', name_slug)
    # Remove multiple consecutive hyphens
    name_slug = re.sub(r'-+', '-', name_slug)
    # Remove leading/trailing hyphens
    name_slug = name_slug.strip('-')
    
    # Only add position suffix for players with known name conflicts
    # Josh Allen QB needs -qb suffix because of Josh Allen LB
    POSITION_SUFFIX_PLAYERS = {
        'josh-allen': 'qb',  # Josh Allen QB vs Josh Allen LB
        # Add more as we discover conflicts
    }
    
    if name_slug in POSITION_SUFFIX_PLAYERS:
        suffix = POSITION_SUFFIX_PLAYERS[name_slug]
        name_slug += f'-{suffix}'
    
    return f"https://www.fantasypros.com/nfl/players/{name_slug}.php"

class DraftManager:
    def __init__(self, session_id: int = None):
        self.session_id = session_id
        # Don't store connection as instance variable to avoid threading issues
        
    def _get_connection(self):
        """Get a new database connection for each operation."""
        return sqlite3.connect(DB_FILE)
    
    def create_draft_config(self, name: str, num_teams: int, num_rounds: int, draft_type: str) -> int:
        """Create a new draft configuration and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO draft_configs (name, num_teams, num_rounds, draft_type)
            VALUES (?, ?, ?, ?)
        ''', (name, num_teams, num_rounds, draft_type))
        conn.commit()
        config_id = cursor.lastrowid
        conn.close()
        return config_id
    
    def create_draft_session(self, config_id: int, session_name: str = None, team_names: List[str] = None) -> int:
        """Create a new draft session and return its ID."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO draft_sessions (config_id, name)
            VALUES (?, ?)
        ''', (config_id, session_name))
        session_id = cursor.lastrowid
        
        # Insert team names if provided
        if team_names:
            for i, team_name in enumerate(team_names, 1):
                cursor.execute('''
                    INSERT INTO draft_teams (session_id, team_number, team_name)
                    VALUES (?, ?, ?)
                ''', (session_id, i, team_name))
        
        conn.commit()
        conn.close()
        self.session_id = session_id
        return session_id
    
    def get_draft_config(self, config_id: int) -> Dict:
        """Get draft configuration details."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM draft_configs WHERE id = ?', (config_id,))
        row = cursor.fetchone()
        result = None
        if row:
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
        conn.close()
        return result
    
    def get_draft_session(self, session_id: int = None) -> Dict:
        """Get draft session details."""
        if session_id is None:
            session_id = self.session_id
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ds.*, dc.name as config_name, dc.num_teams, dc.num_rounds, dc.draft_type
            FROM draft_sessions ds
            JOIN draft_configs dc ON ds.config_id = dc.id
            WHERE ds.id = ?
        ''', (session_id,))
        row = cursor.fetchone()
        result = None
        if row:
            columns = [description[0] for description in cursor.description]
            result = dict(zip(columns, row))
        conn.close()
        return result
    
    def get_all_draft_sessions(self) -> List[Dict]:
        """Get all draft sessions for loading existing drafts."""
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT ds.*, dc.name as config_name, dc.num_teams, dc.num_rounds, dc.draft_type,
                   COUNT(dp.id) as picks_made
            FROM draft_sessions ds
            JOIN draft_configs dc ON ds.config_id = dc.id
            LEFT JOIN draft_picks dp ON ds.id = dp.session_id
            GROUP BY ds.id
            ORDER BY ds.updated_at DESC, ds.created_at DESC
        ''')
        rows = cursor.fetchall()
        results = []
        if rows:
            columns = [description[0] for description in cursor.description]
            results = [dict(zip(columns, row)) for row in rows]
        conn.close()
        return results
    
    def get_most_recent_session(self) -> Optional[Dict]:
        """Get the most recently updated draft session."""
        sessions = self.get_all_draft_sessions()
        return sessions[0] if sessions else None
    
    def load_draft_session(self, session_id: int):
        """Load an existing draft session."""
        # Verify the session exists and is valid
        session = self.get_draft_session(session_id)
        if session:
            self.session_id = session_id
            return True
        return False
    
    def get_team_names(self, session_id: int = None) -> Dict[int, str]:
        """Get team names for a session, returns dict mapping team_number -> team_name."""
        if session_id is None:
            session_id = self.session_id
        
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute('''
            SELECT team_number, team_name 
            FROM draft_teams 
            WHERE session_id = ? 
            ORDER BY team_number
        ''', (session_id,))
        
        team_names = dict(cursor.fetchall())
        conn.close()
        return team_names
    
    def update_team_names(self, team_names: List[str], session_id: int = None):
        """Update team names for a session."""
        if session_id is None:
            session_id = self.session_id
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Delete existing team names
        cursor.execute('DELETE FROM draft_teams WHERE session_id = ?', (session_id,))
        
        # Insert new team names
        for i, team_name in enumerate(team_names, 1):
            cursor.execute('''
                INSERT INTO draft_teams (session_id, team_number, team_name)
                VALUES (?, ?, ?)
            ''', (session_id, i, team_name))
        
        conn.commit()
        conn.close()
    
    def calculate_draft_order(self, num_teams: int, num_rounds: int, draft_type: str) -> List[Tuple[int, int, int]]:
        """
        Calculate the complete draft order.
        Returns list of (pick_number, round_number, team_number) tuples.
        """
        draft_order = []
        pick_number = 1
        
        for round_num in range(1, num_rounds + 1):
            if draft_type == 'snake' and round_num % 2 == 0:
                # Even rounds go in reverse order for snake draft
                teams = list(range(num_teams, 0, -1))
            else:
                # Odd rounds (or straight draft) go in normal order
                teams = list(range(1, num_teams + 1))
            
            for team in teams:
                draft_order.append((pick_number, round_num, team))
                pick_number += 1
        
        return draft_order
    
    def get_current_pick_info(self, session_id: int = None) -> Dict:
        """Get information about the current pick."""
        if session_id is None:
            session_id = self.session_id
            
        session = self.get_draft_session(session_id)
        if not session:
            return None
        
        draft_order = self.calculate_draft_order(
            session['num_teams'], 
            session['num_rounds'], 
            session['draft_type']
        )
        
        current_pick = session['current_pick']
        if current_pick <= len(draft_order):
            pick_info = draft_order[current_pick - 1]  # Convert to 0-based index
            return {
                'pick_number': pick_info[0],
                'round_number': pick_info[1],
                'team_number': pick_info[2],
                'total_picks': len(draft_order)
            }
        return None
    
    def record_pick(self, player_name: str, player_team: str = None, position: str = None, 
                   bye_week: int = None, adp: float = None, projection: float = None,
                   value_score: float = None, vona_score: float = None) -> bool:
        """Record a draft pick and advance to the next pick."""
        if not self.session_id:
            return False
        
        current_pick_info = self.get_current_pick_info()
        if not current_pick_info:
            return False
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Record the pick
        cursor.execute('''
            INSERT INTO draft_picks 
            (session_id, pick_number, round_number, team_number, player_name, 
             player_team, position, bye_week, adp, projection, value_score, vona_score)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            self.session_id, current_pick_info['pick_number'], current_pick_info['round_number'],
            current_pick_info['team_number'], player_name, player_team, position,
            bye_week, adp, projection, value_score, vona_score
        ))
        
        # Advance to next pick
        next_pick = current_pick_info['pick_number'] + 1
        session = self.get_draft_session()
        
        if next_pick <= current_pick_info['total_picks']:
            # Calculate next pick info
            draft_order = self.calculate_draft_order(
                session['num_teams'], session['num_rounds'], session['draft_type']
            )
            next_pick_info = draft_order[next_pick - 1]
            
            cursor.execute('''
                UPDATE draft_sessions 
                SET current_pick = ?, current_round = ?, current_team = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (next_pick, next_pick_info[1], next_pick_info[2], self.session_id))
        else:
            # Draft is complete
            cursor.execute('''
                UPDATE draft_sessions 
                SET status = 'completed', updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (self.session_id,))
        
        conn.commit()
        conn.close()
        return True
    
    def get_draft_picks(self, session_id: int = None) -> pd.DataFrame:
        """Get all picks for a draft session."""
        if session_id is None:
            session_id = self.session_id
        
        conn = self._get_connection()
        df = pd.read_sql_query('''
            SELECT * FROM draft_picks 
            WHERE session_id = ? 
            ORDER BY pick_number
        ''', conn, params=(session_id,))
        conn.close()
        return df
    
    def get_available_players(self, session_id: int = None) -> pd.DataFrame:
        """Get all players not yet drafted in this session."""
        if session_id is None:
            session_id = self.session_id
        
        conn = self._get_connection()
        
        # Get all players from projections and ADP data
        query = '''
            SELECT 
                p.player,
                p.team,
                'QB' as position,
                a.bye_week,
                a.avg_adp as adp,
                p.fantasy_points as projection
            FROM qb_projections p
            LEFT JOIN overall_adp a ON p.player = a.player
            WHERE p.player NOT IN (
                SELECT player_name FROM draft_picks WHERE session_id = ?
            )
            
            UNION ALL
            
            SELECT 
                p.player,
                p.team,
                'RB' as position,
                a.bye_week,
                a.avg_adp as adp,
                p.fantasy_points as projection
            FROM rb_projections p
            LEFT JOIN overall_adp a ON p.player = a.player
            WHERE p.player NOT IN (
                SELECT player_name FROM draft_picks WHERE session_id = ?
            )
            
            UNION ALL
            
            SELECT 
                p.player,
                p.team,
                'WR' as position,
                a.bye_week,
                a.avg_adp as adp,
                p.fantasy_points as projection
            FROM wr_projections p
            LEFT JOIN overall_adp a ON p.player = a.player
            WHERE p.player NOT IN (
                SELECT player_name FROM draft_picks WHERE session_id = ?
            )
            
            UNION ALL
            
            SELECT 
                p.player,
                p.team,
                'TE' as position,
                a.bye_week,
                a.avg_adp as adp,
                p.fantasy_points as projection
            FROM te_projections p
            LEFT JOIN overall_adp a ON p.player = a.player
            WHERE p.player NOT IN (
                SELECT player_name FROM draft_picks WHERE session_id = ?
            )
            
            UNION ALL
            
            SELECT 
                p.player,
                p.team,
                'K' as position,
                a.bye_week,
                a.avg_adp as adp,
                p.fantasy_points as projection
            FROM k_projections p
            LEFT JOIN overall_adp a ON p.player = a.player
            WHERE p.player NOT IN (
                SELECT player_name FROM draft_picks WHERE session_id = ?
            )
            
            UNION ALL
            
            SELECT 
                p.team_name as player,
                '' as team,
                'DST' as position,
                a.bye_week,
                a.avg_adp as adp,
                p.fantasy_points as projection
            FROM dst_projections p
            LEFT JOIN overall_adp a ON p.team_name = a.player
            WHERE p.team_name NOT IN (
                SELECT player_name FROM draft_picks WHERE session_id = ?
            )
            
            ORDER BY adp ASC NULLS LAST
        '''
        
        df = pd.read_sql_query(query, conn, params=(session_id,) * 6)
        conn.close()
        return df
    
    def undo_last_pick(self, session_id: int = None) -> bool:
        """Undo the most recent pick and go back one pick."""
        if session_id is None:
            session_id = self.session_id
        
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Get the most recent pick
        cursor.execute('''
            SELECT pick_number, round_number, team_number 
            FROM draft_picks 
            WHERE session_id = ? 
            ORDER BY pick_number DESC 
            LIMIT 1
        ''', (session_id,))
        
        last_pick = cursor.fetchone()
        if not last_pick:
            conn.close()
            return False
        
        # Delete the last pick
        cursor.execute('''
            DELETE FROM draft_picks 
            WHERE session_id = ? AND pick_number = ?
        ''', (session_id, last_pick[0]))
        
        # Update session to go back to that pick
        cursor.execute('''
            UPDATE draft_sessions 
            SET current_pick = ?, current_round = ?, current_team = ?, 
                status = 'active', updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        ''', (last_pick[0], last_pick[1], last_pick[2], session_id))
        
        conn.commit()
        conn.close()
        return True
    
    def delete_draft_session(self, session_id: int) -> bool:
        """Delete a draft session and all associated data."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        try:
            # Delete in order due to foreign key constraints
            cursor.execute('DELETE FROM draft_picks WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM draft_settings WHERE session_id = ?', (session_id,))
            cursor.execute('DELETE FROM draft_teams WHERE session_id = ?', (session_id,))
            
            # Get config_id before deleting the session
            cursor.execute('SELECT config_id FROM draft_sessions WHERE id = ?', (session_id,))
            config_result = cursor.fetchone()
            config_id = config_result[0] if config_result else None
            
            # Delete the session
            cursor.execute('DELETE FROM draft_sessions WHERE id = ?', (session_id,))
            
            # Check if this config is used by other sessions, if not, delete it
            if config_id:
                cursor.execute('SELECT COUNT(*) FROM draft_sessions WHERE config_id = ?', (config_id,))
                remaining_sessions = cursor.fetchone()[0]
                if remaining_sessions == 0:
                    cursor.execute('DELETE FROM draft_configs WHERE id = ?', (config_id,))
            
            conn.commit()
            conn.close()
            return True
            
        except Exception as e:
            conn.rollback()
            conn.close()
            return False

def get_replacement_levels() -> Dict[str, Dict]:
    """Get replacement level data for all positions."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT position, replacement_rank, replacement_value FROM replacement_levels')
    levels = {}
    for row in cursor.fetchall():
        levels[row[0]] = {
            'rank': row[1],
            'value': row[2]
        }
    conn.close()
    return levels

def update_replacement_levels(levels: Dict[str, int]):
    """Update replacement level ranks for all positions."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    for position, rank in levels.items():
        cursor.execute('''
            UPDATE replacement_levels 
            SET replacement_rank = ?, updated_at = CURRENT_TIMESTAMP 
            WHERE position = ?
        ''', (rank, position))
    conn.commit()
    conn.close()

def calculate_replacement_values():
    """Calculate actual replacement values based on current projections and ranks."""
    conn = sqlite3.connect(DB_FILE)
    
    # Get replacement ranks
    cursor = conn.cursor()
    cursor.execute('SELECT position, replacement_rank FROM replacement_levels')
    replacement_ranks = dict(cursor.fetchall())
    
    replacement_values = {}
    
    for position, rank in replacement_ranks.items():
        if position == 'DST':
            # DST uses team_name from dst_projections
            cursor.execute('''
                SELECT fantasy_points 
                FROM dst_projections 
                ORDER BY fantasy_points DESC 
                LIMIT 1 OFFSET ?
            ''', (rank - 1,))
        else:
            # Other positions use standard projections tables
            table_name = f"{position.lower()}_projections"
            cursor.execute(f'''
                SELECT fantasy_points 
                FROM {table_name} 
                ORDER BY fantasy_points DESC 
                LIMIT 1 OFFSET ?
            ''', (rank - 1,))
        
        result = cursor.fetchone()
        if result:
            replacement_values[position] = result[0]
            # Update the database with calculated value
            cursor.execute('''
                UPDATE replacement_levels 
                SET replacement_value = ?, updated_at = CURRENT_TIMESTAMP 
                WHERE position = ?
            ''', (result[0], position))
        else:
            replacement_values[position] = 0.0
    
    conn.commit()
    conn.close()
    return replacement_values

def calculate_value_score(projection: float, position: str, replacement_levels: Dict[str, Dict]) -> float:
    """Calculate value score (projection - replacement level)."""
    if position in replacement_levels and projection is not None:
        replacement_value = replacement_levels[position].get('value', 0)
        if replacement_value:
            return projection - replacement_value
    return 0.0

def get_draft_settings(session_id: int) -> Dict:
    """Get draft settings for a session."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM draft_settings WHERE session_id = ?', (session_id,))
    row = cursor.fetchone()
    result = None
    if row:
        columns = [description[0] for description in cursor.description]
        result = dict(zip(columns, row))
    conn.close()
    return result or {}

def update_draft_settings(session_id: int, my_team_number: int = None, notes: str = None):
    """Update draft settings for a session."""
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO draft_settings (session_id, my_team_number, notes, updated_at)
        VALUES (?, ?, ?, CURRENT_TIMESTAMP)
    ''', (session_id, my_team_number, notes))
    conn.commit()
    conn.close()

def calculate_vona_scores(session_id: int, available_players: pd.DataFrame) -> pd.DataFrame:
    """Calculate VONA (Value Over Next Available) scores for all available players."""
    
    # Get draft session info
    dm = DraftManager(session_id)
    session = dm.get_draft_session(session_id)
    current_pick_info = dm.get_current_pick_info(session_id)
    
    if not current_pick_info:
        # Draft is complete, return 0 VONA for all
        available_players['vona_score'] = 0.0
        return available_players
    
    current_pick = current_pick_info['pick_number']
    num_teams = session['num_teams']
    draft_type = session['draft_type']
    
    # Calculate picks until next turn for current team
    picks_until_next_turn = calculate_picks_until_next_turn(
        current_pick, num_teams, draft_type
    )
    
    # Get predicted next picks based on ADP
    # For VONA calculation, assume current pick takes the player with best ADP (most likely to be drafted)
    predicted_picks = get_predicted_next_picks(available_players, picks_until_next_turn, exclude_current_pick_best_vona=False)
    
    # Count positions in predicted picks
    position_counts = count_positions_in_predicted_picks(predicted_picks)
    
    # Apply scarcity adjustment (+1 if > 0, else 0)
    scarcity_adjustments = {}
    for position in ['QB', 'RB', 'WR', 'TE', 'K', 'DST']:
        count = position_counts.get(position, 0)
        scarcity_adjustments[position] = count + 1 if count > 0 else 0
    
    # Calculate VONA scores
    vona_scores = []
    
    for _, player in available_players.iterrows():
        position = player['position']
        scarcity_rank = scarcity_adjustments.get(position, 0)
        
        if scarcity_rank == 0:
            # No scarcity - use max value at position as baseline
            position_players = available_players[
                available_players['position'] == position
            ].copy()
            
            if len(position_players) > 0:
                # Get the highest value score at this position
                max_value_at_position = position_players['value_score'].max()
                vona_score = player['value_score'] - max_value_at_position
            else:
                vona_score = 0.0
        else:
            # Get the Nth best value score at this position
            position_players = available_players[
                available_players['position'] == position
            ].copy()
            
            if len(position_players) >= scarcity_rank:
                # Sort by value_score descending and get the Nth best
                position_players = position_players.sort_values(
                    'value_score', ascending=False
                )
                nth_best_value = position_players.iloc[scarcity_rank - 1]['value_score']
                vona_score = player['value_score'] - nth_best_value
            else:
                # Not enough players at position, use minimum value
                vona_score = player['value_score']
        
        vona_scores.append(vona_score)
    
    available_players['vona_score'] = vona_scores
    return available_players

def calculate_picks_until_next_turn(current_pick: int, num_teams: int, draft_type: str) -> int:
    """Calculate how many picks until the current team picks again."""
    
    # Determine current round and position in round (1-indexed)
    current_round = ((current_pick - 1) // num_teams) + 1
    position_in_round = ((current_pick - 1) % num_teams) + 1
    
    if draft_type == 'snake':
        # Remaining picks in current round
        remaining_in_round = num_teams - position_in_round
        
        # Calculate position in next round
        if current_round % 2 == 1:  # Currently in odd round (1, 2, 3, ..., N)
            # Next round is even (N, N-1, N-2, ..., 1)
            # Your position in next round is (N - position + 1)
            next_round_position = num_teams - position_in_round + 1
        else:  # Currently in even round (N, N-1, N-2, ..., 1)
            # Next round is odd (1, 2, 3, ..., N)
            # Your position in next round is (N - position + 1)
            next_round_position = num_teams - position_in_round + 1
        
        # Picks before your turn in next round
        picks_in_next_round = next_round_position - 1
        
        return remaining_in_round + picks_in_next_round
        
    else:  # Straight draft
        # In straight draft, always same position each round
        remaining_in_round = num_teams - position_in_round
        picks_in_next_round = position_in_round - 1
        return remaining_in_round + picks_in_next_round

def get_predicted_next_picks(available_players: pd.DataFrame, num_picks: int, exclude_current_pick_best_vona: bool = False) -> List[Dict]:
    """Get predicted next picks based on ADP.
    
    Args:
        available_players: DataFrame of available players
        num_picks: Number of picks to predict
        exclude_current_pick_best_vona: If True, assume current pick takes highest VONA player
                                       and exclude them from predictions
    """
    
    # Filter out players without ADP data and sort by ADP
    players_with_adp = available_players[
        available_players['adp'].notna()
    ].copy()
    
    # If we should exclude the best VONA player (assume current pick takes them)
    if exclude_current_pick_best_vona and len(players_with_adp) > 0:
        # Check if VONA scores exist (they might not during VONA calculation)
        if 'vona_score' in players_with_adp.columns:
            # Find the player with highest VONA score
            best_vona_player = players_with_adp.loc[players_with_adp['vona_score'].idxmax()]
            # Remove this player from consideration
            players_with_adp = players_with_adp[players_with_adp['player'] != best_vona_player['player']].copy()
    
    players_with_adp = players_with_adp.sort_values('adp')
    
    # Take the next N players by ADP
    predicted_picks = []
    for i in range(min(num_picks, len(players_with_adp))):
        player = players_with_adp.iloc[i]
        pick_data = {
            'player': player['player'],
            'position': player['position'],
            'team': player['team'],
            'adp': player['adp']
        }
        
        # Only include VONA score if it exists
        if 'vona_score' in players_with_adp.columns:
            pick_data['vona_score'] = player['vona_score']
        else:
            pick_data['vona_score'] = 0.0  # Default value during VONA calculation
            
        predicted_picks.append(pick_data)
    
    return predicted_picks

def count_positions_in_predicted_picks(predicted_picks: List[Dict]) -> Dict[str, int]:
    """Count how many of each position are in the predicted picks."""
    
    position_counts = {'QB': 0, 'RB': 0, 'WR': 0, 'TE': 0, 'K': 0, 'DST': 0}
    
    for pick in predicted_picks:
        position = pick['position']
        if position in position_counts:
            position_counts[position] += 1
    
    return position_counts