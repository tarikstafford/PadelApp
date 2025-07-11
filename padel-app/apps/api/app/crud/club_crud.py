from typing import Optional

from sqlalchemy import asc, desc  # For sorting
from sqlalchemy.orm import Session

from app.models.club import Club as ClubModel
from app.schemas.club_schemas import ClubCreate, ClubUpdate  # For future C/U operations


def get_club(db: Session, club_id: int) -> Optional[ClubModel]:
    """Retrieve a single club by its ID."""
    return db.query(ClubModel).filter(ClubModel.id == club_id).first()


def get_clubs(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    name: Optional[str] = None,
    city: Optional[str] = None,
    sort_by: Optional[str] = None,  # e.g., "name", "city"
    sort_desc: bool = False,
) -> list[ClubModel]:
    """Retrieve a list of clubs with pagination, filtering, and sorting."""
    query = db.query(ClubModel)

    if name:
        query = query.filter(
            ClubModel.name.ilike(f"%{name}%")
        )  # Case-insensitive search
    if city:
        query = query.filter(ClubModel.city.ilike(f"%{city}%"))

    if sort_by:
        column_to_sort = getattr(ClubModel, sort_by, None)
        if column_to_sort is not None:  # Check if attribute exists and is valid
            if sort_desc:
                query = query.order_by(desc(column_to_sort))
            else:
                query = query.order_by(asc(column_to_sort))
        else:
            # Default sort or log warning if sort_by field is invalid
            query = query.order_by(
                ClubModel.id
            )  # Default sort by ID if sort_by is invalid
    else:
        query = query.order_by(ClubModel.id)  # Default sort

    return query.offset(skip).limit(limit).all()


def create_club(db: Session, club: ClubCreate) -> ClubModel:
    """Create a new club."""
    db_club = ClubModel(**club.model_dump(exclude={"owner_id"}), owner_id=club.owner_id)
    db.add(db_club)
    db.commit()
    db.refresh(db_club)
    return db_club


def update_club(db: Session, db_obj: ClubModel, obj_in: ClubUpdate) -> ClubModel:
    """Update a club's details."""
    update_data = obj_in.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_obj, field, value)
    db.add(db_obj)
    db.commit()
    db.refresh(db_obj)
    return db_obj
