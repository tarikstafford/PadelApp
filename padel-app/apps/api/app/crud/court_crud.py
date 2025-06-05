from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.court import Court as CourtModel
# from app.schemas.court_schemas import CourtCreate, CourtUpdate # For future C/U operations

def get_court(db: Session, court_id: int) -> Optional[CourtModel]:
    """Retrieve a single court by its ID."""
    return db.query(CourtModel).filter(CourtModel.id == court_id).first()

def get_courts_by_club(
    db: Session, 
    club_id: int, 
    skip: int = 0, 
    limit: int = 50 # Default limit for courts per club, can be adjusted
) -> List[CourtModel]:
    """Retrieve a list of courts for a specific club with pagination."""
    return (
        db.query(CourtModel)
        .filter(CourtModel.club_id == club_id)
        .order_by(CourtModel.name) # Default sort by court name
        .offset(skip)
        .limit(limit)
        .all()
    )

# Placeholder for create_court
# def create_court(db: Session, court: CourtCreate, club_id: int) -> CourtModel:
#     db_court = CourtModel(**court.model_dump(), club_id=club_id)
#     db.add(db_court)
#     db.commit()
#     db.refresh(db_court)
#     return db_court

# Placeholder for update_court
# def update_court(db: Session, db_court: CourtModel, court_in: CourtUpdate) -> CourtModel:
#     update_data = court_in.model_dump(exclude_unset=True)
#     for key, value in update_data.items():
#         setattr(db_court, key, value)
#     db.add(db_court)
#     db.commit()
#     db.refresh(db_court)
#     return db_court 