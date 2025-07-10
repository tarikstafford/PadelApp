import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.crud.game_invitation_crud import game_invitation_crud
from app.database import get_db
from app.models.game import GameType
from app.models.game_player import GamePlayerStatus
from app.models.team import Team
from app.schemas.game_invitation_schemas import (
    GameInvitationResponse,
    OnboardingRequiredResponse,
    TeamInviteRequest,
    TeamInvitationResponse,
)
from app.schemas.game_schemas import TeamJoinRequest
from app.crud.team_crud import team_crud
from app.services.elo_rating_service import elo_rating_service
from app.services.game_expiration_service import game_expiration_service
from app.crud.game_history_crud import game_history_crud
from app.schemas.game_history_schemas import (
    GameHistoryQuery,
    GameHistoryResponse,
    GameStatistics,
    EloProgressionResponse,
    PartnerStatistics,
)

router = APIRouter()


@router.get("/public", response_model=list[schemas.Game])
async def read_public_games_list(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    target_date: Optional[date] = Query(
        None, description="Filter public games by a specific date (YYYY-MM-DD)"
    ),
    future_only: bool = Query(
        True, description="Only show games in the future (default: true)"
    ),
    buffer_hours: Optional[int] = Query(
        None,
        ge=0,
        le=24,
        description="Hours before game start to hide from discovery (default: 1 hour)"
    ),
):
    """
    Retrieve a list of public games that have available slots for discovery.

    Games are filtered to exclude:
    - Games that are not PUBLIC
    - Games that are not SCHEDULED (completed, cancelled, expired)
    - Games that are full (4 players already accepted)
    - Games that have already started
    - Games that start within the buffer time (default 1 hour)

    By default, only shows future games unless future_only=false.
    """
    return crud.game_crud.get_public_games(
        db=db,
        skip=skip,
        limit=limit,
        target_date=target_date,
        future_only=future_only,
        buffer_hours=buffer_hours
    )


@router.post("", response_model=schemas.Game, status_code=status.HTTP_201_CREATED)
async def create_new_game(
    game_in: schemas.GameCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Create a new game session for a booking.
    The creator is automatically added as the first accepted player.
    """
    # 1. Validate the booking
    booking = crud.booking_crud.get_booking(db, booking_id=game_in.booking_id)
    if not booking:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Booking with id {game_in.booking_id} not found.",
        )
    # 2. Authorization: Only booking owner can create a game for it
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create a game for this booking.",
        )

    # 3. Check if a game already exists for this booking
    existing_game = (
        db.query(models.Game)
        .filter(models.Game.booking_id == game_in.booking_id)
        .first()
    )
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A game already exists for booking id {game_in.booking_id}.",
        )

    # 4. Create the game
    created_game_orm = crud.game_crud.create_game(
        db=db,
        game_in=game_in,
        club_id=booking.court.club_id,
        start_time=booking.start_time,
        end_time=booking.end_time,
    )

    # 5. Add the creator as the first player with status ACCEPTED
    crud.game_player_crud.add_player_to_game(
        db=db,
        game_id=created_game_orm.id,
        user_id=current_user.id,
        status=GamePlayerStatus.ACCEPTED,
    )

    # 6. Fetch the game again with players for the response model
    game_with_players = crud.game_crud.get_game(db, game_id=created_game_orm.id)
    if not game_with_players:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve created game details.",
        )

    return game_with_players


@router.get("/{game_id}", response_model=schemas.Game)
async def read_game_details(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Retrieve details for a specific game, including its players and their statuses.
    Ensures the current user is a participant of the game.
    Auto-expires the game if it's past the end time.
    """
    try:
        # Try to expire game but don't fail if there's an issue
        try:
            game_expiration_service.check_single_game_expiration(db, game_id)
        except Exception as exp_error:
            logging.warning(f"Failed to check game expiration for game {game_id}: {exp_error}")
            # Continue without failing the request

        game = crud.game_crud.get_game(db, game_id=game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
            )

        # Safe check for participants
        try:
            is_participant = False
            if game.players:
                is_participant = any(gp.user_id == current_user.id for gp in game.players)
        except Exception as e:
            logging.exception(f"Error checking participants: {e}")
            is_participant = False

        # Safe check for creator
        try:
            is_creator = False
            if game.booking and hasattr(game.booking, "user_id"):
                is_creator = game.booking.user_id == current_user.id
        except Exception as e:
            logging.exception(f"Error checking creator: {e}")
            is_creator = False

        # Check if game is public - public games can be viewed by anyone
        is_public_game = game.game_type == "PUBLIC"

        if not is_public_game and not is_participant and not is_creator:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to access this game's details.",
            )

        return game
    except HTTPException:
        # Re-raise HTTP exceptions as they are expected
        raise
    except Exception as e:
        # Log the error with full stack trace
        import traceback
        error_details = traceback.format_exc()
        logging.exception(f"Error retrieving game {game_id}: {e!s}")
        logging.exception(f"Full traceback:\n{error_details}")

        # Include more details in development/debugging
        error_message = f"Error retrieving game {game_id}: {e!s}"
        logging.exception(f"Error type: {type(e).__name__}")

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message,
        )


