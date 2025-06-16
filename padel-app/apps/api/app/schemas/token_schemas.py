from typing import Optional
from pydantic import BaseModel
from app.models.user_role import UserRole

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None # Added refresh_token
    token_type: str = "bearer"
    role: Optional[UserRole] = None

class TokenData(BaseModel):
    sub: Optional[str] = None
    role: Optional[UserRole] = None
    token_type: Optional[str] = None

class RefreshTokenRequest(BaseModel):
    refresh_token: str 