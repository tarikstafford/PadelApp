from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import models, schemas
from app.core import security
from app.crud.game_score_crud import game_score_crud
from app.database import get_db
from app.models.game_score import ScoreStatus
from app.schemas.game_score_schemas import (
    AdminScoreResolutionRequest,
    GameScoreListResponse,
    ScoreConfirmationRequest,
    ScoreConfirmationResponse,
    ScoreCounterRequest,
    ScoreStatusResponse,
    ScoreSubmissionRequest,
    ScoreSubmissionResponse,
)
from app.services.elo_rating_service import elo_rating_service
from app.services.notification_service import notification_service

router = APIRouter()


@router.post("/games/{game_id}/scores", response_model=ScoreSubmissionResponse)
async def submit_game_score(
    game_id: int,
    score_request: ScoreSubmissionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Submit a score for a completed game"""

    # Check if user can submit score
    can_submit, message = game_score_crud.can_submit_score(db, game_id, current_user.id)
    if not can_submit:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Verify user is on the team they claim to be submitting for
    user_team = game_score_crud.get_user_team_for_game(db, game_id, current_user.id)
    if user_team != score_request.submitted_by_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You are not a member of team {score_request.submitted_by_team}",
        )

    # Create the score submission
    score_data = schemas.game_score_schemas.GameScoreCreate(
        game_id=game_id,
        team1_score=score_request.team1_score,
        team2_score=score_request.team2_score,
        submitted_by_team=score_request.submitted_by_team,
    )

    game_score = game_score_crud.create_game_score(
        db=db, score_data=score_data, submitted_by_user_id=current_user.id
    )

    # Send notifications to opposing team
    notification_service.send_score_submitted_notifications(
        db=db,
        game_id=game_id,
        score_id=game_score.id,
        submitting_team=score_request.submitted_by_team,
    )

    # Check if other team can now confirm

    return ScoreSubmissionResponse(
        success=True,
        message="Score submitted successfully. Waiting for confirmation from opposing team.",
        score=game_score,
        can_confirm=False,  # Submitter cannot confirm their own score
    )


@router.post(
    "/games/{game_id}/scores/{score_id}/confirm",
    response_model=ScoreConfirmationResponse,
)
async def confirm_game_score(
    game_id: int,
    score_id: int,
    confirmation_request: ScoreConfirmationRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Confirm a submitted score"""

    # Check if user can confirm this score
    can_confirm, message = game_score_crud.can_confirm_score(
        db, score_id, current_user.id
    )
    if not can_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Get user's team
    user_team = game_score_crud.get_user_team_for_game(db, game_id, current_user.id)
    if not user_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a participant in this game",
        )

    # Confirm the score
    game_score = game_score_crud.confirm_score(
        db=db,
        score_id=score_id,
        confirming_team=user_team,
        confirming_user_id=current_user.id,
    )

    if not game_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Score not found"
        )

    is_final = game_score.status == ScoreStatus.CONFIRMED

    if is_final:
        # Score is now confirmed by both teams - update ELO ratings
        await _update_elo_ratings_for_confirmed_score(db, game_score)

        # Send confirmation notifications to all players
        notification_service.send_score_confirmed_notifications(db, game_id)

        message = "Score confirmed by both teams! ELO ratings have been updated."
    else:
        message = (
            "Score confirmation recorded. Waiting for confirmation from other team."
        )

    return ScoreConfirmationResponse(
        success=True, message=message, score=game_score, is_final=is_final
    )


