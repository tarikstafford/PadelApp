from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("", response_model=schemas.LeaderboardResponse)
def get_leaderboard(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
):
    """
    Retrieve a leaderboard of users, sorted by ELO rating.
    """
    leaderboard_data = crud.leaderboard_crud.get_leaderboard_users(db, skip=skip, limit=limit)
    users = leaderboard_data["data"]
    total = leaderboard_data["total"]

    formatted_users = []
    for user in users:
        club_name = None
        if user.club_admin_entries and user.club_admin_entries[0].club:
            club_name = user.club_admin_entries[0].club.name
            
        formatted_users.append(
            schemas.LeaderboardUserResponse(
                id=user.id,
                full_name=user.full_name,
                avatar_url=user.profile_picture_url,
                club_name=club_name,
                elo_rating=user.elo_rating,
            )
        )

    return {
        "users": formatted_users,
        "total": total,
        "offset": skip,
        "limit": limit,
    } 