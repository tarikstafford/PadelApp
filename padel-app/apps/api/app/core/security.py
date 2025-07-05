from datetime import datetime, timedelta, timezone
from typing import Any, Optional, Union

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session

# Import moved inside function to avoid circular import
from app.core.config import settings
from app.database import get_db  # To get db session for get_current_user
from app.models.user import User as UserModel  # Renamed to avoid conflict
from app.schemas.token_schemas import TokenData

# OAuth2PasswordBearer scheme, points to the token URL (login endpoint)
# The tokenUrl doesn't prevent this scheme from being used for other token
# types (like Bearer)
# It's more for documentation and OpenAPI specification.
reusable_oauth2 = OAuth2PasswordBearer(tokenUrl=f"{settings.API_V1_STR}/auth/login")

# Configure the password hashing context
# We'll use bcrypt as it's a strong and widely recommended algorithm
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)


def create_access_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    role: Optional[str] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )

    to_encode = {"exp": expire, "sub": str(subject), "token_type": "access"}
    if role:
        to_encode["role"] = role

    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(
    subject: Union[str, Any],
    expires_delta: Optional[timedelta] = None,
    role: Optional[str] = None,
) -> str:
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.REFRESH_TOKEN_EXPIRE_MINUTES
        )
    to_encode = {"exp": expire, "sub": str(subject), "token_type": "refresh"}
    if role:
        to_encode["role"] = role
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def decode_token_payload(token: str) -> Optional[TokenData]:
    """
    Decodes the JWT token and returns the payload if valid.
    Raises HTTPException for invalid tokens (expired, bad signature, etc.).
    """
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        # Ensure that 'sub' (subject) and 'exp' (expiration) are present
        if payload.get("sub") is None or payload.get("exp") is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Could not validate credentials: malformed token payload",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Pydantic will also validate the types (e.g. exp is int)
        return TokenData(
            sub=payload["sub"],
            role=payload.get("role"),
            token_type=payload.get("token_type"),
        )

        # Check if token is expired
        # Note: jwt.decode already checks 'exp' claim by default if present.
        # However, an explicit check or custom leeway might be desired in some
        # scenarios.
        # For now, we trust jwt.decode to handle expiration based on 'exp'.
        # If jwt.decode raises JWTError for expiration, it will be caught below.

    except JWTError as e:
        # Handles expired signature, invalid signature, etc.
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Could not validate credentials: {e!s}",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except Exception as e:  # Catch any other unexpected errors during decoding
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Error decoding token: {e!s}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_user(
    db: Session = Depends(get_db), token: str = Depends(reusable_oauth2)
) -> UserModel:
    token_payload = decode_token_payload(token)
    if not token_payload or not token_payload.sub:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Could not validate credentials: subject missing in token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if token_payload.token_type != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type, expected access token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    from app import crud  # Import here to avoid circular import
    user = crud.user_crud.get_user_by_email(db, email=token_payload.sub)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


async def get_current_active_user(
    current_user: UserModel = Depends(get_current_user),
) -> UserModel:
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


async def get_current_admin_user(
    current_user: UserModel = Depends(get_current_active_user),
) -> UserModel:
    """Dependency to ensure current user has admin privileges"""
    from app.models.user_role import UserRole
    
    if current_user.role not in [UserRole.ADMIN, UserRole.SUPER_ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not enough permissions. Admin access required."
        )
    return current_user
