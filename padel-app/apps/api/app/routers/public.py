import logging
from datetime import date
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app import crud, schemas
from app.database import get_db

router = APIRouter()


@router.get("/games", response_model=list[schemas.Game])
async def read_public_games(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    target_date: Optional[date] = Query(
        None, description="Filter public games by a specific date (YYYY-MM-DD)"
    ),
    future_only: bool = Query(
        True, description="Only show games in the future (default: true)"
    ),
):
    """
    Retrieve a list of public games that have available slots.
    """
    try:
        logging.info(
            f"Fetching public games: skip={skip}, limit={limit}, target_date={target_date}"
        )
        public_games = crud.game_crud.get_public_games(
            db=db, skip=skip, limit=limit, target_date=target_date, future_only=future_only
        )
        logging.info(f"Successfully fetched {len(public_games)} public games")
        return public_games
    except Exception as e:
        logging.error(f"Error fetching public games: {e!s}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Failed to fetch public games: {e!s}"
        )
