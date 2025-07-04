# Testing Documentation

## Overview

This document outlines the testing strategy, tools, and procedures for the PadelGo application. It covers unit tests, integration tests, end-to-end tests, and manual testing procedures across all services.

## Testing Strategy

### Test Pyramid

```
        E2E Tests
       /           \
    Integration Tests
   /                 \
  Unit Tests (Base)
```

- **Unit Tests (70%)**: Fast, isolated component testing
- **Integration Tests (20%)**: API and database integration
- **End-to-End Tests (10%)**: Full user workflow testing

### Test Coverage Goals

- **Backend**: 80%+ code coverage
- **Frontend**: 70%+ component coverage
- **Critical Paths**: 100% coverage (auth, payments, tournaments)

## Backend Testing

### Test Structure

```
padel-app/apps/api/tests/
├── conftest.py                 # Test configuration
├── test_*.py                   # Test modules
└── utils/                      # Test utilities
    ├── user.py
    ├── club.py
    ├── game.py
    └── booking.py
```

### Test Configuration (`conftest.py`)

```python
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import get_db, Base

# Test database
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture(scope="function")
def db_session():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        yield db_session
    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()
```

### Unit Tests

#### Authentication Tests (`test_auth_router.py`)

```python
def test_register_user(client, db_session):
    """Test user registration."""
    response = client.post("/api/v1/auth/register", json={
        "full_name": "John Doe",
        "email": "john@example.com",
        "password": "securepassword"
    })
    assert response.status_code == 201
    assert "id" in response.json()

def test_login_user(client, db_session):
    """Test user login."""
    # Create user first
    user = create_test_user(db_session)
    
    response = client.post("/api/v1/auth/login", data={
        "username": user.email,
        "password": "testpassword"
    })
    assert response.status_code == 200
    assert "access_token" in response.json()
```

#### Game Tests (`test_games_api.py`)

```python
def test_create_game(authenticated_client, db_session):
    """Test game creation."""
    club = create_test_club(db_session)
    court = create_test_court(db_session, club.id)
    booking = create_test_booking(db_session, court.id)
    
    response = authenticated_client.post(f"/api/v1/games", json={
        "booking_id": booking.id,
        "game_type": "PRIVATE",
        "skill_level": "INTERMEDIATE"
    })
    assert response.status_code == 201
    assert response.json()["booking_id"] == booking.id

def test_join_public_game(authenticated_client, db_session):
    """Test joining a public game."""
    game = create_test_public_game(db_session)
    
    response = authenticated_client.post(f"/api/v1/games/{game.id}/join")
    assert response.status_code == 201
```

#### ELO Rating Tests (`test_elo_rating_service.py`)

```python
def test_elo_calculation():
    """Test ELO rating calculation."""
    from app.services.elo_rating_service import EloRatingService
    
    elo_service = EloRatingService()
    
    # Test expected score calculation
    expected = elo_service.calculate_expected_score(1400, 1500)
    assert 0.35 < expected < 0.40  # Weaker player vs stronger
    
    # Test rating update
    new_rating = elo_service.calculate_new_rating(1400, 1500, 1.0, 32)
    assert new_rating > 1400  # Win increases rating

def test_team_elo_update(db_session):
    """Test team game ELO updates."""
    # Create 4 players with known ratings
    players = [
        create_test_user(db_session, elo_rating=1400),
        create_test_user(db_session, elo_rating=1450),
        create_test_user(db_session, elo_rating=1500),
        create_test_user(db_session, elo_rating=1550)
    ]
    
    game = create_test_team_game(db_session, players)
    submit_game_result(db_session, game.id, winning_team=1)
    
    # Check rating updates
    updated_players = [get_user_elo(db_session, p.id) for p in players]
    assert updated_players[0] > 1400  # Winner gained
    assert updated_players[2] < 1500  # Loser lost
```

#### Tournament Tests (`test_tournament_api.py`)

