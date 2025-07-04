# Tournament System Documentation

## Overview

The PadelGo tournament system provides comprehensive tournament management capabilities for padel clubs. It features ELO-based categorization, automated bracket generation, match scheduling, and trophy awarding.

## Features

### 1. ELO-Based Categories

Tournaments are organized into skill-based categories to ensure fair competition:

- **Bronze**: ELO 800-1099 (Entry level)
- **Silver**: ELO 1100-1399 (Intermediate)
- **Gold**: ELO 1400-1699 (Advanced)
- **Platinum**: ELO 1700+ (Elite)

### 2. Tournament Types

- **Single Elimination**: Standard knockout format
- **Round Robin**: Everyone plays everyone (future feature)
- **Swiss System**: Pairing based on performance (future feature)

### 3. Registration & Eligibility

- Teams register for tournaments in their ELO category
- Automatic eligibility verification based on team average ELO
- Registration deadlines and maximum team limits
- Entry fees per category (configurable)

### 4. Match Management

- Automated bracket generation
- Court booking integration
- Match scheduling with conflict detection
- Score tracking and result submission
- Automatic advancement to next rounds

### 5. Trophy System

Winners receive trophies based on tournament placement:
- **GOLD**: 1st place
- **SILVER**: 2nd place  
- **BRONZE**: 3rd place
- **PARTICIPATION**: All participants

## Tournament Lifecycle

### 1. Creation (Club Admin)

```
POST /api/v1/tournaments
{
  "name": "Summer Championship",
  "description": "Annual summer tournament",
  "category": "GOLD",
  "start_date": "2024-08-01T09:00:00Z",
  "end_date": "2024-08-01T18:00:00Z",
  "registration_deadline": "2024-07-25T23:59:59Z",
  "max_teams": 16,
  "entry_fee": 50.00
}
```

### 2. Team Registration

```
POST /api/v1/tournaments/{tournament_id}/register
{
  "team_id": 123,
  "team_name": "Thunder Padel"
}
```

### 3. Bracket Generation

```
POST /api/v1/tournaments/{tournament_id}/generate-bracket
```

This automatically:
- Creates tournament matches based on registered teams
- Schedules matches across available courts
- Sets up single-elimination bracket structure

### 4. Match Results

```
PUT /api/v1/tournaments/matches/{match_id}
{
  "team1_score": 2,
  "team2_score": 1,
  "winner_team_id": 456
}
```

### 5. Tournament Finalization

```
POST /api/v1/tournaments/{tournament_id}/finalize
```

This triggers:
- Trophy distribution to winners
- ELO updates for all participants
- Tournament completion status

## Database Schema

### Core Tables

#### tournaments
- Primary tournament configuration
- Category, dates, fees, limits
- Status tracking (DRAFT, OPEN, ACTIVE, COMPLETED)

#### tournament_teams
- Team registrations for tournaments
- Registration timestamps and status
- Team eligibility verification

#### tournament_matches
- Individual match data
- Round progression (Round 1, Quarterfinals, etc.)
- Scoring and results
- Court assignments

#### tournament_court_bookings
- Court reservations for matches
- Integration with regular booking system
- Time slot management

#### user_trophies
- Trophy awards for tournament winners
- Historical achievement tracking
- Trophy type and tournament reference

### Key Relationships

```
TOURNAMENT (1) -> (M) TOURNAMENT_TEAMS
TOURNAMENT (1) -> (M) TOURNAMENT_MATCHES
TOURNAMENT (1) -> (M) TOURNAMENT_COURT_BOOKINGS
TOURNAMENT (1) -> (M) USER_TROPHIES
```

## Business Rules

### ELO Calculations

1. **Team ELO**: Average of both players' ELO ratings
2. **Category Eligibility**: Team ELO must fall within category range
3. **Tournament Impact**: Tournament games have higher K-factor (40 vs 32)

### Match Scheduling

1. **Court Priority**: Tournament matches get priority booking
2. **Time Slots**: Matches scheduled in 2-hour blocks
3. **Rest Periods**: Minimum 30 minutes between team matches

### Bracket Generation

