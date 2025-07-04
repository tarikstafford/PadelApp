# PadelGo Database Schema

This document contains a visual representation of the database schema for the PadelGo application.

```mermaid
erDiagram
    USER {
        int id PK
        string full_name
        string email UK
        string hashed_password
        string profile_picture_url
        bool is_active
        UserRole role
        float elo_rating
        PreferredPosition preferred_position
        bool is_superuser
    }

    CLUB {
        int id PK
        string name
        string address
        string city
        string postal_code
        string phone
        string email
        text description
        time opening_time
        time closing_time
        text amenities
        string image_url
        int owner_id FK
    }

    COURT {
        int id PK
        string name
        int club_id FK
        SurfaceType surface_type
        bool is_indoor
        decimal price_per_hour
        CourtAvailabilityStatus default_availability_status
    }

    BOOKING {
        int id PK
        int court_id FK
        int user_id FK
        datetime start_time
        datetime end_time
        BookingStatus status
    }

    GAME {
        int id PK
        int club_id FK
        int booking_id UK, FK
        int team1_id FK
        int team2_id FK
        GameType game_type
        string skill_level
        datetime start_time
        datetime end_time
        int winning_team_id FK
        bool result_submitted
    }

    TEAM {
        int id PK
        string name
    }

    team_players {
        int team_id PK, FK
        int user_id PK, FK
    }

    GAME_PLAYER {
        int game_id PK, FK
        int user_id PK, FK
        GamePlayerStatus status
    }

    CLUB_ADMIN {
        int id PK
        int user_id FK
        int club_id FK
    }

    ELO_ADJUSTMENT_REQUEST {
        int id PK
        int user_id FK
        int current_elo
        int requested_elo
        string reason
        EloAdjustmentRequestStatus status
        datetime created_at
        datetime updated_at
    }

    TOURNAMENT {
        int id PK
        string name
        text description
        int club_id FK
        TournamentCategory category
        datetime start_date
        datetime end_date
        datetime registration_deadline
        int max_teams
        decimal entry_fee
        TournamentStatus status
        datetime created_at
        datetime updated_at
    }

    TOURNAMENT_TEAM {
        int id PK
        int tournament_id FK
        int team_id FK
        string team_name
        datetime registered_at
        TournamentTeamStatus status
    }

    TOURNAMENT_MATCH {
        int id PK
        int tournament_id FK
        int team1_id FK
        int team2_id FK
        int round_number
        int match_number
        datetime scheduled_time
        int court_id FK
        int winner_team_id FK
        int team1_score
        int team2_score
        MatchStatus status
        datetime created_at
        datetime updated_at
    }

    TOURNAMENT_COURT_BOOKING {
        int id PK
        int tournament_id FK
        int court_id FK
        datetime start_time
        datetime end_time
        int match_id FK
        BookingStatus status
    }

    TOURNAMENT_CATEGORY_CONFIG {
        int id PK
        int tournament_id FK
        TournamentCategory category
        int min_elo
        int max_elo
        int max_teams
        decimal entry_fee
    }

    USER_TROPHY {
        int id PK
        int user_id FK
        int tournament_id FK
        TrophyType trophy_type
        datetime awarded_at
    }

    GAME_INVITATION {
        int id PK
        int game_id FK
        int inviter_id FK
        int invitee_id FK
        string token
        GameInvitationStatus status
        datetime created_at
        datetime expires_at
    }

    USER ||--o{ CLUB : "owns (1-to-1)"
    USER ||--o{ BOOKING : "creates"
    USER ||--|{ ELO_ADJUSTMENT_REQUEST : "requests"
    USER ||--o{ USER_TROPHY : "earns"
    USER ||--o{ GAME_INVITATION : "sends"
    USER ||--o{ GAME_INVITATION : "receives"
    
    CLUB ||--|{ COURT : "has"
    CLUB ||--o{ GAME : "hosts"
    CLUB ||--o{ TOURNAMENT : "organizes"
    
    COURT ||--o{ BOOKING : "is for"
    COURT ||--o{ TOURNAMENT_MATCH : "hosts"
    COURT ||--o{ TOURNAMENT_COURT_BOOKING : "is booked for"
    
    BOOKING ||--|| GAME : "results in (1-to-1)"

    GAME }o--|| TEAM : "has (team 1)"
    GAME }o--|| TEAM : "has (team 2)"
    GAME }o--|| TEAM : "is won by"
    GAME ||--o{ GAME_INVITATION : "has"

    TEAM       }o--o{ team_players : "links to"
    USER       }o--o{ team_players : "links to"

    GAME       ||--o{ GAME_PLAYER : "has"
    USER       ||--o{ GAME_PLAYER : "is"

    CLUB       ||--|{ CLUB_ADMIN : "has"
    USER       ||--|{ CLUB_ADMIN : "is"

    TOURNAMENT ||--o{ TOURNAMENT_TEAM : "has"
    TOURNAMENT ||--o{ TOURNAMENT_MATCH : "contains"
    TOURNAMENT ||--o{ TOURNAMENT_COURT_BOOKING : "books"
    TOURNAMENT ||--o{ TOURNAMENT_CATEGORY_CONFIG : "configures"
    TOURNAMENT ||--o{ USER_TROPHY : "awards"

    TEAM ||--o{ TOURNAMENT_TEAM : "participates in"
    TOURNAMENT_TEAM ||--o{ TOURNAMENT_MATCH : "plays in (team 1)"
    TOURNAMENT_TEAM ||--o{ TOURNAMENT_MATCH : "plays in (team 2)"
    TOURNAMENT_TEAM ||--o{ TOURNAMENT_MATCH : "wins"

    TOURNAMENT_MATCH ||--|| TOURNAMENT_COURT_BOOKING : "is scheduled for"
```