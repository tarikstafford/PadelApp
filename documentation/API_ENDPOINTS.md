# PadelGo API Endpoints

This document provides a comprehensive list of all API endpoints available in the PadelGo application, grouped by their respective routers.

---

## 🔒 Authentication (`/api/v1/auth`)

Handles user registration, login, and token management.

| Method | Path                           | Description                                       | Request Body                  | Response Body                 |
| :----- | :----------------------------- | :------------------------------------------------ | :---------------------------- | :---------------------------- |
| `POST` | `/register-admin`              | Create a new club admin user.                     | `AdminUserCreate`             | `Token`                       |
| `POST` | `/register`                    | Create a new player user.                         | `UserCreate`                  | `User`                        |
| `POST` | `/login`                       | Log in to get an access and refresh token.        | `UserLogin`                   | `Token`                       |
| `GET`  | `/users/me`                    | Get the current authenticated user's profile.     | -                             | `User`                        |
| `POST` | `/refresh-token`               | Refresh an access token using a refresh token.    | `RefreshTokenRequest`         | `Token`                       |

---

## 👤 Users (`/api/v1/users`)

Endpoints for managing user profiles and interactions.

| Method | Path                               | Description                                      | Request Body                  | Response Body                 |
| :----- | :--------------------------------- | :----------------------------------------------- | :---------------------------- | :---------------------------- |
| `GET`  | `/me`                              | Get the current authenticated user's profile.    | -                             | `User`                        |
| `PUT`  | `/me`                              | Update the current user's profile information.   | `UserUpdate`                  | `User`                        |
| `POST` | `/me/profile-picture`              | Upload a profile picture for the current user.   | `UploadFile` (form-data)      | `User`                        |
| `GET`  | `/me/elo-adjustment-requests`      | Get ELO adjustment requests for current user.    | -                             | `List[EloAdjustmentRequest]`  |
| `GET`  | `/search`                          | Search for users by name or email.               | - (Query: `query`, `limit`)   | `List[UserSearchResult]`      |
| `POST` | `/{user_id}/request-elo-adjustment`| Request a manual ELO rating adjustment.          | `EloAdjustmentRequest`        | `{"message": "..."}`          |

---

## 🏠 Clubs (`/api/v1/clubs`)

Endpoints for creating, viewing, and managing padel clubs.

| Method | Path               | Description                                           | Request Body   | Response Body        |
| :----- | :----------------- | :---------------------------------------------------- | :------------- | :------------------- |
| `POST` | `/`                | Create a new club (requires CLUB_ADMIN role).         | `ClubCreate`   | `Club`               |
| `GET`  | `/`                | Retrieve a list of clubs with filtering and sorting.  | - (Query)      | `List[Club]`         |
| `GET`  | `/{club_id}`       | Retrieve details for a specific club and its courts.  | -              | `ClubWithCourts`     |
| `GET`  | `/{club_id}/courts`| Retrieve the list of courts for a specific club.      | -              | `List[Court]`        |

---

## 🎾 Courts (`/api/v1/courts`)

Endpoints for managing courts within a club.

| Method | Path                    | Description                                       | Request Body   | Response Body             |
| :----- | :---------------------- | :------------------------------------------------ | :------------- | :------------------------ |
| `POST` | `/`                     | Create a new court for the admin's club.          | `CourtCreate`  | `Court`                   |
| `GET`  | `/{court_id}/availability` | Get the availability time slots for a specific court on a given date. | - (Query: `date`) | `List[CalendarTimeSlot]` |

---

## 📅 Bookings (`/api/v1/bookings`)

Endpoints for creating and viewing court bookings.

| Method | Path          | Description                                           | Request Body   | Response Body   |
| :----- | :------------ | :---------------------------------------------------- | :------------- | :-------------- |
| `POST` | `/`           | Create a new booking for the authenticated user.      | `BookingCreate`| `Booking`       |
| `GET`  | `/`           | Retrieve all bookings for the authenticated user.     | - (Query)      | `List[Booking]` |
| `GET`  | `/{booking_id}`| Retrieve details for a specific booking.              | -              | `Booking`       |

---

