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


@router.post("/{team_id}/players", response_model=schemas.Team)
async def add_player_to_team(
    team_id: int,
    player_request: schemas.AddPlayerRequest,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Add a player to a team. Only team members can add players.
    """
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if current user is in the team (has permission to add players)
    if current_user not in team.players:
        raise HTTPException(
            status_code=403,
            detail="You can only add players to teams you're a member of",
        )
    
    # Get the user to add
    user_to_add = db.query(models.User).filter(models.User.id == player_request.user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is already in the team
    if user_to_add in team.players:
        raise HTTPException(status_code=400, detail="User is already in the team")
    
    # Add the user to the team
    return team_crud.add_player_to_team(db=db, team=team, user=user_to_add)


@router.delete("/{team_id}/players/{user_id}", response_model=schemas.Team)
async def remove_player_from_team(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Remove a player from a team. Only team members can remove players.
    """
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if current user is in the team (has permission to remove players)
    if current_user not in team.players:
        raise HTTPException(
            status_code=403,
            detail="You can only remove players from teams you're a member of",
        )
    
    # Get the user to remove
    user_to_remove = db.query(models.User).filter(models.User.id == user_id).first()
    if not user_to_remove:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if user is in the team
    if user_to_remove not in team.players:
        raise HTTPException(status_code=400, detail="User is not in this team")
    
    # Don't allow removing yourself if you're the only member
    if user_to_remove == current_user and len(team.players) == 1:
        raise HTTPException(
            status_code=400, 
            detail="Cannot remove yourself as the only team member. Delete the team instead."
        )
    
    # Remove the user from the team
    team.players.remove(user_to_remove)
    db.commit()
    db.refresh(team)
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


@router.post("/{team_id}/leave")
async def leave_team(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Leave a team.
    """
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    
    # Check if user is in the team
    if current_user not in team.players:
        raise HTTPException(status_code=400, detail="You are not in this team")
    
    # Don't allow leaving if you're the only member
    if len(team.players) == 1:
        raise HTTPException(
            status_code=400, 
            detail="Cannot leave as the only team member. Delete the team instead."
        )
    
    # Remove the user from the team
    team.players.remove(current_user)
    db.commit()
    return {"message": "Successfully left the team"}