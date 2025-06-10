from fastapi import Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.status import HTTP_401_UNAUTHORIZED

from app.core.security import decode_token_payload
from app.crud import user_crud
from app.database import SessionLocal

class AuthenticationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        request.state.user = None
        auth_header = request.headers.get("Authorization")
        if auth_header:
            try:
                scheme, token = auth_header.split()
                if scheme.lower() == "bearer":
                    token_payload = decode_token_payload(token)
                    if token_payload and token_payload.sub:
                        db = SessionLocal()
                        try:
                            user = user_crud.get_user_by_email(db, email=token_payload.sub)
                            request.state.user = user
                        finally:
                            db.close()
            except Exception:
                # This middleware should not block requests, just attach user if possible.
                # The authorization middleware will handle blocking.
                pass

        response = await call_next(request)
        return response 