## 🏆 Games (`/api/v1/games`)

Endpoints for managing game sessions, invitations, and results.

| Method | Path                                 | Description                                       | Request Body                  | Response Body                 |
| :----- | :----------------------------------- | :------------------------------------------------ | :---------------------------- | :---------------------------- |
| `POST` | `/`                                  | Create a new game for a booking.                  | `GameCreate`                  | `Game`                        |
| `GET`  | `/{game_id}`                         | Retrieve details for a specific game.             | -                             | `Game`                        |
| `POST` | `/{game_id}/invitations`             | Invite a player to a game.                        | `UserInviteRequest`           | `GamePlayer`                  |
| `PUT`  | `/{game_id}/invitations/{user_id}`   | Respond to a game invitation (accept/decline).    | `InvitationResponseRequest`   | `GamePlayer`                  |
| `GET`  | `/public`                            | Retrieve a list of public games with open slots.  | - (Query)                     | `List[Game]`                  |
| `POST` | `/{game_id}/join`                    | Request to join a public game.                    | -                             | `GamePlayer`                  |
| `PUT`  | `/{game_id}/players/{user_id}/status`| Manage the status of a player in a game.          | `InvitationResponseRequest`   | `GamePlayer`                  |
| `POST` | `/{game_id}/result`                  | Submit the result of a game and update ELOs.      | `GameResultRequest`           | `GameWithRatingsResponse`     |

---

## 🏅 Leaderboard (`/api/v1/leaderboard`)

Endpoint for retrieving the user leaderboard.

| Method | Path | Description                                 | Request Body | Response Body         |
| :----- | :--- | :------------------------------------------ | :----------- | :-------------------- |
| `GET`  | `/`  | Retrieve a paginated leaderboard of users sorted by ELO rating. | - (Query)    | `LeaderboardResponse` |

---

## 🏆 Tournaments (`/api/v1/tournaments`)

Comprehensive tournament management system with ELO-based categories and automated bracket generation.

| Method | Path                                     | Description                                       | Request Body                | Response Body               |
| :----- | :--------------------------------------- | :------------------------------------------------ | :-------------------------- | :-------------------------- |
| `POST` | `/`                                      | Create a new tournament (club admin only).        | `TournamentCreate`          | `Tournament`                |
| `GET`  | `/`                                      | Get all public tournaments with filtering.        | - (Query)                   | `List[Tournament]`          |
| `GET`  | `/club`                                  | Get tournaments for the current admin's club.     | - (Query)                   | `List[Tournament]`          |
| `GET`  | `/{tournament_id}`                       | Get detailed tournament information.               | -                           | `TournamentDetail`          |
| `PUT`  | `/{tournament_id}`                       | Update tournament details (club admin only).      | `TournamentUpdate`          | `Tournament`                |
| `DELETE`| `/{tournament_id}`                      | Delete a tournament (club admin only).            | -                           | `{"message": "..."}`        |
| `POST` | `/{tournament_id}/register`              | Register a team for the tournament.               | `TeamRegistrationRequest`   | `TournamentTeam`            |
| `GET`  | `/{tournament_id}/teams`                 | Get all registered teams for the tournament.      | -                           | `List[TournamentTeam]`      |
| `POST` | `/{tournament_id}/generate-bracket`      | Generate tournament bracket (club admin only).    | -                           | `TournamentBracket`         |
| `GET`  | `/{tournament_id}/bracket`               | Get the tournament bracket and current standings.  | -                           | `TournamentBracket`         |
| `GET`  | `/{tournament_id}/matches`               | Get all matches for the tournament.               | -                           | `List[TournamentMatch]`     |
| `PUT`  | `/matches/{match_id}`                    | Update match results (club admin only).          | `MatchResultUpdate`         | `TournamentMatch`           |
| `POST` | `/{tournament_id}/finalize`              | Finalize tournament and award trophies.           | -                           | `TournamentResult`          |

---

## 👥 Teams (`/api/v1/teams`)

Team management for tournament participation and competitive play.