MAX_PLAYERS_PER_GAME = 4


@router.post(
    "/{game_id}/invitations",
    response_model=schemas.GamePlayer,
    status_code=status.HTTP_201_CREATED,
)
async def invite_player_to_game(
    game_id: int,
    invite_request: schemas.UserInviteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Invite a player to a specific game.
    """
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    if not game.booking or game.booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the game creator can invite players.",
        )

    user_to_invite = crud.user_crud.get_user(
        db, user_id=invite_request.user_id_to_invite
    )
    if not user_to_invite:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User to invite not found."
        )

    if user_to_invite.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You cannot invite yourself to the game.",
        )

    existing_game_player = crud.game_player_crud.get_game_player(
        db, game_id=game_id, user_id=user_to_invite.id
    )
    if existing_game_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User {user_to_invite.email} is already part of this game with status: {existing_game_player.status.value}",
        )

    accepted_players_count = sum(
        1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED
    )
    if accepted_players_count >= MAX_PLAYERS_PER_GAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Game is already full."
        )

    new_game_player_orm = crud.game_player_crud.add_player_to_game(
        db=db,
        game_id=game_id,
        user_id=user_to_invite.id,
        status=GamePlayerStatus.INVITED,
    )

    # Manually attach the loaded user to the relationship for the response
    new_game_player_orm.user = user_to_invite

    return new_game_player_orm


@router.put(
    "/{game_id}/invitations/{invited_user_id}", response_model=schemas.GamePlayer
)
async def respond_to_game_invitation(
    game_id: int,
    invited_user_id: int,
    response_in: schemas.InvitationResponseRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Allows an invited user to respond (accept/decline) to a game invitation.
    """
    if current_user.id != invited_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot respond to an invitation for another user.",
        )

    game_player_record = crud.game_player_crud.get_game_player(
        db, game_id=game_id, user_id=current_user.id
    )

    if not game_player_record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found for this user and game.",
        )

    if game_player_record.status != GamePlayerStatus.INVITED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invitation cannot be responded to. Current status: {game_player_record.status.value}",
        )

    if response_in.status not in [GamePlayerStatus.ACCEPTED, GamePlayerStatus.DECLINED]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid response status. Must be 'accepted' or 'declined'.",
        )

    if response_in.status == GamePlayerStatus.ACCEPTED:
        game = crud.game_crud.get_game(db, game_id=game_id)
        if not game:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Game not found."
            )

        accepted_players_count = sum(
            1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED
        )
        if accepted_players_count >= MAX_PLAYERS_PER_GAME:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot accept invitation, game is already full.",
            )

    updated_game_player_orm = crud.game_player_crud.update_game_player_status(
        db=db, game_player=game_player_record, status=response_in.status
    )

    # Manually attach the loaded user to the relationship for the response
    updated_game_player_orm.user = current_user

    return updated_game_player_orm


