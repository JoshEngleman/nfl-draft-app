# VONA (Value Over Next Available) Calculation

## Overview
VONA is a dynamic value calculation that considers positional scarcity based on expected draft flow using ADP data.

## Example Scenario
- **Current Pick**: 5th overall
- **League Size**: 10 teams
- **Picks until next turn**: 10 picks (picks 6-15)

## Step-by-Step Process

### 1. Identify Next Available Picks
- After pick 5, there are 10 picks before we pick again (6-15)
- Use ADP to predict which players will be drafted in picks 6-15

### 2. Count Expected Positions Drafted
From the ADP-predicted picks 6-15:
- **RBs expected**: 4 players
- **WRs expected**: 6 players  
- **QBs expected**: 0 players
- **TEs expected**: 0 players
- **K expected**: 0 players
- **DST expected**: 0 players

### 3. Calculate Position Scarcity Adjustment
- If count = 0: Keep at 0 (no scarcity adjustment)
- If count > 0: Add 1 to the count
- **RB scarcity**: 4 + 1 = 5
- **WR scarcity**: 6 + 1 = 7
- **QB scarcity**: 0 (no adjustment)

### 4. Calculate VONA Scores
- **RB VONA**: Player's Value Score - 5th highest remaining RB Value Score
- **WR VONA**: Player's Value Score - 7th highest remaining WR Value Score  
- **QB VONA**: 0 (no scarcity, so no VONA benefit)

## Implementation Logic
```python
def calculate_vona(current_pick, num_teams, available_players, draft_picks_until_next_turn):
    # 1. Get next N picks based on ADP
    next_picks = get_predicted_next_picks(available_players, draft_picks_until_next_turn)
    
    # 2. Count positions in predicted picks
    position_counts = count_positions_in_picks(next_picks)
    
    # 3. Apply scarcity adjustment (+1 if > 0)
    scarcity_adjustments = {pos: (count + 1 if count > 0 else 0) 
                           for pos, count in position_counts.items()}
    
    # 4. Calculate VONA for each available player
    vona_scores = {}
    for player in available_players:
        if scarcity_adjustments[player.position] == 0:
            vona_scores[player] = 0
        else:
            nth_best_value = get_nth_best_value_at_position(
                available_players, 
                player.position, 
                scarcity_adjustments[player.position]
            )
            vona_scores[player] = player.value_score - nth_best_value
    
    return vona_scores
```

## Key Benefits
1. **Dynamic Scarcity**: Adjusts based on expected draft flow
2. **Positional Runs**: Accounts for when positions will be heavily drafted
3. **Forward-Looking**: Considers what will be available at your next pick
4. **Draft Position Aware**: Different calculations based on where you're drafting