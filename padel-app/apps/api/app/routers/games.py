from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from datetime import date

from app import crud, models, schemas # For models.User, schemas (GameCreate, GameResponse)
from app.database import get_db
from app.core import security # For get_current_active_user
from app.models.game_player import GamePlayerStatus # For setting initial player status
from app.models.game import GameType # Import GameType for checking public games

router = APIRouter()

@router.post("/", response_model=schemas.GameResponse, status_code=status.HTTP_201_CREATED)
async def create_new_game(
    game_in: schemas.GameCreate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
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
            detail=f"Booking with id {game_in.booking_id} not found."
        )
    # 2. Authorization: Only booking owner can create a game for it
    if booking.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to create a game for this booking."
        )
    
    # 3. Check if a game already exists for this booking
    existing_game = db.query(models.Game).filter(models.Game.booking_id == game_in.booking_id).first()
    if existing_game:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"A game already exists for booking id {game_in.booking_id}."
        )

    # 4. Create the game
    created_game_orm = crud.game_crud.create_game(db=db, game_in=game_in)

    # 5. Add the creator as the first player with status ACCEPTED
    crud.game_player_crud.add_player_to_game(
        db=db, 
        game_id=created_game_orm.id, 
        user_id=current_user.id, 
        status=GamePlayerStatus.ACCEPTED
    )

    # 6. Fetch the game again with players for the response model
    # The get_game CRUD function is designed to eager load players and their user details.
    game_with_players = crud.game_crud.get_game(db, game_id=created_game_orm.id)
    if not game_with_players: # Should not happen if creation was successful
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to retrieve created game details.")
        
    return game_with_players


@router.get("/{game_id}", response_model=schemas.GameResponse)
async def read_game_details(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Retrieve details for a specific game, including its players and their statuses.
    Ensures the current user is a participant of the game.
    """
    game = crud.game_crud.get_game(db, game_id=game_id) # This eager loads players.players.user
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    # Authorization: Check if the current user is part of the game
    is_participant = any(gp.user_id == current_user.id for gp in game.players)
    
    # Alternative: if game creator should always have access, even if not in GamePlayers (though they are auto-added)
    # booking_owner_id = game.booking.user_id # Accessing via game.booking relationship
    # if not is_participant and current_user.id != booking_owner_id: 

    if not is_participant:
        # A stricter check might be: if not is_participant and current_user.id != game.booking.user_id:
        # However, game.booking might not be loaded by default by get_game. For now, just participant check.
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Not authorized to access this game's details."
        )
        
    return game 

MAX_PLAYERS_PER_GAME = 4 # Define a constant for max players

@router.post("/{game_id}/invitations", response_model=schemas.GamePlayerResponse, status_code=status.HTTP_201_CREATED)
async def invite_player_to_game(
    game_id: int,
    invite_request: schemas.UserInviteRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Invite a player to a specific game.
    """
    game = crud.game_crud.get_game(db, game_id=game_id) # Eager loads booking and players.player
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    # Authorization: Only the game creator (booking owner) can invite players
    if not game.booking or game.booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the game creator can invite players.")

    # Validation: User to be invited exists
    user_to_invite = crud.user_crud.get_user(db, user_id=invite_request.user_id_to_invite)
    if not user_to_invite:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User to invite not found.")

    # Validation: Cannot invite self
    if user_to_invite.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot invite yourself to the game.")

    # Validation: Check if user is already part of the game (invited, accepted, etc.)
    existing_game_player = crud.game_player_crud.get_game_player(db, game_id=game_id, user_id=user_to_invite.id)
    if existing_game_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"User {user_to_invite.email} is already part of this game with status: {existing_game_player.status.value}"
        )
    
    # Validation: Check if game is full (e.g., 4 accepted players)
    accepted_players_count = sum(1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED)
    if accepted_players_count >= MAX_PLAYERS_PER_GAME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is already full.")

    # Add player to game with INVITED status
    new_game_player_orm = crud.game_player_crud.add_player_to_game(
        db=db, game_id=game_id, user_id=user_to_invite.id, status=GamePlayerStatus.INVITED
    )
    
    # For the response, we need to manually construct the GamePlayerResponse
    # because the add_player_to_game returns the ORM model, and we need the nested UserSchema.
    # Fetching the user again for simplicity, or one could pass the user_to_invite ORM model to a modified add_player_to_game
    # that constructs the GamePlayer ORM with the full User model for the relationship.
    # However, the `get_game` used in `read_game_details` already handles this eager loading.
    # For now, let's return a simplified response or refetch the game player with its user.
    # A simpler approach for now might be to return the ORM object, and let Pydantic handle it if User schema is available on GamePlayer.player

    # To ensure the response_model `schemas.GamePlayerResponse` is correctly populated, 
    # especially the nested `user: schemas.User`, we need to ensure the `player` relationship 
    # on `new_game_player_orm` is populated with a full User ORM object.
    # The `add_player_to_game` currently does not do this. 
    # Let's refetch the GamePlayer instance after creation to ensure relationships are loaded or directly assign.
    
    # Simplest for now, though less efficient: refetch GamePlayer to ensure relations for Pydantic.
    # More efficient: ensure add_player_to_game populates the 'player' relationship directly or allow Pydantic to handle if User schema is compatible.
    # For now, assuming GamePlayerResponse needs the User object loaded for the player field.
    db.refresh(new_game_player_orm, attribute_names=["player"]) # Attempt to refresh the 'player' relationship
    if not new_game_player_orm.player: # If refresh didn't populate, manually set (less ideal) or ensure it does
        new_game_player_orm.player = user_to_invite # Assign the fetched User ORM model

    return new_game_player_orm 