@router.post(
    "/{game_id}/join",
    response_model=schemas.GamePlayer,
    status_code=status.HTTP_201_CREATED,
)
async def request_to_join_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Allows an authenticated user to request to join a public game.
    """
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    if game.game_type != GameType.PUBLIC:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This game is not public."
        )

    accepted_players_count = sum(
        1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED
    )
    if accepted_players_count >= MAX_PLAYERS_PER_GAME:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Game is already full."
        )

    existing_game_player = crud.game_player_crud.get_game_player(
        db, game_id=game_id, user_id=current_user.id
    )
    if existing_game_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are already part of this game with status: {existing_game_player.status.value}",
        )

    new_game_player = crud.game_player_crud.add_player_to_game(
        db=db,
        game_id=game_id,
        user_id=current_user.id,
        status=GamePlayerStatus.ACCEPTED,
    )

    # Manually attach the loaded user to the relationship for the response
    new_game_player.user = current_user

    return new_game_player


@router.put(
    "/{game_id}/players/{player_user_id}/status", response_model=schemas.GamePlayer
)
async def manage_game_player_status(
    game_id: int,
    player_user_id: int,
    status_update: schemas.InvitationResponseRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Allows the game creator to manage the status of players who requested to join.
    """
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    if not game.booking or game.booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the game creator can manage player status.",
        )

    game_player_to_manage = crud.game_player_crud.get_game_player(
        db, game_id=game_id, user_id=player_user_id
    )
    if not game_player_to_manage:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found in this game.",
        )

    if game_player_to_manage.status != GamePlayerStatus.REQUESTED_TO_JOIN:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only manage players who have requested to join.",
        )

    if status_update.status not in [
        GamePlayerStatus.ACCEPTED,
        GamePlayerStatus.DECLINED,
    ]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid status. Must be 'accepted' or 'declined'.",
        )

    if status_update.status == GamePlayerStatus.ACCEPTED:
        accepted_players_count = sum(
            1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED
        )
        if accepted_players_count >= MAX_PLAYERS_PER_GAME:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Cannot accept player, game is full.",
            )

    updated_game_player = crud.game_player_crud.update_game_player_status(
        db=db, game_player=game_player_to_manage, status=status_update.status
    )

    # Manually attach the loaded user to the relationship for the response
    updated_game_player.user = current_user

    return updated_game_player


def validate_game_exists(db: Session, game_id: int) -> models.Game:
    game = crud.game_crud.get_game_with_teams(db, game_id=game_id)
    if not game:
        raise HTTPException(status_code=404, detail="Game not found")
    return game


def validate_game_not_scored(game: models.Game):
    if game.winning_team_id is not None:
        raise HTTPException(
            status_code=400, detail="Game result has already been submitted"
        )


def validate_winning_team(db: Session, team_id: int) -> models.Team:
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Winning team not found")
    return team


@router.post(
    "/{game_id}/result",
    response_model=schemas.GameWithRatingsResponse,
    status_code=status.HTTP_200_OK,
)
async def submit_game_result(
    game_id: int,
    result_in: schemas.GameResultRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Submit the result of a game, triggering ELO rating updates.
    """
    game = validate_game_exists(db, game_id)
    validate_game_not_scored(game)
    winning_team = validate_winning_team(db, result_in.winning_team_id)

    if game.team1_id == winning_team.id:
        losing_team = game.team2
    elif game.team2_id == winning_team.id:
        losing_team = game.team1
    else:
        raise HTTPException(
            status_code=400, detail="Winning team is not part of this game"
        )

    winning_players = winning_team.players
    losing_players = losing_team.players

    # Update ratings using EloRatingService
    elo_rating_service.update_ratings(winning_players, losing_players, 1, 0)

    # Set the winning team on the game
    game.winning_team_id = winning_team.id

    # Add the game and all updated player objects to the session
    db.add(game)
    db.add_all(winning_players)
    db.add_all(losing_players)

    # Persist all changes to the database
    db.commit()
    db.refresh(game)

    return game


# Game Invitation Endpoints


@router.post("/{game_id}/invitations/links", response_model=GameInvitationResponse)
async def create_game_invitation(
    game_id: int,
    invitation_data: schemas.GameInvitationCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Create a shareable invitation link for a game.
    Only the game creator or participants can create invitations.
    """
    # Check if game exists
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    # Check if user is authorized (game creator or participant)
    user_in_game = any(player.user_id == current_user.id for player in game.players)
    if not user_in_game:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only game participants can create invitation links",
        )

    # Create invitation
    invitation = game_invitation_crud.create_invitation(
        db=db,
        game_id=game_id,
        created_by=current_user.id,
        expires_in_hours=invitation_data.expires_in_hours,
        max_uses=invitation_data.max_uses,
    )

    # Build the invitation URL
    # Get frontend URL from environment or use a default
    import os
    base_url = os.getenv("FRONTEND_URL", "https://padelgo-frontend-production.up.railway.app")
    invite_url = f"{base_url}/games/invite/{invitation.token}"

    return GameInvitationResponse(
        id=invitation.id,
        game_id=invitation.game_id,
        token=invitation.token,
        created_at=invitation.created_at,
        expires_at=invitation.expires_at,
        is_active=invitation.is_active,
        max_uses=invitation.max_uses,
        current_uses=invitation.current_uses,
        invite_url=invite_url,
    )


