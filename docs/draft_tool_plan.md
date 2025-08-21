# Live Draft Tool - Implementation Plan

## Overview
Convert Excel-based live draft utility to Streamlit app with real-time value calculations and pick tracking.

## Core Requirements

### Draft Configuration
- [ ] Set number of teams (8, 10, 12, 14, 16, etc.)
- [ ] Set number of rounds (typically 15-17 for fantasy)
- [ ] Choose draft type: Snake vs Straight
- [ ] Name/save draft configurations

### Live Draft Interface
- [ ] Visual draft board showing all picks by round/team
- [ ] Easy player search and assignment to picks
- [ ] Real-time pick tracking
- [ ] Undo/edit previous picks

### Recommendation Engine
- [ ] Value calculation formula (user's proprietary model)
- [ ] Real-time recalculation after each pick
- [ ] Display top recommended players for active drafter
- [ ] Consider positional needs, scarcity, value over replacement

### Data Integration
- [ ] Use projections data for player values
- [ ] Use ADP data for market value/reach analysis
- [ ] Combine both for comprehensive player valuation

## Technical Architecture

### Database Schema
```sql
-- Draft configurations
CREATE TABLE draft_configs (
    id INTEGER PRIMARY KEY,
    name TEXT,
    num_teams INTEGER,
    num_rounds INTEGER,
    draft_type TEXT, -- 'snake' or 'straight'
    created_at TIMESTAMP
);

-- Individual draft sessions
CREATE TABLE draft_sessions (
    id INTEGER PRIMARY KEY,
    config_id INTEGER,
    current_pick INTEGER,
    status TEXT, -- 'active', 'completed', 'paused'
    created_at TIMESTAMP
);

-- Draft picks tracking
CREATE TABLE draft_picks (
    id INTEGER PRIMARY KEY,
    session_id INTEGER,
    pick_number INTEGER,
    round_number INTEGER,
    team_number INTEGER,
    player_name TEXT,
    player_team TEXT,
    position TEXT,
    picked_at TIMESTAMP
);
```

### Streamlit App Structure
```
📁 pages/
  📄 01_projections.py (existing tables)
  📄 02_draft_tool.py (new live draft interface)
  
📁 components/
  📄 draft_board.py (visual draft grid)
  📄 player_search.py (searchable player list)
  📄 value_calculator.py (recommendation engine)
  
📁 utils/
  📄 draft_logic.py (snake/straight draft order)
  📄 value_formulas.py (user's recommendation model)
```

## Key Features to Implement

### 1. Draft Setup Page
- Form to configure new draft
- Load existing draft configurations
- Validation for reasonable team/round counts

### 2. Live Draft Board
- Grid layout: Rounds (rows) x Teams (columns)
- Color coding for different positions
- Click-to-assign player functionality
- Real-time updates

### 3. Player Search & Assignment
- Searchable/filterable player list
- Show projections + ADP data
- Quick assign to current pick
- Remove/reassign players

### 4. Recommendation Engine
- Calculate player values after each pick
- Consider remaining roster needs
- Factor in positional scarcity
- Display top 5-10 recommendations

### 5. Draft Analytics
- Team roster summaries
- Positional analysis
- Value tracking (steals/reaches)
- Export draft results

## Questions for User

1. **Value Formula**: What specific factors does your recommendation formula consider?
   - Projected points vs ADP?
   - Positional scarcity?
   - Roster construction needs?
   - Other proprietary factors?

2. **Draft Flow**: 
   - Do you want to track all teams' picks or just focus on your team?
   - Should the tool auto-advance to next pick or manual control?

3. **Player Data**:
   - Any additional player attributes needed (injury status, etc.)?
   - Should we pull in additional data sources?

4. **Interface Preferences**:
   - Preferred layout for the draft board?
   - Most important info to display for each player?

5. **Export/Save**:
   - What format for exporting draft results?
   - Need to save/resume draft sessions?

## Implementation Priority
1. Basic draft configuration and setup
2. Draft board visualization
3. Player search and assignment
4. Snake draft logic
5. Recommendation engine integration
6. Advanced analytics and export

Would you like me to proceed with this plan, or would you prefer to discuss any specific aspects first?