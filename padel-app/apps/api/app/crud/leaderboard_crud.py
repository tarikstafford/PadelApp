from sqlalchemy.orm import Session, contains_eager
from app import models

def get_leaderboard_users(db: Session, skip: int = 0, limit: int = 100):
    query = (
        db.query(models.User)
        .outerjoin(models.ClubAdmin, models.User.id == models.ClubAdmin.user_id)
        .outerjoin(models.Club, models.ClubAdmin.club_id == models.Club.id)
        .options(contains_eager(models.User.club_admin_entries).contains_eager(models.ClubAdmin.club))
        .order_by(models.User.elo_rating.desc())
    )
    total = query.count()
    users = query.offset(skip).limit(limit).all()
    return {"data": users, "total": total, "offset": skip, "limit": limit} 