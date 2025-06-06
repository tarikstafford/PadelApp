from fastapi import FastAPI
# from fastapi.staticfiles import StaticFiles # No longer needed
# from pathlib import Path # No longer needed

from app.core.config import settings
from app.routers import auth_router, clubs_router, courts_router, bookings_router, games_router, users_router # Import users_router

app = FastAPI(
    title=settings.PROJECT_NAME,
    version="0.1.0",
    description="API for the PadelGo application to manage bookings, players, and games.",
    openapi_url=f"{settings.API_V1_STR}/openapi.json" # Standard practice to version OpenAPI spec
)

# Mount static files directory - REMOVED as it's not currently used
# This assumes your main.py is in app/ and you want to serve a top-level static/ directory
# relative to the api app's root (padel-app/apps/api/app/static)
# static_files_path = Path(__file__).parent / "static"
# app.mount("/static", StaticFiles(directory=static_files_path), name="static")

# Include the authentication router
app.include_router(auth_router, prefix=f"{settings.API_V1_STR}/auth", tags=["Auth"])
app.include_router(clubs_router, prefix=f"{settings.API_V1_STR}/clubs", tags=["Clubs"]) # Corrected tag
app.include_router(courts_router, prefix=f"{settings.API_V1_STR}/courts", tags=["Courts"]) # Added courts_router
app.include_router(bookings_router, prefix=f"{settings.API_V1_STR}/bookings", tags=["Bookings"]) # Added bookings_router
app.include_router(games_router, prefix=f"{settings.API_V1_STR}/games", tags=["Games"]) # Added games_router
app.include_router(users_router, prefix=f"{settings.API_V1_STR}/users", tags=["Users"]) # Added users_router

@app.get("/")
async def read_root():
    """Root endpoint to check if the API is running."""
    return {"message": f"Welcome to {settings.PROJECT_NAME}"}

@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint."""
    return {"status": "ok"} 