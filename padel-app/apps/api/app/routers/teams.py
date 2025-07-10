from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.core import security
from app.crud.team_crud import team_crud
from app.database import get_db
from app.models.team_membership import TeamMembershipRole
from app.schemas.team_schemas import (
    AddPlayerRequest,
    TeamMembershipResponse,
    TeamMembershipUpdate,
    TeamGameHistoryResponse,
    TeamStatsResponse,
)

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
    player_request: AddPlayerRequest,
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
    user_to_add = (
        db.query(models.User).filter(models.User.id == player_request.user_id).first()
    )
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
            detail="Cannot remove yourself as the only team member. Delete the team instead.",
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
            detail="Cannot leave as the only team member. Delete the team instead.",
        )

    # Remove the user from the team
    team.players.remove(current_user)
    db.commit()
    return {"message": "Successfully left the team"}


# New Team Membership Management Endpoints

@router.post("/{team_id}/members", response_model=TeamMembershipResponse)
async def add_team_member(
    team_id: int,
    member_request: AddPlayerRequest,
    role: TeamMembershipRole = TeamMembershipRole.MEMBER,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Add a member to a team. Only team admins/owners can add members.
    """
    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if current user is admin/owner
    if not team_crud.is_team_admin(db=db, team_id=team_id, user_id=current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only team admins and owners can add members",
        )

    # Check if user exists
    user_to_add = db.query(models.User).filter(models.User.id == member_request.user_id).first()
    if not user_to_add:
        raise HTTPException(status_code=404, detail="User not found")

    # Add the member
    membership = team_crud.add_team_member(
        db=db, team_id=team_id, user_id=member_request.user_id, role=role
    )

    if not membership:
        raise HTTPException(
            status_code=400, detail="User is already a member of this team"
        )

    return membership


@router.delete("/{team_id}/members/{user_id}")
async def remove_team_member(
    team_id: int,
    user_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Remove a member from a team. Only team admins/owners can remove members.
    Members can remove themselves.
    """
    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check permissions: admin/owner OR removing self
    is_admin = team_crud.is_team_admin(db=db, team_id=team_id, user_id=current_user.id)
    is_removing_self = current_user.id == user_id

    if not (is_admin or is_removing_self):
        raise HTTPException(
            status_code=403,
            detail="Only team admins/owners can remove members, or you can remove yourself",
        )

    # Check if user to remove exists in the team
    if not team_crud.is_team_member(db=db, team_id=team_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="User is not a member of this team")

    # Remove the member
    success = team_crud.remove_team_member(db=db, team_id=team_id, user_id=user_id)

    if not success:
        raise HTTPException(
            status_code=400, detail="Failed to remove member from team"
        )

    return {"message": "Member removed successfully"}


@router.put("/{team_id}/members/{user_id}", response_model=TeamMembershipResponse)
async def update_team_member_role(
    team_id: int,
    user_id: int,
    role_update: TeamMembershipUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Update a team member's role. Only team owners can update roles.
    """
    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if current user is owner
    current_membership = (
        db.query(models.TeamMembership)
        .filter(
            models.TeamMembership.team_id == team_id,
            models.TeamMembership.user_id == current_user.id,
            models.TeamMembership.is_active == True,
        )
        .first()
    )

    if not current_membership or current_membership.role != TeamMembershipRole.OWNER:
        raise HTTPException(
            status_code=403,
            detail="Only team owners can update member roles",
        )

    # Check if user to update exists in the team
    if not team_crud.is_team_member(db=db, team_id=team_id, user_id=user_id):
        raise HTTPException(status_code=404, detail="User is not a member of this team")

    # Update the role
    if role_update.role:
        membership = team_crud.update_team_member_role(
            db=db, team_id=team_id, user_id=user_id, new_role=role_update.role
        )

        if not membership:
            raise HTTPException(
                status_code=400, detail="Failed to update member role"
            )

        return membership

    raise HTTPException(status_code=400, detail="No role specified for update")


@router.get("/{team_id}/members", response_model=list[TeamMembershipResponse])
async def get_team_members(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get all members of a team. Only team members can view the member list.
    """
    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if current user is a member
    if not team_crud.is_team_member(db=db, team_id=team_id, user_id=current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only team members can view the member list",
        )

    # Get team members
    members = team_crud.get_team_members(db=db, team_id=team_id)
    return members


@router.get("/{team_id}/history", response_model=list[TeamGameHistoryResponse])
async def get_team_history(
    team_id: int,
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get team's game history. Only team members can view the history.
    """
    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if current user is a member
    if not team_crud.is_team_member(db=db, team_id=team_id, user_id=current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only team members can view the team history",
        )

    # Get team history
    history = team_crud.get_team_history(db=db, team_id=team_id, limit=limit)
    return history


@router.get("/{team_id}/stats", response_model=TeamStatsResponse)
async def get_team_stats(
    team_id: int,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get team statistics. Only team members can view the stats.
    """
    # Check if team exists
    team = team_crud.get_team(db=db, team_id=team_id)
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    # Check if current user is a member
    if not team_crud.is_team_member(db=db, team_id=team_id, user_id=current_user.id):
        raise HTTPException(
            status_code=403,
            detail="Only team members can view the team stats",
        )

    # Get team stats
    stats = team_crud.get_team_stats(db=db, team_id=team_id)
    if not stats:
        raise HTTPException(status_code=404, detail="Team stats not found")

    return stats
