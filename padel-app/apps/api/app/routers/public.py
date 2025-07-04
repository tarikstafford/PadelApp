from typing import List, Optional
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from datetime import date
import logging

from app import crud, schemas
from app.database import get_db

router = APIRouter()

@router.get("/games", response_model=List[schemas.Game])
async def read_public_games(
    db: Session = Depends(get_db),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=200),
    target_date: Optional[date] = Query(None, description="Filter public games by a specific date (YYYY-MM-DD)")
):
    """
    Retrieve a list of public games that have available slots.
    """
    try:
        logging.info(f"Fetching public games: skip={skip}, limit={limit}, target_date={target_date}")
        public_games = crud.game_crud.get_public_games(
            db=db, skip=skip, limit=limit, target_date=target_date
        )
        logging.info(f"Successfully fetched {len(public_games)} public games")
        return public_games
    except Exception as e:
        logging.error(f"Error fetching public games: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch public games: {str(e)}") 