@router.get("/invitations/{token}/info")
async def get_invitation_info(token: str, db: Session = Depends(get_db)):
    """
    Get public information about a game invitation.
    This endpoint doesn't require authentication and is used for preview.
    """
    invitation_info = game_invitation_crud.get_invitation_info(db, token)

    if not invitation_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitation not found or expired",
        )

    return invitation_info


@router.post("/invitations/{token}/accept")
async def accept_game_invitation(
    token: str,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Accept a game invitation and join the game.
    User must be authenticated.
    
    If user has not completed onboarding, returns special response indicating
    onboarding is required before they can join the game.
    """
    # Use the new method that checks onboarding status
    result = game_invitation_crud.accept_invitation_with_onboarding_check(
        db, token, current_user.id
    )

    if not result["success"]:
        # Check if this is an onboarding requirement
        if result.get("requires_onboarding", False):
            # Get frontend URL from environment
            import os
            base_url = os.getenv("FRONTEND_URL", "https://padelgo-frontend-production.up.railway.app")
            onboarding_url = f"{base_url}/onboarding?invitation_token={token}"

            # Return special onboarding required response
            return OnboardingRequiredResponse(
                success=False,
                message=result["message"],
                requires_onboarding=True,
                game_id=result["game_id"],
                invitation_token=result["invitation_token"],
                onboarding_redirect_url=onboarding_url
            )
        else:
            # Regular error response
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=result["message"]
            )

    return {
        "message": result["message"],
        "game_id": result["game_id"],
        "redirect_url": f"/games/{result['game_id']}",
    }


@router.delete("/{game_id}/leave")
async def leave_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Leave a game. Players can only leave if it's more than 24 hours before the start time.
    Game creators cannot leave if they are the only player.
    """
    # Check if game exists and auto-expire if needed
    game_expiration_service.check_single_game_expiration(db, game_id)

    # Check if user can leave the game
    leave_check = crud.game_player_crud.can_leave_game(db, game_id, current_user.id)

    if not leave_check["can_leave"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=leave_check["reason"]
        )

    # Remove player from game
    success = crud.game_player_crud.remove_player_from_game(
        db, game_id, current_user.id
    )

    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to leave game",
        )

    return {"message": "Successfully left the game"}


@router.post("/expire-past-games")
async def expire_past_games(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Expire all games that are past their end time.
    This endpoint can be called manually or by a scheduled job.
    """
    # TODO: Add admin role check here if needed
    # if not current_user.is_admin:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")

    expired_game_ids = game_expiration_service.expire_past_games(db)

    return {
        "message": f"Expired {len(expired_game_ids)} games",
        "expired_game_ids": expired_game_ids,
    }


@router.post("/{game_id}/join-team")
async def team_join_game(
    game_id: int,
    team_join_request: TeamJoinRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Allow a team to join a game. The requesting user must be a team admin/owner.
    This adds all team members to the game.
    """
    # Check if game exists
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    # Check if game is public and can accept more players
    if game.game_type != GameType.PUBLIC:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, detail="This game is not public"
        )

    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_join_request.team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Check if current user is team admin/owner
    if not team_crud.is_team_admin(db=db, team_id=team_join_request.team_id, user_id=current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only team admins and owners can join teams to games",
        )

    # Get team members
    team_members = team_crud.get_team_members(db=db, team_id=team_join_request.team_id)

    if not team_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Team has no active members"
        )

    # Check if game has enough slots for all team members
    accepted_players_count = sum(
        1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED
    )

    available_slots = MAX_PLAYERS_PER_GAME - accepted_players_count

    if len(team_members) > available_slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game only has {available_slots} available slots, but team has {len(team_members)} members",
        )

    # Check if any team members are already in the game
    existing_players = set(p.user_id for p in game.players)
    team_member_ids = set(member.user_id for member in team_members)

    overlap = existing_players.intersection(team_member_ids)
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some team members are already in this game",
        )

    # Add all team members to the game
    added_players = []
    for member in team_members:
        new_game_player = crud.game_player_crud.add_player_to_game(
            db=db,
            game_id=game_id,
            user_id=member.user_id,
            status=GamePlayerStatus.ACCEPTED,
        )
        added_players.append(new_game_player)

    return {
        "message": f"Team '{team.name}' successfully joined the game",
        "team_id": team.id,
        "team_name": team.name,
        "members_added": len(added_players),
        "game_id": game_id,
    }


