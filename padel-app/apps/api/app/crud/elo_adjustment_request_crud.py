from sqlalchemy.orm import Session
from app import models, schemas

def create_elo_adjustment_request(db: Session, request: schemas.EloAdjustmentRequest, user_id: int) -> models.EloAdjustmentRequest:
    db_request = models.EloAdjustmentRequest(
        user_id=user_id,
        current_rating=db.query(models.User).filter(models.User.id == user_id).first().elo_rating,
        requested_rating=request.requested_rating,
        reason=request.reason,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request 