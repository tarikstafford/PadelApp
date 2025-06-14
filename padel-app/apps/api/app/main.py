import cloudinary
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

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
)
from app.middleware.auth import AuthenticationMiddleware

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="API for the PadelGo application to manage bookings, players, and games.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Standard practice to version OpenAPI spec
)

# Add Authentication Middleware
app.add_middleware(AuthenticationMiddleware)

# CORS Middleware Configuration
# This allows the frontend (running on a different domain) to communicate with the backend.
# In a real production environment, you would want to restrict origins to your actual frontend URL.
# For this project, allowing all origins is acceptable.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Temporarily allow all origins for debugging
    allow_credentials=True,
    allow_methods=["*"], # Allows all methods
    allow_headers=["*"], # Allows all headers
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