```python
def test_create_tournament(admin_client, db_session):
    """Test tournament creation."""
    response = admin_client.post("/api/v1/tournaments", json={
        "name": "Summer Championship",
        "category": "GOLD",
        "start_date": "2024-08-01T09:00:00Z",
        "end_date": "2024-08-01T18:00:00Z",
        "registration_deadline": "2024-07-25T23:59:59Z",
        "max_teams": 16
    })
    assert response.status_code == 201

def test_tournament_registration(client, db_session):
    """Test team tournament registration."""
    tournament = create_test_tournament(db_session, category="GOLD")
    team = create_test_team(db_session, avg_elo=1500)  # Gold category
    
    response = client.post(f"/api/v1/tournaments/{tournament.id}/register", json={
        "team_id": team.id
    })
    assert response.status_code == 201

def test_bracket_generation(admin_client, db_session):
    """Test tournament bracket generation."""
    tournament = create_test_tournament_with_teams(db_session, num_teams=8)
    
    response = admin_client.post(f"/api/v1/tournaments/{tournament.id}/generate-bracket")
    assert response.status_code == 201
    
    # Verify bracket structure
    matches = get_tournament_matches(db_session, tournament.id)
    assert len(matches) == 7  # 8 teams = 7 matches total
```

### Integration Tests

#### Database Integration

```python
def test_user_club_relationship(db_session):
    """Test user-club database relationships."""
    user = create_test_user(db_session)
    club = create_test_club(db_session, owner_id=user.id)
    
    # Test relationship loading
    assert club.owner.id == user.id
    assert user.owned_club.id == club.id

def test_booking_game_cascade(db_session):
    """Test booking-game cascade deletion."""
    booking = create_test_booking(db_session)
    game = create_test_game(db_session, booking_id=booking.id)
    
    # Delete booking should cascade to game
    db_session.delete(booking)
    db_session.commit()
    
    assert get_game_by_id(db_session, game.id) is None
```

#### API Integration

```python
def test_complete_booking_flow(client, db_session):
    """Test complete booking to game flow."""
    user = create_test_user(db_session)
    club = create_test_club(db_session)
    court = create_test_court(db_session, club.id)
    
    # 1. Create booking
    booking_response = client.post("/api/v1/bookings", json={
        "court_id": court.id,
        "start_time": "2024-08-01T10:00:00Z",
        "end_time": "2024-08-01T12:00:00Z"
    })
    booking_id = booking_response.json()["id"]
    
    # 2. Create game from booking
    game_response = client.post("/api/v1/games", json={
        "booking_id": booking_id,
        "game_type": "PRIVATE"
    })
    game_id = game_response.json()["id"]
    
    # 3. Submit game result
    result_response = client.post(f"/api/v1/games/{game_id}/result", json={
        "winning_team_id": 1,
        "team1_score": 6,
        "team2_score": 4
    })
    
    assert all(r.status_code in [200, 201] for r in [booking_response, game_response, result_response])
```

## Frontend Testing

### Test Structure

```
padel-app/apps/web/
├── __tests__/
│   ├── components/
│   ├── pages/
│   └── utils/
├── cypress/
│   ├── e2e/
│   ├── fixtures/
│   └── support/
└── jest.config.js
```

### Unit Tests (Jest + React Testing Library)

#### Component Tests

```typescript
// __tests__/components/GameCard.test.tsx
import { render, screen } from '@testing-library/react';
import { GameCard } from '@/components/GameCard';

describe('GameCard', () => {
  const mockGame = {
    id: 1,
    booking: { court: { name: 'Court 1' } },
    game_type: 'PUBLIC',
    players: []
  };

  it('renders game information correctly', () => {
    render(<GameCard game={mockGame} />);
    
    expect(screen.getByText('Court 1')).toBeInTheDocument();
    expect(screen.getByText('PUBLIC')).toBeInTheDocument();
  });

  it('shows join button for public games', () => {
    render(<GameCard game={mockGame} />);
    
    expect(screen.getByRole('button', { name: /join/i })).toBeInTheDocument();
  });
});
```

#### Hook Tests

```typescript
// __tests__/hooks/useApi.test.tsx
import { renderHook } from '@testing-library/react';
import { useApi } from '@/hooks/useApi';

describe('useApi', () => {
  it('handles successful API calls', async () => {
    const { result } = renderHook(() => useApi());
    
    const response = await result.current.get('/api/v1/clubs');
    
    expect(response.data).toBeDefined();
    expect(result.current.loading).toBe(false);
  });

  it('handles API errors', async () => {
    const { result } = renderHook(() => useApi());
    
    try {
      await result.current.get('/api/v1/invalid');
    } catch (error) {
      expect(result.current.error).toBeDefined();
    }
  });
});
```

