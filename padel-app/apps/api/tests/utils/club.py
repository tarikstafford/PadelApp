from faker import Faker
from sqlalchemy.orm import Session

from app import crud
from app.models.club import Club
from app.schemas.club_schemas import ClubCreate

fake = Faker()


def create_random_club(db: Session, owner_id: int) -> Club:
    club_in = ClubCreate(
        name=fake.company(),
        description=fake.text(),
        address=fake.street_address(),
        city=fake.city(),
        postal_code=fake.postcode(),
        phone=fake.phone_number(),
        email=fake.company_email(),
    )
    return crud.club_crud.create_club(db=db, club_in=club_in, owner_id=owner_id)
