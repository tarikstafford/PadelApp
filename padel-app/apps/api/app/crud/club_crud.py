from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc, asc # For sorting

from app.models.club import Club as ClubModel
from app.schemas.club_schemas import ClubCreate, ClubUpdate # For future C/U operations

def get_club(db: Session, club_id: int) -> Optional[ClubModel]:
    """Retrieve a single club by its ID."""
    return db.query(ClubModel).filter(ClubModel.id == club_id).first()

def get_clubs(
    db: Session, 
    skip: int = 0, 
    limit: int = 100, 
    name: Optional[str] = None,
    city: Optional[str] = None,
    sort_by: Optional[str] = None, # e.g., "name", "city"
    sort_desc: bool = False
) -> List[ClubModel]:
    """Retrieve a list of clubs with pagination, filtering, and sorting."""
    query = db.query(ClubModel)

    if name:
        query = query.filter(ClubModel.name.ilike(f"%{name}%")) # Case-insensitive search
    if city:
        query = query.filter(ClubModel.city.ilike(f"%{city}%"))
    
    if sort_by:
        column_to_sort = getattr(ClubModel, sort_by, None)
        if column_to_sort is not None: # Check if attribute exists and is valid
            if sort_desc:
                query = query.order_by(desc(column_to_sort))
            else:
                query = query.order_by(asc(column_to_sort))
        else:
            # Default sort or log warning if sort_by field is invalid
            query = query.order_by(ClubModel.id) # Default sort by ID if sort_by is invalid
    else:
        query = query.order_by(ClubModel.id) # Default sort

    return query.offset(skip).limit(limit).all()

# Placeholder for create_club
def create_club(db: Session, club: ClubCreate) -> ClubModel:
    db_club = ClubModel(**club.model_dump())
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club

# Placeholder for update_club
def update_club(db: Session, db_club: ClubModel, club_in: ClubUpdate) -> ClubModel:
    update_data = club_in.model_dump(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_club, key, value)
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club 