### Club Admin Testing

#### Component Tests

```typescript
// __tests__/components/TournamentForm.test.tsx
import { render, screen, fireEvent } from '@testing-library/react';
import { TournamentForm } from '@/components/TournamentForm';

describe('TournamentForm', () => {
  it('validates required fields', async () => {
    render(<TournamentForm />);
    
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    
    expect(screen.getByText(/name is required/i)).toBeInTheDocument();
    expect(screen.getByText(/category is required/i)).toBeInTheDocument();
  });

  it('submits form with valid data', async () => {
    const mockSubmit = jest.fn();
    render(<TournamentForm onSubmit={mockSubmit} />);
    
    fireEvent.change(screen.getByLabelText(/name/i), {
      target: { value: 'Test Tournament' }
    });
    fireEvent.change(screen.getByLabelText(/category/i), {
      target: { value: 'GOLD' }
    });
    
    fireEvent.click(screen.getByRole('button', { name: /create/i }));
    
    expect(mockSubmit).toHaveBeenCalledWith(expect.objectContaining({
      name: 'Test Tournament',
      category: 'GOLD'
    }));
  });
});
```

## End-to-End Testing

### Cypress Configuration

```typescript
// cypress.config.ts
export default defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    videosFolder: 'cypress/videos',
    screenshotsFolder: 'cypress/screenshots',
  },
});
```

### E2E Test Examples

#### User Authentication Flow

```typescript
// cypress/e2e/auth.cy.ts
describe('Authentication', () => {
  it('allows user to register and login', () => {
    cy.visit('/auth/register');
    
    // Registration
    cy.get('[data-cy=full-name]').type('John Doe');
    cy.get('[data-cy=email]').type('john@example.com');
    cy.get('[data-cy=password]').type('password123');
    cy.get('[data-cy=submit]').click();
    
    cy.url().should('include', '/dashboard');
    
    // Logout
    cy.get('[data-cy=user-menu]').click();
    cy.get('[data-cy=logout]').click();
    
    // Login
    cy.visit('/auth/login');
    cy.get('[data-cy=email]').type('john@example.com');
    cy.get('[data-cy=password]').type('password123');
    cy.get('[data-cy=submit]').click();
    
    cy.url().should('include', '/dashboard');
  });
});
```

#### Tournament Management Flow

```typescript
// cypress/e2e/tournaments.cy.ts
describe('Tournament Management', () => {
  beforeEach(() => {
    cy.loginAsAdmin();
  });

  it('creates and manages a tournament', () => {
    cy.visit('/tournaments/new');
    
    // Create tournament
    cy.get('[data-cy=tournament-name]').type('Summer Championship');
    cy.get('[data-cy=category]').select('GOLD');
    cy.get('[data-cy=start-date]').type('2024-08-01');
    cy.get('[data-cy=max-teams]').type('16');
    cy.get('[data-cy=submit]').click();
    
    cy.contains('Tournament created successfully');
    
    // Navigate to tournament management
    cy.get('[data-cy=manage-tournament]').click();
    
    // Verify tournament details
    cy.contains('Summer Championship');
    cy.contains('GOLD');
    cy.contains('16 teams max');
  });

  it('generates tournament bracket', () => {
    cy.createTournamentWithTeams(8);
    
    cy.get('[data-cy=generate-bracket]').click();
    cy.contains('Bracket generated successfully');
    
    // Verify bracket structure
    cy.get('[data-cy=bracket-match]').should('have.length', 7);
    cy.get('[data-cy=round-1]').should('contain', '4 matches');
  });
});
```

## Manual Testing

### Test Cases

#### Critical User Flows

1. **User Registration & Profile Setup**
   - Register new account
   - Complete profile information
   - Upload profile picture
   - Set preferred position

2. **Club Discovery & Booking**
   - Browse available clubs
   - View club details and courts
   - Check court availability
   - Create booking
   - Confirm booking details

3. **Game Creation & Management**
   - Create private game from booking
   - Invite players to game
   - Accept/decline invitations
   - Submit game results
   - View ELO rating updates