@router.post("/{game_id}/invite-team", response_model=TeamInvitationResponse)
async def invite_team_to_game(
    game_id: int,
    team_invite_request: TeamInviteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Invite a team to a game. Only the game creator can invite teams.
    This sends invitations to all team members.
    """
    # Check if game exists
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    # Check if current user is the game creator
    if not game.booking or game.booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the game creator can invite teams",
        )

    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_invite_request.team_id)
    if not team:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Team not found"
        )

    # Get team members
    team_members = team_crud.get_team_members(db=db, team_id=team_invite_request.team_id)

    if not team_members:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Team has no active members"
        )

    # Check if game has enough slots for all team members
    accepted_players_count = sum(
        1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED
    )

    available_slots = MAX_PLAYERS_PER_GAME - accepted_players_count

    if len(team_members) > available_slots:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Game only has {available_slots} available slots, but team has {len(team_members)} members",
        )

    # Check if any team members are already in the game
    existing_players = set(p.user_id for p in game.players)
    team_member_ids = set(member.user_id for member in team_members)

    overlap = existing_players.intersection(team_member_ids)
    if overlap:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Some team members are already in this game",
        )

    # Invite all team members to the game
    invited_count = 0
    for member in team_members:
        # Check if member is already invited
        existing_game_player = crud.game_player_crud.get_game_player(
            db, game_id=game_id, user_id=member.user_id
        )

        if not existing_game_player:
            # Add team member as invited
            crud.game_player_crud.add_player_to_game(
                db=db,
                game_id=game_id,
                user_id=member.user_id,
                status=GamePlayerStatus.INVITED,
            )
            invited_count += 1

    return TeamInvitationResponse(
        message=f"Team '{team.name}' successfully invited to the game",
        team_id=team.id,
        team_name=team.name,
        invited_members=invited_count,
        game_id=game_id,
    )


# Position Management Endpoints

@router.put("/{game_id}/players/{user_id}/position", response_model=schemas.GamePlayerWithPosition)
async def update_player_position(
    game_id: int,
    user_id: int,
    position_update: schemas.GamePlayerPositionUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Update a player's position and team assignment in a game.
    Only the game creator or team admins can update positions.
    """
    # Check if game exists
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    # Check if user is authorized (game creator or participant)
    is_creator = game.booking and game.booking.user_id == current_user.id
    is_participant = any(player.user_id == current_user.id for player in game.players)

    if not is_creator and not is_participant:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only game creator or participants can update positions",
        )

    # Check if the target player exists in the game
    target_player = crud.game_player_crud.get_game_player(db, game_id, user_id)
    if not target_player:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Player not found in this game",
        )

    # Check if the target player is accepted
    if target_player.status != GamePlayerStatus.ACCEPTED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Can only assign positions to accepted players",
        )

    # Validate the position assignment
    validation = crud.game_player_crud.validate_position_assignment(
        db, game_id, user_id, position_update.position, position_update.team_side
    )

    if not validation["valid"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=validation["reason"],
        )

    # Update the position
    updated_player = crud.game_player_crud.update_player_position(
        db, game_id, user_id, position_update.position, position_update.team_side
    )

    if not updated_player:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update player position",
        )

    return updated_player


