from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app import crud, models
from app.core import security
from app.database import get_db
from app.schemas import token_schemas, user_schemas

router = APIRouter()


@router.post(
    "/register-admin",
    response_model=token_schemas.Token,
    status_code=status.HTTP_201_CREATED,
)
async def register_admin(
    user_in: user_schemas.AdminUserCreate, db: Session = Depends(get_db)
):
    """
    Create a new club admin user and return tokens.
    """
    db_user = crud.user_crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Create the user with the CLUB_ADMIN role
    user_to_create = user_schemas.UserCreate(
        email=user_in.email,
        password=user_in.password,
        full_name=user_in.full_name,
        role=models.UserRole.CLUB_ADMIN,
    )
    new_user = crud.user_crud.create_user(db=db, user=user_to_create)

    # Generate tokens
    access_token = security.create_access_token(
        subject=new_user.email, role=new_user.role.value
    )
    refresh_token = security.create_refresh_token(subject=new_user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": new_user.role,
    }


@router.post(
    "/register", response_model=token_schemas.Token, status_code=status.HTTP_201_CREATED
)
async def register_new_user(
    user_in: user_schemas.UserCreate, db: Session = Depends(get_db)
):
    """
    Create new user and return tokens for immediate login.
    """
    db_user = crud.user_crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )

    # Ensure role is set to PLAYER if not provided
    if not user_in.role:
        user_in.role = models.UserRole.PLAYER

    new_user = crud.user_crud.create_user(db=db, user=user_in)

    # Generate tokens
    access_token = security.create_access_token(
        subject=new_user.email, role=new_user.role.value
    )
    refresh_token = security.create_refresh_token(subject=new_user.email)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": new_user.role,
    }


@router.post("/login", response_model=token_schemas.Token)
async def login_for_access_token(
    user_in: user_schemas.UserLogin, db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token and refresh token.
    """
    user = crud.user_crud.get_user_by_email(db, email=user_in.email)
    if not user or not security.verify_password(user_in.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user"
        )

    access_token = security.create_access_token(
        subject=user.email,  # Using email as subject for simplicity, user.id is
                        # also common
        role=user.role.value,
    )
    refresh_token = security.create_refresh_token(
        subject=user.email, role=user.role.value
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
    }


@router.get("/users/me", response_model=user_schemas.User)
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user),
):
    """
    Get current user's profile.
    """
    return current_user


@router.post("/refresh-token", response_model=token_schemas.Token)
async def refresh_access_token(
    token_request: token_schemas.RefreshTokenRequest,
):
    """
    Refresh an access token using a valid refresh token.
    """
    try:
        payload = security.decode_token_payload(token_request.refresh_token)
        if not payload or payload.token_type != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: type mismatch or decoding failed",
                headers={"WWW-Authenticate": "Bearer"},
            )

        # Subject should be present if decode_token_payload was successful and
        # checked for sub
        if payload.sub is None or payload.role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: subject or role missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access_token = security.create_access_token(
            subject=payload.sub, role=payload.role
        )
    except HTTPException:  # Re-raise HTTPExceptions from decode_token_payload
        raise
    except Exception as e:
        # Catch any other unexpected errors during refresh token processing
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing refresh token: {e!s}",
        )
    else:
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            "refresh_token": token_request.refresh_token,
            "role": payload.role,
        }
