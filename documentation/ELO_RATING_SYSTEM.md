# ELO Rating System Documentation

## Overview

The PadelGo ELO rating system provides skill-based matchmaking and tournament categorization for players. It tracks individual player performance across all games and adjusts ratings based on match outcomes and opponent strength.

## Core Concepts

### What is ELO?

ELO is a rating system originally designed for chess that calculates the relative skill levels of players. In PadelGo:

- Higher ELO = Higher skill level
- Ratings change based on game results
- Beating stronger opponents yields more points
- Losing to weaker opponents costs more points

### Rating Ranges

| Category | ELO Range | Skill Level | Description |
|----------|-----------|-------------|-------------|
| **Bronze** | 800-1099 | Beginner | New to padel, learning basics |
| **Silver** | 1100-1399 | Intermediate | Consistent play, good fundamentals |
| **Gold** | 1400-1699 | Advanced | Strong tactical awareness |
| **Platinum** | 1700+ | Elite | Exceptional skill and experience |

## ELO Calculation

### Basic Formula

```
New Rating = Old Rating + K × (Actual Score - Expected Score)
```

Where:
- **K-factor**: Determines rating volatility (32 for regular games, 40 for tournaments)
- **Actual Score**: 1 for win, 0 for loss
- **Expected Score**: Probability of winning based on rating difference

### Expected Score Calculation

```
Expected Score = 1 / (1 + 10^((Opponent Rating - Player Rating) / 400))
```

### Team Games (Padel)

For team-based games, individual ratings are updated based on:

1. **Team Average**: Combined ELO of both players divided by 2
2. **Individual Contribution**: Each player's rating affects team strength
3. **Shared Outcome**: Both players on winning team gain points

## Implementation Details

### Starting Rating

- **New Players**: Begin with ELO 1200 (Silver category)
- **Provisional Period**: First 10 games have higher K-factor (40)
- **Calibration**: Initial placement based on early performance

### K-Factor Variations

| Game Type | K-Factor | Reason |
|-----------|----------|---------|
| Regular Game | 32 | Standard competitive play |
| Tournament | 40 | Higher stakes, more accurate |
| Provisional | 40 | New player calibration |

### Rating Floors and Ceilings

- **Minimum Rating**: 100 (prevents negative ratings)
- **Maximum Rating**: 3000 (theoretical ceiling)
- **Decay**: Inactive players may have ratings adjusted

## Database Schema

### Core Tables

```sql
-- User ratings stored in users table
ALTER TABLE users ADD COLUMN elo_rating DECIMAL(8,2) DEFAULT 1200.00;

-- Rating history tracking
CREATE TABLE elo_rating_history (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    game_id INTEGER REFERENCES games(id),
    old_rating DECIMAL(8,2),
    new_rating DECIMAL(8,2),
    rating_change DECIMAL(8,2),
    opponent_rating DECIMAL(8,2),
    game_result VARCHAR(10), -- 'WIN' or 'LOSS'
    k_factor INTEGER,
    created_at TIMESTAMP DEFAULT NOW()
);

-- Manual adjustment requests
CREATE TABLE elo_adjustment_requests (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    current_elo DECIMAL(8,2),
    requested_elo DECIMAL(8,2),
    reason TEXT,
    status VARCHAR(20) DEFAULT 'PENDING',
    admin_notes TEXT,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);
```

## Service Implementation

### ELO Rating Service (`app/services/elo_rating_service.py`)

#### Core Functions

```python
class EloRatingService:
    def calculate_expected_score(self, player_rating: float, opponent_rating: float) -> float:
        """Calculate expected score for a player against opponent."""
        return 1 / (1 + 10 ** ((opponent_rating - player_rating) / 400))
    
    def calculate_new_rating(self, current_rating: float, opponent_rating: float, 
                           actual_score: float, k_factor: int = 32) -> float:
        """Calculate new rating after a game."""
        expected = self.calculate_expected_score(current_rating, opponent_rating)
        return current_rating + k_factor * (actual_score - expected)
    
    def update_ratings_for_game(self, game_id: int) -> Dict[str, float]:
        """Update all player ratings after a game."""
        # Implementation handles team games with 4 players
```

#### Game Result Processing

1. **Fetch Game Data**: Get game details and participants
2. **Calculate Team Ratings**: Average ELO for each team
3. **Update Individual Ratings**: Each player vs opposing team average
4. **Store History**: Record rating changes for audit trail
5. **Update User Records**: Save new ratings to user profiles

### Usage Examples

#### Manual Rating Calculation

```python
from app.services.elo_rating_service import EloRatingService

elo_service = EloRatingService()

# Player A (1400) beats Player B (1500)
player_a_new = elo_service.calculate_new_rating(
    current_rating=1400,
    opponent_rating=1500,
    actual_score=1.0,  # Win
    k_factor=32
)
# Result: ~1415.36 (+15.36 points)

player_b_new = elo_service.calculate_new_rating(
    current_rating=1500,
    opponent_rating=1400,
    actual_score=0.0,  # Loss
    k_factor=32
)
# Result: ~1484.64 (-15.36 points)
```

#### Team Game Processing

```python
# Team 1: Players A (1400) + B (1300) = Team ELO 1350
# Team 2: Players C (1500) + D (1450) = Team ELO 1475
# Team 1 wins

# Each Team 1 player gains points against 1475 team rating
# Each Team 2 player loses points against 1350 team rating
```

