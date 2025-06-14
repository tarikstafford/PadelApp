from sqlalchemy.orm import Session
from app import models, schemas

def create_elo_adjustment_request(db: Session, request: schemas.EloAdjustmentRequestCreate, user_id: int) -> models.EloAdjustmentRequest:
    db_request = models.EloAdjustmentRequest(
        **request.dict(),
        user_id=user_id,
        status="pending"
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request 