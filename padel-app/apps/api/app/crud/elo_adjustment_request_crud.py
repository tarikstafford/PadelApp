from sqlalchemy.orm import Session

from app import models, schemas


def create_elo_adjustment_request(
    db: Session,
    request: schemas.EloAdjustmentRequestCreate,
    user_id: int,
    current_elo: float,
) -> models.EloAdjustmentRequest:
    db_request = models.EloAdjustmentRequest(
        **request.dict(),
        user_id=user_id,
        status="pending",
        current_elo=current_elo,
        requested_elo=request.requested_rating,
    )
    db.add(db_request)
    db.commit()
    db.refresh(db_request)
    return db_request


def get_elo_adjustment_requests_by_user(
    db: Session, user_id: int
) -> list[models.EloAdjustmentRequest]:
    """
    Retrieve all ELO adjustment requests for a specific user.
    """
    return (
        db.query(models.EloAdjustmentRequest)
        .filter(models.EloAdjustmentRequest.user_id == user_id)
        .order_by(models.EloAdjustmentRequest.created_at.desc())
        .all()
    )
