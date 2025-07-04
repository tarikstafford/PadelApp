from faker import Faker
from sqlalchemy.orm import Session

from app import crud
from app.models.user import User
from app.schemas.user_schemas import UserCreate

fake = Faker()


def create_random_user(db: Session) -> User:
    email = fake.email()
    password = fake.password()
    user_in = UserCreate(email=email, password=password, full_name=fake.name())
    return crud.user_crud.create_user(db=db, user_in=user_in)