@router.put("/{game_id}/invitations/{invited_user_id}", response_model=schemas.GamePlayerResponse)
async def respond_to_game_invitation(
    game_id: int,
    invited_user_id: int,
    response_in: schemas.InvitationResponseRequest, # Contains new status ("accepted" or "declined")
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user) # The user responding
):
    """
    Allows an invited user to respond (accept/decline) to a game invitation.
    """
    # Authorization: User can only respond to their own invitation
    if current_user.id != invited_user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Cannot respond to an invitation for another user.")

    game_player_record = crud.game_player_crud.get_game_player(db, game_id=game_id, user_id=current_user.id)

    if not game_player_record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Invitation not found for this user and game.")

    if game_player_record.status != GamePlayerStatus.INVITED:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=f"Invitation cannot be responded to. Current status: {game_player_record.status.value}"
        )
    
    # Validate the new status from the request
    if response_in.status not in [GamePlayerStatus.ACCEPTED, GamePlayerStatus.DECLINED]:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid response status. Must be 'accepted' or 'declined'.")

    if response_in.status == GamePlayerStatus.ACCEPTED:
        # Check if game is full before accepting
        game = crud.game_crud.get_game(db, game_id=game_id) # Fetch game to count accepted players
        if not game: # Should not happen if game_player_record was found
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found.")
        
        accepted_players_count = sum(1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED)
        if accepted_players_count >= MAX_PLAYERS_PER_GAME:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot accept invitation, game is already full.")

    updated_game_player_orm = crud.game_player_crud.update_game_player_status(
        db=db, game_player=game_player_record, status=response_in.status
    )

    # TODO: Notify game creator (game.booking.user_id) about the response (accepted/declined).

    db.refresh(updated_game_player_orm, attribute_names=["player"]) # Ensure player relation is loaded for response
    if not updated_game_player_orm.player:
         updated_game_player_orm.player = current_user # Fallback if refresh didn't load it

    return updated_game_player_orm 

@router.get("/public/", response_model=List[schemas.GameResponse])
async def read_public_games(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    target_date: Optional[date] = Query(None, description="Filter public games by a specific date (YYYY-MM-DD)")
    # Add more filters like club_id, city, skill_level if needed
):
    """
    Retrieve a list of public games that have available slots.
    Supports pagination and filtering by date.
    """
    public_games = crud.game_crud.get_public_games(
        db=db, skip=skip, limit=limit, target_date=target_date
    )
    return public_games 