## API Integration

### Game Result Submission

```
POST /api/v1/games/{game_id}/result
{
  "winning_team_id": 123,
  "team1_score": 6,
  "team2_score": 4
}
```

This endpoint automatically:
1. Validates game completion
2. Calculates ELO changes for all players
3. Updates user ratings
4. Records rating history

### ELO Adjustment Requests

```
POST /api/v1/users/{user_id}/request-elo-adjustment
{
  "requested_elo": 1450,
  "reason": "Previous tournament results not recorded"
}
```

Users can request manual ELO adjustments for:
- Missing game results
- Technical errors
- Tournament corrections
- Initial placement disputes

## Frontend Integration

### Profile Display

```typescript
interface UserEloData {
  current_elo: number;
  category: 'BRONZE' | 'SILVER' | 'GOLD' | 'PLATINUM';
  rank: number;
  games_played: number;
  rating_change_30d: number;
}
```

### Leaderboard

```
GET /api/v1/leaderboard?limit=100&category=GOLD
```

Returns paginated rankings with:
- Current ELO ratings
- Category standings
- Recent rating changes
- Game statistics

### Rating History Chart

```typescript
interface RatingHistoryPoint {
  date: string;
  rating: number;
  game_id?: number;
  opponent_rating?: number;
  change: number;
}
```

## Tournament Integration

### Category Eligibility

Tournament registration automatically checks:

```python
def check_tournament_eligibility(user_id: int, tournament_category: str) -> bool:
    user_elo = get_user_elo(user_id)
    category_ranges = {
        'BRONZE': (800, 1099),
        'SILVER': (1100, 1399),
        'GOLD': (1400, 1699),
        'PLATINUM': (1700, 3000)
    }
    min_elo, max_elo = category_ranges[tournament_category]
    return min_elo <= user_elo <= max_elo
```

### Team Eligibility

```python
def check_team_eligibility(team_id: int, tournament_category: str) -> bool:
    team_average_elo = calculate_team_average_elo(team_id)
    return check_tournament_eligibility_by_elo(team_average_elo, tournament_category)
```

## Business Rules

### Rating Protection

1. **Minimum Games**: Players need 10+ games for stable rating
2. **Inactive Decay**: Ratings may decrease after 90 days inactivity
3. **Manipulation Prevention**: Unusual rating patterns trigger review

### Fair Play

1. **Balanced Teams**: Auto-suggestions for balanced team composition
2. **Skill Gaps**: Warnings for large ELO differences (400+ points)
3. **Sandbagging**: Detection of intentional rating manipulation

### Administrative Controls

1. **Manual Adjustments**: Admins can correct rating errors
2. **Reset Options**: Full or partial rating resets
3. **Historical Preservation**: All changes tracked and auditable

## Analytics & Insights

### Player Analytics

- **Rating Progression**: Track improvement over time
- **Performance Patterns**: Win/loss against different skill levels
- **Optimal Opponents**: Suggest matches for rating growth

### Club Analytics

- **Member Distribution**: ELO distribution across club members
- **Tournament Participation**: Category participation rates
- **Skill Development**: Average rating improvements

### System Health

- **Rating Inflation**: Monitor overall rating trends
- **Category Balance**: Ensure even distribution across categories
- **Algorithm Performance**: Validate prediction accuracy

## Configuration

### System Parameters

```python
# ELO Configuration
ELO_STARTING_RATING = 1200
ELO_K_FACTOR_REGULAR = 32
ELO_K_FACTOR_TOURNAMENT = 40
ELO_K_FACTOR_PROVISIONAL = 40
ELO_MINIMUM_RATING = 100
ELO_MAXIMUM_RATING = 3000

# Category Boundaries
CATEGORY_RANGES = {
    'BRONZE': (800, 1099),
    'SILVER': (1100, 1399),
    'GOLD': (1400, 1699),
    'PLATINUM': (1700, 3000)
}
```

### Customization Options

- **Starting Rating**: Adjustable based on club demographics
- **K-Factors**: Tunable for different game types
- **Category Ranges**: Customizable skill level boundaries
- **Decay Rates**: Configurable inactivity penalties

## Troubleshooting

### Common Issues

1. **Rating Not Updating**
   - Check game result submission
   - Verify all players have valid ELO
   - Review service logs for errors

2. **Incorrect Rating Changes**
   - Validate opponent ratings at game time
   - Check K-factor application
   - Review calculation logic

3. **Category Misclassification**
   - Verify current ELO ranges
   - Check for recent rating updates
   - Review manual adjustments

### Diagnostic Queries

```sql
-- Check player rating history
SELECT * FROM elo_rating_history 
WHERE user_id = 123 
ORDER BY created_at DESC LIMIT 10;

-- Review large rating changes
SELECT * FROM elo_rating_history 
WHERE ABS(rating_change) > 50;

-- Monitor system health
SELECT 
    COUNT(*) as total_players,
    AVG(elo_rating) as avg_rating,
    STDDEV(elo_rating) as rating_stddev
FROM users 
WHERE elo_rating IS NOT NULL;
```

---

The ELO rating system provides fair, competitive matchmaking while enabling skill-based tournament organization and player progression tracking throughout the PadelGo platform.