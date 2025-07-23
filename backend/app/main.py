"""
Main FastAPI application
"""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import settings
from .database import db
from .routers import persons, schools, search, tournaments, wrestlers

print("🔥 FastAPI app is starting!")

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    if settings.database_url:
        try:
            await db.connect()
            print("🚀 Application started with database connection")
        except Exception as e:
            print(f"⚠️ Failed to connect to database: {e}")
            print("📝 Running without database connection")
    else:
        print("📝 No database URL configured, running without database")
    yield
    # Shutdown
    if db.pool:
        await db.disconnect()
        print("🔌 Database connection closed")


app = FastAPI(
    title="NCAA Wrestling API",
    description="API for NCAA wrestling data with wrestler search and profiles",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "https://louden-swain-grogs84-grogs84s-projects.vercel.app",
        "https://*.vercel.app",  # Allow all Vercel preview deployments
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",  # Better wildcard support
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(persons.router, prefix="/api/persons", tags=["persons"])
app.include_router(wrestlers.router, prefix="/api/wrestlers", tags=["wrestlers"])
app.include_router(schools.router, prefix="/api/schools", tags=["schools"])
app.include_router(tournaments.router, prefix="/api/tournaments", tags=["tournaments"])
app.include_router(search.router, prefix="/api", tags=["search"])


@app.get("/")
async def root():
    return {"message": "NCAA Wrestling API", "version": "1.0.0"}


@app.get("/health")
async def health_check():
    return {"status": "healthy"}
