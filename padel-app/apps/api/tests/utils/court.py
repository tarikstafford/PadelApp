from faker import Faker
from sqlalchemy.orm import Session

from app import crud
from app.models.court import Court, SurfaceType
from app.schemas.court_schemas import CourtCreate

fake = Faker()


def create_random_court(db: Session, club_id: int) -> Court:
    court_in = CourtCreate(
        name=f"Court {fake.random_int(min=1, max=20)}",
        surface_type=SurfaceType.ARTIFICIAL_GRASS,
        club_id=club_id,
    )
    return crud.court_crud.create_court(db=db, court_in=court_in)