4. **Tournament Participation**
   - View available tournaments
   - Register team for tournament
   - View tournament bracket
   - Check match schedule
   - Submit match results

5. **Club Admin Workflows**
   - Club registration and setup
   - Court management (CRUD)
   - Tournament creation
   - Bracket generation
   - Dashboard analytics

### Manual Test Checklist

#### Pre-deployment Testing

- [ ] User authentication (register/login/logout)
- [ ] Profile management and picture upload
- [ ] Club browsing and court availability
- [ ] Booking creation and management
- [ ] Game creation and player invitations
- [ ] Public game joining
- [ ] ELO rating calculations
- [ ] Tournament registration and management
- [ ] Bracket generation and match scheduling
- [ ] Admin dashboard functionality
- [ ] Responsive design on mobile/tablet
- [ ] Error handling and user feedback
- [ ] Performance on slow connections

#### Browser Compatibility

- [ ] Chrome (latest)
- [ ] Firefox (latest)
- [ ] Safari (latest)
- [ ] Edge (latest)
- [ ] Mobile browsers (iOS Safari, Chrome Mobile)

### Performance Testing

#### Load Testing

```bash
# Using Artillery for API load testing
npm install -g artillery

# Load test configuration
# artillery.yml
config:
  target: 'https://padelgo-backend-production.up.railway.app'
  phases:
    - duration: 60
      arrivalRate: 10
scenarios:
  - name: "Get public games"
    requests:
      - get:
          url: "/api/v1/public/games?limit=10"
```

#### Frontend Performance

```javascript
// Lighthouse CI configuration
module.exports = {
  ci: {
    collect: {
      url: ['http://localhost:3000', 'http://localhost:3000/tournaments'],
      startServerCommand: 'npm start',
    },
    assert: {
      assertions: {
        'categories:performance': ['error', {minScore: 0.8}],
        'categories:accessibility': ['error', {minScore: 0.9}],
      },
    },
  },
};
```

## Testing Commands

### Backend

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test file
pytest tests/test_auth_router.py

# Run with verbose output
pytest -v

# Run only failed tests
pytest --lf
```

### Frontend

```bash
# Run unit tests
npm test

# Run with coverage
npm run test:coverage

# Run E2E tests
npm run cypress:run

# Open Cypress UI
npm run cypress:open

# Run tests in watch mode
npm run test:watch
```

### Database Testing

```bash
# Create test database
createdb padelgo_test

# Run migration tests
pytest tests/test_migrations.py

# Test database performance
pytest tests/test_performance.py --benchmark-only
```

## Continuous Integration

### GitHub Actions

```yaml
# .github/workflows/test.yml
name: Test Suite
on: [push, pull_request]

jobs:
  backend-tests:
    runs-on: ubuntu-latest
    services:
      postgres:
        image: postgres:13
        env:
          POSTGRES_PASSWORD: postgres
        options: >-
          --health-cmd pg_isready
          --health-interval 10s
          --health-timeout 5s
          --health-retries 5
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: |
          pip install -r requirements.txt
      - name: Run tests
        run: |
          pytest --cov=app --cov-report=xml
      - name: Upload coverage
        uses: codecov/codecov-action@v1

  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Setup Node.js
        uses: actions/setup-node@v2
        with:
          node-version: '18'
      - name: Install dependencies
        run: npm ci
      - name: Run tests
        run: npm run test:ci
      - name: Run E2E tests
        run: npm run cypress:run
```

## Quality Metrics

### Coverage Requirements

- **Backend API**: 80% minimum coverage
- **Frontend Components**: 70% minimum coverage
- **Critical Paths**: 100% coverage required

### Performance Benchmarks

- **API Response Time**: < 200ms average
- **Database Queries**: < 100ms average
- **Frontend Load Time**: < 3 seconds
- **Core Web Vitals**: All metrics in "Good" range

### Quality Gates

- All tests must pass
- Coverage thresholds must be met
- No critical security vulnerabilities
- Performance benchmarks must be met
- Manual testing checklist completed

---

This comprehensive testing strategy ensures the reliability, performance, and quality of the PadelGo platform across all environments and user scenarios.