@router.post(
    "/games/{game_id}/scores/{score_id}/counter",
    response_model=ScoreConfirmationResponse,
)
async def counter_game_score(
    game_id: int,
    score_id: int,
    counter_request: ScoreCounterRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Dispute/counter a submitted score"""

    # Check if user can confirm this score (same permissions as confirming)
    can_confirm, message = game_score_crud.can_confirm_score(
        db, score_id, current_user.id
    )
    if not can_confirm:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=message)

    # Get user's team
    user_team = game_score_crud.get_user_team_for_game(db, game_id, current_user.id)
    if not user_team:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You are not a participant in this game",
        )

    # Counter the score
    game_score = game_score_crud.counter_score(
        db=db,
        score_id=score_id,
        confirming_team=user_team,
        confirming_user_id=current_user.id,
        counter_team1_score=counter_request.counter_team1_score,
        counter_team2_score=counter_request.counter_team2_score,
        counter_notes=counter_request.counter_notes,
    )

    if not game_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Score not found"
        )

    # Send dispute notifications
    notification_service.send_score_submitted_notifications(
        db=db,
        game_id=game_id,
        score_id=score_id,
        submitting_team=user_team,  # The disputing team becomes the "submitter" of the counter
    )

    return ScoreConfirmationResponse(
        success=True,
        message="Score disputed. The original submitting team can now review your counter-proposal.",
        score=game_score,
        is_final=False,
    )


@router.get("/games/{game_id}/scores", response_model=GameScoreListResponse)
async def get_game_scores(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Get all score submissions for a game"""

    # Verify user is participant in the game
    user_team = game_score_crud.get_user_team_for_game(db, game_id, current_user.id)
    if not user_team:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view scores for games you participated in",
        )

    scores = game_score_crud.get_game_scores_by_game(db, game_id)
    latest_score = game_score_crud.get_latest_game_score(db, game_id)

    return GameScoreListResponse(
        scores=scores, total_count=len(scores), latest_score=latest_score
    )


@router.get("/games/{game_id}/scores/status", response_model=ScoreStatusResponse)
async def get_score_status(
    game_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """Get score submission status for a game"""

    user_team = game_score_crud.get_user_team_for_game(db, game_id, current_user.id)
    if not user_team:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only check status for games you participated in",
        )

    can_submit, submit_message = game_score_crud.can_submit_score(
        db, game_id, current_user.id
    )
    latest_score = game_score_crud.get_latest_game_score(db, game_id)

    can_confirm = False
    if latest_score:
        can_confirm, _ = game_score_crud.can_confirm_score(
            db, latest_score.id, current_user.id
        )

    message = submit_message
    if latest_score:
        if latest_score.status == ScoreStatus.PENDING:
            if can_confirm:
                message = "Score submitted by opposing team. Please confirm or dispute."
            else:
                message = "Score submitted. Waiting for opposing team confirmation."
        elif latest_score.status == ScoreStatus.CONFIRMED:
            message = "Score confirmed by both teams."
        elif latest_score.status == ScoreStatus.DISPUTED:
            message = "Score is disputed. Waiting for resolution."
        elif latest_score.status == ScoreStatus.RESOLVED:
            message = "Score dispute has been resolved by admin."

    return ScoreStatusResponse(
        can_submit=can_submit,
        can_confirm=can_confirm,
        message=message,
        user_team=user_team,
        latest_score=latest_score,
    )


@router.post(
    "/admin/scores/{score_id}/resolve", response_model=ScoreConfirmationResponse
)
async def admin_resolve_disputed_score(
    score_id: int,
    resolution_request: AdminScoreResolutionRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_admin_user),
):
    """Admin endpoint to resolve disputed scores"""

    game_score = game_score_crud.resolve_disputed_score(
        db=db,
        score_id=score_id,
        final_team1_score=resolution_request.final_team1_score,
        final_team2_score=resolution_request.final_team2_score,
        admin_notes=resolution_request.admin_notes,
    )

    if not game_score:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Score not found"
        )

    # Update ELO ratings with resolved score
    await _update_elo_ratings_for_confirmed_score(db, game_score)

    # Send notifications to all players
    notification_service.send_score_confirmed_notifications(db, game_score.game_id)

    return ScoreConfirmationResponse(
        success=True,
        message="Score dispute resolved by admin. ELO ratings have been updated.",
        score=game_score,
        is_final=True,
    )


async def _update_elo_ratings_for_confirmed_score(db: Session, game_score):
    """Update ELO ratings for all players based on confirmed score"""
    game = game_score.game

    if not game.team1 or not game.team2:
        return

    # Determine winning and losing teams
    winning_team_number = game_score.get_winning_team()
    if winning_team_number == 0:
        return  # Tie game, no ELO update

    if winning_team_number == 1:
        winning_players = game.team1.players
        losing_players = game.team2.players
    else:
        winning_players = game.team2.players
        losing_players = game.team1.players

    # Use existing ELO service to update ratings
    elo_rating_service.update_ratings(winning_players, losing_players, 1, 0)
