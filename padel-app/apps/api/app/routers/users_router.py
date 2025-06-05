from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app import crud, models, schemas # For models.User, schemas.User
from app.database import get_db
from app.core import security # For get_current_active_user

router = APIRouter()

@router.get("/search", response_model=List[schemas.User])
async def search_for_users(
    query: str = Query(..., min_length=1, description="Search query for user name or email"),
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=50),
    db: Session = Depends(get_db),
    current_user: models.User = Depends(security.get_current_active_user) # Ensure only authenticated users can search
):
    """
    Search for users by name or email. 
    Excludes the current authenticated user from the search results.
    """
    if not query.strip():
        # Or return empty list, or raise bad request for empty query if desired.
        # For now, returning empty list if query is just whitespace.
        return [] 
        
    users = crud.user_crud.search_users(
        db=db, query=query, current_user_id=current_user.id, skip=skip, limit=limit
    )
    return users

# Other user-specific (non-auth) endpoints could go here in the future,
# e.g., GET /users/{user_id} to get a public profile (if such a feature exists). 