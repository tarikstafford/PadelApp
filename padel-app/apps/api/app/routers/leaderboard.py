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
    users = crud.leaderboard_crud.get_leaderboard_users(db, skip=skip, limit=limit)
    total = crud.leaderboard_crud.get_leaderboard_users_count(db)

    formatted_users = [
        schemas.LeaderboardUserResponse(
            id=user.id,
            full_name=user.full_name,
            avatar_url=user.profile_picture_url,
            club_name=user.club.name if user.club else None,
            elo_rating=user.elo_rating,
        )
        for user in users
    ]

    return {
        "users": formatted_users,
        "total": total,
        "skip": skip,
        "limit": limit,
    } 