@router.get("/{game_id}/positions", response_model=list[schemas.GamePlayerWithPosition])
async def get_game_positions(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get all player positions for a game.
    """
    # Check if game exists
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    # Check if user is authorized (game creator, participant, or public game)
    is_creator = game.booking and game.booking.user_id == current_user.id
    is_participant = any(player.user_id == current_user.id for player in game.players)
    is_public_game = game.game_type == GameType.PUBLIC

    if not is_creator and not is_participant and not is_public_game:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to view this game's positions",
        )

    # Get all players with positions
    players = crud.game_player_crud.get_players_with_positions(db, game_id)

    return players


@router.post("/{game_id}/assign-positions")
async def auto_assign_positions(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Auto-assign positions to all players in a game.
    Only the game creator can auto-assign positions.
    Requires exactly 4 accepted players.
    """
    # Check if game exists
    game = crud.game_crud.get_game(db, game_id=game_id)
    if not game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Game not found"
        )

    # Check if user is authorized (only game creator)
    if not game.booking or game.booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only the game creator can auto-assign positions",
        )

    # Auto-assign positions
    result = crud.game_player_crud.auto_assign_positions(db, game_id)

    if not result["success"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=result["reason"],
        )

    return {
        "message": "Positions assigned successfully",
        "assignments": result["assignments"],
    }


# Game History Endpoints

@router.get("/history", response_model=GameHistoryResponse)
async def get_current_user_game_history(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of records to return"),
    start_date: Optional[str] = Query(None, description="Filter games from this date (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="Filter games until this date (YYYY-MM-DD)"),
    result_filter: Optional[str] = Query("ALL", description="Filter by result: ALL, WINS, LOSSES, DRAWS"),
    partner_id: Optional[int] = Query(None, description="Filter by partner user ID"),
    opponent_id: Optional[int] = Query(None, description="Filter by opponent user ID"),
    club_id: Optional[int] = Query(None, description="Filter by club ID"),
    completed_only: bool = Query(True, description="Only include completed games"),
):
    """
    Get the current user's game history with filtering and pagination.
    """
    from datetime import datetime

    # Parse dates
    start_date_parsed = None
    end_date_parsed = None

    if start_date:
        try:
            start_date_parsed = datetime.fromisoformat(start_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid start_date format. Use YYYY-MM-DD"
            )

    if end_date:
        try:
            end_date_parsed = datetime.fromisoformat(end_date)
        except ValueError:
            raise HTTPException(
                status_code=400,
                detail="Invalid end_date format. Use YYYY-MM-DD"
            )

    # Create query object
    query = GameHistoryQuery(
        skip=skip,
        limit=limit,
        start_date=start_date_parsed,
        end_date=end_date_parsed,
        result_filter=result_filter,
        partner_id=partner_id,
        opponent_id=opponent_id,
        club_id=club_id,
        completed_only=completed_only,
    )

    # Get game history
    games, total_count = game_history_crud.get_user_game_history(
        db=db,
        user_id=current_user.id,
        query=query,
    )

    has_more = (skip + limit) < total_count

    return GameHistoryResponse(
        games=games,
        total_count=total_count,
        has_more=has_more,
    )


@router.get("/history/statistics", response_model=GameStatistics)
async def get_current_user_game_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    limit_recent: int = Query(10, ge=1, le=50, description="Number of recent games to include in statistics"),
):
    """
    Get comprehensive game statistics for the current user.
    """
    return game_history_crud.get_user_game_statistics(
        db=db,
        user_id=current_user.id,
        limit_recent=limit_recent,
    )


@router.get("/history/elo-progression", response_model=EloProgressionResponse)
async def get_current_user_elo_progression(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    limit: int = Query(50, ge=1, le=200, description="Number of games to include in progression"),
):
    """
    Get ELO progression over time for the current user.
    """
    progression = game_history_crud.get_user_elo_progression(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )

    return EloProgressionResponse(progression=progression)


@router.get("/history/partners", response_model=list[PartnerStatistics])
async def get_current_user_partner_statistics(
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
    limit: int = Query(10, ge=1, le=50, description="Number of partners to return"),
):
    """
    Get statistics with different partners for the current user.
    """
    return game_history_crud.get_partner_statistics(
        db=db,
        user_id=current_user.id,
        limit=limit,
    )
