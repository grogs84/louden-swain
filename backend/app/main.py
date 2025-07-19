"""
Main FastAPI application
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from .database import db
from .routers import wrestlers, schools, tournaments, search


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await db.connect()
    yield
    # Shutdown
    await db.disconnect()


app = FastAPI(
    title="NCAA Wrestling API",
    description="API for NCAA wrestling data with wrestler search and profiles",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
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
