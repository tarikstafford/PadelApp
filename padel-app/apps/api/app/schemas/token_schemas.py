from typing import Optional
from pydantic import BaseModel

class Token(BaseModel):
    access_token: str
    refresh_token: Optional[str] = None # Added refresh_token
    token_type: str = "bearer"

class TokenPayload(BaseModel):
    sub: Optional[str] = None # Subject of the token (e.g., user_id or email)
    exp: Optional[int] = None # Expiry time (timestamp)
    token_type: Optional[str] = None # To differentiate between access and refresh tokens if needed in payload 

class RefreshTokenRequest(BaseModel):
    refresh_token: str 