@router.post("/{game_id}/join", response_model=schemas.GamePlayerResponse, status_code=status.HTTP_201_CREATED)
async def request_to_join_game(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Allows an authenticated user to request to join a public game.
    Creates a GamePlayer entry with status 'requested_to_join'.
    """
    game = crud.game_crud.get_game(db, game_id=game_id) # Eager loads booking and players
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    if game.game_type != GameType.PUBLIC:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="This game is not public. Cannot request to join.")

    if not game.booking: # Should be loaded by get_game
         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Game booking details missing.")
         
    if game.booking.user_id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="You cannot request to join your own game.")

    existing_game_player = crud.game_player_crud.get_game_player(db, game_id=game_id, user_id=current_user.id)
    if existing_game_player:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are already associated with this game (status: {existing_game_player.status.value})."
        )

    accepted_players_count = sum(1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED)
    if accepted_players_count >= MAX_PLAYERS_PER_GAME:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Game is already full.")

    # Add player to game with REQUESTED_TO_JOIN status
    new_game_player_request_orm = crud.game_player_crud.add_player_to_game(
        db=db, game_id=game_id, user_id=current_user.id, status=GamePlayerStatus.REQUESTED_TO_JOIN
    )

    # TODO: Notify game creator (game.booking.user_id) about the new join request.

    db.refresh(new_game_player_request_orm, attribute_names=["player"]) 
    if not new_game_player_request_orm.player:
        new_game_player_request_orm.player = current_user
        
    return new_game_player_request_orm 

@router.put("/{game_id}/players/{player_user_id}/status", response_model=schemas.GamePlayerResponse)
async def manage_game_player_status(
    game_id: int,
    player_user_id: int, # The ID of the user whose status is being changed
    status_update: schemas.InvitationResponseRequest, # Reusing this schema as it just contains a status field
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user) # The game creator performing the action
):
    """
    Allows the game creator to manage a player's status in their game 
    (e.g., accept/decline a join request, or change other statuses if needed).
    """
    game = crud.game_crud.get_game(db, game_id=game_id) # Eager loads booking and players
    if not game:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Game not found")

    # Authorization: Only the game creator (booking owner) can manage player statuses
    if not game.booking or game.booking.user_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Only the game creator can manage player statuses for this game.")

    game_player_to_manage = crud.game_player_crud.get_game_player(db, game_id=game_id, user_id=player_user_id)
    if not game_player_to_manage:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Player not found in this game.")

    # Logic for approving/declining a REQUESTED_TO_JOIN status
    if game_player_to_manage.status == GamePlayerStatus.REQUESTED_TO_JOIN:
        if status_update.status not in [GamePlayerStatus.ACCEPTED, GamePlayerStatus.DECLINED]:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid status update for a join request. Must be 'accepted' or 'declined'.")
        
        if status_update.status == GamePlayerStatus.ACCEPTED:
            accepted_players_count = sum(1 for p in game.players if p.status == GamePlayerStatus.ACCEPTED)
            if accepted_players_count >= MAX_PLAYERS_PER_GAME:
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Cannot accept player, game is already full.")
    # Add other specific status transition validations here if needed for other use cases
    # For example, can an INVITED player be directly changed to DECLINED by creator? Or only by player?
    # For now, this endpoint is primarily for REQUESTED_TO_JOIN management.

    elif game_player_to_manage.status == GamePlayerStatus.INVITED and status_update.status == GamePlayerStatus.DECLINED:
        # Allow creator to mark an unanswered invite as declined (e.g., if player unresponsive)
        pass # Allow this transition
    # Potentially add more allowed transitions by creator if needed
    # else:
    #     raise HTTPException(
    #         status_code=status.HTTP_400_BAD_REQUEST, 
    #         detail=f"Cannot directly change player status from {game_player_to_manage.status.value} to {status_update.status.value} via this action."
    #     )

    updated_game_player_orm = crud.game_player_crud.update_game_player_status(
        db=db, game_player=game_player_to_manage, status=status_update.status
    )

    # TODO: Notify player_user_id about their status change (approved/declined join request, or other status changes by creator).

    db.refresh(updated_game_player_orm, attribute_names=["player"]) # Ensure player relation is loaded
    if not updated_game_player_orm.player:
        # This part might be tricky if player_to_manage was not the current_user
        # We need to fetch the user object for player_user_id if not already loaded on game_player_to_manage.player
        managed_user_orm = crud.user_crud.get_user(db, user_id=player_user_id)
        updated_game_player_orm.player = managed_user_orm
