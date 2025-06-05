from fastapi import APIRouter, Depends, HTTPException, status, File, UploadFile
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app import crud, models, schemas # schemas will have User, UserCreate, Token, UserUpdate
from app.core import security
from app.database import get_db
from app.services import file_service # Import file_service

router = APIRouter()

@router.post("/register", response_model=schemas.User, status_code=status.HTTP_201_CREATED)
async def register_new_user(
    user_in: schemas.UserCreate, 
    db: Session = Depends(get_db)
):
    """
    Create new user.
    """
    db_user = crud.user_crud.get_user_by_email(db, email=user_in.email)
    if db_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered",
        )
    created_user = crud.user_crud.create_user(db=db, user=user_in)
    return created_user

@router.post("/login", response_model=schemas.Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    """
    OAuth2 compatible token login, get an access token and refresh token.
    """
    user = crud.user_crud.get_user_by_email(db, email=form_data.username)
    if not user or not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Inactive user"
        )
    
    access_token = security.create_access_token(
        subject=user.email # Using email as subject for simplicity, user.id is also common
    )
    refresh_token = security.create_refresh_token(
        subject=user.email
    )
    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }

@router.post("/refresh-token", response_model=schemas.Token)
async def refresh_access_token(
    token_request: schemas.RefreshTokenRequest,
    # db: Session = Depends(get_db) # Not strictly needed if refresh token is self-contained and not stored/revoked in DB
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
        
        # Subject should be present if decode_token_payload was successful and checked for sub
        if payload.sub is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token: subject missing",
                headers={"WWW-Authenticate": "Bearer"},
            )

        new_access_token = security.create_access_token(subject=payload.sub)
        return {
            "access_token": new_access_token,
            "token_type": "bearer",
            # Optionally, decide if a new refresh token should be issued (token rotation)
            # For simplicity, we are not rotating refresh tokens here.
            "refresh_token": None # Or omit if your Token schema allows it to be optional
        }
    except HTTPException as e: # Re-raise HTTPExceptions from decode_token_payload
        raise e
    except Exception as e:
        # Catch any other unexpected errors during refresh token processing
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error processing refresh token: {str(e)}",
        ) 

@router.get("/users/me", response_model=schemas.User)
async def read_users_me(
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Fetch the current logged in user.
    """
    return current_user

@router.put("/users/me", response_model=schemas.User)
async def update_user_me(
    user_in: schemas.UserUpdate,
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user)
):
    """
    Update current user.
    """
    try:
        updated_user = crud.user_crud.update_user(db=db, db_user=current_user, user_in=user_in)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )
    return updated_user

@router.post("/users/me/profile-picture", response_model=schemas.User)
async def upload_profile_picture(
    current_user: models.User = Depends(security.get_current_active_user),
    db: Session = Depends(get_db),
    file: UploadFile = File(...)
):
    """
    Upload a profile picture for the current user.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Invalid file type. Only images are allowed.")

    try:
        file_url = file_service.save_profile_picture(file=file, user_id=current_user.id)
        
        # Create UserUpdate schema instance with the new profile picture URL
        user_update_data = schemas.UserUpdate(profile_picture_url=file_url)
        
        # Update the user in the database
        updated_user = crud.user_crud.update_user(db=db, db_user=current_user, user_in=user_update_data)
        
        return updated_user
    except IOError as e:
        raise HTTPException(status_code=500, detail=f"Could not save profile picture: {e}")
    except ValueError as e: # If crud.update_user raises an error (e.g. during other validations)
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        # Log the exception e for debugging
        print(f"Unexpected error during profile picture upload: {e}")
        raise HTTPException(status_code=500, detail="An unexpected error occurred during profile picture upload.") 