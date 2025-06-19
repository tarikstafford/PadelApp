from typing import List, Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import date

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
    public_games = crud.game_crud.get_public_games(
        db=db, skip=skip, limit=limit, target_date=target_date
    )
    return public_games 