1. **Seeding**: Teams seeded by ELO rating (highest = #1 seed)
2. **Bracket Size**: Must be power of 2 (8, 16, 32 teams)
3. **Byes**: Automatic byes for insufficient teams

## Error Handling

### Registration Errors
- **TEAM_NOT_ELIGIBLE**: Team ELO outside category range
- **TOURNAMENT_FULL**: Maximum teams reached
- **REGISTRATION_CLOSED**: Past registration deadline
- **DUPLICATE_REGISTRATION**: Team already registered

### Match Errors
- **INVALID_SCORE**: Score format validation
- **COURT_CONFLICT**: Court booking conflicts
- **MATCH_NOT_SCHEDULED**: Match not ready for results

### Bracket Errors
- **INSUFFICIENT_TEAMS**: Need minimum 4 teams
- **ALREADY_GENERATED**: Bracket already exists
- **INVALID_TOURNAMENT_STATE**: Tournament not ready

## API Usage Examples

### Get Tournament Details
```javascript
const tournament = await fetch('/api/v1/tournaments/123')
const data = await tournament.json()
// Returns tournament with teams, matches, and bracket
```

### Register Team
```javascript
const registration = await fetch('/api/v1/tournaments/123/register', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    team_id: 456,
    team_name: 'Thunder Padel'
  })
})
```

### View Bracket
```javascript
const bracket = await fetch('/api/v1/tournaments/123/bracket')
const data = await bracket.json()
// Returns complete bracket with match results
```

## Frontend Integration

### Tournament Pages

1. **`/tournaments`**: Public tournament listing
2. **`/tournaments/[id]`**: Tournament details and bracket
3. **`/tournaments/[id]/manage`**: Admin management (club admin only)

### Components

- **TournamentCard**: Tournament overview display
- **BracketView**: Interactive tournament bracket
- **RegistrationForm**: Team registration interface
- **MatchSchedule**: Match timing and court assignments
- **TrophyDisplay**: Winner achievements

## Configuration

### Category Settings

Categories can be customized per tournament:

```sql
INSERT INTO tournament_category_configs (
  tournament_id, category, min_elo, max_elo, max_teams, entry_fee
) VALUES (
  123, 'GOLD', 1400, 1699, 16, 50.00
);
```

### Tournament Templates

Common tournament configurations:
- **Weekend Tournament**: 2-day, 16 teams max
- **League Night**: Weekly, 8 teams max
- **Championship**: Multi-day, 32 teams max

## Monitoring & Analytics

### Key Metrics

- Tournament participation rates
- Category distribution
- Revenue per tournament
- Average match duration
- Court utilization during tournaments

### Reporting

- Tournament completion reports
- Financial summaries
- Player participation analytics
- ELO progression tracking

## Future Enhancements

### Planned Features

1. **Multi-Category Tournaments**: Single tournament with multiple divisions
2. **Round Robin Format**: Complete league-style tournaments
3. **Live Scoring**: Real-time match updates
4. **Streaming Integration**: Live match streaming
5. **Advanced Analytics**: Player performance metrics

### Integration Opportunities

- **Payment Processing**: Automated entry fee collection
- **Calendar Integration**: Tournament schedule sync
- **Social Media**: Automated tournament updates
- **Mobile App**: Tournament management on mobile

## Troubleshooting

### Common Issues

1. **Bracket Generation Fails**
   - Check minimum team count (4 teams)
   - Verify tournament status is OPEN
   - Ensure no existing bracket

2. **Team Registration Rejected**
   - Verify team ELO within category range
   - Check registration deadline
   - Confirm tournament capacity

3. **Match Scheduling Conflicts**
   - Review court availability
   - Check for double-booked courts
   - Verify match timing constraints

### Support Commands

```sql
-- Check tournament status
SELECT * FROM tournaments WHERE id = 123;

-- View registered teams
SELECT * FROM tournament_teams WHERE tournament_id = 123;

-- Check bracket generation
SELECT * FROM tournament_matches WHERE tournament_id = 123;
```

---

This comprehensive tournament system provides clubs with professional-grade tournament management capabilities while maintaining integration with the existing PadelGo platform.