| Method | Path                                     | Description                                       | Request Body                | Response Body               |
| :----- | :--------------------------------------- | :------------------------------------------------ | :-------------------------- | :-------------------------- |
| `POST` | `/`                                      | Create a new team.                                | `TeamCreate`                | `Team`                      |
| `GET`  | `/`                                      | Get teams for the current user.                   | -                           | `List[Team]`                |
| `GET`  | `/{team_id}`                             | Get team details.                                 | -                           | `TeamDetail`                |
| `PUT`  | `/{team_id}`                             | Update team information.                          | `TeamUpdate`                | `Team`                      |
| `DELETE`| `/{team_id}`                            | Delete a team.                                    | -                           | `{"message": "..."}`        |
| `POST` | `/{team_id}/invite`                      | Invite a player to join the team.                 | `TeamInviteRequest`         | `{"message": "..."}`        |
| `PUT`  | `/{team_id}/members/{user_id}`           | Accept/decline team invitation.                   | `TeamInviteResponse`        | `{"message": "..."}`        |

---

## 🌐 Public (`/api/v1/public`)

Public endpoints accessible without authentication.

| Method | Path                                     | Description                                       | Request Body                | Response Body               |
| :----- | :--------------------------------------- | :------------------------------------------------ | :-------------------------- | :-------------------------- |
| `GET`  | `/games`                                 | Get public games with available slots.            | - (Query)                   | `List[Game]`                |
| `GET`  | `/tournaments`                           | Get public tournaments.                           | - (Query)                   | `List[Tournament]`          |

---

## 🛡️ Admin (`/api/v1/admin`)

Protected endpoints for administrative actions. Require `CLUB_ADMIN`, `ADMIN`, or `SUPER_ADMIN` role.

| Method | Path                                     | Description                                       | Request Body                | Response Body               |
| :----- | :--------------------------------------- | :------------------------------------------------ | :-------------------------- | :-------------------------- |
| `GET`  | `/test`                                  | Test route to verify admin authentication.        | -                           | `User`                      |
| `GET`  | `/my-club`                               | Retrieve the club owned by the current admin.     | -                           | `Club`                      |
| `PUT`  | `/club/{club_id}`                        | Update details for a specific club.               | `ClubUpdate`                | `Club`                      |
| `GET`  | `/club/{club_id}`                        | Retrieve details for a specific club.             | -                           | `Club`                      |
| `GET`  | `/club/{club_id}/courts`                 | Retrieve courts for a specific club.              | -                           | `List[Court]`               |
| `GET`  | `/club/{club_id}/schedule`               | Retrieve schedule for a club on a given date.     | - (Query)                   | `ScheduleResponse`          |
| `GET`  | `/my-club/schedule`                      | Retrieve schedule for the admin's own club.       | - (Query)                   | `ScheduleResponse`          |
| `GET`  | `/my-club/courts`                        | Retrieve courts for the admin's own club.         | -                           | `List[Court]`               |
| `POST` | `/my-club/courts`                        | Create a new court for the admin's own club.      | `CourtCreateForAdmin`       | `Court`                     |
| `PUT`  | `/my-club/courts/{court_id}`             | Update a court in the admin's own club.           | `CourtUpdate`               | `Court`                     |
| `DELETE`| `/my-club/courts/{court_id}`            | Delete a court from the admin's own club.         | -                           | `Court`                     |
| `GET`  | `/my-club/bookings`                      | Get bookings for the admin's own club.            | - (Query)                   | `List[Booking]`             |
| `GET`  | `/club/{club_id}/bookings`               | Get bookings for a specific club.                 | - (Query)                   | `List[Booking]`             |
| `GET`  | `/bookings/{booking_id}/game`            | Get the game associated with a booking.           | -                           | `GameResponse`              |
| `POST` | `/my-club/profile-picture`               | Upload a profile picture for the admin's club.    | `UploadFile` (form-data)    | `Club`                      |
| `POST` | `/my-club`                               | Create a club for the current admin.              | `ClubCreateForAdmin`        | `Club`                      |
| `GET`  | `/club/{club_id}/dashboard-summary`      | Get a dashboard summary for a club.               | - (Query)                   | `DashboardSummary`          |


</rewritten_file> 