import cloudinary
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from app.core.config import settings
from app.routers import (
    auth_router,
    clubs_router,
    courts_router,
    bookings_router,
    games_router,
    users_router,
    admin_router,
    leaderboard_router,
    public_router,
)
from app.routers.tournaments import router as tournaments_router
from app.middleware.auth import AuthenticationMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="API for the PadelGo application to manage bookings, players, and games.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Standard practice to version OpenAPI spec
)

# Add Authentication Middleware
app.add_middleware(AuthenticationMiddleware)

# Custom exception handler for Pydantic validation errors
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    try:
        body_str = exc.body.decode('utf-8')
    except (AttributeError, UnicodeDecodeError):
        body_str = "Could not decode request body"

    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": body_str},
    )

# Set all CORS enabled origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files directory
static_files_path = Path(__file__).parent / "static"
app.mount("/static", StaticFiles(directory=static_files_path), name="static")

# Include the authentication router
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(clubs_router, prefix=f"{settings.API_V1_STR}/clubs", tags=["Clubs"]) # Corrected tag
app.include_router(courts_router, prefix=f"{settings.API_V1_STR}/courts", tags=["Courts"]) # Added courts_router
app.include_router(bookings_router, prefix=f"{settings.API_V1_STR}/bookings", tags=["Bookings"]) # Added bookings_router
app.include_router(games_router, prefix=f"{settings.API_V1_STR}/games", tags=["Games"]) # Added games_router
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"]) # Added users_router
app.include_router(admin_router, prefix=f"{settings.API_V1_STR}/admin", tags=["Admin"])
app.include_router(leaderboard_router, prefix=f"{settings.API_V1_STR}/leaderboard", tags=["Leaderboard"])
app.include_router(public_router, prefix=f"{settings.API_V1_STR}/public", tags=["Public"])
app.include_router(tournaments_router, prefix=f"{settings.API_V1_STR}")

@app.on_event("startup")
async def startup_event():
    """Initializes Cloudinary configuration on application startup."""
    cloudinary.config(
        cloud_name=settings.CLOUDINARY_CLOUD_NAME,
        api_key=settings.CLOUDINARY_API_KEY,
        api_secret=settings.CLOUDINARY_API_SECRET,
        secure=True,
    )

@app.get("/")
async def read_root():
    """Root endpoint to check if the API is running."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"} 