from typing import Optional, Any, List
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.core.security import get_password_hash, verify_password
from app.models.user import User as UserModel # Alias to avoid confusion with Pydantic User schema
from app.schemas.user_schemas import UserCreate, UserUpdate

def get_user(db: Session, user_id: int) -> Optional[UserModel]:
    """Retrieve a user by their ID."""
    return db.query(UserModel).filter(UserModel.id == user_id).first()

def get_user_by_email(db: Session, email: str) -> Optional[UserModel]:
    """Retrieve a user by their email address."""
    return db.query(UserModel).filter(UserModel.email == email).first()

def create_user(db: Session, user: UserCreate) -> UserModel:
    """Create a new user in the database."""
    hashed_password = get_password_hash(user.password)
    db_user = UserModel(
        email=user.email,
        hashed_password=hashed_password,
        name=user.name,
        is_active=user.is_active if user.is_active is not None else True,
        role=user.role
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def update_user(db: Session, db_user: UserModel, user_in: UserUpdate) -> UserModel:
    """Update a user's details."""
    update_data = user_in.model_dump(exclude_unset=True) # Pydantic V2

    if "password" in update_data and update_data["password"]:
        hashed_password = get_password_hash(update_data["password"])
        db_user.hashed_password = hashed_password
        del update_data["password"] # Avoid setting it directly via setattr
    
    # Prevent changing email to one that already exists by another user
    if "email" in update_data and update_data["email"] != db_user.email:
        existing_user = get_user_by_email(db, email=update_data["email"])
        if existing_user and existing_user.id != db_user.id:
            raise ValueError("An account with this email already exists.")

    for field, value in update_data.items():
        setattr(db_user, field, value)
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def search_users(
    db: Session, 
    query: str, 
    current_user_id: int, 
    skip: int = 0, 
    limit: int = 20
) -> List[UserModel]:
    """Search for users by name or email, excluding the current user."""
    search_term = f"%{query}%"
    return (
        db.query(UserModel)
        .filter(
            UserModel.id != current_user_id, # Exclude the current user
            or_(
                UserModel.name.ilike(search_term),
                UserModel.email.ilike(search_term)
            )
        )
        .offset(skip)
        .limit(limit)
        .all()
    )

# Placeholder for user update - can be expanded later
# def update_user(db: Session, user: UserModel, user_in: UserUpdate) -> UserModel:
#     ... 