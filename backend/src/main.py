"""
Main FastAPI application entry point
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .api.admin import router as admin_router
from .api.auth import router as auth_router
from .api.matches import router as matches_router
from .api.participants import router as participants_router
from .api.tournaments import router as tournaments_router
from .core.config import settings
from .core.database import close_db, init_db
from .schemas.base import APIResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan events"""
    # Startup
    try:
        # Only initialize database if DATABASE_URL is set to a real database
        if not settings.database_url.startswith("postgresql+asyncpg://user:password"):
            await init_db()
            print("Database initialized successfully")
        else:
            print("Skipping database initialization (using default config)")
    except Exception as e:
        print(f"Database initialization failed: {e}")

    yield

    # Shutdown
    try:
        if not settings.database_url.startswith("postgresql+asyncpg://user:password"):
            await close_db()
            print("Database connections closed")
        else:
            print("Skipping database cleanup (using default config)")
    except Exception as e:
        print(f"Database cleanup failed: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.api_title,
    description=settings.api_description,
    version=settings.api_version,
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routers
app.include_router(auth_router.router, prefix="/api/auth", tags=["authentication"])
app.include_router(
    tournaments_router.router, prefix="/api/tournaments", tags=["tournaments"]
)
app.include_router(matches_router.router, prefix="/api/matches", tags=["matches"])
app.include_router(
    participants_router.router, prefix="/api/participants", tags=["participants"]
)
app.include_router(admin_router.router, prefix="/api/admin", tags=["admin"])


@app.get("/")
async def root():
    """Root endpoint"""
    return APIResponse.success(
        {
            "message": "Wrestling Tournament Management API",
            "version": settings.api_version,
            "environment": settings.environment,
        }
    )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return APIResponse.success(
        {
            "status": "healthy",
            "service": "wrestling-tournament-api",
            "version": settings.api_version,
        }
    )
