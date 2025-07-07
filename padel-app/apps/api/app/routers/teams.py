from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import crud, models, schemas
from app.core import security
from app.crud.team_crud import team_crud
from app.database import get_db

router = APIRouter()


@router.get("/{team_id}", response_model=schemas.Team)
async def get_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get a specific team by ID.
    """
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user has access to this team
    # For now, allow access to any team (public view)
    # In the future, this could be restricted to team members only
    return team


@router.post("/{team_id}/join")
async def join_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Join a team.
    """
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is already in the team
    if current_user in team.players:
        raise HTTPException(status_code=400, detail="You are already in this team")
    
    # Add the user to the team
    team_crud.add_player_to_team(db=db, team=team, user=current_user)
    return {"message": "Successfully joined the team"}