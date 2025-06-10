from typing import List, Optional
from sqlalchemy.orm import Session

from app.models.club_admin import ClubAdmin as ClubAdminModel
from app.schemas.club_admin_schemas import ClubAdminCreate

def create_club_admin(db: Session, club_admin: ClubAdminCreate) -> ClubAdminModel:
    """Assign an admin role to a user for a specific club."""
    db_club_admin = ClubAdminModel(
        user_id=club_admin.user_id,
        club_id=club_admin.club_id
    )
    db.add(db_club_admin)
    db.commit()
    db.refresh(db_club_admin)
    return db_club_admin

def get_club_admin(db: Session, user_id: int, club_id: int) -> Optional[ClubAdminModel]:
    """Get a specific club admin entry."""
    return db.query(ClubAdminModel).filter(
        ClubAdminModel.user_id == user_id,
        ClubAdminModel.club_id == club_id
    ).first()

def get_club_admins_by_club(db: Session, club_id: int) -> List[ClubAdminModel]:
    """Get all admins for a specific club."""
    return db.query(ClubAdminModel).filter(ClubAdminModel.club_id == club_id).all()

def get_club_admins_by_user(db: Session, user_id: int) -> List[ClubAdminModel]:
    """Get all club admin entries for a specific user."""
    return db.query(ClubAdminModel).filter(ClubAdminModel.user_id == user_id).all()

def remove_club_admin(db: Session, user_id: int, club_id: int) -> Optional[ClubAdminModel]:
    """Remove an admin role from a user for a specific club."""
    db_club_admin = get_club_admin(db, user_id=user_id, club_id=club_id)
    if db_club_admin:
        db.delete(db_club_admin)
        db.commit()
    return db_club_admin 