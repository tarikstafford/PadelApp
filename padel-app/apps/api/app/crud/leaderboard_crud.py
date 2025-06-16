from sqlalchemy.orm import Session, joinedload
from app import models

def get_leaderboard_users(db: Session, skip: int = 0, limit: int = 100):
    users = db.query(models.User).options(joinedload(models.User.club)).order_by(models.User.elo_rating.desc()).offset(skip).limit(limit).all()
    total = db.query(models.User).count()
    return {"data": users, "total": total, "offset": skip, "limit": limit} 